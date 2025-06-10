import os
import sys
import zipfile
import tempfile
import requests
import re
from lxml import etree
from docx import Document
from docx.oxml.ns import qn
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import (
    Base,
    Work,
    Chapter,
    Section,
    Passage,
    Footnote,
)  # Make sure Footnote is defined

# Setup DB
engine = create_engine("sqlite:///capital_glossary.db")
Session = sessionmaker(bind=engine)
session = Session()


def get_input_source():
    mode = input("📥 Source: Type 'file' or 'url': ").strip().lower()
    if mode == "file":
        path = input("📄 Enter the path to the .docx file: ").strip()
        if not os.path.exists(path):
            print("❌ File not found.")
            sys.exit(1)
        return path
    elif mode == "url":
        url = input("🌐 Enter the URL to download the .docx file: ").strip()
        response = requests.get(url)
        if response.status_code != 200:
            print("❌ Failed to download file.")
            sys.exit(1)
        temp_path = tempfile.mktemp(suffix=".docx")
        with open(temp_path, "wb") as f:
            f.write(response.content)
        return temp_path
    else:
        print("❌ Invalid input.")
        sys.exit(1)


def select_work():
    """Prompt the user to choose an existing Work or create a new one."""
    update = input("🔄 Update existing work? (yes/no): ").strip().lower()
    if update == "yes":
        works = session.query(Work).order_by(Work.id).all()
        if not works:
            print("❌ No works found in the database.")
            sys.exit(1)
        print("Available works:")
        for w in works:
            print(f"{w.id}: {w.title} by {w.author}")
        selected = input("Enter the ID of the work to update: ").strip()
        try:
            work = session.get(Work, int(selected))
        except Exception:
            work = None
        if not work:
            print("❌ Work not found.")
            sys.exit(1)
        print(f"🔗 Using existing Work record with ID {work.id}")
        return work

    title = input("📘 Title of the work: ").strip()
    author = input("✍️  Author: ").strip()
    year = input("📅 Year (optional): ").strip()
    description = input("📝 Description (optional): ").strip()

    work = session.query(Work).filter_by(title=title, author=author).first()
    if work:
        print(f"🔗 Using existing Work record with ID {work.id}")
    else:
        work = Work(title=title, author=author, year=year, description=description)
        session.add(work)
        session.commit()
        print(f"✅ Created Work: {title} with ID {work.id}")
    return work


def extract_notes(docx_path):
    """Return a mapping of note id -> text for footnotes or endnotes."""
    with zipfile.ZipFile(docx_path) as z:
        xml_part = None
        note_tag = None
        try:
            xml_part = z.read("word/footnotes.xml")
            note_tag = "footnote"
        except KeyError:
            try:
                xml_part = z.read("word/endnotes.xml")
                note_tag = "endnote"
            except KeyError:
                return {}

    notes_root = etree.fromstring(xml_part)
    namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    notes = {}
    for fn in notes_root.findall(f"w:{note_tag}", namespaces):
        fn_id = fn.get(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id"
        )
        if fn_id in ("-1", "0"):
            continue
        paragraphs = fn.findall(".//w:p", namespaces)
        text = " ".join(
            "".join(node.text for node in p.iter() if node.text) for p in paragraphs
        )
        notes[fn_id] = text.strip()
    return notes


def paragraph_text_with_refs(para):
    """Return paragraph text with <sup> markers for footnote/endnote references."""
    refs = []
    parts = []
    for node in para._element.iter():
        local = etree.QName(node).localname
        if local in {"footnoteReference", "endnoteReference"}:
            fn_id = node.get(qn("w:id"))
            if fn_id:
                parts.append(f"<sup>{fn_id}</sup>")
                refs.append(fn_id)
        elif local == "t":
            if node.text:
                parts.append(node.text)
        elif local in {"tab"}:
            parts.append("\t")
        elif local in {"br", "cr"}:
            parts.append("\n")
    return "".join(parts).strip(), refs


def parse_and_store(docx_path, work):
    doc = Document(docx_path)
    footnotes = extract_notes(docx_path)
    has_footnotes = bool(footnotes)

    print("\n⚠️  This will write data to your database.")
    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("🛑 Aborted.")
        sys.exit(0)

    existing_chapters = {
        c.title: c for c in session.query(Chapter).filter_by(work_id=work.id).all()
    }
    chapter_id = (
        1
        if not existing_chapters
        else max(c.id for c in existing_chapters.values()) + 1
    )
    paragraph_id = 1
    chapter_title = f"Chapter {chapter_id}"
    chapter = existing_chapters.get(chapter_title)
    if not chapter:
        chapter = Chapter(id=chapter_id, title=chapter_title, work_id=work.id)
        session.add(chapter)
        session.commit()
    else:
        chapter_id = chapter.id

    in_notes = False
    notes_buffer = []
    last_passage_id = None

    for i, para in enumerate(doc.paragraphs):
        plain_text = para.text.strip()
        if not plain_text:
            continue

        # --- handle note parsing mode ---
        if in_notes:
            if plain_text.isupper() or plain_text.lower().startswith("chapter "):
                # flush buffered notes before starting new chapter
                for num, content in notes_buffer:
                    session.add(
                        Footnote(
                            passage_id=last_passage_id,
                            footnote_number=num,
                            content=content.strip(),
                        )
                    )
                notes_buffer = []
                in_notes = False
                # fall through to chapter handling
            else:
                m = re.match(r"^(\d+)[\).]?\s*(.*)", plain_text)
                if m:
                    notes_buffer.append([m.group(1), m.group(2)])
                elif notes_buffer:
                    notes_buffer[-1][1] += " " + plain_text
                continue

        if plain_text.isupper() or plain_text.lower().startswith("chapter "):
            # new chapter starts
            session.commit()
            chapter_id += 1
            paragraph_id = 1
            chapter_title = plain_text
            chapter = existing_chapters.get(chapter_title)
            if not chapter:
                chapter = Chapter(id=chapter_id, title=chapter_title, work_id=work.id)
                session.add(chapter)
                session.commit()
                existing_chapters[chapter_title] = chapter
            else:
                chapter_id = chapter.id
            continue

        # detect start of footnotes list
        if re.match(r"^\d+[\).]?\s+", plain_text) and paragraph_id > 1:
            in_notes = True
            m = re.match(r"^(\d+)[\).]?\s*(.*)", plain_text)
            notes_buffer.append([m.group(1), m.group(2)])
            continue

        if has_footnotes:
            text, fn_matches = paragraph_text_with_refs(para)
        else:
            text = plain_text
            fn_matches = []

        passage_id = f"{work.id}.ch{chapter_id}.p{paragraph_id}"
        last_passage_id = passage_id
        passage = session.get(Passage, passage_id)
        if passage:
            passage.text = text
        else:
            passage = Passage(
                id=passage_id,
                chapter=chapter_id,
                section=None,
                paragraph=paragraph_id,
                text=text,
                translation="moore_aveling_1887",
                work_id=work.id,
            )
            session.add(passage)

        # Add footnotes from docx refs (if any)
        for fn_id in fn_matches:
            existing_fn = (
                session.query(Footnote)
                .filter_by(passage_id=passage_id, footnote_number=fn_id)
                .first()
            )
            if existing_fn:
                existing_fn.content = footnotes.get(fn_id, "")
            else:
                session.add(
                    Footnote(
                        passage_id=passage_id,
                        footnote_number=fn_id,
                        content=footnotes.get(fn_id, ""),
                    )
                )

        paragraph_id += 1

    # flush any trailing notes at end of document
    for num, content in notes_buffer:
        session.add(
            Footnote(
                passage_id=last_passage_id,
                footnote_number=num,
                content=content.strip(),
            )
        )

    session.commit()
    print("✅ All passages and footnotes imported.")
    print("📌 Done.")


if __name__ == "__main__":
    print("📚 Marx Parser Booting Up")
    work = select_work()
    docx_path = get_input_source()
    parse_and_store(docx_path, work)
