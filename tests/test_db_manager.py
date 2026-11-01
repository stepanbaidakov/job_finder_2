
import textwrap
from unittest.mock import MagicMock, patch

from config import config
from src.db_manager import DBManager

DB_MANAGER = DBManager()


def test_init():
    """Test initialization of DBManager."""
    assert DB_MANAGER.database_name == "hh_ru"
    assert DB_MANAGER.params == config()


@patch("src.db_manager.psycopg2.connect")
def test_get_companies_and_vacancies_count(mock_connect):
    """Test retrieving companies and their vacancy counts."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn

    mock_cur.fetchall.return_value = [
        ("IT-hunters", 40),
        ("MyRest", 12),
    ]

    expected_result = [
        {"company": "IT-hunters", "vacancies_amount": 40},
        {"company": "MyRest", "vacancies_amount": 12},
    ]

    result = DB_MANAGER.get_companies_and_vacancies_count()

    expected_sql = textwrap.dedent("""
        SELECT employers.name, COUNT(vacancy_id) AS vacancies_count
        FROM employers
        JOIN vacancies USING(employer_id)
        GROUP BY employer_id, employers.name
    """).strip()

    mock_connect.assert_called_once_with(
        dbname=DB_MANAGER.database_name,
        **DB_MANAGER.params,
    )
    mock_cur.execute.assert_called_once_with(expected_sql)
    mock_cur.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert result == expected_result


@patch("src.db_manager.psycopg2.connect")
def test_get_all_vacancies(mock_connect):
    """Test retrieving all vacancies."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn

    expected_result = [
        (
            "IT-hunters",
            "Data Analyst",
            120000,
            "https://hh.ru/vacancy/123",
        ),
        (
            "MyRest",
            "Python Developer",
            None,
            "https://hh.ru/vacancy/456",
        ),
    ]
    mock_cur.fetchall.return_value = expected_result

    result = DB_MANAGER.get_all_vacancies()

    expected_sql = textwrap.dedent("""
        SELECT employers.name, vacancies.name, salary, url
        FROM vacancies
        JOIN employers USING(employer_id)
    """).strip()

    mock_connect.assert_called_once_with(
        dbname=DB_MANAGER.database_name,
        **DB_MANAGER.params,
    )
    mock_cur.execute.assert_called_once_with(expected_sql)
    mock_cur.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert result == expected_result


@patch("src.db_manager.psycopg2.connect")
def test_get_avg_salary(mock_connect):
    """Test calculating the average salary."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn
    mock_cur.fetchone.return_value = (100500.4,)

    result = DB_MANAGER.get_avg_salary()

    expected_sql = textwrap.dedent("""
        SELECT AVG(salary) AS avg_salary
        FROM vacancies
    """).strip()

    mock_connect.assert_called_once_with(
        dbname=DB_MANAGER.database_name,
        **DB_MANAGER.params,
    )
    mock_cur.execute.assert_called_once_with(expected_sql)
    mock_cur.fetchone.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert result == 100500


@patch("src.db_manager.psycopg2.connect")
def test_get_avg_salary_when_salary_is_none(mock_connect):
    """Test average salary when the database returns NULL."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn
    mock_cur.fetchone.return_value = (None,)

    result = DB_MANAGER.get_avg_salary()

    assert result == 0
    mock_conn.close.assert_called_once()


@patch("src.db_manager.psycopg2.connect")
def test_get_vacancies_with_higher_salary(mock_connect):
    """Test retrieving vacancies with above-average salaries."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn

    expected_result = [
        (1, 10, "Python Developer", 150000, "https://hh.ru/vacancy/123"),
        (2, 20, "Data Analyst", 130000, "https://hh.ru/vacancy/456"),
    ]
    mock_cur.fetchall.return_value = expected_result

    result = DB_MANAGER.get_vacancies_with_higher_salary()

    expected_sql = textwrap.dedent("""
        SELECT *
        FROM vacancies
        WHERE salary > (SELECT AVG(salary) FROM vacancies)
    """).strip()

    mock_connect.assert_called_once_with(
        dbname=DB_MANAGER.database_name,
        **DB_MANAGER.params,
    )
    mock_cur.execute.assert_called_once_with(expected_sql)
    mock_cur.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert result == expected_result


@patch("src.db_manager.psycopg2.connect")
def test_get_vacancies_with_keyword(mock_connect):
    """Test searching vacancies by keyword."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn

    expected_result = [
        (1, 10, "Python Developer", 150000, "https://hh.ru/vacancy/123"),
    ]
    mock_cur.fetchall.return_value = expected_result

    result = DB_MANAGER.get_vacancies_with_keyword("Python")

    expected_sql = textwrap.dedent("""
        SELECT *
        FROM vacancies
        WHERE vacancies.name ILIKE %s
    """).strip()

    mock_connect.assert_called_once_with(
        dbname=DB_MANAGER.database_name,
        **DB_MANAGER.params,
    )
    mock_cur.execute.assert_called_once_with(
        expected_sql,
        ("%Python%",),
    )
    mock_cur.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert result == expected_result


@patch("src.db_manager.psycopg2.connect")
def test_get_vacancies_with_keyword_no_results(mock_connect):
    """Test keyword search when no vacancies match."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur
    mock_connect.return_value = mock_conn
    mock_cur.fetchall.return_value = []

    result = DB_MANAGER.get_vacancies_with_keyword("NoSuchJob")

    assert result == []
    mock_cur.execute.assert_called_once_with(
        textwrap.dedent("""
            SELECT *
            FROM vacancies
            WHERE vacancies.name ILIKE %s
        """).strip(),
        ("%NoSuchJob%",),
    )
    mock_conn.close.assert_called_once()
