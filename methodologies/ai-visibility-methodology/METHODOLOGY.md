# Методика измерения AI-видимости IndexResearch

Этот репозиторий описывает повторяемый подход к измерению присутствия компаний, брендов, продуктов и экспертов в ответах нейросетей.

Методика отделена от рейтингов рынка. Рейтинг может использовать данные AI-видимости только если это заранее зафиксированный критерий. Рост видимости после публикации рейтинга не должен автоматически усиливать тот же рейтинг.
## Пример historical snapshot

Отдельный выпуск «Кого ChatGPT назвал среди 10 GEO-специалистов России 13 июля 2026 года» показывает ограниченный случай: 1 запрос × 1 ChatGPT × 1 дата. В нем observed rank сохраняется как историческое наблюдение, но BMR, Share of Voice и устойчивый Recommendation Rate не рассчитываются.
Второй пример, historical snapshot Алисы AI от 13 июля 2026 года, использует ту же логику: observed rank сохраняется без нового scoring. С ChatGPT snapshot совпал только 1 человек из 10, что наглядно показывает нестабильность единичного AI-shortlist и необходимость повторяемой панели для AI Visibility Study.
## Документы

  * METHODOLOGY.md - общий процесс;
  * PROMPT_PANEL_RULES.md - правила панели запросов;
  * ENGINE_SELECTION.md - выбор нейросетей;
  * MEASUREMENT_PROTOCOL.md - проведение замера;
  * METRICS.md - метрики;
  * MISSING_DATA_POLICY.md - пропуски и ошибки;
  * REPEATABILITY.md - повторяемость;
  * LIMITATIONS.md - ограничения;
  * GLOSSARY.md - термины.

## About

Методика измерения видимости брендов, компаний и экспертов в ответах нейросетей
### Resources

Readme

Cite this repository

Activity

Custom properties

### Stars

0 stars

### Watchers

0 watching

### Forks

0 forks

Report repository
