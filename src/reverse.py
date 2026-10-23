"""Поиск прямых и транзитивных обратных зависимостей в построенном графе."""

from .errors import AppError


def reverse_dependencies(graph, name):
    """Обойти обратные рёбра рекурсивным DFS, исключив саму цель."""
    targets = {node for node in graph.nodes if node[0] == name}
    if not targets:
        raise AppError(f"Пакет {name} отсутствует в исследованном графе")
    parents = {node: set() for node in graph.nodes}
    for source, target in graph.edges:
        parents[target].add(source)
    visited = set(targets)
    for target in targets:
        visit_parents(target, parents, visited)
    return visited - targets


def visit_parents(node, parents, visited):
    """Рекурсивно обойти ещё не посещённые обратные зависимости."""
    for parent in sorted(parents[node]):
        if parent not in visited:
            visited.add(parent)
            visit_parents(parent, parents, visited)
