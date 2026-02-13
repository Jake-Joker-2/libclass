import os
import pickle
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class StorageInterface(ABC):
    
    @abstractmethod
    def save_data(self, data: Dict) -> None:
        """Сохранить данные"""
        pass
    
    @abstractmethod
    def load_data(self) -> Dict:
        """Загрузить данные"""
        pass

class Book:
    
    def __init__(self, title: str, author: str):
        self.__title = title          
        self.__author = author        
        self.__status = "доступна"    
        self.__borrowed_by = None     
        return self.__title
    
    def get_author(self) -> str:
        return self.__author
    
    def get_status(self) -> str:
        return self.__status
    
    def set_status(self, status: str) -> None:
        self.__status = status
    
    def get_borrowed_by(self):
        return self.__borrowed_by
    
    def set_borrowed_by(self, user_name: str) -> None:
        self.__borrowed_by = user_name
    
    def __str__(self) -> str:
        return f"'{self.__title}' - {self.__author} [{self.__status}]"


class User:
    
    def __init__(self, name: str):
        self.__name = name               
        self.__borrowed_books: List[Book] = [] 
    
    def get_name(self) -> str:
        return self.__name
    
    def get_borrowed_books(self) -> List[Book]:
        return self.__borrowed_books.copy() 
    
    def add_book(self, book: Book) -> None:
        self.__borrowed_books.append(book)
    
    def remove_book(self, book: Book) -> bool:
        if book in self.__borrowed_books:
            self.__borrowed_books.remove(book)
            return True
        return False
    
    def __str__(self) -> str:
        books_count = len(self.__borrowed_books)
        return f"{self.__name} (книг на руках: {books_count})"


class Librarian:
    
    def __init__(self, name: str):
        self.__name = name
    
    def get_name(self) -> str:
        return self.__name
    
    def __str__(self) -> str:
        return f"Библиотекарь: {self.__name}"


class Person(ABC):
    
    def __init__(self, name: str):
        self._name = name
    
    def get_name(self) -> str:
        return self._name
    
    @abstractmethod
    def get_role(self) -> str:
        pass
    
    def __str__(self) -> str:
        return f"{self.get_role()}: {self._name}"


class LibraryUser(Person):
    
    def __init__(self, name: str):
        super().__init__(name)
        self.__borrowed_books: List[Book] = []
    
    def get_role(self) -> str:
        return "Пользователь"
    
    def get_borrowed_books(self) -> List[Book]:
        return self.__borrowed_books.copy()
    
    def add_book(self, book: Book) -> None:
        self.__borrowed_books.append(book)
    
    def remove_book(self, book: Book) -> bool:
        if book in self.__borrowed_books:
            self.__borrowed_books.remove(book)
            return True
        return False


class LibraryLibrarian(Person):
    
    def __init__(self, name: str):
        super().__init__(name)
    
    def get_role(self) -> str:
        return "Библиотекарь"

class LibrarySystem:
    
    def __init__(self, storage: StorageInterface):
        self.__storage = storage
        self.__books: List[Book] = []
        self.__users: List[LibraryUser] = []
        self.__librarians: List[LibraryLibrarian] = []
        self.__current_librarian = None
        self.__current_user = None
        self.__load_data()
    
    def __load_data(self) -> None:
        data = self.__storage.load_data()
        self.__books = data.get('books', [])
        self.__users = data.get('users', [])
        self.__librarians = data.get('librarians', [])
    
    def save_data(self) -> None:
        data = {
            'books': self.__books,
            'users': self.__users,
            'librarians': self.__librarians
        }
        self.__storage.save_data(data)
    
    def add_person(self, person: Person) -> None:
        if isinstance(person, LibraryUser):
            self.__users.append(person)
            print(f"Пользователь {person.get_name()} добавлен")
        elif isinstance(person, LibraryLibrarian):
            self.__librarians.append(person)
            print(f"Библиотекарь {person.get_name()} добавлен")
    
    def get_all_persons(self) -> List[Person]:
        persons: List[Person] = []
        persons.extend(self.__users)
        persons.extend(self.__librarians)
        return persons
    
    def add_book(self, title: str, author: str) -> None:
        book = Book(title, author)
        self.__books.append(book)
        print(f"Книга '{title}' добавлена")
    
    def remove_book(self, title: str) -> bool:
        for book in self.__books:
            if book.get_title().lower() == title.lower():
                if book.get_status() == "выдана":
                    print(f"Нельзя удалить книгу '{title}', она выдана пользователю")
                    return False
                self.__books.remove(book)
                print(f"Книга '{title}' удалена")
                return True
        print(f"Книга '{title}' не найдена")
        return False
    
    def get_available_books(self) -> List[Book]:
        return [book for book in self.__books if book.get_status() == "доступна"]
    
    def get_all_books(self) -> List[Book]:
        return self.__books.copy()
    
    def borrow_book(self, user: LibraryUser, book_title: str) -> bool:
        for book in self.__books:
            if book.get_title().lower() == book_title.lower():
                if book.get_status() == "доступна":
                    book.set_status("выдана")
                    book.set_borrowed_by(user.get_name())
                    user.add_book(book)
                    print(f"Книга '{book_title}' выдана пользователю {user.get_name()}")
                    return True
                else:
                    print(f"Книга '{book_title}' уже выдана")
                    return False
        print(f"Книга '{book_title}' не найдена")
        return False
    
    def return_book(self, user: LibraryUser, book_title: str) -> bool:
        for book in user.get_borrowed_books():
            if book.get_title().lower() == book_title.lower():
                book.set_status("доступна")
                book.set_borrowed_by(None)
                user.remove_book(book)
                print(f"Книга '{book_title}' возвращена")
                return True
        print(f"Книга '{book_title}' не найдена среди ваших книг")
        return False
    
    def get_user_by_name(self, name: str) -> Optional[LibraryUser]:
        for user in self.__users:
            if user.get_name().lower() == name.lower():
                return user
        return None
    
    def get_librarian_by_name(self, name: str) -> Optional[LibraryLibrarian]:
        for librarian in self.__librarians:
            if librarian.get_name().lower() == name.lower():
                return librarian
        return None
    
    def login_as_librarian(self, name: str) -> bool:
        librarian = self.get_librarian_by_name(name)
        if librarian:
            self.__current_librarian = librarian
            print(f"Добро пожаловать, {name}!")
            return True
        print("Библиотекарь не найден")
        return False
    
    def login_as_user(self, name: str) -> bool:
        user = self.get_user_by_name(name)
        if user:
            self.__current_user = user
            print(f"Добро пожаловать, {name}!")
            return True
        print("Пользователь не найден")
        return False
    
    def logout(self) -> None:
        self.__current_librarian = None
        self.__current_user = None
        print("Выход выполнен")
    
    def is_librarian_logged_in(self) -> bool:
        return self.__current_librarian is not None
    
    def is_user_logged_in(self) -> bool:
        return self.__current_user is not None
    
    def get_current_user(self) -> Optional[LibraryUser]:
        return self.__current_user


class FileStorage(StorageInterface):
    
    def __init__(self, filename: str = "library_data.txt"):
        self.__filename = filename
    
    def save_data(self, data: Dict) -> None:
        try:
            with open(self.__filename, 'wb') as file:
                pickle.dump(data, file)
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
    
    def load_data(self) -> Dict:
        if not os.path.exists(self.__filename):
            return {'books': [], 'users': [], 'librarians': []}
        
        try:
            with open(self.__filename, 'rb') as file:
                return pickle.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return {'books': [], 'users': [], 'librarians': []}

class LibraryApp:
    
    def __init__(self):
        self.__storage = FileStorage()
        self.__library = LibrarySystem(self.__storage)
        self.__initialize_default_data()
    
    def __initialize_default_data(self) -> None:
        if not self.__library.get_all_persons():
            self.__library.add_person(LibraryLibrarian("Админ"))
            self.__library.add_person(LibraryUser("Иван"))
            self.__library.add_person(LibraryUser("Мария"))
            
            self.__library.add_book("Война и мир", "Лев Толстой")
            self.__library.add_book("Преступление и наказание", "Федор Достоевский")
            self.__library.add_book("Мастер и Маргарита", "Михаил Булгаков")
    
    def run(self) -> None:
        print("=" * 50)
        print("Добро пожаловать в библиотечную систему!")
        print("=" * 50)
        
        while True:
            if not self.__library.is_librarian_logged_in() and not self.__library.is_user_logged_in():
                self.__show_auth_menu()
            elif self.__library.is_librarian_logged_in():
                self.__show_librarian_menu()
            elif self.__library.is_user_logged_in():
                self.__show_user_menu()
    
    def __show_auth_menu(self) -> None:
        print("\nВыберите роль:")
        print("1. Библиотекарь")
        print("2. Пользователь")
        print("3. Выйти")
        
        choice = input("Ваш выбор: ")
        
        if choice == "1":
            name = input("Введите имя библиотекаря: ")
            if not self.__library.login_as_librarian(name):
                print("Хотите зарегистрироваться? (да/нет)")
                if input().lower() == "да":
                    self.__library.add_person(LibraryLibrarian(name))
                    self.__library.login_as_librarian(name)
        
        elif choice == "2":
            name = input("Введите имя пользователя: ")
            if not self.__library.login_as_user(name):
                print("Пользователь не найден. Обратитесь к библиотекарю для регистрации.")
        
        elif choice == "3":
            self.__library.save_data()
            print("До свидания!")
            exit()
    
    def __show_librarian_menu(self) -> None:
        print("\n" + "=" * 30)
        print("Меню библиотекаря:")
        print("1. Добавить новую книгу")
        print("2. Удалить книгу")
        print("3. Зарегистрировать нового пользователя")
        print("4. Просмотреть список всех пользователей")
        print("5. Просмотреть список всех книг")
        print("6. Выйти из аккаунта")
        print("7. Сохранить и выйти из программы")
        
        choice = input("Ваш выбор: ")
        
        if choice == "1":
            title = input("Введите название книги: ")
            author = input("Введите автора книги: ")
            self.__library.add_book(title, author)
        
        elif choice == "2":
            title = input("Введите название книги для удаления: ")
            self.__library.remove_book(title)
        
        elif choice == "3":
            name = input("Введите имя нового пользователя: ")
            if self.__library.get_user_by_name(name):
                print("Пользователь с таким именем уже существует")
            else:
                self.__library.add_person(LibraryUser(name))
        
        elif choice == "4":
            print("\nСписок пользователей:")
            users = [p for p in self.__library.get_all_persons() 
                    if isinstance(p, LibraryUser)]
            if users:
                for user in users:
                    print(f"  • {user}")
                    for book in user.get_borrowed_books():
                        print(f"      - {book.get_title()}")
            else:
                print("  Пользователей нет")
        
        elif choice == "5":
            print("\nСписок всех книг:")
            books = self.__library.get_all_books()
            if books:
                for book in books:
                    borrower = f" (у {book.get_borrowed_by()})" if book.get_borrowed_by() else ""
                    print(f"  • {book}{borrower}")
            else:
                print("  Книг нет")
        
        elif choice == "6":
            self.__library.logout()
        
        elif choice == "7":
            self.__library.save_data()
            print("Данные сохранены. До свидания!")
            exit()
    
    def __show_user_menu(self) -> None:
        current_user = self.__library.get_current_user()
        
        print("\n" + "=" * 30)
        print(f"Меню пользователя ({current_user.get_name()}):")
        print("1. Просмотреть доступные книги")
        print("2. Взять книгу")
        print("3. Вернуть книгу")
        print("4. Просмотреть список взятых книг")
        print("5. Выйти из аккаунта")
        print("6. Сохранить и выйти из программы")
        
        choice = input("Ваш выбор: ")
        
        if choice == "1":
            print("\nДоступные книги:")
            available_books = self.__library.get_available_books()
            if available_books:
                for book in available_books:
                    print(f"  • {book}")
            else:
                print("  Нет доступных книг")
        
        elif choice == "2":
            title = input("Введите название книги, которую хотите взять: ")
            self.__library.borrow_book(current_user, title)
        
        elif choice == "3":
            title = input("Введите название книги, которую хотите вернуть: ")
            self.__library.return_book(current_user, title)
        
        elif choice == "4":
            print("\nВаши книги:")
            borrowed_books = current_user.get_borrowed_books()
            if borrowed_books:
                for book in borrowed_books:
                    print(f"  • {book}")
            else:
                print("  У вас нет взятых книг")
        
        elif choice == "5":
            self.__library.logout()
        
        elif choice == "6":
            self.__library.save_data()
            print("Данные сохранены. До свидания!")
            exit()


if __name__ == "__main__":
    app = LibraryApp()
    app.run()