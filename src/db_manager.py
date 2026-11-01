
import textwrap
from typing import Any

import psycopg2

from config import config


class DBManager:
    """A class for retrieving data from the database."""

    def __init__(self) -> None:
        self.database_name = "hh_ru"
        self.params = config()

    def get_companies_and_vacancies_count(self) -> list[dict[str, Any]]:
        """Retrieve all companies and the number of vacancies at each company."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                textwrap.dedent("""
                    SELECT employers.name, COUNT(vacancy_id) AS vacancies_count
                    FROM employers
                    JOIN vacancies USING(employer_id)
                    GROUP BY employer_id, employers.name
                """).strip()
            )
            rows = cur.fetchall()

        conn.close()
        return [
            {"company": row[0], "vacancies_amount": row[1]}
            for row in rows
        ]

    def get_all_vacancies(self) -> list[tuple[Any, ...]]:
        """Retrieve all vacancies, including company names, titles, salaries, and links."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                textwrap.dedent("""
                    SELECT employers.name, vacancies.name, salary, url
                    FROM vacancies
                    JOIN employers USING(employer_id)
                """).strip()
            )
            rows = cur.fetchall()

        conn.close()
        return rows

    def get_avg_salary(self) -> int:
        """Calculate the average salary across all vacancies."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                textwrap.dedent("""
                    SELECT AVG(salary) AS avg_salary
                    FROM vacancies
                """).strip()
            )
            result = cur.fetchone()[0]

        conn.close()
        return round(result) if result is not None else 0

    def get_vacancies_with_higher_salary(self) -> list[tuple[Any, ...]]:
        """Retrieve vacancies with salaries above the average salary."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                textwrap.dedent("""
                    SELECT *
                    FROM vacancies
                    WHERE salary > (SELECT AVG(salary) FROM vacancies)
                """).strip()
            )
            rows = cur.fetchall()

        conn.close()
        return rows

    def get_vacancies_with_keyword(
        self, key_word: str
    ) -> list[tuple[Any, ...]]:
        """Retrieve vacancies whose titles contain the specified keyword."""
        conn = psycopg2.connect(dbname=self.database_name, **self.params)

        with conn.cursor() as cur:
            cur.execute(
                textwrap.dedent("""
                    SELECT *
                    FROM vacancies
                    WHERE vacancies.name ILIKE %s
                """).strip(),
                (f"%{key_word}%",),
            )
            rows = cur.fetchall()

        conn.close()
        return rows
