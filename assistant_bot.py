import sys
from functools import wraps
from collections import UserDict

# Декоратор для обробки помилок введення
def input_error(func):
    @wraps(func)
    def inner(args, contacts, command):
        try:
            return func(args, contacts, command)
        except ValueError:
            if command == "phone":
                return f"Помилка у команді 'phone': Введіть phone та ім'я (наприклад, 'phone John')."
            return f"Помилка у команді '{command}': Введіть ім’я та номер телефону (наприклад, '{command} John 1234567890')."
        except KeyError:
            name = args[0] if args else "невідоме ім'я"
            return f"Помилка: Контакт '{name}' не знайдено в списку."
        except IndexError:
            if command == "phone":
                return f"Помилка у команді '{command}': Введіть ім'я (наприклад, '{command} John')."
            return f"Помилка у команді '{command}': Введіть коректні аргументи (наприклад, '{command} Ім'я Телефон')."
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

    def add_phone(self, phone_number):
        """Додає телефон до списку."""
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        """Видаляє телефон зі списку."""
        self.phones = [p for p in self.phones if p.value != phone_number]

    def edit_phone(self, old_phone, new_phone):
        """Редагує існуючий телефон."""
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError(f"Телефон {old_phone} не знайдено.")

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
    name, phone = args  # Може викликати IndexError
    #contacts[name] = phone

    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)

    return "Контакт додано."

# Функція для зміни номера телефону контакту
@input_error
def change_contact(args, book, command):
    name, old_phone, new_phone = args  # Може викликати IndexError
    # if name not in contacts:
    #     raise KeyError  # Викликаємо KeyError, якщо контакт не існує
    # contacts[name] = phone
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Контакт оновлено."

# Функція для показу номера телефону за ім’ям
@input_error
def show_phone(args, book, command):
    name = args[0]  # Може викликати IndexError
    # if name not in contacts:
    #     raise KeyError  # Викликаємо KeyError, якщо контакт не існує
    # return contacts[name]
    record = book.find(name)
    if not record:
        raise KeyError
    return "; ".join(phone.value for phone in record.phones)

# Функція для показу всіх контактів
@input_error
def show_all(args, book, command):  # Додано args для консистентності з декоратором
    if not book.data:
        return "Список контактів порожній."
    # result = "\n".join(f"{name}: {phone}" for name, phone in contacts.items())
    # return result
    return "\n".join(str(record) for record in book.data.values())
    

# Основна функція бота
def main():
    # contacts = {}
    book = AddressBook()
    print("Ласкаво просимо до бота-помічника!")# повідомлення на початку програми
    
    while True:
        user_input = input("Введіть команду: ").strip()
        if not user_input:
            print("Введіть команду!")
            continue
        
        command, *args = parse_input(user_input)

        if command in ["close", "exit", "ex"]:
            print("До побачення!")
            break
        elif command == "info":
            print("hello, hi, привіт - вітання"
                  "\nadd - додати контакт"
                  "\nchange - змінити контакт"
                  "\nphone - показати номер"
                  "\nall - показати всі контакти"
                  "\nclose, exit, ex - вихід")
        elif command in ["hello", "hi", "привіт"]:
            print("Чим я можу вам допомогти?"
                  "\n\nadd - додати контакт"
                  "\nchange - змінити контакт"
                  "\nphone - показати номер"
                  "\nall - показати всі контакти"
                  "\nclose, exit, ex - вихід")
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