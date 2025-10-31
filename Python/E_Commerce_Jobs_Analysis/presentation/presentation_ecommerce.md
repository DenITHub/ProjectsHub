---
marp: true
theme: default
paginate: true
class: lead
---

# Анализ рынка труда:  
## E-Commerce Specialist в Германии

---

## Цель проекта

Изучить рынок труда для профессии **E-Commerce Specialist** в Германии (LinkedIn) и определить:

- ключевые **Hard Skills и Tools**,  
- требования по **языкам**,  
- различия по направлениям:  
  - Marketplaces  
  - Online Sales  
  - Online Marketing.

---

## Источник данных

**Платформа:** LinkedIn  
**Файлы:** 19 JSON-файлов  
**После очистки:** 1932 вакансии  
**Период:** *2025-04 → 2025-10*  
**Языки вакансий:**  
- 🇩🇪 Deutsch — 76%  
- 🇬🇧 English — 18%  
- 🇩🇪/🇬🇧 Bilingual — 6%

---

## Методология

1. Очистка данных и дедупликация  
2. Классификация направлений:
   - *Marketplaces*  
   - *Online Sales*  
   - *Online Marketing*  
3. Извлечение Hard Skills и Tools (по ключевым словам)  
4. Анализ частоты упоминаний  
5. Визуализация и отчёт в `.md`

---

## Распределение направлений

![width:300px](./languages_pie.png)

- **Online Sales** — 37%  
- **Mixed / Cross-functional** — 46%  
- **Online Marketing** — 12%  
- **Marketplaces** — 3%  
- **Unclear** — 2%

---

## Топ-15 Hard Skills (навыки)

![width:400px](./skills_top15.png)

**Топ-5:**
1. Excel  
2. KPI  
3. SEO  
4. SEA  
5. CRM  

---

## Топ-15 Tools (инструменты)

![width:400px](./tools_top15.png)

**Топ-5:**
1. Excel / MS Office  
2. Google Ads  
3. Google Analytics  
4. API  
5. CMS / CRM  

---

## Hard Skills по направлениям

![width:400px](./skills_online_marketing.png)

**Online Marketing** — фокус на SEO, SEA, SEM, Analytics  
**Online Sales** — Excel, CRM, KPI, Auftragsbearbeitung  
**Marketplaces** — Shopify, Shopware, PIM  

---

## Tools по направлениям

![width:400px](./tools_online_sales.png)

**Marketplaces:** Amazon, Shopware, Shopify  
**Online Sales:** Excel, API, CRM  
**Online Marketing:** Google Ads, Analytics, CMS  

---

## Кластеры e-commerce-релевантных вакансий

![width:400px](./titles_ecom_top20.png)

- Online Marketing Manager  
- E-Commerce Manager  
- Digital Marketing Manager  
- Marketplace Manager  
- Sales Specialist E-Commerce  

---

## Кластеры по направлениям

### Marketplaces
![width:550px](./titles_ecom_marketplaces.png)

### Online Marketing
![width:550px](./titles_ecom_online_marketing.png)

### Online Sales
![width:550px](./titles_ecom_online_sales.png)

---

## Выводы

- Рынок E-Commerce в Германии остаётся **высококонкурентным**.  
- Самые востребованные навыки — **аналитика и производительность (KPI, Excel, CRM)**.  
- В **Online Marketing** преобладают SEO, SEA, SEM и Google-инструменты.  
- **Marketplaces** остаются нишевым направлением (≈3–4% рынка).  
- Основной язык вакансий — 🇩🇪 немецкий.

---

## Рекомендации

1. В учебные программы добавить:
   - Google Ads / Analytics / Tag Manager  
   - Excel KPI Reporting  
   - CRM Basics (Salesforce / HubSpot)
2. Уделить внимание **немецкому языку** (B2+).
3. Для marketplace-направления — модули по **Amazon Seller Central, Shopify**.
4. Продолжить анализ **soft skills** и **динамики по месяцам**.

---

## Следующие шаги

- Добавить анализ **Soft Skills** (из описаний).  
- Проверить **динамику рынка по месяцам**.  
- Создать **дашборд** (Streamlit / Tableau) для интерактивного просмотра.  

---

# Спасибо за внимание!

**Автор:** *Denys Mierkulov*
mierkulov@gmx.de / www.linkedin.com/in/denysmierkulov
*ICH Data Analytics Internship — 2025*


https://docs.google.com/presentation/d/1Q2AZzQwl4hU1IaXS3eB96c8rpLdnz2zKd3ZIF6h-KeM/edit?usp=sharing