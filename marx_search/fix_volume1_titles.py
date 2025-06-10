import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)


def main():
    with Session() as session:
        work = session.execute(text("SELECT id FROM works WHERE title = :t"), {"t": "Capital, Volume I"}).fetchone()
        if not work:
            print("Work not found")
            return
        wid = work[0]
        chapters = session.execute(text("SELECT id, title FROM chapters WHERE work_id = :wid ORDER BY id"), {"wid": wid}).fetchall()
        for num, (cid, title) in enumerate(chapters, start=1):
            m = re.match(r"chapter\s*\d+[:.]\s*(.*)", title, flags=re.I)
            new_title = m.group(1).strip() if m else title
            session.execute(text("UPDATE chapters SET title = :title, number = :num WHERE id = :cid"), {"title": new_title, "num": num, "cid": cid})
        session.commit()
        print(f"Updated {len(chapters)} chapter titles for Volume I")


if __name__ == "__main__":
    main()
