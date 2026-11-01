from unittest.mock import Mock, patch

from src.hh_api import get_data

MOCK_EMPLOYER_DATA = {
    "id": "123",
    "name": "Test Company",
    "description": "A test employer",
}

MOCK_VACANCIES_PAGE_0 = {
    "items": [{"id": "v1", "title": "Dev 1"}],
    "pages": 2,
    "page": 0,
    "per_page": 100,
    "found": 2,
}

MOCK_VACANCIES_PAGE_1 = {
    "items": [{"id": "v2", "title": "Dev 2"}],
    "pages": 2,
    "page": 1,
    "per_page": 100,
    "found": 2,
}


@patch("src.hh_api.requests.Session.get")
def test_get_data(mock_get):
    """
    Тестирует функцию для одного работодателя, имитируя 2 страницы вакансий.
    """

    def side_effect_func(url, params=None):
        mock_response = Mock()

        if "employers/123" in url:
            mock_response.json.return_value = MOCK_EMPLOYER_DATA
            mock_response.raise_for_status.return_value = None
            return mock_response

            # Если запрос к /vacancies с page=0
        elif params and params.get("page") == 0:
            mock_response.json.return_value = MOCK_VACANCIES_PAGE_0
            mock_response.raise_for_status.return_value = None
            return mock_response

            # Если запрос к /vacancies с page=1
        elif params and params.get("page") == 1:
            mock_response.json.return_value = MOCK_VACANCIES_PAGE_1
            mock_response.raise_for_status.return_value = None
            return mock_response

        return mock_response

    mock_get.side_effect = side_effect_func

    result = get_data(employer_ids=["123"])
    assert len(result) == 1
    assert result[0]["employer"]["name"] == "Test Company"
    assert len(result[0]["vacancies"]) == 2  # Обе вакансии с обеих страниц
    assert result[0]["vacancies"][0]["title"] == "Dev 1"
    assert result[0]["vacancies"][1]["title"] == "Dev 2"

    # Проверяем, сколько раз вызывался requests.get (1 раз для данных о компании + 2 раза для вакансий)
    assert mock_get.call_count == 3
