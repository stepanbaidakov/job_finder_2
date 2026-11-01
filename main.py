from config import config
from src.db_creation import save_to_database, setup_database
from src.db_manager import DBManager
from src.hh_api import get_data

employer_ids = [
    "5591530",
    "3147167",
    "11181389",
    "3655078",
    "3669216",
    "3407499",
    "5046934",
    "217918",
    "1062788",
    "2910384",
    "18071",
    "2235",
    "1852940",
]


def main():
    params = config()
    data = get_data(employer_ids)
    setup_database("hh_ru", params)
    save_to_database(data, "hh_ru", params)
    db_manager = DBManager()

    user_input = input(
        "Would you like to see all companies and the number of vacancies at each company? (yes/no): "
    ).casefold()
    if user_input == "yes":
        return_list = db_manager.get_companies_and_vacancies_count()
        for company in return_list:
            print(
                f"Company: {company['company']}, "
                f"Number of vacancies: {company['vacancies_amount']}"
            )

    user_input = input(
        "Would you like to see all vacancies, including the company name, "
        "vacancy title, salary, and link? (yes/no): "
    ).casefold()
    if user_input == "yes":
        return_list = db_manager.get_all_vacancies()
        for vacancy in return_list:
            print(
                f"Company: {vacancy[0]}, {vacancy[1]}, "
                f"{vacancy[2]} RUB, {vacancy[3]}"
            )

    user_input = input(
        "Would you like to see the average salary across all vacancies? (yes/no): "
    ).casefold()
    if user_input == "yes":
        print(f"{db_manager.get_avg_salary()} RUB")

    user_input = input(
        "Would you like to see all vacancies with a salary above the average? (yes/no): "
    ).casefold()
    if user_input == "yes":
        return_list = db_manager.get_vacancies_with_higher_salary()
        for vacancy in return_list:
            print(
                f"Company ID: {vacancy[0]}, Vacancy ID: {vacancy[1]}, "
                f"{vacancy[2]}, {vacancy[3]} RUB, {vacancy[4]}"
            )

    user_input = input(
        "Would you like to search for vacancies whose titles contain a specific keyword? (yes/no): "
    ).casefold()
    if user_input == "yes":
        word_input = input("Enter a keyword to filter vacancies: ")
        return_list = db_manager.get_vacancies_with_keyword(word_input)
        for vacancy in return_list:
            if vacancy[3] is None:
                print(
                    f"Company ID: {vacancy[0]}, Vacancy ID: {vacancy[1]}, "
                    f"{vacancy[2]}, {vacancy[3]}, {vacancy[4]}"
                )
            else:
                print(
                    f"Company ID: {vacancy[0]}, Vacancy ID: {vacancy[1]}, "
                    f"{vacancy[2]}, {vacancy[3]} RUB, {vacancy[4]}"
                )


if __name__ == "__main__":
    main()