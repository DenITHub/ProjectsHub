#Результаты поиска
#Автоматическая разметка

from tabulate import tabulate

def display_results(results, title="Results"):
    if not results:
        #print(f"\n{title}")
        #print("=" * 120)
        print("No results found.")
        return
    if all(isinstance(row, tuple) and len(row) == 2 for row in results):
        headers = ["Query", "Count"]
    elif all(isinstance(row, tuple) and len(row) == 3 for row in results):
        headers = ["Title", "Year", "Description"]
    elif all(isinstance(row, tuple) and len(row) == 4 for row in results):
        headers = ["Title", "Year", "Description", "Genre"]
    else:
        headers = [f"Column {i+1}" for i in range(len(results[0]))]

    print(tabulate(results, headers=headers, tablefmt="fancy_grid"))

#Команды для пользователя
def display_menu():
    print("\n Commands:")
    print("1. keyword       - Search by keyword")
    print("2. genre_year    - Search by genre and year")
    print("3. top           - Show most popular queries")
    print("4. exit          - Exit the program")



##Разметка в ручную результатов по ключу, жанру и году-----------------------------------------------------------------
#def display_results(results, title="Results"):
#    print(f"\n{title}")
#    print("=" * 120)

#    if not results:
#        print("No results found.")
#        return

#    # Kолоноки
#    num_columns = len(results[0])
#    if num_columns == 3:
#        headers = ["Title", "Year", "Description"]
#        col_widths = [30, 6, 60]
#    elif num_columns == 4:
#        headers = ["Title", "Year", "Description", "Genre"]
#        col_widths = [30, 6, 50, 15]
#    else:
#        headers = [f"Col{i+1}" for i in range(num_columns)]
#        col_widths = [20] * num_columns

#    # Заголовок
#    header_line = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
#    separator = "-+-".join("-" * w for w in col_widths)

#    print(header_line)
#    print(separator)

#    # Строки
#    for row in results:
#        row_line = " | ".join(f"{str(cell)[:w]:<{w}}" for cell, w in zip(row, col_widths))
#        print(row_line)

#    print("=" * 120)
    
##Разметка в ручную топ запросов---------------------------------------------------------------------------
#def display_top_queries(queries):
#    if not queries:
#        print("No popular queries found.")
#        return

#    # Ширина колонок
#    col1_width = max(len("Query"), max(len(str(row[0])) for row in queries))
#    col2_width = len("Count")

#    # Заголовок и рамки
#    print("\nTop Search Queries")
#    print("═" * (col1_width + col2_width + 7))

#    # Заголовки
#    print(f"│ {'Query'.ljust(col1_width)} │ {'Count'.rjust(col2_width)} │")
#    print(f"├{'─' * (col1_width + 2)}┼{'─' * (col2_width + 2)}┤")

#    # Строки
#    for query, count in queries:
#        print(f"│ {query.ljust(col1_width)} │ {str(count).rjust(col2_width)} │")

#    # Низ рамки
#    print("═" * (col1_width + col2_width + 7))
##--------------------------------------------------------------------------------

#Автоматическая разметка ключ, жанр, год
#from tabulate import tabulate
#def display_results(results, title="Results"):
#    if not results:
#        print("No results found.")
#        return
#    headers = ["Title", "Year", "Description"]
#    if len(results[0]) == 4:
#        headers = ["Title", "Year", "Description", "Genre"]

#    print(tabulate(results, headers=headers, tablefmt="fancy_grid"))

#-------------------------------------------------------------------------------------------------
    ## isinstance: проверяет, является ли объект экземпляром указанного класса или типа.
    #  tuple: неизменяемая упорядоченная коллекция элементов в Python.
    #  tabulate: библиотека для форматирования табличных данных.
#--------------------------------------------------------------------------------------------------
    ## Если каждая строка состоит из 2 элементов (кортежей), 
    # 'all()' проверяет, что это условие истинно для *всех* строк в 'results'.
    # 'isinstance(row, tuple)' проверяет, что элемент 'row' является кортежем.
    # 'len(row) == 2' проверяет, что длина кортежа равна 2 - и аналогично для остальных строк.
#---------------------------------------------------------------------------------------------------
#Результаты поиска
#Выводит заголовок и разделитель
#Если results пуст — выводит "No results found" и завершает работу
#Иначе — выводит каждую строку, объединяя элементы через " | "
#Завершает вывод горизонтальной линией

#Команды для пользователя
#Выводит список команд:
#1. keyword      - Search by keyword
#2. genre_year   - Search by genre and year
#3. top           - Show most popular queries
#4. exit         - Exit the program