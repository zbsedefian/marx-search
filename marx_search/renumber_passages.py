from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Passage, TermPassageLink

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)


def renumber_all():
    """Assign sequential integer IDs to all passages."""
    with Session() as session:
        passages = (
            session.query(Passage)
            .order_by(Passage.chapter, Passage.paragraph)
            .all()
        )
        for idx, passage in enumerate(passages, start=1):
            new_id = str(idx)
            if passage.id == new_id:
                continue
            old_id = passage.id
            session.query(TermPassageLink).filter(
                TermPassageLink.passage_id == old_id
            ).update({"passage_id": new_id})
            passage.id = new_id
        session.commit()
        print("✅ Passages renumbered with sequential IDs")


if __name__ == "__main__":
    renumber_all()
