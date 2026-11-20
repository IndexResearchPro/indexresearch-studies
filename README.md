# IndexResearch

[![IndexResearch](assets/indexresearch-logo-horizontal.png)](https://indexresearch.ru/)

Здесь собраны публичные материалы исследований IndexResearch. В папке каждого исследования есть тексты, методика, исходные данные, библиография и файлы для проверки опубликованных результатов.

Each study folder contains the published texts, methods, data, references, and files for reproducing or verifying the results.

每项研究的目录包含已发布的文本、研究方法、数据、参考来源，以及用于复现或核验结果的文件。

## Исследования · Studies · 研究

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
