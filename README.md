# Marx Search

This project provides a simple FastAPI backend and a React front end for
searching various Marxist texts.

## Technical

Run `migrate.py` to initialize the database or add the `work_id` column to an
existing one. By default the application uses a local SQLite database at
`marx_texts.db`.

This repository contains a small web app split into two main directories:

1. **`marx_search`** – FastAPI/SQLAlchemy backend
2. **`marx_search_frontend`** – React frontend (with Tailwind CSS)

```
marx_search/
    database.py
    main.py
    migrate.py
    models.py
    schemas.py
marx_search_frontend/
    public/
    src/
        App.js
        NavBar.js
        pages/
        components/
        darkmode/
```

## Backend Highlights
- **Database setup** – `database.py` defines the SQLite engine and `SessionLocal` used throughout the app.
- **Models** – `models.py` defines SQLAlchemy tables for passages, terms, chapters and more.
- **API routes** – `main.py` configures CORS and exposes endpoints to read passages, chapters and search terms.
- **Schemas** – `schemas.py` exposes the Pydantic response models.
- **Migration script** – `migrate.py` adds `work_id` columns and creates a default `works` entry.
- **Web scraping tool** – `scrape_marxists.py` fetches Marxist texts from marxists.org and stores them in the database.
- **Parts seeder** – `seed_parts.py` inserts high level Part records so chapters can be grouped in the table of contents.

## Frontend Highlights
- Built with React and React Router. `App.js` defines routes for the reader, glossary and search pages.
- Navigation bar with search input and dark‑mode toggle.
- Dark mode handled via a context provider.
- Key pages: `Reader.js`, `Glossary.js`, `TermDetail.js`, `SearchResults.js`.
- Tailwind configuration in `tailwind.config.js`.

## Getting Started
1. **Run the backend**: start the FastAPI app (for example via `uvicorn marx_search.main:app --reload`). Ensure the SQLite database exists.
2. **Run the frontend**: inside `marx_search_frontend/`, run `npm start` to launch the React app.
3. **Explore API endpoints**: review the routes in `main.py` to learn about the available data.
4. **Learn the data schema**: inspect `models.py` and `migrate.py` to see how tables relate.
5. **Check the React components**: look under `src/pages` and `src/components` to see how data from the API is rendered.

### Importing additional works

Run `python marx_search/scrape_marxists.py` to automatically download a set of texts from [marxists.org](https://www.marxists.org) and insert them into `marx_texts.db`. The scraper parses each work's table of contents to grab all chapter and section links. For each work you will be shown a summary of the chapters, sections and passages that will be added and asked to confirm before anything is committed. It currently ingests:
* Critique of the Gotha Program
* Manifesto of the Communist Party
* Capital, Volume II
* Capital, Volume III

After scraping new works, run `python marx_search/seed_parts.py` to populate the `parts` table. This groups chapters into logical parts for the table of contents.

### Passage numbering

Each passage now has a simple integer ID that increments across the whole
database. Paragraph numbers still restart at the beginning of each chapter and
sections are tracked only for the table of contents.  If you previously imported
data that numbered paragraphs within sections, run
`python marx_search/renumber_passages.py` to rewrite the IDs and remove the
per‑section numbering.

Currently the project contains no automated tests. Potential improvements include adding tests and expanding these instructions further.

