# Vacancy Search Application with DB

An application for retrieving company and vacancy data from the [hh.ru](https://hh.ru/) platform and storing it in a database. It allows users to retrieve information about companies and their vacancies, analyze salary data, and search for vacancies by keyword.

## Features

The application provides the following features:

- get and store employer and vacancy data from the hh.ru API using a database;
- analyze and display saved data

## Architecture and Key Features

- **API Integration** is used to retrieve employer and vacancy data from hh.ru using the `requests` library.
- **Database Management** is implemented using PostgreSQL and `psycopg2`.
- **Object-Oriented Programming (OOP)** is used to implement the `DBManager` class, which provides methods for querying and analyzing database data.
- **SQL Queries** are used to retrieve companies, filter vacancies, calculate average salaries, and compare salaries against the overall average.

## Tech Stack

- Python
- PostgreSQL
- psycopg2
- Requests
- python-dotenv
- hh.ru API
- SQL
- pytest
- Poetry

## Installation

### 1. Clone the repository

Clone the project repository from GitHub and navigate to the project directory.

```bash
git clone https://github.com/stepanbaidakov/job_finder_2
cd job-finder-2
```

### 2. Install dependencies

If the project uses Poetry, install the dependencies with:

```bash
poetry install
```

To install dependencies without installing the project itself:

```bash
poetry install --no-root
```

Alternatively, if a `requirements.txt` file is available, install the dependencies using pip:

```bash
pip install -r requirements.txt
```

Make sure PostgreSQL and the required Python packages are installed before running the application.

### 3. Register an application on hh.ru

To access the hh.ru API, you may need an access token.

1. Open the [hh.ru developer portal](https://dev.hh.ru/).
2. Sign in to your hh.ru account.
3. Review the API documentation and authentication requirements.
4. Register an application if required by the selected authentication method.
5. Obtain the credentials or access token needed for your API requests.

Keep your credentials private and follow the current hh.ru API authentication requirements.

### 4. Obtain an Access Token

After registering your application, use your `client_id` and `client_secret` to send an HTTP `POST` request to the hh.ru token endpoint:

`https://hh.ru/oauth/token`

Include the following form data in the request:

- `grant_type=client_credentials`
- `client_id=YOUR_CLIENT_ID`
- `client_secret=YOUR_CLIENT_SECRET`

Example using `curl`:

```bash
curl -X POST https://hh.ru/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

The response contains an `access_token`. Copy its value for the next step.

### 4. Configure Environment and Database Connection

Configure the application by creating a `.env` file for the hh.ru API access token and a `database.ini` file for the database connection settings.

**1. Configure the API access token**

Use the `.env.example` file provided in the repository as a template.

1. Create a copy of `.env.example` and name it `.env`.
2. Open `.env` and replace the placeholder with your actual hh.ru API access token:

```dotenv
ACCESS_TOKEN=YOUR_ACCESS_TOKEN
```

3. Save the file.

The application will use this token to authorize requests to the hh.ru API.

Do not commit `.env` to GitHub. Make sure it is listed in `.gitignore`. The `.env.example` file should contain only placeholder values and can be committed to the repository.

**2. Configure the database connection**

1. Create a copy of `database.ini.sample` and name it `database.ini`.
2. Open `database.ini` and replace the placeholder with your actual configs of your database.
For PostgreSQL, the configuration may look like this:

```ini
[postgresql]
host=localhost
user=YOUR_DATABASE_USER
password=YOUR_DATABASE_PASSWORD
port=5432
```

3. Save the file.

The application uses `setup_database()` to prepare the database and `save_to_database()` to store the retrieved employer and vacancy data.

## Running the Application

Run the application using Poetry:

```bash
poetry run python main.py
```

If the Poetry virtual environment is already activated, run:

```bash
python main.py
```

When started, the application retrieves employer and vacancy data from hh.ru, sets up the database, saves the retrieved information, and then prompts the user to select the required operations.

## Database Manager

The `DBManager` class connects to PostgreSQL and provides the following methods:

- **`get_companies_and_vacancies_count()`** — retrieves all companies and the number of vacancies associated with each company.
- **`get_all_vacancies()`** — retrieves all vacancies, including company names, vacancy titles, salary information, and vacancy links.
- **`get_avg_salary()`** — calculates the average salary across all vacancies.
- **`get_vacancies_with_higher_salary()`** — retrieves vacancies with salaries above the average.
- **`get_vacancies_with_keyword(word)`** — searches for vacancies whose titles contain the specified keyword.

The application uses these methods to display the requested information in the console.

## Output

The application stores employer and vacancy data in a database.

Users can choose which information to display:

- companies and their vacancy counts;
- all vacancies with company names, titles, salaries, and links;
- the average salary across vacancies;
- vacancies with salaries above the average;
- vacancies whose titles contain a specified keyword.

The results are displayed in the console.

## Testing

The project can be tested using `pytest`.

To run all tests:

```bash
poetry run pytest
```

To run tests with more detailed output:

```bash
poetry run pytest -v
```

If the virtual environment is already activated, you can also run:

```bash
pytest
```

The project uses `unittest.mock` to mock external API requests and database interactions where appropriate, allowing tests to verify application behavior without relying on live API responses or a running database.
