import sys
from functools import wraps
from collections import UserDict
from datetime import datetime, timedelta
import pickle
import difflib

# Декоратор для обробки помилок введення
def input_error(func):
    # Визначити словник конфігурації помилок для кожної команди
    error_messages = {
        "add": {
            "ValueError": "",  # Буде замінено динамічними повідомленнями
            "IndexError": "Вибачте, для команди 'add' потрібні ім'я та номер телефону. Наприклад: 'add Іван 0661234567'"
        },
        "change": {
            "ValueError": "",  # Буде замінено динамічними повідомленнями
            "IndexError": "Вибачте, для команди 'change' потрібні ім'я, старий і новий номери. Наприклад: 'change Іван 0661234567 0961234567'"
        },
        "phone": {
            "ValueError": "Вибачте, ім'я має містити лише літери. Наприклад: 'phone Іван'",
            "IndexError": "Вибачте, для команди 'phone' потрібне лише ім'я. Наприклад: 'phone Іван'"
        },
        "all": {
            "IndexError": "Команда 'all' не потребує аргументів. Просто введіть 'all'."
        },
        "add-birthday": {
            "ValueError": "",  # Буде замінено динамічними повідомленнями
            "IndexError": "Вибачте, для команди 'add-birthday' потрібні ім'я та дата (DD.MM.YYYY). Наприклад: 'add-birthday Іван 15.05.1990'"
        },
        "show-birthday": {
            "IndexError": "Вибачте, для команди 'show-birthday' потрібне лише ім'я. Наприклад: 'show-birthday Іван'"
        },
        "birthdays": {
            "IndexError": "Команда 'birthdays' не потребує аргументів. Просто введіть 'birthdays'."
        },
        "delete-phone": {
            "ValueError": "Вибачте, цей номер телефону не знайдено у контакта.",
            "IndexError": "Вибачте, для команди 'delete-phone' потрібні ім'я та номер телефону. Наприклад: 'delete-phone Іван 0661234567'"
        },
        "delete-contact": {
            "IndexError": "Вибачте, для команди 'delete-contact' потрібне лише ім'я. Наприклад: 'delete-contact Іван'"
        },
        "default": {
            "ValueError": "Вибачте, введено некоректні дані.",
            "IndexError": "Вибачте, введено некоректну кількість аргументів."
        }
    }
    
    @wraps(func)
    def inner(args, book, command=None):
        try:
            # Перевірка кількості аргументів
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
            return func(args, book, command)
        except ValueError as e:
            args_str = " ".join(args) if args else "немає аргументів"
            return f"{str(e)}. Ви ввели: '{args_str}'"
        except KeyError:
            name = args[0] if args else "невідоме ім’я"
            return f"Вибачте, контакт '{name}' не знайдено в адресній книзі."
        except IndexError:
            msg = error_messages.get(command, error_messages["default"])["IndexError"]
            args_str = " ".join(args) if args else "немає аргументів"
            return f"{msg}. Ви ввели: '{args_str}'"
        except Exception as e:
            args_str = " ".join(args) if args else "немає аргументів"
            return f"Вибачте, щось пішло не так: {str(e)}. Ви ввели: '{args_str}'"
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
    def __init__(self, value):
        if not value.replace(" ", "").isalpha():
            raise ValueError("Ім'я має містити лише літери. Наприклад: Іван або Анна Марія")
        super().__init__(value)

# Клас для зберігання номера телефону з валідацією
class Phone(Field):
    def __init__(self, value):
        # Перевірка довжини
        if not value.isdigit():
            raise ValueError("Номер телефону має містити лише цифри.")
        if len(value) != 10:
            raise ValueError(f"Номер телефону має містити 10 цифр, а у вас {len(value)}.")
        # Перевірка коду оператора
        valid_codes = ["050", "066", "067", "068", "095", "096", "097", "098", "099", "063", "073", "093"]
        if not any(value.startswith(code) for code in valid_codes):
            raise ValueError("Номер має починатися з коду оператора, наприклад: 066, 096, 050 тощо.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            if date_obj > datetime.now().date():
                raise ValueError("Дата народження не може бути в майбутньому.")
            if date_obj.year < 1900:
                raise ValueError("Рік народження виглядає нереалістичним. Перевірте, будь ласка.")
            self.value = date_obj
        except ValueError as e:
            if str(e).startswith("Дата народження") or str(e).startswith("Рік народження"):
                raise
            raise ValueError(f"Некоректний формат дати. Використовуйте DD.MM.YYYY, наприклад, 15.05.1990. Помилка: {str(e)}")

# Клас для зберігання інформації про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # Додано поле для дати народження

    def add_phone(self, phone_number, book):
        """Додає телефон до списку з перевіркою на дублювання."""
        try:
            phone = Phone(phone_number)
        except ValueError as e:
            return str(e)
        # Перевірка, чи номер уже є у цього контакту
        if any(p.value == phone_number for p in self.phones):
            return f"Цей номер '{phone_number}' уже є у контакта '{self.name.value}'."
        # Перевірка, чи номер є в іншого контакту
        for record in book.data.values():
            if record != self and any(p.value == phone_number for p in record.phones):
                return f"Цей номер '{phone_number}' уже належить контакту '{record.name.value}'."
        self.phones.append(phone)
        return None  # Успішно додано

    def remove_phone(self, phone_number):
        """Видаляє телефон зі списку."""
        if not any(p.value == phone_number for p in self.phones):
            raise ValueError(f"Номер '{phone_number}' не знайдено в контакті '{self.name.value}'.")
        self.phones = [p for p in self.phones if p.value != phone_number]
        return f"Номер '{phone_number}' успішно видалено з контакту '{self.name.value}'."

    def edit_phone(self, old_phone, new_phone):
        """Редагує існуючий телефон."""
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                try:
                    self.phones[i] = Phone(new_phone)
                    return
                except ValueError as e:
                    raise ValueError(str(e))
        raise ValueError(f"Номер '{old_phone}' не знайдено в контакті '{self.name.value}'.")

    def find_phone(self, phone_number):
        """Шукає телефон у списку."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone.value
        return None

    def add_birthday(self, birthday):
        """Додає день народження до контакту."""
        if self.birthday:
            return f"День народження для '{self.name.value}' уже встановлено: {self.birthday.value.strftime('%d.%m.%Y')}."
        try:
            self.birthday = Birthday(birthday)
            return None
        except ValueError as e:
            return str(e)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones) if self.phones else "немає телефонів"
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "немає даних"
        return f"👤 {self.name.value}\n📞 Телефони: {phones}\n🎂 День народження: {birthday}"

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
        return f"Контакт '{name}' успішно видалено."

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

# Функція для збереження адресної книги у файл
def save_data(book, filename="addressbook.pkl"):
    """Зберігає адресну книгу у файл за допомогою pickle."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# Функція для завантаження адресної книги з файлу
def load_data(filename="addressbook.pkl"):
    """Завантажує адресну книгу з файлу або повертає нову, якщо файл не знайдено."""
    try:
        with open(filename, "rb") as f:
            book = pickle.load(f)
            # Перевірка та виправлення старих даних
            for record in book.data.values():
                if record.birthday and not isinstance(record.birthday, Birthday):
                    try:
                        record.birthday = Birthday(record.birthday)
                    except (ValueError, AttributeError, TypeError):
                        record.birthday = None
            return book
    except (FileNotFoundError, pickle.UnpicklingError, AttributeError):
        return AddressBook()

# Функція для пошуку схожих команд
def suggest_command(input_cmd, valid_commands):
    matches = difflib.get_close_matches(input_cmd, valid_commands, n=10, cutoff=0.5)#n -ксть, cutoff - поріг схожості
    if matches:
        if len(matches) == 1:
            return f"Можливо, ви мали на увазі '{matches[0]}'? Спробуйте ще раз!"
        else:
            return f"Можливо, ви мали на увазі одну з цих команд: {', '.join(f'\'{m}\'' for m in matches)}? Спробуйте ще раз!"
    return "Вибачте, такої команди не існує. Введіть 'help' для списку команд."
# Функція для розбору введеного рядка на команду та аргументи
def parse_input(user_input):
    cmd, *args = user_input.split(maxsplit=3)  # Обмежуємо розбиття для change
    cmd = cmd.strip().lower()
    return cmd, args

# Функція для додавання контакту
@input_error
def add_contact(args, book, command):
    if len(args) != 2:
        raise IndexError
    name, phone = args
    try:
        Name(name)  # Перевірка імені
    except ValueError as e:
        return str(e)
    record = book.find(name)
    if record:
        result = record.add_phone(phone, book)
        if result:
            return result
    else:
        record = Record(name)
        result = record.add_phone(phone, book)
        if result:
            return result
        book.add_record(record)
    return f"Чудово! Контакт '{name}' додано з номером '{phone}'."

# Функція для зміни номера телефону контакту
@input_error
def change_contact(args, book, command):
    if len(args) != 3:
        raise IndexError
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"Вибачте, контакт '{name}' не знайдено в адресній книзі."
    if not record.find_phone(old_phone):
        return f"Номер '{old_phone}' не знайдено у контакта '{name}'."
    for other_record in book.data.values():
        if other_record != record and any(p.value == new_phone for p in other_record.phones):
            return f"Номер '{new_phone}' уже належить контакту '{other_record.name.value}'."
    try:
        record.edit_phone(old_phone, new_phone)
        return f"Номер для '{name}' успішно змінено на '{new_phone}'."
    except ValueError as e:
        return str(e)

# Функція для показу номера телефону за ім’ям
@input_error
def show_phone(args, book, command):
    name = args[0]
    try:
        Name(name)  # Перевірка імені
    except ValueError as e:
        return str(e)
    record = book.find(name)
    if not record:
        raise KeyError
    phones = "; ".join(phone.value for phone in record.phones) if record.phones else "немає телефонів"
    return f"📞 Номери для '{name}': {phones}"

# Функція для показу всіх контактів
@input_error
def show_all(args, book, command):
    if not book.data:
        return "Ваша адресна книга поки порожня. Додайте контакт за допомогою 'add'!"
    result = "📋 Усі контакти:\n" + "-" * 30 + "\n"
    result += "\n\n".join(str(record) for record in book.data.values())
    return result

@input_error
def add_birthday(args, book, command):
    if len(args) != 2:
        raise IndexError
    name, birthday = args
    try:
        Name(name)  # Перевірка імені
    except ValueError as e:
        return str(e)
    record = book.find(name)
    if not record:
        raise KeyError
    result = record.add_birthday(birthday)
    if result:
        return result
    return f"🎉 День народження для '{name}' додано: {birthday}."

@input_error
def show_birthday(args, book, command):
    name = args[0]
    try:
        Name(name)  # Перевірка імені
    except ValueError as e:
        return str(e)
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return f"Для '{name}' день народження ще не встановлено."
    return f"🎂 День народження '{name}': {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book, command):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "Найближчим часом днів народження немає."
    result = "🎈 Найближчі дні народження:\n"
    for entry in upcoming:
        result += f"- {entry['name']}: {entry['congratulation_date']}\n"
    return result.strip()

# Нова функція для видалення телефону
@input_error
def delete_phone(args, book, command):
    if len(args) != 2:
        raise IndexError
    name, phone = args
    try:
        Name(name)  # Перевірка імені
    except ValueError as e:
        return str(e)
    record = book.find(name)
    if not record:
        raise KeyError
    try:
        result = record.remove_phone(phone)
        return result
    except ValueError as e:
        return str(e)

# Нова функція для видалення контакту
@input_error
def delete_contact(args, book, command):
    name = args[0]
    try:
        Name(name)  # Перевірка імені
    except ValueError as e:
        return str(e)
    record = book.find(name)
    if not record:
        raise KeyError
    result = book.delete(name)
    return result

# Основна функція бота
def main():
    book = load_data()  # Завантаження адресної книги при запуску
    valid_commands = [
        "hello", "hi", "привіт", "info", "help", "?", "add", "change", "phone",
        "all", "add-birthday", "show-birthday", "birthdays", "delete-phone",
        "delete-contact", "close", "exit", "ex"
    ]
    print("\n📚 Ласкаво просимо до вашого помічника з контактами! 😊")
    print("Введіть 'help', щоб побачити всі доступні команди.")
    
    while True:
        user_input = input("\nВведіть команду: ").strip()
        if not user_input:
            print("Ой, ви нічого не ввели! Спробуйте ще раз або введіть 'help' для підказки.")
            continue
        
        command, args = parse_input(user_input)

        if command in ["close", "exit", "ex"]:
            save_data(book)
            print("\nДо зустрічі! Ваші контакти збережено. 👋")
            break
        elif command in ["info", "help", "?"]:
            print("📋 Доступні команди:")
            print("- hello, hi, привіт: привітатися з ботом")
            print("- add <ім'я> <телефон>: додати контакт (наприклад, 'add Іван 0661234567')")
            print("- change <ім'я> <старий телефон> <новий телефон>: змінити номер")
            print("- phone <ім'я>: показати номери контакта")
            print("- all: показати всі контакти")
            print("- add-birthday <ім'я> <дата>: додати день народження (DD.MM.YYYY)")
            print("- show-birthday <ім'я>: показати день народження")
            print("- birthdays: показати найближчі дні народження")
            print("- delete-phone <ім'я> <телефон>: видалити номер")
            print("- delete-contact <ім'я>: видалити контакт")
            print("- close, exit, ex: зберегти та вийти")
        elif command in ["hello", "hi", "привіт"]:
            print("Привіт! Як я можу допомогти вам сьогодні? 😊")
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
            print(suggest_command(command, valid_commands))

if __name__ == "__main__":
    main()