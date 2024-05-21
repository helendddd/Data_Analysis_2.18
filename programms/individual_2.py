#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Самостоятельно изучите работу с пакетом python-dotenv.
# Модифицируйте программу задания 1 таким образом, чтобы значения
# необходимых переменных окружения считывались из файла .env.

import argparse
import json
import os
import sys

from dotenv import load_dotenv


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


def save_students(file_name, students):
    """
    Сохранить всех студентов в файл JSON.
    """
    with open(file_name, "w", encoding="utf-8") as fout:
        json.dump(students, fout, ensure_ascii=False, indent=4)


def load_students(file_name):
    """
    Загрузить всех студентов из файла JSON.
    """
    if not os.path.exists(file_name):
        return []

    with open(file_name, "r", encoding="utf-8") as fin:
        loaded = json.load(fin)
    return loaded


def main(command_line=None):
    """
    Главная функция программы.
    """
    load_dotenv()  # Загрузить переменные окружения из файла .env

    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "-d",
        "--data",
        action="store",
        required=False,
        help="The data file name",
    )

    parser = argparse.ArgumentParser("students")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new student"
    )
    add.add_argument(
        "-n", "--name", action="store", required=True, help="Student's name"
    )
    add.add_argument(
        "-g",
        "--group_number",
        action="store",
        required=True,
        help="Student's group number",
    )
    add.add_argument(
        "-p",
        "--performance",
        nargs="+",
        type=int,
        required=True,
        help="Student's performance (list of five marks)",
    )

    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display all students"
    )

    _ = subparsers.add_parser(
        "find", parents=[file_parser], help="Find the students"
    )

    args = parser.parse_args(command_line)

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

    if args.command == "add":
        students = add_student(
            students, args.name, args.group, args.performance
        )
        is_dirty = True

    elif args.command == "display":
        list_students(students)

    elif args.command == "find":
        find(students)

    if is_dirty:
        save_students(data_file, students)


if __name__ == "__main__":
    main()
