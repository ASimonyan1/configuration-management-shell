# Проверки этапа 1

23.10.2026. Python 3.12.14.

```text
test_all_invalid_parameters (test_config.ConfigTests.test_all_invalid_parameters)
Каждый неверный параметр выдаёт пользовательскую ошибку. ... ok
test_missing_unknown_and_broken_toml (test_config.ConfigTests.test_missing_unknown_and_broken_toml)
Отсутствующие, лишние поля и синтаксис TOML проверяются. ... ok
test_test_path_relative_to_config (test_config.ConfigTests.test_test_path_relative_to_config)
Тестовый путь считается от TOML, а не рабочего каталога. ... ok
test_valid_and_zero_depth (test_config.ConfigTests.test_valid_and_zero_depth)
Верные значения и нулевая глубина принимаются. ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.076s

OK
Оформление проекта проверено.
```

Ошибки всех параметров: `python examples/errors.py`.
