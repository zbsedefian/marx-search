from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Part, Work, Chapter

engine = create_engine("sqlite:///marx_texts.db")
Session = sessionmaker(bind=engine)

PARTS = {
    "Capital, Volume I": [
        (1, "Commodities and Money", 1, 3),
        (2, "Transformation of Money into Capital", 4, 6),
        (3, "The Production of Absolute Surplus-Value", 7, 11),
        (4, "Production of Relative Surplus-Value", 12, 15),
        (5, "Production of Absolute and Relative Surplus-Value", 16, 18),
        (6, "Wages", 19, 22),
        (7, "The Accumulation of Capital", 23, 25),
        (8, "Primitive Accumulation", 26, 33),
    ],
    "Capital, Volume II": [
        (1, "The Metamorphoses of Capital and Their Circuits", 1, 4),
        (2, "The Turnover of Capital", 5, 15),
        (3, "The Reproduction and Circulation of the Aggregate Social Capital", 16, 21),
    ],
    "Capital, Volume III": [
        (1, "The Conversion of Surplus-Value into Profit", 1, 7),
        (2, "Transformation of Profit into Average Profit", 8, 12),
        (3, "The Law of the Tendency of the Rate of Profit to Fall", 13, 15),
        (4, "Conversion of Commodity Capital and Money Capital into Commercial Capital and Money-Dealing Capital", 16, 22),
        (5, "Division of Profit into Interest and Profit of Enterprise", 23, 36),
        (6, "Transformation of Surplus-Profit into Ground-Rent", 37, 47),
        (7, "Revenues and Their Sources", 48, 52),
    ],
}

def main():
    with Session() as session:
        for work_title, parts in PARTS.items():
            work = session.query(Work).filter(Work.title == work_title).first()
            if not work:
                print(f"⚠️ Work '{work_title}' not found, skipping.")
                continue
            chapters = (
                session.query(Chapter)
                .filter(Chapter.work_id == work.id)
                .order_by(Chapter.id)
                .all()
            )
            num_to_id = {i + 1: ch.id for i, ch in enumerate(chapters)}
            for number, title, start_num, end_num in parts:
                start_id = num_to_id.get(start_num)
                end_id = num_to_id.get(end_num)
                if start_id is None or end_id is None:
                    print(
                        f"⚠️  Chapters {start_num}-{end_num} not found for work '{work_title}', skipping part {number}."
                    )
                    continue
                exists = (
                    session.query(Part)
                    .filter(
                        Part.work_id == work.id,
                        Part.start_chapter == start_id,
                        Part.end_chapter == end_id,
                    )
                    .first()
                )
                if exists:
                    print(f"ℹ️  Part {number} for '{work_title}' already exists, skipping.")
                    continue
                part = Part(
                    number=number,
                    title=title,
                    start_chapter=start_id,
                    end_chapter=end_id,
                    work_id=work.id,
                )
                session.add(part)
                print(f"Added part {number} for '{work_title}'.")
        session.commit()
        print("✅ Parts inserted.")

if __name__ == "__main__":
    main()
