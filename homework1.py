from collections import UserDict
from datetime import datetime, date, timedelta

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone number (10 digits) please or just name if you are looking for birthday"
        except IndexError:
            return "Give me the needed name"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):

    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if len(value) != 10 or not value.isdigit():
             raise ValueError("Номер повинен містити 10 цифр")
        
class Birthday(Field):
    def __init__(self, value):
        try:
            birthday=datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value) 
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def add_phone(self, number):
        self.phones.append(Phone(number))

    def remove_phone(self, remnum):
        for phone in self.phones:
            if phone.value == remnum:
                 self.phones.remove(phone)
                 return print(f"Запис з номером '{remnum}' видалено.")
        return print(f"Запис з номером '{remnum}' не знайдено.")

    def edit_phone(self, oldnum, newnum):
        Phone(newnum)
        for phone in self.phones:
            if phone.value == oldnum:
                phone.value = newnum
                return
            raise ValueError(f"Номер '{oldnum}' не знайдено.")
             

    def __str__(self):
        phone_numbers = '; '.join(p.value for p in self.phones)
        return f"{self.name}: {phone_numbers}"

class AddressBook(UserDict):
    def add_record(self, record):
        key = record.name.value
        self.data[key] = record
    
    def find(self, neededname):
        return self.data.get(neededname)

    def delete(self, rem):
        if rem in self.data:
            del self.data[rem]
        else:
            print(f"Запис з ім'ям '{rem}' не знайдено.")

    def date_to_string(self, date):
        return date.strftime("%Y.%m.%d")
    
    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0)
        return birthday
    

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        for name, record in self.data.items():
            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)
        
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year+1)
            if birthday_this_year.weekday() >= 5:
                birthday_this_year = self.adjust_for_weekend(birthday_this_year)
            

            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date_str = self.date_to_string(birthday_this_year)
                upcoming_birthdays.append( {"name": name, "congratulation_date": congratulation_date_str})

        return upcoming_birthdays

    
    def __str__(self):
        records = '\n'.join(f"{record}" for name, record in self.data.items())
        return f"Address Book:\n{records}"


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, newnum, *_ = args 
    record = book.find(name)
    if record is None:
        return f'The contact was not found in the book'
    oldnum = record.phones[0].value
    record.edit_phone(oldnum, newnum)
    return f'Contact {name} was updated'

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    return book.find(name)

@input_error
def show_all(book: AddressBook):
    result = []
    for name, value in book.data.items():
        result.append(f'{value}')
    return '\n'.join(result)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record == None:
        return f'The contact was not found in the book'
    record.add_birthday(birthday)
    return f'Birthday was added'

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    return record.birthday 

@input_error
def birthdays(book: AddressBook):
    upcoming = book.get_upcoming_birthdays() 
    result = []
    for el in upcoming:
        result.append(f"{el['name']}: {el['congratulation_date']}")
    if not upcoming:
        return f'Днів народжень не очікуєтся'

    return '\n'.join(result)






def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()