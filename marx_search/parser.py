import os
import sys
import zipfile
import tempfile
import requests
from lxml import etree
from docx import Document
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, Work, Chapter, Section, Passage, Footnote  # Make sure Footnote is defined
from sqlalchemy.exc import IntegrityError

# Setup DB
engine = create_engine("sqlite:///marx_texts.db")
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


def extract_footnotes(docx_path):
    with zipfile.ZipFile(docx_path) as z:
        footnote_xml = z.read("word/footnotes.xml")
        footnotes_root = etree.fromstring(footnote_xml)

    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    footnotes = {}
    for fn in footnotes_root.findall("w:footnote", namespaces):
        fn_id = fn.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")
        if fn_id in ("-1", "0"):  # Skip separators
            continue
        paragraphs = fn.findall(".//w:p", namespaces)
        text = " ".join("".join(node.text for node in p.iter() if node.text) for p in paragraphs)
        footnotes[fn_id] = text.strip()
    return footnotes


def parse_and_store(docx_path):
    doc = Document(docx_path)
    footnotes = extract_footnotes(docx_path)

    title = input("📘 Title of the work: ").strip()
    author = input("✍️  Author: ").strip()
    year = input("📅 Year (optional): ").strip()
    description = input("📝 Description (optional): ").strip()

    print("\n⚠️  This will write data to your database.")
    confirm = input("Proceed? Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("🛑 Aborted.")
        sys.exit(0)

    work = Work(title=title, author=author, year=year, description=description)
    session.add(work)
    session.commit()
    print(f"✅ Created Work: {title} with ID {work.id}")

    chapter_id = 1
    paragraph_id = 1
    chapter_title = f"Chapter {chapter_id}"
    chapter = Chapter(id=chapter_id, title=chapter_title, work_id=work.id)
    session.add(chapter)

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue

        if text.isupper() or text.lower().startswith("chapter "):
            session.commit()
            chapter_id += 1
            paragraph_id = 1
            chapter_title = text
            chapter = Chapter(id=chapter_id, title=chapter_title, work_id=work.id)
            session.add(chapter)
            continue

        # Footnote references look like: <w:footnoteReference w:id="1"/>
        fn_matches = [fn_id for fn_id in footnotes if fn_id in text]
        for fn_id in fn_matches:
            text = text.replace(fn_id, f"<sup>{fn_id}</sup>")

        passage_id = f"{work.id}.ch{chapter_id}.p{paragraph_id}"
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

        # Add footnotes (if any)
        for fn_id in fn_matches:
            session.add(Footnote(
                passage_id=passage_id,
                footnote_number=fn_id,
                content=footnotes[fn_id]
            ))

        paragraph_id += 1

    session.commit()
    print("✅ All passages and footnotes imported.")
    print("📌 Done.")


if __name__ == "__main__":
    print("📚 Marx Parser Booting Up")
    docx_path = get_input_source()
    parse_and_store(docx_path)
