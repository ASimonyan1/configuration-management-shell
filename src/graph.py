"""Рекурсивный DFS с ограничением глубины и обработкой циклов."""

from dataclasses import dataclass, field


@dataclass
class Graph:
    """Ориентированный граф узлов (имя, версия) и рёбер."""

    nodes: set = field(default_factory=set)
    edges: set = field(default_factory=set)
    cycles: set = field(default_factory=set)


class Builder:
    """Обход с повторным раскрытием узла при более коротком пути."""

    def __init__(self, repository, config):
        """Сохранить источник данных, ограничения и состояние обхода."""
        self.repository = repository
        self.config = config
        self.graph = Graph()
        self.best_depth = {}
        self.active = set()

    def build(self):
        """Начать DFS с запрошенного пакета; корень имеет глубину ноль."""
        self.visit((self.config.package, self.config.version), 0)
        return self.graph

    def excluded(self, name):
        """Проверить непустой регистрозависимый фильтр имени."""
        value = self.config.filter_substring
        return bool(value) and value in name

    def visit(self, node, depth):
        """Рекурсивно раскрыть разрешённые узлы в пределах глубины."""
        if self.excluded(node[0]):
            return
        self.graph.nodes.add(node)
        if depth >= self.best_depth.get(node, float("inf")):
            return
        self.best_depth[node] = depth
        dependencies = self.repository.dependencies(*node)
        if depth >= self.config.max_depth:
            return
        self.active.add(node)
        try:
            for name, expression in sorted(dependencies.items()):
                if not self.excluded(name):
                    child = self.repository.resolve(name, expression)
                    self.follow(node, child, depth)
        finally:
            self.active.remove(node)

    def follow(self, parent, child, depth):
        """Сохранить ребро; обратное ребро отметить без новой рекурсии."""
        self.graph.nodes.add(child)
        self.graph.edges.add((parent, child))
        if child in self.active:
            self.graph.cycles.add((parent, child))
        else:
            self.visit(child, depth + 1)


def label(node):
    """Сформировать однозначную подпись версии пакета."""
    return "@".join(node)


def graph_text(graph):
    """Сформировать детерминированное текстовое представление графа."""
    lines = [label(node) for node in sorted(graph.nodes)]
    lines += [f"{label(a)} -> {label(b)}" for a, b in sorted(graph.edges)]
    return "\n".join(lines) or "Граф пуст: корневой пакет отфильтрован"
