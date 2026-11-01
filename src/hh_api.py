import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


def get_data(employer_ids: list[str]) -> list[dict[str, Any]]:
    """Retrieve a list of dictionaries containing vacancies for each employer."""
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}"})
    data = []

    for employer_id in employer_ids:
        employer_data = session.get(
            f"https://api.hh.ru/employers/{employer_id}"
        )
        employer_data.raise_for_status()
        employer_data_json = employer_data.json()

        vacancies_data = []
        params = {"employer_id": employer_id, "per_page": 100, "page": 0}

        while True:
            vacancies_response = session.get(
                "https://api.hh.ru/vacancies", params=params
            )
            vacancies_response.raise_for_status()
            vacancies_json = vacancies_response.json()
            vacancies_data.extend(vacancies_json["items"])

            if params["page"] >= vacancies_json["pages"] - 1:
                break

            params["page"] += 1

        data.append(
            {"employer": employer_data_json, "vacancies": vacancies_data}
        )

    return data