import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from models import Chapter, Section, Passage, Work
from scrape_marxists import parse_page, links_capital_vol3

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)

# Helper to ensure column exists
with engine.connect() as conn:
    cols = [row[1] for row in conn.execute(text("PRAGMA table_info(chapters)")).fetchall()]
    if "chapter_number" not in cols:
        conn.execute(text("ALTER TABLE chapters ADD COLUMN chapter_number INTEGER"))


def main():
    session = Session()

    # 1-33
    for ch in session.query(Chapter).filter(Chapter.id.between(1, 33)).order_by(Chapter.id):
        num = ch.id
        ch.chapter_number = num
        if not ch.title.startswith(f"Chapter {num}:"):
            ch.title = f"Chapter {num}: {ch.title}"

    # delete 34-100
    del_ids = list(range(34, 101))
    session.query(Passage).filter(Passage.chapter.in_(del_ids)).delete(synchronize_session=False)
    session.query(Section).filter(Section.chapter.in_(del_ids)).delete(synchronize_session=False)
    session.query(Chapter).filter(Chapter.id.in_(del_ids)).delete(synchronize_session=False)

    # 101-105
    chs = session.query(Chapter).filter(Chapter.id.between(101, 105)).order_by(Chapter.id).all()
    for i, ch in enumerate(chs, start=1):
        ch.chapter_number = i

    # 107-113
    chs = session.query(Chapter).filter(Chapter.id.between(107, 113)).order_by(Chapter.id).all()
    for i, ch in enumerate(chs, start=1):
        ch.chapter_number = i

    # 114-137
    session.query(Chapter).filter(Chapter.id == 135).delete(synchronize_session=False)
    chs = session.query(Chapter).filter(Chapter.id.between(114, 137)).order_by(Chapter.id).all()
    for i, ch in enumerate(chs, start=1):
        ch.chapter_number = i

    # scrape missing chapter parts for volume II
    work = session.query(Work).filter(Work.title == "Capital, Volume II").first()
    if work:
        urls = [
            "https://www.marxists.org/archive/marx/works/1885-c2/ch20_01.htm",
            "https://www.marxists.org/archive/marx/works/1885-c2/ch20_02.htm",
            "https://www.marxists.org/archive/marx/works/1885-c2/ch20_03.htm",
            "https://www.marxists.org/archive/marx/works/1885-c2/ch20_04.htm",
            "https://www.marxists.org/archive/marx/works/1885-c2/ch21_01.htm",
            "https://www.marxists.org/archive/marx/works/1885-c2/ch21_02.htm",
        ]
        max_id = session.query(func.max(Chapter.id)).scalar() or 0
        next_id = max_id + 1
        counts = {"chapters": 0, "sections": 0, "passages": 0}
        for url in urls:
            parse_page(session, url, next_id, work, counts)
            next_id += 1

    # remove and re-scrape incorrect chapters for Capital Volume III
    del_ids = list(range(138, 191))
    session.query(Passage).filter(Passage.chapter.in_(del_ids)).delete(synchronize_session=False)
    session.query(Section).filter(Section.chapter.in_(del_ids)).delete(synchronize_session=False)
    session.query(Chapter).filter(Chapter.id.in_(del_ids)).delete(synchronize_session=False)

    work_v3 = session.query(Work).filter(Work.title == "Capital, Volume III").first()
    if work_v3:
        urls = links_capital_vol3("https://www.marxists.org/archive/marx/works/1894-c3/")
        max_id = session.query(func.max(Chapter.id)).scalar() or 0
        next_id = max_id + 1
        counts = {"chapters": 0, "sections": 0, "passages": 0}
        for url in urls:
            parse_page(session, url, next_id, work_v3, counts)
            next_id += 1

    # 138-199
    chs = session.query(Chapter).filter(Chapter.id.between(138, 199)).order_by(Chapter.id).all()
    for i, ch in enumerate(chs, start=1):
        ch.chapter_number = i

    # custom updates
    updates = {
        106: ("Appendix", 6),
        194: ("Chapter 20: Simple Reproduction Part 1", 22),
        195: ("Chapter 20: Simple Reproduction Part 2", 23),
        196: ("Chapter 20: Simple Reproduction Part 3", 24),
        197: ("Chapter 20: Simple Reproduction Part 4", 25),
        198: ("Chapter 21: Accumulation and Reproduction on an Extended Scale", 26),
        199: ("Chapter 21: Accumulation and Reproduction on an Extended Scale", 27),
    }
    for cid, (title, num) in updates.items():
        ch = session.get(Chapter, cid)
        if ch:
            ch.title = title
            ch.chapter_number = num

    session.query(Passage).filter(Passage.chapter.in_([136, 137])).delete(synchronize_session=False)
    session.query(Section).filter(Section.chapter.in_([136, 137])).delete(synchronize_session=False)
    session.query(Chapter).filter(Chapter.id.in_([136, 137])).delete(synchronize_session=False)

    session.commit()
    session.close()

if __name__ == "__main__":
    main()
