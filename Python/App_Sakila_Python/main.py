from db_mysql import search_by_keyword, search_by_genre_and_year
from display import display_results, display_menu
from db_sqlite import init_sqlite_db, log_search, get_popular_queries


# Главная функция приложения
def main():
    init_sqlite_db()
    while True:
        display_menu()  # Команды
        command = input("\nEnter command: ").strip().lower()

        # Поиск по ключевому слову
        if command == 'keyword':
            keyword = input("Enter keyword: ").strip()
            log_search(f"keyword:{keyword}")  # Сохраняем запрос 
            results = search_by_keyword(keyword)
            display_results(results, title=f"Search Results for '{keyword}'")

        # Поиск по жанру и году
        elif command == 'genre_year':
            genre = input("Enter genre (e.g., Action, Animation, Children, Classics, Comedy, Documentary, Drama, Family, Foreign, Games, Horror, Music, New, Sci-Fi, Sports, Travel): ").strip().title()
            year = input("Enter year (e.g., 2006): ").strip()
            if year.isdigit():
                log_search(f"genre:{genre},year:{year}")  # Сохраняем запрос 
                results = search_by_genre_and_year(genre, int(year))
                display_results(results, title=f"{genre} Movies from {year}")
            else:
                print("Invalid year format.")

        # Топ запросы
        elif command == 'top':
            queries = get_popular_queries()
            display_results(queries, title="Top Search Queries")

        
        # Завершение программы
        elif command == 'exit':
            print("Exiting application.")
            break

        else:
            print("Unknown command. Try again.")

# Запуск main() 
if __name__ == "__main__":
    main()




#!!!!!!!#Поиск по ключевому слову (1 или keyword)!!!!!!!
#if command in ['1', 'keyword']: нужно ли....!!!!



#!!!!!!!!#Список допустимых жанров#!!!!!!!!!!
#Action
#Animation
#Children
#Classics
#Comedy
#Documentary
#Drama
#Family
#Foreign
#Games
#Horror
#Music
#New
#Sci-Fi
#Sports
#Travel

# Топ запросы
        #elif command == 'top':
        #    queries = get_popular_queries()
        #    if not queries:
        #        print("No popular queries found.")
        #    else:
        #        print("\nTop Search Queries:")
        #        for query, count in queries:
        #            print(f"{query} – {count} times")

#Бесконечный цикл: ждёт ввода команды от пользователя
#Команды:
#'keyword' - запрос ключевого слова - поиск - вывод результатов
#'genre_year' - ввод жанра и года - проверка формата года поиск вывод
#'exit' завершение работы
#другое сообщение об ошибке

#Блок запуска
#if __name__ == "__main__":
#    main()
#Запускает main(), если код выполнен напрямую.

