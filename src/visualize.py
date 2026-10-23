"""Экспорт DOT и отображение SVG, созданного Graphviz."""

import json
import shutil
import subprocess
import webbrowser
from pathlib import Path

from .errors import AppError
from .graph import label

RENDER_TIMEOUT = 30


def dot_text(graph):
    """Экранировать подписи и представить все узлы и рёбра на языке DOT."""
    lines = ['digraph dependencies {', '  rankdir=LR;']
    identifiers = {node: f"n{i}" for i, node in enumerate(sorted(graph.nodes))}
    for node, identifier in identifiers.items():
        text = json.dumps(label(node), ensure_ascii=False)
        lines.append(f"  {identifier} [label={text}];")
    for source, target in sorted(graph.edges):
        lines.append(f"  {identifiers[source]} -> {identifiers[target]};")
    return "\n".join(lines + ['}']) + "\n"


def render(graph, output, show=True):
    """Сохранить DOT, вызвать dot без shell и открыть SVG в браузере."""
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    dot_path = output.with_suffix(".dot")
    dot_path.write_text(dot_text(graph), encoding="utf-8")
    executable = shutil.which("dot")
    if not executable:
        raise AppError(f"Graphviz не найден в PATH; DOT сохранён: {dot_path}")
    svg_path = output.with_suffix(".svg")
    try:
        subprocess.run([executable, "-Tsvg", str(dot_path), "-o",
                        str(svg_path)], check=True, capture_output=True,
                       timeout=RENDER_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        raise AppError(f"Ошибка Graphviz: {exc}") from exc
    if show and not webbrowser.open(svg_path.as_uri()):
        raise AppError(f"Откройте изображение вручную: {svg_path}")
    return svg_path
