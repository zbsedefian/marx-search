import re
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Term, Passage, TermPassageLink
from scrape_marxists import extract_context_snippet


def update_links_for_work(session: Session, work_id: int) -> int:
    """Scan passages for all terms and create TermPassageLink rows."""
    terms = session.query(Term).all()
    passages = session.query(Passage).filter(Passage.work_id == work_id).all()
    added = 0

    for passage in passages:
        text = passage.text or ""
        for term in terms:
            if not term.term:
                continue
            if not re.search(rf"\b{re.escape(term.term)}\b", text, re.IGNORECASE):
                continue
            exists = (
                session.query(TermPassageLink)
                .filter_by(term_id=term.id, passage_id=passage.id)
                .first()
            )
            if exists:
                continue
            snippet = extract_context_snippet(text, term.term)
            link = TermPassageLink(
                term_id=term.id,
                passage_id=passage.id,
                text_snippet=snippet,
                work_id=work_id,
            )
            session.add(link)
            added += 1
    session.commit()
    return added


def main() -> None:
    session = SessionLocal()
    try:
        total_added = 0
        for work_id in (2, 3):
            added = update_links_for_work(session, work_id)
            print(f"Work {work_id}: added {added} links")
            total_added += added
        print(f"Total new links added: {total_added}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
