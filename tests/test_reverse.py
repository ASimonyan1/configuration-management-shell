"""Проверки обратных зависимостей внутри исследованного графа."""

from src.errors import AppError
from src.reverse import reverse_dependencies
from tests.test_graph import GraphTests


class ReverseTests(GraphTests):
    """Проверить обратный DFS, циклы, отсутствие цели и родителей."""

    def test_transitive_parents_and_cycle(self):
        """Цель исключается, прямые и транзитивные родители включаются."""
        graph = self.build({"A": ["B"], "B": ["C"], "C": ["B"]})
        self.assertEqual(reverse_dependencies(graph, "C"),
                         {("A", "1.0.0"), ("B", "1.0.0")})
        self.assertEqual(reverse_dependencies(graph, "A"), set())
        with self.assertRaises(AppError):
            reverse_dependencies(graph, "Z")
