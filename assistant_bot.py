import sys
from functools import wraps
from collections import UserDict
from datetime import datetime, timedelta

# Декоратор для обробки помилок введення
def input_error(func):
    # Визначити словник конфігурації помилок для кожної команди
    error_messages = {
        "add": {
            "ValueError": "Помилка у команді 'add': Номер телефону має бути 10 цифр (наприклад, 'add John 1234567890')",
            "IndexError": "Помилка у команді 'add': Потрібно 2 аргументи: ім'я та телефон (наприклад, 'add John 1234567890')"
        },
        "change": {
            "ValueError": "Помилка у команді 'change': Новий номер телефону має бути 10 цифр (наприклад, 'change John 1234567890 1112223333')",
            "IndexError": "Помилка у команді 'change': Потрібно 3 аргументи: ім'я, старий телефон, новий телефон (наприклад, 'change John 1234567890 1112223333')"
        },
        "phone": {
            "ValueError": "Помилка у команді 'phone': Введіть коректне ім’я (наприклад, 'phone John')",
            "IndexError": "Помилка у команді 'phone': Потрібно 1 аргумент: ім’я (наприклад, 'phone John')"
        },
        "all": {
            "IndexError": "Помилка у команді 'all': Аргументи не потрібні, просто введіть 'all'"
        },
        "add-birthday": {
            "ValueError": "Помилка у команді 'add-birthday': Некоректний формат дати. Використовуйте DD.MM.YYYY (наприклад, 'add-birthday John 15.05.1990')",
            "IndexError": "Помилка у команді 'add-birthday': Потрібно 2 аргументи: ім’я та дата народження (наприклад, 'add-birthday John 15.05.1990')"
        },
        "show-birthday": {
            "IndexError": "Помилка у команді 'show-birthday': Потрібно 1 аргумент: ім’я (наприклад, 'show-birthday John')"
        },
        "birthdays": {
            "IndexError": "Помилка у команді 'birthdays': Аргументи не потрібні, просто введіть 'birthdays'"
        },
        "delete-phone": {
            "ValueError": "Помилка у команді 'delete-phone': Телефон не знайдено у контакта (наприклад, 'delete-phone John 1234567890')",
            "IndexError": "Помилка у команді 'delete-phone': Потрібно 2 аргументи: ім’я та телефон (наприклад, 'delete-phone John 1234567890')"
        },
        "delete-contact": {
            "IndexError": "Помилка у команді 'delete-contact': Потрібно 1 аргумент: ім’я (наприклад, 'delete-contact John')"
        },
        "default": {
            "ValueError": "Помилка: Некоректні дані",
            "IndexError": "Помилка: Некоректна кількість аргументів"
        }
    }
    
    @wraps(func)
    def inner(args, book, command=None):
        try:
            # Спочатку перевіряємо кількість аргументів, щоб IndexError мав пріоритет
            if command == "add" and len(args) != 2:
                raise IndexError
            elif command == "change" and len(args) != 3:
                raise IndexError
            elif command == "phone" and len(args) != 1:
                raise IndexError
            elif command == "all" and len(args) > 0:
                raise IndexError
            elif command == "add-birthday" and len(args) != 2:
                raise IndexError
            elif command == "show-birthday" and len(args) != 1:
                raise IndexError
            elif command == "birthdays" and len(args) > 0:
                raise IndexError
            elif command == "delete-phone" and len(args) != 2:
                raise IndexError
            elif command == "delete-contact" and len(args) != 1:
                raise IndexError
            return func(args, book, command) if 'command' in func.__code__.co_varnames else func(args, book)
        except ValueError as e:
            msg = error_messages.get(command, error_messages["default"])["ValueError"]
            args_str = " ".join(args) if args else "немає аргументів"
            return f"{msg}. Ви ввели: '{args_str}'"
        except KeyError:
            name = args[0] if args else "невідоме ім’я"
            return f"Помилка у команді '{command}': Контакт '{name}' не знайдено в адресній книзі"
        except IndexError:
            msg = error_messages.get(command, error_messages["default"])["IndexError"]
            args_str = " ".join(args) if args else "немає аргументів"
            return f"{msg}. Ви ввели: '{args_str}'"
        except Exception as e:
            args_str = " ".join(args) if args else "немає аргументів"
            return f"Помилка у команді '{command}': Щось пішло не так ({str(e)}). Ви ввели: '{args_str}'"
    return inner

#####

# Базовий клас для полів
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Клас для зберігання імені (обов’язкове поле)
class Name(Field):
    pass

# Клас для зберігання номера телефону з валідацією
class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Номер телефону має містити рівно 10 цифр.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неправельний формат дати. Використовуй DD.MM.YYYY")

# Клас для зберігання інформації про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # Додано поле для дати народження

    def add_phone(self, phone_number, book):
        """Додає телефон до списку з перевіркою на дублювання."""
        phone = Phone(phone_number)
        # Перевірка, чи номер уже є у цього контакту
        if any(p.value == phone_number for p in self.phones):
            return f"Помилка: Номер '{phone_number}' уже є у контакта '{self.name.value}'"
        # Перевірка, чи номер є в іншого контакту
        for record in book.data.values():
            if record != self and any(p.value == phone_number for p in record.phones):
                return f"Помилка: Номер '{phone_number}' уже є у іншого контакта '{record.name.value}'"
        self.phones.append(phone)
        return None  # Успішно додано

    def remove_phone(self, phone_number):
        """Видаляє телефон зі списку."""
        if not any(p.value == phone_number for p in self.phones):
            raise ValueError(f"Телефон '{phone_number}' не знайдено в контакті '{self.name.value}'")
        self.phones = [p for p in self.phones if p.value != phone_number]
        return f"Телефон '{phone_number}' видалено з контакту '{self.name.value}'"

    def edit_phone(self, old_phone, new_phone):
        """Редагує існуючий телефон."""
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Телефон '{old_phone}' не знайдено в контакті '{self.name.value}'.")

    def find_phone(self, phone_number):
        """Шукає телефон у списку."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone.value
        return None

    def add_birthday(self, birthday):
        if self.birthday:
            return f"Помилка: День народження для '{self.name.value}' уже встановлено ({self.birthday.value.strftime('%d.%m.%Y')})"
        self.birthday = Birthday(birthday)
        return None   

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones) if self.phones else "немає телефонів"
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "немає даних"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

# Клас для управління адресною книгою
class AddressBook(UserDict):
    def add_record(self, record):
        """Додає запис до адресної книги."""
        self.data[record.name.value] = record

    def find(self, name):
        """Знаходить запис за ім’ям."""
        return self.data.get(name)

    def delete(self, name):
        """Видаляє запис за ім’ям."""
        if name not in self.data:
            raise KeyError
        del self.data[name]
        return f"Контакт '{name}' видалено"

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        
        for record in self.data.values():
            if not record.birthday:
                continue
            birthday = record.birthday.value
            birthday_this_year = birthday.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            delta = (birthday_this_year - today).days
            
            if 0 <= delta <= 7:
                weekday = birthday_this_year.weekday()
                if weekday >= 5:  # Субота або неділя
                    days_to_add = 7 - weekday if weekday == 5 else 1
                    congratulation_date = birthday_this_year + timedelta(days=days_to_add)
                else:
                    congratulation_date = birthday_this_year
                
                upcoming.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        
        return upcoming
#####

# Функція для розбору введеного рядка на команду та аргументи
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Функція для додавання контакту
@input_error
def add_contact(args, book, command):
    name, phone = args
    record = book.find(name)
    if record:
        result = record.add_phone(phone, book)
        if result:  # Якщо повернуто повідомлення про помилку
            return result
    else:
        record = Record(name)
        result = record.add_phone(phone, book)
        if result:
            return result
        book.add_record(record)
    return "Контакт додано."

# Функція для зміни номера телефону контакту
@input_error
def change_contact(args, book, command):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"Помилка у команді 'change': Контакт '{name}' не знайдено в адресній книзі"
    # Перевірка, чи старий номер існує
    if not record.find_phone(old_phone):
        return f"Помилка у команді 'change': Номер '{old_phone}' не знайдено у контакта '{name}'"
    # Перевірка, чи новий номер уже є в іншого контакту
    for other_record in book.data.values():
        if other_record != record and any(p.value == new_phone for p in other_record.phones):
            return f"Помилка у команді 'change': Номер '{new_phone}' уже є у іншого контакта '{other_record.name.value}'"
    record.edit_phone(old_phone, new_phone)
    return "Контакт оновлено."

# Функція для показу номера телефону за ім’ям
@input_error
def show_phone(args, book, command):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    return "; ".join(phone.value for phone in record.phones)

# Функція для показу всіх контактів
@input_error
def show_all(args, book, command):
    if not book.data:
        return "Список контактів порожній."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book, command):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    result = record.add_birthday(birthday)
    if result:
        return result
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book, command):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return f"No birthday set for {name}."
    return f"Birthday of {name}: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book, command):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    result = "Upcoming birthdays:\n"
    for entry in upcoming:
        result += f"{entry['name']}: {entry['congratulation_date']}\n"
    return result.strip()

# Нова функція для видалення телефону
@input_error
def delete_phone(args, book, command):
    name, phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    result = record.remove_phone(phone)
    return result

# Нова функція для видалення контакту
@input_error
def delete_contact(args, book, command):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    result = book.delete(name)
    return result

# Основна функція бота
def main():
    book = AddressBook()
    print("\nЛаскаво просимо до бота-помічника!")
    
    while True:
        user_input = input("\nВведіть команду: ").strip()
        if not user_input:
            print("Введіть команду!")
            continue
        
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "ex"]:
            print("\nДо побачення!")
            break
        elif command == "info":
            print("hello, hi, привіт - вітання"
                  "\nadd <ім'я> <телефон> - додати контакт"
                  "\nchange <ім'я> <старий телефон> <новий телефон> - змінити телефон"
                  "\nphone <ім'я> - показати номери"
                  "\nall - показати всі контакти"
                  "\nadd-birthday <ім'я> <дата> - додати день народження"
                  "\nshow-birthday <ім'я> - показати день народження"
                  "\nbirthdays - показати найближчі дні народження"
                  "\ndelete-phone <ім'я> <телефон> - видалити телефон контакту"
                  "\ndelete-contact <ім'я> - видалити контакт"
                  "\nclose, exit, ex - вихід")
        elif command in ["hello", "hi", "привіт"]:
            print("Чим я можу вам допомогти?")
        elif command == "add":
            print(add_contact(args, book, command))
        elif command == "change":
            print(change_contact(args, book, command))
        elif command == "phone":
            print(show_phone(args, book, command))
        elif command == "all":
            print(show_all(args, book, command))
        elif command == "add-birthday":
            print(add_birthday(args, book, command))
        elif command == "show-birthday":
            print(show_birthday(args, book, command))
        elif command == "birthdays":
            print(birthdays(args, book, command))
        elif command == "delete-phone":
            print(delete_phone(args, book, command))
        elif command == "delete-contact":
            print(delete_contact(args, book, command))
        else:
            print("Недійсна команда.")

if __name__ == "__main__":
    main()