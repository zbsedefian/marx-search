import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Work, Chapter, Passage

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)
session = Session()


def get_or_create_work(title: str, author: str, year: str | None = None, description: str | None = None) -> Work:
    work = session.query(Work).filter_by(title=title, author=author).first()
    if not work:
        work = Work(title=title, author=author, year=year, description=description)
        session.add(work)
        session.commit()
    return work


def scrape_work(index_url: str, title: str, author: str, year: str | None = None, description: str | None = None):
    """Download passages from marxists.org and store them in the DB."""
    print(f"\nScraping {title} -> {index_url}")
    work = get_or_create_work(title, author, year, description)

    resp = requests.get(index_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Collect chapter links. If none found, treat index page as a single chapter.
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if re.search(r"ch\d+|chapter", href) and href.endswith(".htm"):
            links.append(urljoin(index_url, href))
    if not links:
        links = [index_url]

    existing_chapters = session.query(Chapter).filter_by(work_id=work.id).all()
    next_id = 1 if not existing_chapters else max(c.id for c in existing_chapters) + 1

    for link in links:
        page = requests.get(link)
        page.raise_for_status()
        psoup = BeautifulSoup(page.text, "html.parser")
        header = psoup.find(["h1", "h2", "h3"])
        chapter_title = header.get_text(strip=True) if header else os.path.basename(link)

        chapter = Chapter(id=next_id, title=chapter_title, work_id=work.id)
        session.add(chapter)
        session.commit()

        paragraph_id = 1
        for p in psoup.find_all("p"):
            text = p.get_text(" ", strip=True)
            if not text:
                continue
            passage = Passage(
                id=f"{work.id}.ch{next_id}.p{paragraph_id}",
                chapter=next_id,
                section=None,
                paragraph=paragraph_id,
                text=text,
                translation="marxists.org",
                work_id=work.id,
            )
            session.add(passage)
            paragraph_id += 1
        session.commit()
        next_id += 1


if __name__ == "__main__":
    works = [
        {
            "url": "https://www.marxists.org/archive/marx/works/1857/grundrisse/",
            "title": "The Grundrisse",
            "author": "Karl Marx",
            "year": "1857-1858",
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1875/gotha/ch02.htm",
            "title": "Critique of the Gotha Program",
            "author": "Karl Marx",
            "year": "1875",
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1848/communist-manifesto/",
            "title": "Manifesto of the Communist Party",
            "author": "Karl Marx",
            "year": "1848",
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1885-c2/",
            "title": "Capital, Volume II",
            "author": "Karl Marx",
            "year": "1885",
        },
        {
            "url": "https://www.marxists.org/archive/marx/works/1894-c3/",
            "title": "Capital, Volume III",
            "author": "Karl Marx",
            "year": "1894",
        },
    ]

    for w in works:
        scrape_work(w["url"], w["title"], w["author"], w.get("year"))

    print("\n✅ Done scraping all works.")
