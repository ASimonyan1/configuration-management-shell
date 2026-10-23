# Проверки этапа 5

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
test_cycles_and_self_loop (test_graph.GraphTests.test_cycles_and_self_loop)
Цикл не зацикливает рекурсию и сохраняется в рёбрах. ... ok
test_depth_and_filter (test_graph.GraphTests.test_depth_and_filter)
Глубина ноль оставляет корень; фильтр исключает поддерево. ... ok
test_invalid_repository (test_graph.GraphTests.test_invalid_repository)
Отсутствующие цели и неверные имена отклоняются. ... ok
test_shorter_path_reexpands_shared_node (test_graph.GraphTests.test_shorter_path_reexpands_shared_node)
Более короткий путь раскрывает ещё доступные по глубине узлы. ... ok
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
test_dot_includes_nodes_edges_and_escaping (test_visualize.VisualTests.test_dot_includes_nodes_edges_and_escaping)
Цикл и изолированный узел не теряются при экспорте. ... ok
test_missing_graphviz_preserves_dot (test_visualize.VisualTests.test_missing_graphviz_preserves_dot)
Если dot отсутствует, исходный DOT остаётся доступен. ... ok
test_renderer_and_viewer (test_visualize.VisualTests.test_renderer_and_viewer)
dot получает список аргументов, SVG открывается браузером. ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.048s

OK
Оформление проекта проверено.
```

Ошибки всех параметров: `python examples/errors.py`.
