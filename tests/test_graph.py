"""Проверки рекурсивного DFS, фильтра, циклов и разных путей."""

import json
import tempfile
import unittest
from pathlib import Path

from src.config import Config
from src.errors import AppError
from src.graph import Builder
from src.test_repository import TestRepository


def repository_data(edges):
    """Преобразовать компактный граф в формат тестового репозитория."""
    return {name: {"1.0.0": {"dependencies": {
        child: "1.0.0" for child in children}}}
        for name, children in edges.items()}


class GraphTests(unittest.TestCase):
    """Проверить математические свойства построенного графа."""

    def build(self, edges, depth=8, substring=""):
        """Создать локальный источник и выполнить DFS."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "repo.json"
            path.write_text(json.dumps(repository_data(edges)))
            repository = TestRepository(path)
            config = Config("A", str(path), True, "1.0.0", depth, substring)
            return Builder(repository, config).build()

    def test_cycles_and_self_loop(self):
        """Цикл не зацикливает рекурсию и сохраняется в рёбрах."""
        graph = self.build({"A": ["B", "A"], "B": ["A"]})
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 3)
        self.assertEqual(len(graph.cycles), 2)

    def test_depth_and_filter(self):
        """Глубина ноль оставляет корень; фильтр исключает поддерево."""
        edges = {"A": ["B"], "B": ["C"], "C": []}
        self.assertEqual(len(self.build(edges, 0).nodes), 1)
        self.assertEqual(len(self.build(edges, 1).nodes), 2)
        self.assertEqual(len(self.build(edges, 8, "B").nodes), 1)
        self.assertFalse(self.build(edges, 8, "A").nodes)

    def test_shorter_path_reexpands_shared_node(self):
        """Более короткий путь раскрывает ещё доступные по глубине узлы."""
        edges = {"A": ["B", "D"], "B": ["C"], "C": ["D"],
                 "D": ["E"], "E": ["F"], "F": []}
        graph = self.build(edges, 3)
        self.assertIn(("F", "1.0.0"), graph.nodes)

    def test_invalid_repository(self):
        """Отсутствующие цели и неверные имена отклоняются."""
        for edges in ({"A": ["B"]}, {"A": ["bad"], "bad": []}):
            with self.assertRaises(AppError):
                self.build(edges)
