from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
import models, schemas
import re
from rapidfuzz import process, fuzz

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/passages/{passage_id}", response_model=schemas.PassageOut)
def get_passage(passage_id: str, db: Session = Depends(get_db)):
    passage = db.query(models.Passage).filter(models.Passage.id == passage_id).first()
    if not passage:
        raise HTTPException(status_code=404, detail="Passage not found")
    return passage

@app.get("/passages/", response_model=list[schemas.PassageOut])
def list_passages(
    chapter: int = Query(None),
    section: int = Query(None),
    offset: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(models.Passage)
    if chapter is not None:
        query = query.filter(models.Passage.chapter == chapter)
    if section is not None:
        query = query.filter(models.Passage.section == section)
    return query.offset(offset).limit(limit).all()

@app.get("/terms/", response_model=list[schemas.TermOut])
def list_terms(db: Session = Depends(get_db)):
    return db.query(models.Term).all()

@app.get("/terms/{term_id}", response_model=schemas.TermOut)
def get_term(term_id: str, db: Session = Depends(get_db)):
    term = db.query(models.Term).filter(models.Term.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return term

from sqlalchemy.orm import aliased



@app.get("/terms/{term_id}/passages", response_model=list[schemas.TermPassageLinkOut])
def get_term_links(
    term_id: str,
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10
):
    offset = (page - 1) * page_size

    rows = (
        db.query(
            models.Passage.id.label("id"),
            models.TermPassageLink.passage_id,
            models.Passage.chapter,
            models.Passage.section,
            models.Passage.paragraph,
            models.Passage.text,
            models.Chapter.title.label("chapter_title"),
            models.Section.title.label("section_title"),
        )
        .join(models.Passage, models.Passage.id == models.TermPassageLink.passage_id)
        .join(models.Chapter, models.Chapter.id == models.Passage.chapter)
        .outerjoin(models.Section, (models.Section.chapter == models.Passage.chapter) & (models.Section.section == models.Passage.section))
        .filter(models.TermPassageLink.term_id == term_id)
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Truncate and rename to match response schema
    results = []
    for row in rows:
        if row.text is None:
            continue
        results.append({
            "id": row.id,
            "chapter": row.chapter,
            "section": row.section,
            "paragraph": row.paragraph,
            "text_snippet": extract_context_snippet(row.text, term_id),
            "chapter_title": row.chapter_title,
            "section_title": row.section_title
        })

    return results


def extract_context_snippet(text, term, context_words=50):
    if not text or not term:
        return ""

    # Case-insensitive search
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    match = pattern.search(text)

    if not match:
        return text[:300] + "…"  # fallback if term not found

    start_idx = match.start()
    end_idx = match.end()

    # Split text into words
    words = text.split()
    word_positions = []
    idx = 0
    for word in words:
        pos = text.find(word, idx)
        word_positions.append((word, pos))
        idx = pos + len(word)

    # Find word index of the match
    match_word_index = next(
        (i for i, (_, pos) in enumerate(word_positions) if pos >= start_idx), 0
    )

    # Get surrounding words
    start_word = max(match_word_index - context_words, 0)
    end_word = min(match_word_index + context_words + 1, len(words))

    snippet = " ".join(words[start_word:end_word])
    return snippet + "…" if end_word < len(words) else snippet


@app.get("/terms/{term_id}/passage_count")
def count_term_links(term_id: str, db: Session = Depends(get_db)):
    count = db.query(models.TermPassageLink).filter(models.TermPassageLink.term_id == term_id).count()
    return {"count": count}


@app.get("/chapters/", response_model=list[schemas.ChapterOut])
def get_chapters(db: Session = Depends(get_db)):
    return db.query(models.Chapter).order_by(models.Chapter.id).all()


@app.get("/chapters/{chapter_id}", response_model=schemas.ChapterOut)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter



@app.get("/chapter_data/{chapter_id}", response_model=schemas.ChapterDataOut)
def get_chapter_data(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    passages = db.query(models.Passage).filter(models.Passage.chapter == chapter_id).all()
    sections = db.query(models.Section).filter(models.Section.chapter == chapter_id).all()
    terms = db.query(models.Term).all()

    # Get current part (find the highest start_chapter <= current chapter)
    part = (
        db.query(models.Part)
        .filter(models.Part.start_chapter <= chapter_id)
        .order_by(models.Part.start_chapter.desc())
        .first()
    )

    prev_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id - 1).first()
    next_chapter = db.query(models.Chapter).filter(models.Chapter.id == chapter_id + 1).first()

    return {
        "title": chapter.title,
        "passages": passages,
        "sections": sections,
        "terms": terms,
        "part": {
            "number": part.number,
            "title": part.title
        } if part else None,
        "prev_chapter": {
            "id": prev_chapter.id,
            "title": prev_chapter.title
        } if prev_chapter else None,
        "next_chapter": {
            "id": next_chapter.id,
            "title": next_chapter.title
        } if next_chapter else None
    }



@app.get("/sections/", response_model=list[schemas.SectionOut])
def get_all_sections(chapter: int, db: Session = Depends(get_db)):
    query = db.query(models.Section)
    if chapter is not None:
        query = query.filter(models.Section.chapter == chapter)
    return query.order_by(models.Section.id).all()


@app.get("/sections/{section_id}", response_model=schemas.SectionOut)
def get_section(section_id: str, db: Session = Depends(get_db)):
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@app.get("/parts/", response_model=list[schemas.PartOut])
def get_parts(db: Session = Depends(get_db)):
    return db.query(models.Part).order_by(models.Part.start_chapter).all()


@app.get("/search", response_model=schemas.SearchResults)
def search(
    q: str = Query(..., min_length=2),
    exact: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q_lower = q.lower()
    offset = (page - 1) * page_size

    # -------------------------
    # Match Terms
    # -------------------------
    all_terms = db.query(models.Term).all()

    if exact:
        matching_terms = [
            term for term in all_terms if q_lower in term.term.lower()
        ]
    else:
        matching_terms = [
            term for term in all_terms
            if contains_word(term.term, q_lower) or fuzz.token_set_ratio(q_lower, term.term.lower()) > 90
        ]
    matching_terms = matching_terms[:10]

    # -------------------------
    # Match Passages
    # -------------------------
    all_passages = db.query(models.Passage).all()

    if exact:
        matched_passages = [
            p for p in all_passages if q_lower in (p.text or "").lower()
        ]
    else:
        matched_passages = [
            p for p in all_passages if fuzz.partial_ratio(q_lower, (p.text or "").lower()) > 80
        ]

    # Paginate
    total_passages = len(matched_passages)
    paginated_passages = matched_passages[offset : offset + page_size]

    # Enhance with snippet and titles
    enriched_passages = []
    for p in paginated_passages:
        chapter = db.query(models.Chapter).filter_by(id=p.chapter).first()
        section = db.query(models.Section).filter_by(chapter=p.chapter, section=p.section).first()
        enriched_passages.append({
            "id": p.id,
            "chapter": p.chapter,
            "section": p.section,
            "paragraph": p.paragraph,
            "text": p.text,
            "text_snippet": extract_context_snippet(p.text, q),
            "translation": p.translation,
            "chapter_title": chapter.title if chapter else None,
            "section_title": section.title if section else None,
        })

    return {
        "query": q,
        "terms": matching_terms,
        "passages": enriched_passages,
        "total_passages": total_passages,
        "page": page,
        "page_size": page_size,
    }

@app.get("/parts_with_chapters_sections")
def get_parts_with_chapters_sections(db: Session = Depends(get_db)):
    parts = db.query(models.Part).order_by(models.Part.number).all()
    chapters = db.query(models.Chapter).order_by(models.Chapter.id).all()
    sections = db.query(models.Section).all()

    # Map sections to chapters
    section_map = {}
    for sec in sections:
        section_map.setdefault(sec.chapter, []).append({
            "section": sec.section,
            "title": sec.title
        })

    # Group chapters by part
    result = []
    for part in parts:
        part_chapters = [
            {
                "id": ch.id,
                "title": ch.title,
                "sections": section_map.get(ch.id, [])
            }
            for ch in chapters
            if part.start_chapter <= ch.id <= part.end_chapter
        ]

        result.append({
            "number": part.number,
            "title": part.title,
            "chapters": part_chapters
        })

    return result


def extract_context_snippet(text, term, context_words=40):
    if not text:
        return ""
    words = text.split()
    term_lower = term.lower()

    for i, word in enumerate(words):
        if term_lower in word.lower():
            start = max(i - context_words, 0)
            end = min(i + context_words, len(words))
            return " ".join(words[start:end])
    return " ".join(words[:context_words * 2])

def contains_word(term_text: str, query: str) -> bool:
    """Return True if `query` is a whole word in `term_text`."""
    return re.search(rf"\b{re.escape(query)}\b", term_text, flags=re.IGNORECASE)