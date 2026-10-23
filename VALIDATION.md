# Проверки этапа 2

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
test_dependencies_validation (test_registry.RegistryTests.test_dependencies_validation)
Отсутствующие зависимости допустимы, неверные типы запрещены. ... ok
test_network_and_json_errors (test_registry.RegistryTests.test_network_and_json_errors)
Сетевые ошибки и повреждённые ответы превращаются в AppError. ... ok
test_ranges (test_registry.RegistryTests.test_ranges)
Caret, tilde, OR, маски, сравнения и интервалы работают. ... ok
test_requested_version_and_cache (test_registry.RegistryTests.test_requested_version_and_cache)
Используется указанная версия, метаданные читаются один раз. ... ok
test_selection_and_unsupported_sources (test_registry.RegistryTests.test_selection_and_unsupported_sources)
Выбирается максимальная версия; git/file не угадываются. ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.028s

OK
Оформление проекта проверено.
```

Ошибки всех параметров: `python examples/errors.py`.
