# фреймворк для переноса приложения в веб-сервис 
import streamlit as st
# модуль для работы с табличными данными
import pandas as pd
# модуль для работы с операционной системой
import os
import string
from random import randint

# прямая загрузочная ссылка из Google Drive
library_url = 'https://drive.google.com/uc?id=1Rpdc0_h7Gv67gWnkeP2y8rJfhGBb6dAi' 
# устанавливаем формат страницы браузера: на всю ширину
st.set_page_config(page_title='Electronic library', layout="wide")
st.markdown(
    """
    <h1 style="font-size: 50px; color: green; text-align: center;">Электронная библиотека</h1>
    """,
    unsafe_allow_html=True
)
left, cent,last = st.columns(3)
with cent:
    st.image("https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExcjd4azYzcmNweXd0aHp6bTZhbDJmNDA5bDdseG03d2hvZDJxamxoNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/OIfGZBF6W5kRQrgCf8/giphy.gif")


class Book:
    """
    Создаем класс Book со следующими параметрами: 
    • id (уникальный идентификатор, генерируется автоматически)
    • title (название книги)
    • author (автор книги)
    • year (год издания)
    • status (статус книги: "в наличии", "выдана")
    """
    # статус для новых книг по умолчанию - 'в наличии'
    default_status = 'в наличии'
    # инициализация объекта класса
    def __init__(self, title, author, year, status=default_status):
        self.id = self.generate_id()    # функция будет генерировать ID для книги автоматически
        self.title = title
        self.author = author
        self.year = year
        self.status = status
        
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
        try:
            books = pd.read_csv(library_url)
            return books
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return None

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
        with st.expander("Посмотреть всю библиотеку", expanded=False): # Создаем блок, который можно свернуть
            books = self.load_books()  # загружаем книги 
            if books is None:
                st.error("Не удалось загрузить библиотеку. Проверьте источник файла.")
                return
            if not isinstance(books, pd.DataFrame):
                st.error("Данные библиотеки имеют неверный формат.")
                return
            if books.empty:
                st.warning("Библиотека пуста.")
            else:
                st.success(f"Библиотека содержит {books.shape[0]} книг на данный момент")
                # для красивого вывода сортируем по ID и затем ID устанавливаем в качестве индексов
                st.table(books.sort_values(by='ID').set_index('ID'))
        
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
        st.markdown(
        """
        <p style="font-size: 20px; font-weight: bold;">
        Введите полное или частичное название книги, имя и/или фамилию автора, и/или год издания:
        </p>
        """, unsafe_allow_html=True)
        query = st.text_input("").strip().lower().split()
        
        if st.button("Найти книгу"):
            if not query:
                st.error("Запрос не может быть пустым.")
                return

            books = self.load_books() # загружаем книги

            if books.empty:
                st.error("Библиотека пуста.")
                return
            # объединяем нужные столбцы в один и удаляем знаки препинания
            books['total'] = (
            books['Название книги'] + ' ' + books['Автор книги'] + ' ' + books['Год издания']
            )
            # удаляем знаки препинания
            books['total'] = books['total'].str.translate(str.maketrans("", "", string.punctuation))
            # преобразовываем строку-объект в список слов нижнего регистра
            books['total'] = books['total'].apply(lambda row: str(row).lower().split())
            # ищем совпадения
            mask = books['total'].apply(lambda row: set(query).issubset(row))
            index = books[mask].index.to_list()
            # удаляем вспомогательный столбец
            books.drop(columns=['total'], inplace=True)
            # Вывод результатов
            if not index:
                st.write("### Книги не найдены.")
            else:
                st.markdown("### Найденные книги:")
                st.table(books.iloc[index].set_index('ID'))
    
    """
    3. Функция добавления книги
    """ 
    @classmethod
    def add_book(self):
        # функия очистки полей
        def reset_fields():
            st.session_state.clear()
        # проверяем существование ключей в session_state
        if "title" not in st.session_state:
            st.session_state["title"] = ""
        if "author" not in st.session_state:
            st.session_state["author"] = ""
        if "year" not in st.session_state:
            st.session_state["year"] = ""

        st.markdown(
        """<p style="font-size: 18px; color: red; font-weight: bold;">Вы ответственны за лексически правильное написание!!!
        </p>""", unsafe_allow_html=True)
        st.markdown(
        """<p style="font-size: 18px; font-weight: bold;">Введите название книги:
        </p>""", unsafe_allow_html=True)
        title = st.text_input("Название книги", key='title', label_visibility="hidden",
                              value=st.session_state.get("title", "")).strip()  
        
        st.markdown(
        """<p style="font-size: 18px; font-weight: bold;">Введите автора книги:
        </p>""", unsafe_allow_html=True)
        author = st.text_input("Автор книги", key='author', label_visibility="hidden",
                               value=st.session_state.get("author", "")).strip()
        # on_change=reset_fields
        st.markdown(
        """<p style="font-size: 18px; font-weight: bold;">Введите год издания книги:
        </p>""", unsafe_allow_html=True)
        year = st.text_input("Год издания книги", key='year', label_visibility="hidden",
                             value=st.session_state.get("year", "")).strip()
        
        # если данные не введены
        if st.button("Добавить книгу"):
            if not title or not author or not year:
                st.error("Название, автор и год обязательны!")
            else:
                # создаем объект класса из полученной от пользователя информации
                new_book = Book(title, author, year)
                books = self.load_books()
                # проверяем, есть ли книга с таким же названием
                mask = books['Название книги'].str.contains(new_book.title, case=False)
                
                if not mask.any():  # Если совпадений нет
                    self.save_books(new_book)
                    st.success("Книга успешно добавлена!")
                    st.write(f'ID: {new_book.id}')
                    st.write(f'Название книги: {new_book.title}')
                    st.write(f'Автор: {new_book.author}')
                    st.write(f'Год издания: {new_book.year}')
                    st.write(f'Статус: {new_book.status}')
                    
                    reset_fields()

                else:  # Если книга уже есть в библиотеке
                    st.warning("Такая книга уже есть в библиотеке.")
                    st.table(books[mask])
                
        # Кнопка сброса полей ввода
        if st.button("Очистить"):
            reset_fields()
    
    """
    4. Функция изменения статуса книги
    """
    @classmethod
    def update_status(self):
        try:
            st.markdown(
            """
            <p style="font-size: 18px; font-weight: bold;">Введите ID книги для изменения статуса:
            </p>
            """, unsafe_allow_html=True)
            id_book = st.text_input("ID книги", key="id_book").strip()
            if not id_book.isdigit():
                st.error("ID должен быть числом.")
                return
            
            id_book = int(id_book)  # преобразуем ID в число
            books = self.load_books()
            if books.ID.isin([id_book]).any(): # проверяем наличии книги по этому ID
                st.markdown(
                """
                <p style="font-size: 18px; font-weight: bold;">Введите новый статус ('в наличии' или 'выдана'):
                </p>
                """, unsafe_allow_html=True)
                new_status = st.text_input("Новый статус", key="new_status").strip()
                if new_status not in ["в наличии", "выдана"]:
                    st.error("Допустимый статус: 'в наличии' или 'выдана'.")
                    return
                else:
                    # находим индекс книги с необходимым ID
                    index = books[books.ID == id_book].index[0]
                    # обновляем статус
                    books.at[index, 'Статус'] = new_status
                    # перезаписываем файл
                    books.to_csv(library, mode='w+', index=False)
                    st.success(f"Статус книги с ID {id_book} обновлен.")
            else:
                st.error("Книга с таким ID не найдена.")
        except ValueError:
            st.error("ID должен быть числом.")

    """
    5. Функция удаления книги
    """
    @classmethod
    def delete_book(self):
        try:
            st.markdown(
            """
            <p style="font-size: 18px; font-weight: bold;">Введите ID книги для удаления:
            </p>
            """, unsafe_allow_html=True)
            id_book = st.text_input("ID книги", key="id_book").strip()

            if not id_book.isdigit():
                st.error("ID должен быть числом.")
                return
            id_book = int(id_book)  # преобразуем ID в число
            books = self.load_books()
            if books.ID.isin([id_book]).any():        
                index = books[books.ID == id_book].index[0]  # находим индекс данного объекта
                books.drop(index, axis=0, inplace=True)      # удаляем объект по индексу
                # пересохраняем файл
                books.to_csv(library, mode='w+', index=False)
                st.success(f"Книга с ID {id_book} удалена.")
            else:
                st.warning("Книга с таким ID не найдена.")  # в случае несовпадения ни с одним ID книги
        except ValueError:
            st.error("ID должен быть числом.")   # на случай ошибки ввода ID

# Основной цикл программы
st.markdown(
    """
    <p style="font-size: 30px; font-weight: bold;">Выберите действие:</p>
    """,
    unsafe_allow_html=True
)
# Выпадающее меню для выбора действия
choice = st.radio(
    "",
    ["Показать все книги", "Искать книгу", "Добавить книгу", "Изменить статус книги", "Удалить книгу"]
)
# Реализация выбранного действия
if choice == "Показать все книги":
    Book.show_library()
elif choice == "Искать книгу":
    Book.search_books()
elif choice == "Добавить книгу":
    Book.add_book()
elif choice == "Изменить статус книги":
    Book.update_status()
elif choice == "Удалить книгу":
    Book.delete_book()
