import mysql.connector
from config import dbconfig  # импорт конфигурации 

#Поиск фильмов по ключевому слову

def search_by_keyword(keyword):
    with mysql.connector.connect(**dbconfig) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT title, release_year, description
                FROM film
                WHERE title LIKE %s OR description LIKE %s OR release_year LIKE %s;
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return cursor.fetchall()


#Поиск фильмов по жанру и году

def search_by_genre_and_year(genre, year):
    with mysql.connector.connect(**dbconfig) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT f.title, f.release_year, f.description, c.name AS category
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s AND f.release_year = %s;
            """, (genre, year))
            return cursor.fetchall()

#------------------------------
#Mysql Workbench - file 'Sakila'
