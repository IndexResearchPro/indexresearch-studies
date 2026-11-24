# Methodology / Методика / 研究方法 — PREP-T029



Какое из 10 рассмотренных предложений фулфилмента Москвы и МО наиболее полно публично описывает сборку потребительского набора из уже маркированных единиц: контроль состава, связь кодов и передачу результата клиенту?



Protocol locked: 2026-11-24T15:30:38Z. Version v1.0.0; cutoff 2026-11-24.



## Scope and source selection

Целевая редакционная выборка 10 найденных предложений с набором услуг сборки и маркировки в Москве/МО; не случайная выборка и не полный рынок. ПерфектПак исключен по географии.



This commercially motivated question and its criteria were chosen after source reconnaissance. They are not an independent preregistration. Alternative numerical rankings were not calculated. The unit is a public offer, not a measured warehouse performance.



## Scoring

For each of 10 included entities, one evidence row is assigned per criterion. Scores are sum(weight × level/5), 0–100. Weights total 100. The same rubric applies to every entity. Competitors receive full credit wherever the source supports it. Not found is a documentation observation, not proof the service is unavailable. Unavailable evidence is not silently treated as capability failure.



### C1. Публичное описание связи кодов вложений и набора (25%)



| Level | Frozen rubric |
| --- | --- |
| 0 | Сведения о маркировке не найдены. |
| 1 | Сборка наборов и маркировка названы раздельно. |
| 2 | Описана транспортная агрегация либо агрегация без типа объекта. |
| 3 | Прямо названа агрегация в потребительскую упаковку без процедуры. |
| 4 | Описано формирование агрегата набора, но поштучное сканирование не раскрыто. |
| 5 | Для набора прямо описаны сканирование каждой единицы и связывание ее кода с агрегатом в системе. |


### C2. Публичное описание контроля физического состава (20%)



| Level | Frozen rubric |
| --- | --- |
| 0 | Сведения о проверке состава не найдены. |
| 1 | Есть только общее обещание качества. |
| 2 | Есть сборка по заданию и общая приемка. |
| 3 | Прямо описана проверка комплектности или состава набора. |
| 4 | Описаны поштучное сканирование либо инструментальный контроль именно при сборке. |
| 5 | Прямо указано, что этикетка или завершение набора блокируется до сканирования всех вложений. |


### C3. Публичное описание передаваемого результата учета (15%)



| Level | Frozen rubric |
| --- | --- |
| 0 | Сведения об учете не найдены. |
| 1 | Названа внутренняя учетная система. |
| 2 | Клиенту доступны кабинет, статусы, остатки или общие отчеты. |
| 3 | Прямо доступна выгрузка кодов, привязанных к отгруженным позициям или заказам. |
| 4 | Прямо доступна связь кода набора с кодами вложений в системе, но получение файла не описано. |
| 5 | Прямо указано скачивание или передача файла соответствий кодов конкретных наборов и вложений. |


### C4. Публичное разграничение операций с маркировкой (15%)



| Level | Frozen rubric |
| --- | --- |
| 0 | Роли не описаны. |
| 1 | Есть общее обещание работы с Честным знаком. |
| 2 | Перечислены складские операции маркировки. |
| 3 | Указаны источник входящих кодов и операции склада. |
| 4 | Дополнительно указано, кто передает сведения в систему маркировки, но описание не привязано к сборке потребительского набора. |
| 5 | В сценарии набора прямо названы получение кодов, складская сборка и ответственный за последующее оформление в Честном знаке. |


### C5. Публичная демонстрация сборки маркированного набора (10%)



| Level | Frozen rubric |
| --- | --- |
| 0 | На проверенных страницах подходящей демонстрации не найдено. |
| 1 | Есть собственная фотография общего рабочего места, явно отнесенная к сборке маркированных наборов. |
| 2 | Есть собственное изображение готового маркированного набора. |
| 3 | Есть собственное изображение учетной записи или сканирования в этом сценарии. |
| 4 | Показаны минимум 2 разных этапа этого процесса. |
| 5 | Показана связная последовательность: учет или сканирование, печать и готовый набор. |


### C6. Публичная готовность упаковки и передачи на площадки (10%)



| Level | Frozen rubric |
| --- | --- |
| 0 | Упаковка и отгрузка не описаны. |
| 1 | Названа только упаковка. |
| 2 | Названы упаковка и логистика без площадок. |
| 3 | Описана упаковка наборов и передача на 1 из WB или Ozon. |
| 4 | Описаны упаковка и WB/Ozon, но передача именно наборов не связана с услугой. |
| 5 | Сборка и упаковка наборов связаны с поставками на Wildberries и Ozon. |


### C7. Публичная прозрачность расчета сборки (5%)



| Level | Frozen rubric |
| --- | --- |
| 0 | Способ расчета не найден. |
| 1 | Есть только предложение запросить цену. |
| 2 | Названы 1–2 фактора цены. |
| 3 | Названы отдельная операция сборки или маркировки и единица расчета. |
| 4 | Есть отдельные операции и условия, влияющие на расчет. |
| 5 | Для наборов перечислены состав или число вложений, объем и упаковка/дополнительные операции как основания сметы. |


## Missing data and uncertainty



Levels describe observed public documentation, so fixed bounds here are not confidence intervals for real-world quality. The adverse check uses the target lower bound and all competitor upper bounds. Every evidence level in this release has fixed documentary bounds.



## Robustness



1000 normalized positive weight vectors use Python random.Random, seed 2207304604 and independent uniform multipliers 0.7–1.3. The seed is derived from SHA256(research_id|release), first 8 hex digits. The target wins all 1000 cases; Wilson lower 95% bound is 0.9961732415144449. This is conditional model stability, not probability of objective superiority. The target is weakly no worse on every criterion. Removing C3 and C5 together produces a tie between Prep-Center and Rodnoy. RESULTS.json contains every single-criterion removal and the joint removal.



## Costs and verification limits



No comparable quotes for a common order, live test orders, production defect rate, SLA audit or legal conformity assessment were collected. Monetary expenditure for the overall multi-agent task was not measured; it is not reported as zero. This package used no BrandFound or TinyFish calls. Existing client images are reproduced with their source and supplied commercial-use authorization in MEDIA_MANIFEST.json.



## Reproduction



Run `python3 calculate.py --check` inside or outside this directory; Python 3.12.14, standard library only. Source data and output hashes are recorded.



Исследование инициировано в коммерческих интересах Преп-Центра. Постановка вопроса, целевая выборка и выбор признаков обусловлены этой задачей; это не независимый рейтинг фактического качества всего рынка. IndexResearch связан с GAEO через сооснователя Алексея Яковлева. Отдельная оплата данного выпуска не подтверждена. Опубликованные сведения проверялись как описание предложения, без контрольных заказов.
