from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Passage(Base):
    __tablename__ = "passages"
    id = Column(String, primary_key=True)
    volume = Column(Integer)
    chapter = Column(Integer)
    section = Column(Integer)
    paragraph = Column(Integer)
    text = Column(Text)
    translation = Column(String)

class Term(Base):
    __tablename__ = "terms"
    id = Column(String, primary_key=True)
    term = Column(String)
    definition = Column(Text)
    tags = Column(String)
    aliases = Column(Text)

class TermPassageLink(Base):
    __tablename__ = "term_passage_link"
    term_id = Column(String, ForeignKey("terms.id"), primary_key=True)
    passage_id = Column(String, ForeignKey("passages.id"), primary_key=True)
    text_snippet = Column(Text)

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    volume = Column(Integer, nullable=False)


class Section(Base):
    __tablename__ = "sections"

    id = Column(String, primary_key=True)  # e.g. v1.ch01.sec01
    volume = Column(Integer, nullable=False)
    chapter = Column(Integer, nullable=False)
    section = Column(Integer, nullable=False)
    title = Column(String, nullable=False)


class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    start_chapter = Column(Integer, nullable=False)
    end_chapter = Column(Integer, nullable=False)
    volume = Column(Integer, nullable=False)
