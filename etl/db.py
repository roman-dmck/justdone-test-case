# db.py

from dataclasses import dataclass

import psycopg2
from loguru import logger

DB_CONFIG = {
    "dbname": "justdone",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}

EVENTS_DIR = "data/events"


def get_connection():
    logger.debug("Establishing database connection")
    return psycopg2.connect(**DB_CONFIG)


@dataclass
class Paper:
    """
    A class representing an Arxiv paper.
    """

    id: str
    title: str
    authors: str
    categories: list[str]
    abstract: str
    abstract_uk: str | None = None
    guessed_field: str | None = None
    word_count: int = 0
    word_count_uk: int = 0


def init_papers_table():
    """
    Initialize an empty list of papers.
    """
    sql = """
    CREATE TABLE IF NOT EXISTS papers (
        id VARCHAR(255) PRIMARY KEY,
        title VARCHAR(255),
        authors VARCHAR(255),
        categories VARCHAR(255)[],
        abstract TEXT,
        abstract_uk TEXT,
        guessed_field VARCHAR(255),
        word_count INTEGER,
        word_count_uk INTEGER
    );
    """
    session = get_connection()
    with session:
        with session.cursor() as cursor:
            logger.info("Initializing papers table if not exists")
            cursor.execute(sql)
            session.commit()


# Initialize the database table
init_papers_table()


def insert_papers(papers: list[Paper]):
    """
    Insert a list of papers into the database.
    """

    sql = """
    INSERT INTO papers (id, title, authors, categories, abstract, abstract_uk, guessed_field, word_count, word_count_uk)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING;
    """
    session = get_connection()
    with session:
        with session.cursor() as cursor:
            logger.info(f"Inserting {len(papers)} papers into the database")
            for paper in papers:
                cursor.execute(
                    sql,
                    (
                        paper.id,
                        paper.title,
                        paper.authors,
                        paper.categories,
                        paper.abstract,
                        paper.abstract_uk,
                        paper.guessed_field,
                        paper.word_count,
                        paper.word_count_uk,
                    ),
                )
            session.commit()
            logger.success("All papers inserted (duplicates skipped if any)")
