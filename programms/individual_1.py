#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Использовать словарь, содержащий следующие ключи:
# название пункта назначения рейса; номер рейса; тип самолета.
# Написать программу, выполняющую следующие действия: ввод с клавиатуры
# данных в список, состоящий из словарей заданной структуры;
# записи должны быть размещены в алфавитном порядке по названиям
# пунктов назначения; вывод на экран пунктов назначения и номеров рейсов,
# обслуживаемых самолетом, тип которого введен с клавиатуры;
# если таких рейсов нет, выдать на дисплей соответствующее сообщение.

import argparse
import json
import jsonschema
import os.path
import sys


def add_flight(flights, destination, number, type):
    """
    Функция для добавления нового рейса в список.
    Запрашивает у пользователя название пункта назначения,
    номер рейса и тип самолета,
    создает новый рейс и добавляет его в общий список рейсов,
    сортируя по названию пункта назначения.
    """

    flights.append(
        {
            'destination': destination,
            'flight_number': number,
            'plane_type': type
        }
    )
    return flights


def list_flights(flights):
    """
    Функция для вывода списка рейсов на экран.
    Выводит табличное представление списка рейсов,
    включая номер, название пункта назначения,
    номер рейса и тип самолета.
    """
    if flights:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 20
        )
        print(line)

        print(
            '| {:^4} | {:^30} | {:^20} | {:^20} |'.format(
                "No",
                "Пункт назначения",
                "Номер рейса",
                "Тип самолета"
            )
        )

        print(line)

        for idx, flight in enumerate(flights, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>20} |'.format(
                    idx,
                    flight.get('destination', ''),
                    flight.get('flight_number', ''),
                    flight.get('plane_type', '')
                )
            )
    else:
        print("Список рейсов пуст.")


def find_flights(flights, type):
    """
    Функция для поиска рейсов по типу самолета и вывода результатов на экран.
    Запрашивает у пользователя тип самолета,
    затем ищет все рейсы с этим типом и выводит их табличное представление.
    """
    found = []

    for flight in flights:
        if flight['plane_type'] == type:
            found.append(flight)

    if not found:
        print(f"Рейсов на самолете типа '{type}' не найдено.")
    else:
        list_flights(found)


def save_flights(file_name, flights):
    """
    Сохранить всех работников в файл JSON.
    """
    # Открыть файл с заданным именем для записи.
    with open(file_name, "w", encoding="utf-8") as fout:
        # Выполнить сериализацию данных в формат JSON.
        # Для поддержки кирилицы установим ensure_ascii=False
        json.dump(flights, fout, ensure_ascii=False, indent=4)


def load_flights(file_name):
    """
    Загрузить всех работников из файла JSON.
    """
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "flight_number": {"type": "string"},
                "plane_type": {"type": "string"}
            },
            "required": ["destination", "flight_number", "plane_type"]
        }
    }
    # Открыть файл с заданным именем для чтения.
    with open(file_name, "r", encoding="utf-8") as fin:
        loaded = json.load(fin)
    try:
        jsonschema.validate(loaded, schema)
    except jsonschema.exceptions.ValidationError as e:
        print(">>> Error:")
        print(e.message)  # Ошибка валидацци будет выведена на экран
    return loaded


def main(command_line=None):
    """
    Главная функция программы.
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "-d",
        "--data",
        action="store",
        required=False,
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("flights")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления рейса.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new flight"
    )
    add.add_argument(
        "--destination",
        action="store",
        required=True,
        help="The departure point"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        help="The plane's number"
    )
    add.add_argument(
        "-t",
        "--type",
        action="store",
        help="The type of plane"
    )
    # Создать субпарсер для отображения всех рейсов.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all flights"
    )

    # Создать субпарсер для выбора рейса.
    find = subparsers.add_parser(
        "find",
        parents=[file_parser],
        help="Find the flights"
    )

    find.add_argument(
        "-s",
        "--select",
        action="store",
        type=str,
        required=True,
        help="find flights served by this type of plane"
    )
    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Загрузить все рейсы из файла, если файл существует.
    data_file = args.data
    if not data_file:
        data_file = os.environ.get("FLY_DATA")
    if not data_file:
        print("The data file name is absent", file=sys.stderr)
        sys.exit(1)

    # Загрузить все рейсы из файла, если файл существует.
    is_dirty = False
    if os.path.exists(data_file):
        flights = load_flights(data_file)
    else:
        flights = []

    # Добавить рейс.
    if args.command == "add":
        flights = add_flight(
            flights,
            args.destination,
            args.number,
            args.type
        )
        is_dirty = True

    # Отобразить всех работников.
    elif args.command == "display":
        list_flights(flights)

    # Выбрать требуемых рааботников.
    elif args.command == "find":
        find_flights(flights, args.select)

    # Сохранить данные в файл, если список работников был изменен.
    if is_dirty:
        save_flights(data_file, flights)


if __name__ == '__main__':
    main()
