import pandas as pd
import os             # модуль для работы с операционной системой
import string          

# файл для хранения данных с книгами
library = 'C:\IDE\SkillFactory\Разработка СУ биб-кой\library.csv' 

"""
Создаем класс Book со следующими параметрами: 
• id (уникальный идентификатор, генерируется автоматически)
• title (название книги)
• author (автор книги)
• year (год издания)
• status (статус книги: "в наличии", "выдана")
"""
class Book:

    # статус для новых книг по умолчанию - 'в наличии'
    default_status = 'в наличии'
    # инициализация объекта класса
    def __init__(self, title, author, year, status=default_status):
        self.id = self.generate_id()    # функция будет генерировать ID для книги автоматически
        self.title = title
        self.author = author
        self.year = year
        self.status = status
    
    # функция для представления созданного нового объекта
    def info(self):
        print(f'ID: {self.id}')
        print(f'Название книги: {self.title}')
        print(f'Автор: {self.author}')
        print(f'Год издания: {self.year}')
        print(f'Статус: {self.status}')
    
    """
    Функция автоматической генерации ID
    """
    def generate_id(self):
        if self.load_books().empty:
            return  1                              # если ни одной книги в библиотеке, для первой будет id=1
        else:
            self.id = max(self.load_books().ID)+1  # берем последнее(т.е. максимальное) значение и увеличиваем на единицу  
            return self.id 

    """
    Вспомогательные функции:
        1) для загрузки книг из файла в удобный для обработки табличный формат;
        2) для сохранения новой книги в файл.
    """
    # 1-я доп функция
    @classmethod
    def load_books(self):
        if not os.path.exists(library): # если файла в системе не существует
            return print('Данного файла не существует')
        # загружаем файл и преобразовываем в таблицу 
        books = pd.read_csv(library, sep=',') 
        return books
    # 2-я доп функция
    @classmethod
    def save_books(self, book):
        # записываем новый объект в том же формате dataframe
        new_book = pd.DataFrame({'ID': [book.id], 
                         'Название книги': [book.title], 
                         'Автор книги': [book.author], 
                         'Год издания': [book.year], 
                         'Статус': [book.status]})
        # сохраним новый объект в существующий файл в режиме 'дозапись'
        new_book.to_csv(library, mode='a', index=False, header=False)
        
    """
    Далее следуют основные функция управления электронной библиотекой:
    1. Отображение всех книг: Приложение выводит список всех книг с их id, title, author, year и status.
    2. Поиск книги: Пользователь может искать книги по title, author или year.
    3. Добавление книги: Пользователь вводит title, author и year, 
       после чего книга добавляется в библиотеку с уникальным id и статусом "в наличии".
    4. Изменение статуса книги: Пользователь вводит id книги и новый статус ("в наличии" или "выдана").
    5. Удаление книги: Пользователь вводит id книги, которую нужно удалить.
    """
    
    """
    1. Функция для отображения всех книг в библиотеке
    """
    @classmethod
    def show_library(self):
        if self.load_books().empty:
            print("Библиотека пуста.")
        print(f"Библиотека содержит {self.load_books().shape[0]} книг на данный момент")
        # для красивого вывода сортируем по ID и затем ID устанавливаем в качестве индексов
        print(self.load_books().sort_values(by='ID').set_index('ID'))
    
    """
    2. Функция поиска книги в библиотеке
    """
    @classmethod
    def search_books(self):
        """
        Пользователи часто не помнят полное название книги или имя автора (в основном фамилию), 
        поэтому поиск мы создаем для различных вариантов:
        мы принимаем всю информацию, которую нам предоставит пользователь относительно названия книги, автора или года издания,
        дробим её на отдельные компоненты-слова (создаем множество) и ищем совпадения в библиотеке.
        Чтобы не искать отдельно по столбцам таблицы, мы объединим их в один и также преобразуем в множество.
        """
        query = input(
            "НЕ допустимы лексические ошибки! Вы можете ввести полное название книги или часть, имя и фамилию автора или частично, и/или год:"
            ).strip().lower().split()
        if not query:
            print("Запрос не может быть пустым.")
            return
        else:
            # загружаем библиотеку
            books = self.load_books()
            if books.empty:
                print("Библиотека пуста.")
                return
            # объединяем нужные столбцы в один и удаляем знаки препинания
            books['total'] = books['Название книги'] +' ' + books['Автор книги'] + ' ' + books['Год издания']
            # удаляем все знаки препинания, нам нужны только слова
            books['total'] = books.total.str.translate(str.maketrans(" ", " ", string.punctuation))
            # разделяем строки на отдельные слова и приводим к одному регистру
            books.total = books.total.apply(lambda row: str(row).lower().split())
            # ищем по принципу вхождения подмножества-запроса в множество-информация об объектах построчно по всей таблице
            mask = books.total.apply(lambda row: set(query).issubset(row))
            # для всех найденных совпадений выделяем индексы в список
            index = books[mask].index.to_list()
            # удаляем вспомогательный столбец
            books.drop('total', axis=1, inplace=True)
        
            if not index:       # если список индексов пустой, значит, в библиотеке пока нет такой книги
                print("Книги не найдены.")
            else:
                print("Найденные книги:")
                # выводим для пользователя найденные совпадения
                print(books.iloc[index].set_index('ID'))

    """
    3. Функция добавления книги
    """ 
    @classmethod
    def add_book(self):
        title = input('Вы ответственны за лексически правильное написание!!! Введите название книги:').strip()  
        author = input("Введите автора книги:").strip()  # удаляем лишние боковые пробелы на всякий случай
        year = input("Введите год издания книги:").strip()
    
        # если библиотекарь проигнорировал вводные данные книги, сообщаем ему правила
        if not title or not author or not year:     
            print("Название, автор и год обязательны!")
            return
        else:
            # создаем объект класса из полученной от пользователя информации
            new_book = Book(title, author, year)
            # для начала убедимся, что данной книги у нас нет в библиотеке, мы ищем совпадение только по названию
            books = self.load_books()  # загружаем книги
            # проверяем, есть ли книга с таким же названием
            mask = books['Название книги'].str.contains(new_book.title, case=False)
            if not mask.any():  # если совпадений нет
                self.save_books(new_book)
                print("Книга успешно добавлена!")
                print(new_book.info())
            else:  # Если книга уже есть в библиотеке
                print('Данная книга имеется в библиотеке.')
                # выводим совпадение
                print(books[mask])

    """
    4. Функция изменения статуса книги
    """
    @classmethod
    def update_status(self):
        try:
            id_book = int(input("Введите ID книги для изменения статуса:"))
            
            books = self.load_books()
            # проверяем, что книга с таким ID имеется в библиотеке
            if books.ID.isin([id_book]).any():
                # запрашиваем от пользователя ввести новый статус
                new_status = input("Введите новый статус ('в наличии' или 'выдана'):").strip()
                if new_status not in ["в наличии", "выдана"]:
                    print("Допустимый статус: 'в наличии' или 'выдана'.")
                    return
                else: 
                    # находим в таблице индекс книги с необходимым ID       
                    index = books[books.ID==id_book].index[0]
                    # заменяем статус
                    books.at[index, 'Статус'] = new_status
                    # пересохраняем объекты в тот же файл
                    books.to_csv(library, mode='w+', index=False)
                    print(f"Статус книги с ID {id_book} обновлен.")
            else:                        # not books.ID.isin([id_book]).any()
                print("Книга с таким ID не найдена.")
        except ValueError:
            print("ID должен быть числом.")

    """
    5. Функция удаления книги
    """
    @classmethod
    def delete_book(self):
        try:
            id_book = int(input("Введите ID книги для удаления: "))
            
            books = self.load_books()
            # проверяем, что в библиотеке есть книга с таким ID
            if books.ID.isin([id_book]).any():         
                index = books[books.ID == id_book].index[0]  # находим индекс данного объекта
                books.drop(index, axis=0, inplace=True)      # удаляем объект по индексу
                # пересохраняем файл
                books.to_csv(library, mode='w+', index=False)
                print(f"Книга с ID {id_book} удалена.")
            else:                 # not books.ID.isin([id_book]).any()
                print("Книга с таким ID не найдена.")  # в случае несовпадения ни с одним ID книги
        except ValueError:
            print("ID должен быть числом.")   # на случай ошибки ввода ID


# Основной цикл программы
def main():
    while True:
        print("Управление электронной библиотекой:")
        print("1. Показать все книги")
        print("2. Искать книгу")
        print("3. Добавить книгу")
        print("4. Изменить статус книги")
        print("5. Удалить книгу")
        print("6. Выйти")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            Book.show_library()
        elif choice == "2":
            Book.search_books()
        elif choice == "3":
            Book.add_book()
        elif choice == "4":
            Book.update_status()
        elif choice == "5":
            Book.delete_book()
        elif choice == "6":
            print("До свидания!")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()