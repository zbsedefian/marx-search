# Marx Search

This project provides a simple FastAPI backend and a React front end for
searching various Marxist texts. The backend now supports multiple works
via a `works` table and all resources can be filtered by `work_id`.

Run `migrate.py` to initialize the database or add the `work_id` column to an
existing one. By default the application uses a local SQLite database at
`marx_texts.db`.
