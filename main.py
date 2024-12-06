import os
import platform
from datetime import datetime
import json
from pydantic import BaseModel


# на вход str-меню и кол-во пунктов меню. на выход отображение меню и валидное значение для math-меню
def select_menu(menu="", len=None):
    print(menu)
    while True:
        try:
            if len != None and (menu_item := int(input("Пункт №"))) not in range(
                0, len + 1
            ):
                print("Нет такого пункта меню")
                continue
            clear_console()
            return menu_item
        except ValueError:
            print("Нет такого пункта меню")


def clear_console():
    currentOS = platform.system()
    os.system("cls") if currentOS == "Windows" else os.system("clear")


class TaskManager:
    __MENU_ACTION = """
Доступный действия
0. К выбору файлов
1. Просмотр всех задач
2. Выбрать задачу
3. Поиск задач
4. Добавление новой задачи
"""

    __MENU_FIND_TASK = """
Поиск и сортировка
0. Назад
1. По названию
2. По категории
3. По сроку
4. По приоритету
5. По Статусу
"""

    __CHOOSE_PRIORITY = """
Выбор приоритета
0. Назад
1. Низкий
2. Средний
3. Высокий
"""

    def __init__(self, path):
        self.path = path
        self.category = []
        self.task_list = []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.category = data[0]
                self.category.insert(
                    0, None
                )  # None нужен чтоб выровнять индексы и пункты мелю
                [
                    self.task_list.append(Task.model_validate_json(task))
                    for task in data[1]
                ]
        except:
            print(f"Ошибка декодирования JSON")
            return

        self.show_all_tasks()
        self.task_manager_menu()

    def task_manager_menu(self):
        while True:
            match select_menu(self.__MENU_ACTION, 4):
                case 0:
                    self.task_list = []
                    self.category = []
                    return
                case 1:
                    self.show_all_tasks()
                case 2:
                    self.task_list[select_menu(len=len(self.task_list)) - 1].task(
                        self.task_list
                    )
                    self.save_task_list()
                case 3:
                    self.findTask()
                case 4:
                    self.create_new_task()

    def show_all_tasks(self):
        [print(task) for task in self.task_list] if self.task_list else print("Пусто")

    def findTask(self):
        while True:
            match select_menu(self.__MENU_FIND_TASK, 4):
                case 0:
                    return
                case 1:
                    self.find_by_title()
                case 2:
                    self.find_by_category()
                case 3:
                    self.find_by_date()
                case 4:
                    self.find_by_priority()

    def find_by_title(self):
        title = input("Введите название\n")
        presents = False
        for task in self.task_list:
            if task.title == title:
                presents = True
                print(task)
        not presents and print("Пусто")

    def find_by_category(self):
        [
            print(task)
            for task in self.task_list
            if task.category == self.category[self.choose_category()]
        ]

    def choose_category(self):
        category_menu = "Категории\n0. Назад\n"
        for el in range(1, len(self.category)):
            category_menu += f"{el}. {self.category[el]}\n"
        # else:
        #     category_menu += f"{el}. Создать новую категорию\n" посже сделаю кастомные категории

        menu_item = select_menu(category_menu, len(self.category))
        if menu_item == 0:
            return
        else:
            return menu_item

    def find_by_date(self):
        presents = False
        while True:
            try:
                date_start = datetime.strptime(
                    input(
                        "Ведите дату с которой начнется выборка\nФормат ввода ГГГГ-ММ-ДД\n"
                    ),
                    "%Y-%m-%d",
                )
                date_end = datetime.strptime(
                    input(
                        "Ведите дату на которой закончится выборка\nФормат ввода ГГГГ-ММ-ДД\n"
                    ),
                    "%Y-%m-%d",
                )
                if date_start > date_end:
                    print("Некорректный ввод даты")
                    continue
                break
            except ValueError:
                print("Некорректный ввод даты")
        for task in self.task_list:
            if date_start <= task.due_date <= date_end:
                presents = True
                print(task)
        not presents and print("Пусто")

    def find_by_priority(self):
        priority_order = {
            "Низкий": 1,
            "Средний": 2,
            "Высокий": 3,
        }
        [
            print(task)
            for task in sorted(self.task_list, key=lambda x: priority_order[x.priority])
        ]

    def choose_priority(self):
        match select_menu(self.__CHOOSE_PRIORITY, 3):
            case 0:
                return
            case 1:
                return "Низкий"
            case 2:
                return "Средний"
            case 3:
                return "Высокий"

    def create_new_task(self):
        self.task_list.append(
            Task(
                title=input("Введите название "),
                description=input("Опишите задачу "),
                category=self.category[self.choose_category()],
                due_date=self.check_date(),
                priority=self.choose_priority(),
            )
        )

        self.save_task_list()

    def check_date(self):  # позже объединить с find_by_date
        while True:
            try:
                date = datetime.strptime(
                    input(
                        "Ведите дату к которой нужно успеть\nФормат ввода ГГГГ-ММ-ДД\n"
                    ),
                    "%Y-%m-%d",
                )
                if date < datetime.now():
                    print("Некорректный ввод даты")
                    continue
                return date
            except ValueError:
                print("Некорректный ввод даты")

    def save_task_list(self):
        self.refresh_id()
        categoryList = self.category
        categoryList.pop(0)  # убрал None из категорий для записи в json
        data = [
            categoryList,
            [task.json() for task in self.task_list],
        ]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def refresh_id(self):
        self.task_list = sorted(self.task_list, key=lambda task: task.due_date)
        for el in range(0, len(self.task_list)):
            self.task_list[el].change_data(**{"id": el + 1})


class Task(BaseModel, TaskManager):
    id: int = None
    title: str
    description: str
    category: str
    due_date: datetime
    priority: str
    status: bool = False

    __MENU_ACTION = """
Доступный действия
0. К выбору задач
1. Выполнено/НЕ выполнено
2. Редактировать задачу
3. Удалить задачу
"""

    def task(self, task_list):
        while True:
            status = "Выполнено" if self.status else "Не выполнено"

            print(
                f"""
              
ID: {self.id}
Название: {self.title}
Категория: {self.category}
Срок: {self.due_date}
Приоритет: {self.priority}
Статус: {status}
Описание задачи:
{self.description}

"""
            )

            match select_menu(self.__MENU_ACTION, 3):
                case 0:
                    return
                case 1:
                    self.status = False if self.status else True
                case 2:
                    self.get_new_data()
                case 3:
                    if (
                        input("выточно хотите удалить это задание?\nY-да\nn-нет\n")
                        == "Y"
                    ):
                        return task_list.pop(self.id - 1)

    def get_new_data(self):
        new_data = {}

        while True:
            print(
                f"""
0. К задаче
1. Изменить название: {self.title}
2. Изменить категорию: {self.category}
3. Изменить срок: {self.due_date}
4. Изменить приоритет: {self.priority}
5. Изменить описание задачи:
{self.description}
"""
            )
            match select_menu(len=5):
                case 0:
                    break
                case 1:
                    new_data["title"] = input("Введите новое название ")
                case 2:
                    new_data["category"] = self.category[self.choose_category()]
                case 3:
                    new_data["due_date"] = self.check_date()
                case 4:
                    new_data["priority"] = self.choose_priority()
                case 5:
                    new_data["description"] = input("Введите новое описание ")

        self.change_data(**new_data)

    def change_data(self, **kwargs):
        [
            value is not None and setattr(self, key, value)
            for key, value in kwargs.items()
        ]

    def __str__(self):
        status = "Выполнено" if self.status else "Не выполнено"

        return f"""
ID: {self.id}
Название: {self.title}
Категория: {self.category}
Срок: {self.due_date}
Приоритет: {self.priority}
Статус: {status}
"""


def main():
    directory = "./tasks/"
    files = [None]  # None нужен чтоб выровнять индексы и пункты мелю

    menu = "Выбор файла \n0. Выход\n"
    for file in os.listdir(directory):
        if file.endswith(".json"):
            files.append(file)
            menu += f"{files.index(file)}. {file}\n"
    else:
        menu += f"{len(files)}. Cоздать новый файл"

    match menu_item := select_menu(menu, len(files)):
        case 0:
            print("Выход")
            return False
        case x if x in range(1, len(files)):
            path = directory + files[menu_item]
            TaskManager(path)
        case x if x == len(files):
            while True:
                if (
                    new_file_name := input("Введите название файла: ") + ".json"
                    in files
                ):
                    print(f"Это имя файла уже занято")
                    continue
                break
            path = directory + new_file_name
            with open(path, "w"):
                pass
            TaskManager(path)

    return True


while __name__ == "__main__":
    if not main():
        break
