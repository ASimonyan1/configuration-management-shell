"""Проверки DOT и команды рендеринга без внешних программ."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.errors import AppError
from src.graph import Graph
from src.visualize import dot_text, render


class VisualTests(unittest.TestCase):
    """Проверить экранирование, одиночные узлы и открытие изображения."""

    def test_dot_includes_nodes_edges_and_escaping(self):
        """Цикл и изолированный узел не теряются при экспорте."""
        a, b = ('A"', "1.0.0"), ("B", "1.0.0")
        text = dot_text(Graph({a, b}, {(a, a)}))
        self.assertIn('n0 -> n0;', text)
        self.assertIn('A\\"@1.0.0', text)
        self.assertIn('B@1.0.0', text)

    def test_renderer_and_viewer(self):
        """dot получает список аргументов, SVG открывается браузером."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph"
            with patch("src.visualize.shutil.which", return_value="dot"):
                with patch("src.visualize.subprocess.run") as run:
                    with patch("src.visualize.webbrowser.open") as show:
                        result = render(Graph(), path)
            self.assertEqual(run.call_args.args[0][1], "-Tsvg")
            show.assert_called_once_with(result.as_uri())
            self.assertTrue(path.with_suffix(".dot").exists())

    def test_missing_graphviz_preserves_dot(self):
        """Если dot отсутствует, исходный DOT остаётся доступен."""
        with tempfile.TemporaryDirectory() as folder:
            with patch("src.visualize.shutil.which", return_value=None):
                with self.assertRaises(AppError):
                    render(Graph(), Path(folder) / "graph")
