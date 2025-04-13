# Команди бота

Цей документ містить перелік усіх можливих правильних і помилкових вводів команд для бота.

## Правильні вводи

### `hello`, `hi`, `привіт`
- `hello`
- `hi`
- `привіт`

### `info`, `help`, `?`
- `info`
- `help`
- `?`

### `birthdays`
- `birthdays`

### `all`
- `all`

### `close`, `exit`, `ex`
- `close`
- `exit`
- `ex`

### `add <ім'я> <телефон>`
- `add Іван 0661234567`
- `add Анна 0967654321`
- `add Марія 0509876543`
- `add Іван 0981112233`

### `change <ім'я> <старий телефон> <новий телефон>`
- `change Іван 0661234567 0961234567`
- `change Анна 0967654321 0507654321`

### `phone <ім'я>`
- `phone Іван`
- `phone Анна`

### `add-birthday <ім'я> <дата>`
- `add-birthday Іван 15.05.1990`
- `add-birthday Анна 20.11.1985`

### `show-birthday <ім'я>`
- `show-birthday Іван`
- `show-birthday Анна`

### `delete-phone <ім'я> <телефон>`
- `delete-phone Іван 0661234567`
- `delete-phone Анна 0967654321`

### `delete-contact <ім'я>`
- `delete-contact Іван`
- `delete-contact Анна`

---

## Помилкові вводи

### `hello`, `hi`, `привіт`
- `hello test`
- `hi 123`
- `привіт Іван`

### `info`, `help`, `?`
- `info test`
- `help 123`
- `? Іван`

### `add <ім'я> <телефон>`
- `add`
- `add Іван`
- `add Іван123 0661234567`
- `add 123 0661234567`
- `add Іван@ 0661234567`
- `add Іван 066123456`
- `add Іван 06612345678`
- `add Іван abc1234567`
- `add Іван 0123456789`
- `add Іван 0661234567` *(якщо номер уже є в Івана)*
- `add Анна 0661234567` *(якщо номер належить Івану)*

### `change <ім'я> <старий телефон> <новий телефон>`
- `change`
- `change Іван`
- `change Іван 0661234567`
- `change Іван123 0661234567 0961234567`
- `change Іван 0661234567 0961234567` *(Іван не існує)*
- `change Іван 0999999999 0961234567`
- `change Іван 066123456 0961234567`
- `change Іван abc1234567 0961234567`
- `change Іван 0123456789 0961234567`
- `change Іван 0661234567 096123456`
- `change Іван 0661234567 abc1234567`
- `change Іван 0661234567 0123456789`
- `change Іван 0661234567 0509876543` *(номер належить Анні)*

### `phone <ім'я>`
- `phone`
- `phone Іван 123`
- `phone Іван123`
- `phone Іван` *(Іван не існує)*

### `all`
- `all Іван`

### `add-birthday <ім'я> <дата>`
- `add-birthday`
- `add-birthday Іван`
- `add-birthday Іван123 15.05.1990`
- `add-birthday Іван 15.05.1990` *(Іван не існує)*
- `add-birthday Іван 32.12.2025`
- `add-birthday Іван 15.13.1990`
- `add-birthday Іван 2025-12-15`
- `add-birthday Іван 15.05.2026`
- `add-birthday Іван 15.05.1899`
- `add-birthday Іван 20.11.1985` *(Іван уже має день народження)*

### `show-birthday <ім'я>`
- `show-birthday`
- `show-birthday Іван 123`
- `show-birthday Іван123`
- `show-birthday Іван` *(Іван не існує)*

### `birthdays`
- `birthdays Іван`

### `delete-phone <ім'я> <телефон>`
- `delete-phone`
- `delete-phone Іван`
- `delete-phone Іван123 0661234567`
- `delete-phone Іван 0661234567` *(Іван не існує)*
- `delete-phone Іван 0999999999`

### `delete-contact <ім'я>`
- `delete-contact`
- `delete-contact Іван 123`
- `delete-contact Іван123`
- `delete-contact Іван` *(Іван не існує)*

### Некоректні команди
- `ad`
- `phon`
- `helo`
- `xyz`
- `123`
- *(Порожній ввід)*
