---
name: Git Status
invokable: true
---
Задача: показать статус git. Используй инструмент run_terminal_command.
Выполни команду ровно: git status
Выведи сырой вывод терминала без комментариев.

---
name: Git Push
invokable: true
---
Задача: сделать push текущей ветки. Используй run_terminal_command.
Команда: git push
Только сырой вывод терминала.

---
name: Git Commit
invokable: true
---
Задача: сделать commit всех изменений. Используй run_terminal_command.
Шаги:
1) git add .
2) git commit -m "<сообщение коммита из запроса пользователя>"
Если сообщение не передано — спроси краткое (<= 72 символов).

---
name: Git Commit (AI)
invokable: true
---
Задача: сгенерировать короткое осмысленное сообщение коммита по diff и закоммитить.
Шаги:
1) Используй run_terminal_command: git add .
2) Получи краткий обзор изменений: run_terminal_command: git diff --cached --name-only
3) Сгенерируй короткое сообщение (рус/англ по содержанию файлов), без воды.
4) run_terminal_command: git commit -m "<сгенерированное сообщение>"

---
name: Git Sync
invokable: true
---
Задача: one-click add → commit (AI) → push.
Шаги:
1) run_terminal_command: git add .
2) run_terminal_command: git diff --cached --name-only
3) Сгенерируй короткое сообщение коммита по изменённым файлам.
4) run_terminal_command: git commit -m "<сгенерированное>"
5) run_terminal_command: git push
