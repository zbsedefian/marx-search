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


@app.get("/works/", response_model=list[schemas.WorkOut])
def list_works(db: Session = Depends(get_db)):
    return db.query(models.Work).all()


@app.get("/works/{work_id}", response_model=schemas.WorkOut)
def get_work(work_id: int, db: Session = Depends(get_db)):
    work = db.query(models.Work).filter(models.Work.id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    return work


@app.get("/terms/", response_model=list[schemas.TermOut])
def list_terms(work_id: int = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Term)
    if work_id is not None:
        query = query.filter(models.Term.work_id == work_id)
    return query.all()

@app.get("/terms/{term_id}", response_model=schemas.TermOut)
def get_term(term_id: str, db: Session = Depends(get_db)):
    term = db.query(models.Term).filter(models.Term.id == term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Term not found")
    return term




@app.get("/terms/{term_id}/passages", response_model=list[schemas.TermPassageLinkOut])
def get_term_links(
    term_id: str,
    work_id: int = Query(None),
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10
):
    offset = (page - 1) * page_size

    query = (
        db.query(
            models.Passage.id.label("id"),
            models.TermPassageLink.passage_id,
            models.TermPassageLink.work_id,
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
    )
    if work_id is not None:
        query = query.filter(models.TermPassageLink.work_id == work_id)
    rows = query.offset(offset).limit(page_size).all()

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
            "section_title": row.section_title,
            "work_id": row.work_id
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
def count_term_links(term_id: str, work_id: int = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.TermPassageLink).filter(models.TermPassageLink.term_id == term_id)
    if work_id is not None:
        query = query.filter(models.TermPassageLink.work_id == work_id)
    count = query.count()
    return {"count": count}


@app.get("/chapters/", response_model=list[schemas.ChapterOut])
def get_chapters(work_id: int = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Chapter)
    if work_id is not None:
        query = query.filter(models.Chapter.work_id == work_id)
    return query.order_by(models.Chapter.id).all()


@app.get("/chapter_data/{chapter_id}", response_model=schemas.ChapterDataOut)
def get_chapter_data(
    chapter_id: int,
    work_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    chapter_query = db.query(models.Chapter).filter(models.Chapter.id == chapter_id)
    if work_id is not None:
        chapter_query = chapter_query.filter(models.Chapter.work_id == work_id)
    chapter = chapter_query.first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    passages = db.query(models.Passage).filter(models.Passage.chapter == chapter_id)
    if work_id is not None:
        passages = passages.filter(models.Passage.work_id == work_id)
    passages = passages.all()

    sections = db.query(models.Section).filter(models.Section.chapter == chapter_id)
    if work_id is not None:
        sections = sections.filter(models.Section.work_id == work_id)
    sections = sections.all()

    terms = db.query(models.Term)
    if work_id is not None:
        terms = terms.filter(models.Term.work_id == work_id)
    terms = terms.all()

    # Get current part (find the highest start_chapter <= current chapter)
    part = (
        db.query(models.Part)
        .filter(models.Part.start_chapter <= chapter_id)
        .order_by(models.Part.start_chapter.desc())
        .first()
    )

    prev_chapter_query = db.query(models.Chapter).filter(models.Chapter.id == chapter_id - 1)
    next_chapter_query = db.query(models.Chapter).filter(models.Chapter.id == chapter_id + 1)
    if work_id is not None:
        prev_chapter_query = prev_chapter_query.filter(models.Chapter.work_id == work_id)
        next_chapter_query = next_chapter_query.filter(models.Chapter.work_id == work_id)
    prev_chapter = prev_chapter_query.first()
    next_chapter = next_chapter_query.first()

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
            "title": prev_chapter.title,
            "work_id": prev_chapter.work_id
        } if prev_chapter else None,
        "next_chapter": {
            "id": next_chapter.id,
            "title": next_chapter.title,
            "work_id": next_chapter.work_id
        } if next_chapter else None
    }


@app.get("/passages/{passage_id}/footnotes", response_model=list[schemas.FootnoteOut])
def get_passage_footnotes(passage_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Footnote)
        .filter(models.Footnote.passage_id == passage_id)
        .order_by(models.Footnote.footnote_number)
        .all()
    )







@app.get("/search", response_model=schemas.SearchResults)
def search(
    q: str = Query(..., min_length=2),
    exact: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    work_id: int = Query(None),
    db: Session = Depends(get_db),
):
    q_lower = q.lower()
    offset = (page - 1) * page_size

    # -------------------------
    # Match Terms
    # -------------------------
    term_query = db.query(models.Term)
    if work_id is not None:
        term_query = term_query.filter(models.Term.work_id == work_id)
    all_terms = term_query.all()

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
    passage_query = db.query(models.Passage)
    if work_id is not None:
        passage_query = passage_query.filter(models.Passage.work_id == work_id)
    all_passages = passage_query.all()

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
            "work_id": p.work_id,
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
def get_parts_with_chapters_sections(
    work_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    parts = db.query(models.Part).order_by(models.Part.number).all()

    chapters_query = db.query(models.Chapter)
    if work_id is not None:
        chapters_query = chapters_query.filter(models.Chapter.work_id == work_id)
    chapters = chapters_query.order_by(models.Chapter.id).all()

    sections_query = db.query(models.Section)
    if work_id is not None:
        sections_query = sections_query.filter(models.Section.work_id == work_id)
    sections = sections_query.all()

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

        if part_chapters:
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
