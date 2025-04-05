import sys
from functools import wraps
from collections import UserDict

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
        "default": {
            "ValueError": "Помилка: Некоректні дані для команди '{command}'",
            "IndexError": "Помилка: Некоректна кількість аргументів для команди '{command}'"
        }
    }
    
    @wraps(func)
    # внутрішня функція для обробки помилок
    def inner(args, contacts, command):
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
            return func(args, contacts, command)
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

# Клас для зберігання інформації про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

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
        self.phones = [p for p in self.phones if p.value != phone_number]

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

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

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
        if name in self.data:
            del self.data[name]

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
        else:
            print("Недійсна команда.")

if __name__ == "__main__":
    main()