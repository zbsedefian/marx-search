from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Passage(Base):
    __tablename__ = "passages"
    id = Column(String, primary_key=True)
    chapter = Column(Integer)
    section = Column(Integer)
    paragraph = Column(Integer)
    text = Column(Text)
    translation = Column(String)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False)
    work = relationship("Work", backref="passages")

class Term(Base):
    __tablename__ = "terms"
    id = Column(String, primary_key=True)
    term = Column(String)
    definition = Column(Text)
    tags = Column(String)
    aliases = Column(Text)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False)
    work = relationship("Work", backref="terms")

class TermPassageLink(Base):
    __tablename__ = "term_passage_link"
    term_id = Column(String, ForeignKey("terms.id"), primary_key=True)
    passage_id = Column(String, ForeignKey("passages.id"), primary_key=True)
    text_snippet = Column(Text)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False)

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    chapter_number = Column(Integer, nullable=True)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False)
    work = relationship("Work", backref="chapters")


class Section(Base):
    __tablename__ = "sections"

    id = Column(String, primary_key=True)  # e.g. v1.ch01.sec01
    chapter = Column(Integer, nullable=False)
    section = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    work_id = Column(Integer, ForeignKey("works.id"), nullable=False)
    work = relationship("Work", backref="sections")


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    start_chapter = Column(Integer, nullable=False)
    end_chapter = Column(Integer, nullable=False)


class Work(Base):
    __tablename__ = "works"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    year = Column(String)
    description = Column(Text)

