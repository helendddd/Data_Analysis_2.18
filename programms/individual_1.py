#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Использовать словарь, содержащий следующие ключи: фамилия и инициалы; номер
# группы; успеваемость (список из 5 элементов). Написать программу, выполняющую
# следующее: ввод с клавиатуры данных в список; записи должны быть упорядочены
# по алфавиту; вывод на дисплей фамилий и номеров групп для всех студентов,
# имеющих хотя бы одну оценку 2; если таких студентов
# нет, вывести соответствующее сообщение.

# Добавьте возможность получения имени файла данных,
# используя соответстсвующую переменную окружения.

import argparse
import json
import os.path
import sys

import jsonschema


def add_student(students, name, group_number, performance):
    """
    Функция для добавления нового ученика в список.
    Запрашивает у пользователя Фамилию и инициалы студента,
    номер группы и успеваемость,
    создает новую запись и добавляет ее в общий список студентов,
    сортируя по фамилии.
    """

    students.append(
        {
            "name": name,
            "group_number": group_number,
            "performance": performance,
        }
    )
    return students


def list_students(students):
    """
    Функция для вывода списка студентов.
    Выводит табличное представление списка,
    включая номер, фамилию,
    номер группы и успеваемость.
    """
    if students:
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 20, "-" * 20
        )
        print(line)

        print(
            "| {:^4} | {:^30} | {:^20} | {:^20} |".format(
                "No", "Фамилия и инициалы", "Номер группы", "Успеваемость"
            )
        )

        print(line)

        for idx, student in enumerate(students, 1):
            print(
                "| {:>4} | {:<30} | {:<20} | {:>20} |".format(
                    idx,
                    student.get("name", ""),
                    student.get("group_number", ""),
                    ", ".join(map(str, student.get("performance", []))),
                )
            )
        print(line)
    else:
        print("Список студентов пуст.")


def find(students):
    """
    Функция для поиска студентов с отметкой 2.
    """
    found = []

    for student in students:
        if 2 in student["performance"]:
            found.append(student)

    if not found:
        print("Студентов с отметкой 2 не найдено")
    else:
        list_students(found)
    return found


def save(file_name, students):
    """
    Сохранить всех студентов в файл JSON.
    """
    # Открыть файл с заданным именем для записи.
    with open(file_name, "w", encoding="utf-8") as fout:
        # Выполнить сериализацию данных в формат JSON.
        # Для поддержки кирилицы установим ensure_ascii=False
        json.dump(students, fout, ensure_ascii=False, indent=4)


def load_students(file_name):
    """
    Загрузить всех студентов из файла JSON.
    """
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "group_number": {"type": "string"},
                "performance": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "minItems": 5,
                    "maxItems": 5,
                },
            },
            "required": ["name", "group_number", "performance"],
        },
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
        help="The data file name",
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("students")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления студента.
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new student"
    )
    add.add_argument(
        "-n", "--name", action="store", required=True, help="Student's name"
    )
    add.add_argument(
        "-g", "--group", action="store", help="Student's group number"
    )
    add.add_argument(
        "-p",
        "--performance",
        nargs="+",
        type=int,
        required=True,
        help="Student's performance (list of five marks)",
    )
    # Создать субпарсер для отображения всех студентов.
    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display all students"
    )

    # Создать субпарсер для нахождения студентов с оценкой "2".
    _ = subparsers.add_parser(
        "find", parents=[file_parser], help="Find the students"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Загрузить всех студентов 18из файла, если файл существует.
    data_file = args.data
    if not data_file:
        data_file = os.environ.get("STUDENTS_DATA")
    if not data_file:
        print("The data file name is absent", file=sys.stderr)
        sys.exit(1)

    is_dirty = False
    if os.path.exists(data_file):
        students = load_students(data_file)
    else:
        students = []

    # Добавить студента.
    if args.command == "add":
        students = add_student(
            students, args.name, args.group, args.performance
        )
        is_dirty = True

    # Отобразить всех студентов.
    elif args.command == "display":
        list_students(students)

    # Выбрать студентов подходящих по условию.
    elif args.command == "find":
        find(students)

    # Сохранить данные в файл, если список студентов был изменен.
    if is_dirty:
        save(data_file, students)


if __name__ == "__main__":
    main()
