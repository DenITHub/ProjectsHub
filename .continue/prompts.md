---
name: Git Status
invokable: true
description: "Показать статус git в терминале"
command: git status
---

---
name: Git Push
invokable: true
description: "Выполнить push текущей ветки"
command: git push
---

---
name: Git Commit
invokable: true
description: "Закоммитить все изменения"
steps:
  - git add .
  - git commit -m "<сообщение коммита>"
---

---
name: Git Commit (AI)
invokable: true
description: "Сгенерировать сообщение коммита по diff и закоммитить"
steps:
  - git add .
  - git diff --cached --name-only
  - git commit -m "<AI сообщение>"
---

---
name: Git Sync
invokable: true
description: "Добавить, сгенерировать commit и push"
steps:
  - git add .
  - git diff --cached --name-only
  - git commit -m "<AI сообщение>"
  - git push
---
