from textwrap import dedent
from unittest.mock import MagicMock, call, patch

from src.db_creation import save_to_database, setup_database


@patch("psycopg2.connect")
def test_setup_database(mock_connect):
    mock_conn_postgres = MagicMock()
    mock_conn_hh = MagicMock()
    mock_cur = MagicMock()

    mock_conn_hh.cursor.return_value.__enter__.return_value = mock_cur
    mock_conn_postgres.cursor.return_value.__enter__.return_value = mock_cur

    def side_effect_connect(**kwargs):
        if kwargs.get("dbname") == "postgres":
            return mock_conn_postgres
        elif kwargs.get("dbname") == "hh_ru":
            return mock_conn_hh
        return MagicMock()

    mock_connect.side_effect = side_effect_connect
    params = {"user": "test", "password": "pwd"}
    database_name = "hh_ru"
    setup_database(database_name, params)

    mock_connect.assert_any_call(dbname="postgres", **params)
    mock_connect.assert_any_call(dbname="hh_ru", **params)

    expected_calls = [
        call(
            dedent("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = 'hh_ru'
                  AND pid <> pg_backend_pid();
            """).strip()
        ),
        call("DROP DATABASE IF EXISTS hh_ru"),
        call("CREATE DATABASE hh_ru"),
        call(
            dedent("""
                CREATE TABLE employers (
                    employer_id TEXT PRIMARY KEY,
                    name TEXT
                )
            """).strip()
        ),
        call(
            dedent("""
                CREATE TABLE vacancies (
                    vacancy_id TEXT PRIMARY KEY,
                    employer_id TEXT REFERENCES employers(employer_id),
                    name TEXT,
                    salary INT,
                    url TEXT
                )
            """).strip()
        ),
    ]

    mock_cur.execute.assert_has_calls(expected_calls, any_order=False)

    mock_cur.execute.assert_has_calls(expected_calls, any_order=False)

    mock_conn_postgres.close.assert_called_once()
    mock_conn_hh.close.assert_called_once()
    mock_connect.assert_any_call(dbname="postgres", **params)
    mock_connect.assert_any_call(dbname="hh_ru", **params)
    mock_conn_hh.commit.assert_called_once()


@patch("psycopg2.connect")
def test_save_to_database(mock_connect):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_cur.fetchone.return_value = ("E100",)

    mock_data = [
        {
            "employer": {"id": "E100", "name": "Company A"},
            "vacancies": [
                {
                    "id": "V001",
                    "name": "Dev",
                    "salary": {"from": 50000, "to": 70000},
                    "url": "http://url1.com",
                },
                {
                    "id": "V002",
                    "name": "QA",
                    "salary": None,  # Пример с None зарплатой
                    "url": "http://url2.com",
                },
                {
                    "id": "V003",
                    "name": "Dev",
                    "salary": {"from": None, "to": 70000},
                    "url": "http://url3.com",
                },
                {
                    "id": "V004",
                    "name": "QA",
                    "salary": {"from": 50000, "to": None},
                    "url": "http://url4.com",
                },
            ],
        },
    ]
    mock_db_params = {"user": "test", "password": "pwd"}
    mock_db_name = "test_db"

    save_to_database(mock_data, mock_db_name, mock_db_params)

    mock_connect.assert_called_once_with(dbname=mock_db_name, **mock_db_params)
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
    expected_calls = [
        call(
            dedent("""
                INSERT INTO employers (employer_id, name)
                VALUES (%s, %s)
                RETURNING employer_id
            """).strip(),
            ("E100", "Company A"),
        ),
        call(
            dedent("""
                INSERT INTO vacancies
                    (vacancy_id, employer_id, name, salary, url)
                VALUES (%s, %s, %s, %s, %s)
            """).strip(),
            ("V001", "E100", "Dev", 60000, "http://url1.com"),
        ),
        call(
            dedent("""
                INSERT INTO vacancies
                    (vacancy_id, employer_id, name, salary, url)
                VALUES (%s, %s, %s, %s, %s)
            """).strip(),
            ("V002", "E100", "QA", None, "http://url2.com"),
        ),
        call(
            dedent("""
                INSERT INTO vacancies
                    (vacancy_id, employer_id, name, salary, url)
                VALUES (%s, %s, %s, %s, %s)
            """).strip(),
            ("V003", "E100", "Dev", 70000, "http://url3.com"),
        ),
        call(
            dedent("""
                INSERT INTO vacancies
                    (vacancy_id, employer_id, name, salary, url)
                VALUES (%s, %s, %s, %s, %s)
            """).strip(),
            ("V004", "E100", "QA", 50000, "http://url4.com"),
        ),
    ]

    mock_cur.execute.assert_has_calls(expected_calls, any_order=False)

    mock_cur.execute.assert_has_calls(expected_calls, any_order=False)
