import os
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from marx_search.models import (
    Base,
    Work,
    Chapter,
    Section,
    Passage,
    Term,
    TermPassageLink,
    Part,
)
from marx_search.seed_parts import SECTIONS as PART_DEFS

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)

NEW_TERMS = {
    "Capital, Volume II": [
        "department I",
        "department II",
        "turnover time",
        "circuit of capital",
        "fixed capital",
        "circulating capital",
        "productive capital",
        "money capital",
        "annual turnover",
    ],
    "Capital, Volume III": [
        "cost-price",
        "price of production",
        "average profit",
        "commercial capital",
        "money-dealing capital",
        "interest",
        "profit of enterprise",
    ],
}


def extract_context_snippet(text: str, term: str, context_words: int = 40) -> str:
    """Return a snippet of text around the first occurrence of `term`."""
    if not text:
        return ""
    words = text.split()
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    m = pattern.search(text)
    if not m:
        return " ".join(words[: context_words * 2])
    start_word = len(text[: m.start()].split())
    end_word = len(text[: m.end()].split())
    start = max(start_word - context_words, 0)
    end = min(end_word + context_words, len(words))
    snippet = " ".join(words[start:end])
    if end < len(words):
        snippet += "…"
    return snippet


def seed_terms(session, work: Work):
    """Insert predefined terms for the given work if they don't exist."""
    terms = NEW_TERMS.get(work.title, [])
    for term_text in terms:
        term_id = term_text.lower().replace(" ", "-")
        if session.get(Term, term_id):
            continue
        t = Term(
            id=term_id,
            term=term_text,
            definition="",
            tags="",
            aliases=None,
            work_id=work.id,
        )
        session.add(t)


def insert_parts(session, work: Work):
    sections = PART_DEFS.get(work.title)
    if not sections:
        return
    chapters = (
        session.query(Chapter)
        .filter(Chapter.work_id == work.id)
        .order_by(Chapter.id)
        .all()
    )
    num_to_id = {i + 1: ch.id for i, ch in enumerate(chapters)}
    for number, title, start_num, end_num in sections:
        start_id = num_to_id.get(start_num)
        end_id = num_to_id.get(end_num)
        if start_id is None or end_id is None:
            continue
        exists = (
            session.query(Part)
            .filter(Part.start_chapter == start_id, Part.end_chapter == end_id)
            .first()
        )
        if exists:
            continue
        session.add(
            Part(
                number=number,
                title=title,
                start_chapter=start_id,
                end_chapter=end_id,
            )
        )


def extract_year(text: str) -> str | None:
    m = re.search(r"(18\d{2}|19\d{2})", text)
    return m.group(1) if m else None


def parse_index(index_url: str):
    """Return list of (full_link, label) entries and attempt to parse the year."""
    resp = requests.get(index_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    year = extract_year(soup.get_text())
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    parsed = urlparse(index_url)
    base_url = (
        index_url
        if parsed.path.endswith("/")
        else index_url[: index_url.rfind("/") + 1]
    )
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".htm") or ".htm#" in href:
            full = urljoin(base_url, href)
            if full.startswith(base_url) and full not in seen:
                entries.append((full, a.get_text(strip=True)))
                seen.add(full)
    return entries, year


def get_or_create_work(
    session,
    title: str,
    author: str,
    year: str | None = None,
    description: str | None = None,
) -> Work:
    work = session.query(Work).filter_by(title=title, author=author).first()
    if not work:
        work = Work(
            title=title, author=author, year=year, description=description
        )
        session.add(work)
        session.flush()
    return work


def parse_page(
    session,
    url: str,
    chapter_id: int,
    chapter_number: int,
    work: Work,
    counts: dict,
):
    """Download a single page and store its chapter, sections and passages."""
    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")

    header = soup.find(["h1", "h2", "h3"])
    chapter_title = (
        header.get_text(strip=True) if header else os.path.basename(url)
    )

    chapter = Chapter(
        id=chapter_id,
        chapter_number=chapter_number,
        title=chapter_title,
        work_id=work.id,
    )
    session.add(chapter)
    counts["chapters"] += 1
    session.flush()

    paragraph_id = 1
    current_section = None
    section_count = 1

    terms = session.query(Term).filter(Term.work_id == work.id).all()

    for element in soup.find_all(["h2", "h3", "p"]):
        if element.name in {"h2", "h3"}:
            if element == header:
                continue
            sec = Section(
                id=f"{work.id}.ch{chapter_id}.sec{section_count}",
                chapter=chapter_id,
                section=section_count,
                title=element.get_text(strip=True),
                work_id=work.id,
            )
            session.add(sec)
            counts["sections"] += 1
            current_section = section_count
            section_count += 1
        elif element.name == "p":
            text = element.get_text(" ", strip=True)
            if not text:
                continue
            passage = Passage(
                id=f"{work.id}.ch{chapter_id}.p{paragraph_id}",
                chapter=chapter_number,
                section=current_section,
                paragraph=paragraph_id,
                text=text,
                translation="marxists.org",
                work_id=work.id,
            )
            session.add(passage)
            counts["passages"] += 1
            session.flush()

            for term in terms:
                if re.search(rf"\b{re.escape(term.term)}\b", text, re.IGNORECASE):
                    snippet = extract_context_snippet(text, term.term)
                    session.add(
                        TermPassageLink(
                            term_id=term.id,
                            passage_id=passage.id,
                            text_snippet=snippet,
                            work_id=work.id,
                        )
                    )
                    counts["links"] += 1
            paragraph_id += 1


def scrape_work(
    session,
    index_url: str,
    title: str,
    author: str,
    year: str | None = None,
    description: str | None = None,
    links: list[str] | None = None,
):
    """Download passages from marxists.org and store them in the DB."""
    print(f"\nScraping {title} -> {index_url}")

    toc_links, detected_year = parse_index(index_url)
    if not year:
        year = detected_year
    if links is None:
        links = [u for u, _ in toc_links] or [index_url]

    work = get_or_create_work(session, title, author, year, description)
    seed_terms(session, work)

    max_id = session.query(func.max(Chapter.id)).scalar() or 0
    next_id = max_id + 1
    max_num = (
        session.query(func.max(Chapter.chapter_number))
        .filter(Chapter.work_id == work.id)
        .scalar()
        or 0
    )
    next_num = max_num + 1

    counts = {"chapters": 0, "sections": 0, "passages": 0, "links": 0}
    for link in links:
        try:
            parse_page(session, link, next_id, next_num, work, counts)
            next_id += 1
            next_num += 1
        except Exception as e:
            print(f"⚠️  Failed to scrape {link}: {e}")
            session.rollback()

    print(
        f"Ready to insert {counts['chapters']} chapters, {counts['sections']} sections,"
        f" {counts['passages']} passages and {counts['links']} term links for '{title}'"
        f" ({year or 'unknown'})."
    )
    insert_parts(session, work)
    confirm = input("Commit to database? [y/N]: ").strip().lower()
    if confirm == "y":
        session.commit()
        print(f"✅ Committed {title}\n")
    else:
        session.rollback()
        print("❌ Aborted, rolled back changes\n")


def collect_numeric_anchors(url: str) -> list[str]:
    """Return links to numeric anchors within a given page."""
    anchors: list[str] = []
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        names = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#"):
                name = href[1:]
                if re.fullmatch(r"\d+(?:\.\d+)*", name):
                    names.add(name)
        for name in sorted(
            names, key=lambda s: [int(p) for p in s.split(".")]
        ):
            anchors.append(f"{url}#{name}")
    except Exception:
        pass
    return anchors


def links_capital_vol2(base: str) -> list[str]:
    links = [urljoin(base, "ch00.htm#1885"), urljoin(base, "ch00.htm#1893")]
    for i in range(1, 21):
        chapter_url = urljoin(base, f"ch{i:02d}.htm")
        links.append(chapter_url)
        links.extend(collect_numeric_anchors(chapter_url))

    ch21_01 = urljoin(base, "ch21_01.htm")
    links.append(ch21_01)
    links.extend(collect_numeric_anchors(ch21_01))

    ch21_02 = urljoin(base, "ch21_02.htm")
    links.append(ch21_02)
    links.extend(collect_numeric_anchors(ch21_02))

    return links


def links_capital_vol3(base: str) -> list[str]:
    links = [urljoin(base, "pref.htm")]
    for i in range(1, 53):
        links.append(urljoin(base, f"ch{i:02d}.htm"))
    for anchor in ["intro", "law", "stock"]:
        links.append(urljoin(base, f"supp.htm#{anchor}"))
    return links


if __name__ == "__main__":
    works = [
        {
            "url": "https://www.marxists.org/archive/marx/works/1875/gotha/",
            "title": "Critique of the Gotha Program",
            "author": "Karl Marx",
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1848/communist-manifesto/",
            "title": "Manifesto of the Communist Party",
            "author": "Karl Marx",
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1885-c2/",
            "title": "Capital, Volume II",
            "author": "Karl Marx",
            "links": links_capital_vol2(
                "https://www.marxists.org/archive/marx/works/1885-c2/"
            ),
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1894-c3/",
            "title": "Capital, Volume III",
            "author": "Karl Marx",
            "links": links_capital_vol3(
                "https://www.marxists.org/archive/marx/works/1894-c3/"
            ),
        },
    ]

    for w in works:
        with Session() as session:
            scrape_work(
                session,
                w["url"],
                w["title"],
                w["author"],
                links=w.get("links"),
            )

    print("\n✅ Done scraping all works.")
