import os
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models import Base, Work, Chapter, Section, Passage

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)


def extract_year(text: str) -> str | None:
    m = re.search(r"(18\d{2}|19\d{2})", text)
    return m.group(1) if m else None


def parse_index(index_url: str):
    """Return list of (full_link, label) entries and attempt to parse the year."""
    resp = requests.get(index_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    year = extract_year(soup.get_text())
    entries = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".htm") or ".htm#" in href:
            full = urljoin(index_url, href)
            entries.append((full, a.get_text(strip=True)))
    return entries, year


def get_or_create_work(session, title: str, author: str, year: str | None = None, description: str | None = None) -> Work:
    work = session.query(Work).filter_by(title=title, author=author).first()
    if not work:
        work = Work(title=title, author=author, year=year, description=description)
        session.add(work)
        session.flush()
    return work


def parse_page(session, url: str, chapter_id: int, work: Work, counts: dict):
    """Download a single page and store its chapter, sections and passages."""
    page = requests.get(url)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")

    header = soup.find(["h1", "h2", "h3"])
    chapter_title = header.get_text(strip=True) if header else os.path.basename(url)

    chapter = Chapter(id=chapter_id, title=chapter_title, work_id=work.id)
    session.add(chapter)
    counts["chapters"] += 1
    session.flush()

    paragraph_id = 1
    current_section = None
    section_count = 1

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
                chapter=chapter_id,
                section=current_section,
                paragraph=paragraph_id,
                text=text,
                translation="marxists.org",
                work_id=work.id,
            )
            session.add(passage)
            counts["passages"] += 1
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

    max_id = session.query(func.max(Chapter.id)).scalar() or 0
    next_id = max_id + 1

    counts = {"chapters": 0, "sections": 0, "passages": 0}
    for link in links:
        try:
            parse_page(session, link, next_id, work, counts)
            next_id += 1
        except Exception as e:
            print(f"⚠️  Failed to scrape {link}: {e}")

    print(
        f"Ready to insert {counts['chapters']} chapters, {counts['sections']} sections,"
        f" {counts['passages']} passages for '{title}' ({year or 'unknown'})."
    )
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
        for name in sorted(names, key=lambda s: [int(p) for p in s.split(".")]):
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
            "links": links_capital_vol2("https://www.marxists.org/archive/marx/works/1885-c2/"),
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1894-c3/",
            "title": "Capital, Volume III",
            "author": "Karl Marx",
            "links": links_capital_vol3("https://www.marxists.org/archive/marx/works/1894-c3/"),
        },
    ]

    for w in works:
        with Session() as session:
            scrape_work(session, w["url"], w["title"], w["author"], links=w.get("links"))

    print("\n✅ Done scraping all works.")

