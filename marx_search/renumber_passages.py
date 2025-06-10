import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Passage, TermPassageLink, Chapter

# Adjust the DB URL if needed
engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)

def renumber_chapter(session, chapter: Chapter):
    """Renumber paragraphs sequentially within a chapter."""
    passages = (
        session.query(Passage)
        .filter(Passage.chapter == chapter.id)
        .order_by(Passage.paragraph)
        .all()
    )
    for idx, passage in enumerate(passages, start=1):
        if passage.paragraph == idx:
            continue
        old_id = passage.id
        new_id = re.sub(r"p\d+$", f"p{idx}", old_id)
        # Update related links
        session.query(TermPassageLink).filter(
            TermPassageLink.passage_id == old_id
        ).update({"passage_id": new_id})
        passage.id = new_id
        passage.paragraph = idx
    session.commit()


def renumber_all():
    with Session() as session:
        chapters = session.query(Chapter).order_by(Chapter.id).all()
        for ch in chapters:
            renumber_chapter(session, ch)
        print("✅ Renumbered paragraphs per chapter")


if __name__ == "__main__":
    renumber_all()
