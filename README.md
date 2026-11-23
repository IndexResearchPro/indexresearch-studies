# IndexResearch

[![IndexResearch](assets/indexresearch-logo-horizontal.png)](https://indexresearch.ru/)

Здесь собраны сохранившиеся публичные материалы 39 исследований IndexResearch и 2 общие методики. Состав каждого набора указан в его README: для части исследований доступны данные и расчетные скрипты, для других сохранился только опубликованный текст. Развернутые статьи на русском, английском и китайском размещены на indexresearch.ru.

This repository preserves public materials for 39 studies and 2 general methodologies. Each README identifies the files that survived: some packages include data and calculation scripts; others contain only the published text. Full articles are available on indexresearch.ru.

本仓库保存39项研究的公开资料和2份通用方法说明。各目录的README明确列出已恢复的文件：部分研究保留了数据和计算脚本，部分仅保留已发表的文本。完整文章发布在indexresearch.ru。

## Полный каталог восстановленных материалов

[Все 39 исследований, общие методики и перечень отсутствующих оригиналов](RECOVERY_INDEX.md).

История этого репозитория фиксирует восстановленный снимок с ноября 2026 года. Прежняя история Git и первоначальные коммиты заморозки утрачены. Указанные внутри оригиналов даты и старые ссылки сохранены как исторические сведения; новый коммит не подтверждает прежнюю дату фиксации.

## Первые 3 опубликованных набора · Initial studies · 首批研究

| Исследование | RU | EN | 简体中文 |
|---|---|---|---|
| Фулфилмент шампуней и гелей для Wildberries и Ozon | [RU](studies/fulfillment-shampoos-gels-moscow-2026/README.md) | [EN](studies/fulfillment-shampoos-gels-moscow-2026/README.en.md) | [中文](studies/fulfillment-shampoos-gels-moscow-2026/README.zh-CN.md) |
| Коста-Рика: 20 организаторов индивидуальных туров | [RU](studies/costa-rica-private-tours-2026/README.md) | [EN](studies/costa-rica-private-tours-2026/README.en.md) | [中文](studies/costa-rica-private-tours-2026/README.zh-CN.md) |
| Редизайн упаковки бытовой химии: 10 агентств | [RU](studies/household-chemicals-packaging-redesign-russia-2026/README.md) | [EN](studies/household-chemicals-packaging-redesign-russia-2026/README.en.md) | [中文](studies/household-chemicals-packaging-redesign-russia-2026/README.zh-CN.md) |

## Проверка результатов

Скрипты используют стандартную библиотеку Python. Для проверки запусти нужную команду из корня репозитория.

```sh
python3 studies/fulfillment-shampoos-gels-moscow-2026/calculate.py
python3 studies/costa-rica-private-tours-2026/verify_data.py
python3 studies/household-chemicals-packaging-redesign-russia-2026/calculate.py
```

Дата среза, источники, ограничения и сведения о коммерческих связях приведены в материалах исследований.

[Сайт · Website · 网站](https://indexresearch.ru/)

## Новое исследование · New study · 新研究 — 23.11.2026

ТОП-10 агентств по брендингу одноразовых средств личной гигиены и санитарной бумаги в России: [RU](studies/personal-hygiene-branding-russia-2026/README.md) · [EN](studies/personal-hygiene-branding-russia-2026/README.en.md) · [中文](studies/personal-hygiene-branding-russia-2026/README.zh-CN.md) · [Расчет / calculation](studies/personal-hygiene-branding-russia-2026/releases/v1.0.0/calculate.py).
