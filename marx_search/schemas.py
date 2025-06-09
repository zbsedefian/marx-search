from typing import Optional, List

from pydantic import BaseModel

class PassageOut(BaseModel):
    id: str
    chapter: int
    section: int
    paragraph: int
    text: str
    translation: str
    work_id: int

    class Config:
        from_attributes = True

class TermOut(BaseModel):
    id: str
    term: str
    definition: str
    tags: str
    aliases: Optional[str]
    work_id: int

    class Config:
        from_attributes = True


class TermPassageLinkOut(BaseModel):
    id: str
    chapter: int
    section: Optional[int]
    paragraph: int
    text_snippet: str
    chapter_title: str
    section_title: Optional[str]
    work_id: int

    class Config:
        from_attributes = True


class ChapterOut(BaseModel):
    id: int
    title: str
    work_id: int

    class Config:
        from_attributes = True


class SectionOut(BaseModel):
    id: str
    chapter: int
    section: int
    title: str
    work_id: int

    class Config:
        from_attributes = True


class ChapterNavOut(BaseModel):
    id: int
    title: str
    work_id: int

class PartInfo(BaseModel):
    number: int
    title: str

class ChapterDataOut(BaseModel):
    title: str
    passages: List[PassageOut]
    sections: List[SectionOut]
    terms: List[TermOut]
    part: PartInfo | None = None
    prev_chapter: ChapterNavOut | None = None
    next_chapter: ChapterNavOut | None = None



class PartOut(BaseModel):
    number: int
    title: str
    start_chapter: int

    class Config:
        from_attributes = True


class WorkOut(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    year: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SearchResults(BaseModel):
    query: str
    terms: list[TermOut]
    passages: list[PassageOut]
    total_passages: int
    page: int
    page_size: int
