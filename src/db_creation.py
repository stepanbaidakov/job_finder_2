from textwrap import dedent
from typing import Any

import psycopg2


def setup_database(database_name: str, params: dict) -> None:
    """Create the database and tables."""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute(
            dedent("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                  AND pid <> pg_backend_pid();
            """).strip().replace("datname = %s", f"datname = '{database_name}'")
        )
        cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
        cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        cur.execute(
            dedent("""
                CREATE TABLE employers (
                    employer_id TEXT PRIMARY KEY,
                    name TEXT
                )
            """).strip()
        )
        cur.execute(
            dedent("""
                CREATE TABLE vacancies (
                    vacancy_id TEXT PRIMARY KEY,
                    employer_id TEXT REFERENCES employers(employer_id),
                    name TEXT,
                    salary INT,
                    url TEXT
                )
            """).strip()
        )

    conn.commit()
    conn.close()


def save_to_database(
    data: list[dict[str, Any]], database_name: str, params: dict
) -> None:
    """Populate database tables with data."""
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer in data:
            employer_data = employer["employer"]
            employer_id = employer_data["id"]

            cur.execute(
                dedent("""
                    INSERT INTO employers (employer_id, name)
                    VALUES (%s, %s)
                    RETURNING employer_id
                """).strip(),
                (employer_id, employer_data["name"]),
            )

            employer_id = cur.fetchone()[0]

            for vacancy in employer["vacancies"]:
                salary_data = vacancy["salary"]

                if salary_data is None:
                    salary = None
                elif salary_data["from"] is None:
                    salary = int(salary_data["to"])
                elif salary_data["to"] is None:
                    salary = int(salary_data["from"])
                else:
                    salary = int(
                        (salary_data["from"] + salary_data["to"]) / 2
                    )

                cur.execute(
                    dedent("""
                        INSERT INTO vacancies
                            (vacancy_id, employer_id, name, salary, url)
                        VALUES (%s, %s, %s, %s, %s)
                    """).strip(),
                    (
                        vacancy["id"],
                        employer_id,
                        vacancy["name"],
                        salary,
                        vacancy["url"],
                    ),
                )

    conn.commit()
    conn.close()
