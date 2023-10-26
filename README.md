# Yatube

### Описание:
Это простой блог на Django. Пользователи могут писать посты с добавлением картинок, комментировать посты других авторов, подписываться на них. Посты можно добавлять в сообщества, доступны отдельные страницы просмотра всех постов каждого сообщества, всех постов каждого автора. Редактировать и удалять посты и комментарии могут только их авторы и администраторы.

### Проект использует следующий стек технологий:

* Python
* Django
* SQlite3

### Как запустить проект:

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Aleskerovz/hw05_final.git
```
```
cd hw05_final
```
2. Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
* Если у вас Linux/macOS
    ```
    source venv/bin/activate
    ```
* Если у вас windows
    ```
    source venv/scripts/activate
    ```
```
python3 -m pip install --upgrade pip
```
3. Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Выполнить миграции:
```
python3 manage.py migrate
```
5. Запустить проект:
```
python3 manage.py runserver
```
