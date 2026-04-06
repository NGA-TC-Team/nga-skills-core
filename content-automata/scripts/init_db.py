#!/usr/bin/env python3
"""content-automata 콘텐츠 풀 SQLite DB 초기화 스크립트."""

import sqlite3
import os
import sys
from pathlib import Path

DB_DIR = Path.home() / ".claude" / "skills" / "content-automata" / "data"
DB_PATH = DB_DIR / "content_pool.db"


def init_db(db_path: str | None = None):
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS collection_runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at  TEXT NOT NULL,
            finished_at TEXT,
            period_from TEXT NOT NULL,
            period_to   TEXT NOT NULL,
            status      TEXT DEFAULT 'running'  -- running | completed | failed
        );

        CREATE TABLE IF NOT EXISTS raw_sources (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          INTEGER NOT NULL REFERENCES collection_runs(id),
            source_id       TEXT NOT NULL,      -- sources.json의 id
            source_name     TEXT NOT NULL,
            source_type     TEXT NOT NULL,      -- web | chrome | email
            title           TEXT,
            url             TEXT,
            original_url    TEXT,
            author          TEXT,
            text_content    TEXT,
            summary         TEXT,
            collected_at    TEXT NOT NULL,
            metadata        TEXT,              -- JSON blob for extra fields
            UNIQUE(run_id, source_id, url)
        );

        CREATE TABLE IF NOT EXISTS content_pool (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          INTEGER NOT NULL REFERENCES collection_runs(id),
            content_type    TEXT NOT NULL,      -- breaking | column
            title           TEXT NOT NULL,
            angle           TEXT,              -- 칼럼용 앵글
            priority        TEXT DEFAULT 'medium',
            source_ids      TEXT,              -- JSON array of raw_sources.id
            created_at      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS drafts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            pool_id         INTEGER NOT NULL REFERENCES content_pool(id),
            run_id          INTEGER NOT NULL REFERENCES collection_runs(id),
            draft_number    INTEGER NOT NULL,   -- 1-7
            content         TEXT NOT NULL,
            persona_slug    TEXT,
            created_at      TEXT NOT NULL,
            published       INTEGER DEFAULT 0,
            published_at    TEXT,
            publish_platform TEXT              -- threads | x
        );

        CREATE INDEX IF NOT EXISTS idx_raw_sources_run ON raw_sources(run_id);
        CREATE INDEX IF NOT EXISTS idx_raw_sources_source ON raw_sources(source_id);
        CREATE INDEX IF NOT EXISTS idx_content_pool_run ON content_pool(run_id);
        CREATE INDEX IF NOT EXISTS idx_drafts_run ON drafts(run_id);
    """)

    conn.commit()
    conn.close()
    print(f"DB initialized at {path}")


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else None
    init_db(db)
