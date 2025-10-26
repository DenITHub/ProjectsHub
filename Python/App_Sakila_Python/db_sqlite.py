#Таблица запросов 
import sqlite3

def init_sqlite_db():
    with sqlite3.connect("search_log.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


#Функция на добления логов

def log_search(query_text):
    with sqlite3.connect("search_log.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO search_log (query_text) VALUES (?)", (query_text,))
        conn.commit()


#Функция популярных запросов

def get_popular_queries():
    with sqlite3.connect("search_log.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT query_text, COUNT(*) as frequency
            FROM search_log
            GROUP BY query_text
            ORDER BY frequency DESC
            LIMIT 10;
        """)
        return cursor.fetchall()
