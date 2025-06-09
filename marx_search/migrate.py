from sqlalchemy.orm import Session
from sqlalchemy import delete
from database import SessionLocal
import models
from rapidfuzz import fuzz

MATCH_THRESHOLD = 90  # You can adjust this if needed

def rebuild_term_passage_links():
    db: Session = SessionLocal()

    print("Clearing existing term-passage links...")
    db.execute(delete(models.TermPassageLink))
    db.commit()

    terms = db.query(models.Term).all()
    passages = db.query(models.Passage).all()

    print(f"Linking {len(terms)} terms against {len(passages)} passages...")

    count = 0
    for term in terms:
        term_text = term.term.lower()

        for passage in passages:
            if not passage.text:
                continue

            # Match using British spelling; exact substring match preferred, fallback to fuzzy
            if term_text in passage.text.lower() or fuzz.partial_ratio(term_text, passage.text.lower()) >= MATCH_THRESHOLD:
                link = models.TermPassageLink(term_id=term.id, passage_id=passage.id)
                db.add(link)
                count += 1

    db.commit()
    db.close()
    print(f"✅ Inserted {count} term-passage links.")

if __name__ == "__main__":
    rebuild_term_passage_links()


