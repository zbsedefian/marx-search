from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    MetaData,
    Table,
    text,
)
from sqlalchemy.orm import sessionmaker, declarative_base

# Setup
engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Define Work model
class Work(Base):
    __tablename__ = "works"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String)
    description = Column(Text)

# Reflect existing tables
metadata = MetaData()
metadata.reflect(bind=engine)

def add_column_if_missing(table_name, column_name, column_type="INTEGER"):
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        if column_name not in table.columns:
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"))
            print(f"✅ Added '{column_name}' column to {table_name}")

# Add work_id columns
tables_to_update = ["chapters", "passages", "sections", "terms", "term_passage_link"]
for table in tables_to_update:
    add_column_if_missing(table, "work_id")

# Add chapter number column if missing
add_column_if_missing("chapters", "number")

# Create works table
Work.__table__.create(bind=engine, checkfirst=True)
print("✅ Ensured 'works' table exists")

# Insert default work
default_work = Work(title="Capital, Volume I", author="Karl Marx", description="The first volume of Capital.")
session.add(default_work)
session.commit()
print(f"✅ Inserted work: {default_work.title} with ID {default_work.id}")

# Update all tables with work_id
session.execute(text(f"UPDATE chapters SET work_id = {default_work.id}"))
works = session.execute(text("SELECT id FROM works")).fetchall()
for (wid,) in works:
    chapters = session.execute(
        text("SELECT id FROM chapters WHERE work_id = :wid ORDER BY id"),
        {"wid": wid},
    ).fetchall()
    for idx, (cid,) in enumerate(chapters, start=1):
        session.execute(
            text("UPDATE chapters SET number = :num WHERE id = :cid"),
            {"num": idx, "cid": cid},
        )
session.execute(text(f"""
    UPDATE passages
    SET work_id = (
        SELECT work_id FROM chapters WHERE chapters.id = passages.chapter
    )
"""))
session.execute(text(f"""
    UPDATE sections
    SET work_id = (
        SELECT work_id FROM chapters WHERE chapters.id = sections.chapter
    )
"""))
session.execute(text(f"UPDATE terms SET work_id = {default_work.id}"))
session.execute(text(f"""
    UPDATE term_passage_link
    SET work_id = (
        SELECT passages.work_id
        FROM passages
        WHERE passages.id = term_passage_link.passage_id
    )
"""))

session.commit()
print("✅ Set work_id across all relevant tables")
session.close()
