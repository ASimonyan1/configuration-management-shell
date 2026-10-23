"""Самостоятельное разрешение распространённых диапазонов npm SemVer."""

import re

from .errors import AppError

PARTS = 3
OPERATORS = {">", ">=", "<", "<=", "="}


def numbers(value):
    """Разобрать стабильную версию без сторонних библиотек."""
    clean = value.lstrip("v=").split("+")[0]
    if not re.fullmatch(r"\d+\.\d+\.\d+", clean):
        raise AppError(f"Неподдерживаемая версия диапазона: {value}")
    return tuple(int(item) for item in clean.split("."))


def partial(value):
    """Развернуть неполную версию или маску в нижнюю и верхнюю границу."""
    parts = value.lstrip("v").split(".")
    if len(parts) > PARTS:
        raise AppError(f"Неверная версия: {value}")
    fixed = []
    for item in parts:
        if item.lower() in {"x", "*"}:
            break
        if not item.isdigit():
            raise AppError(f"Неподдерживаемый диапазон: {value}")
        fixed.append(int(item))
    low = tuple(fixed + [0] * (PARTS - len(fixed)))
    if not fixed:
        return low, None, False
    if len(fixed) == PARTS:
        return low, low, True
    high = list(low)
    high[len(fixed) - 1] += 1
    return low, tuple(high), False


def compare(version, operator, boundary):
    """Сравнить тройки версии с заданным оператором."""
    values = {">": version > boundary, ">=": version >= boundary,
              "<": version < boundary, "<=": version <= boundary,
              "=": version == boundary}
    return values[operator]


def compatible(version, token):
    """Проверить caret или tilde с правилами нулевой основной версии."""
    low, high, exact = partial(token[1:])
    fixed = re.split(r"[xX*]", token[1:])[0].rstrip(".")
    if not fixed:
        return True
    count = len(fixed.split("."))
    if token[0] == "~":
        index = min(count - 1, 1)
    else:
        index = next((i for i, part in enumerate(low) if part), count - 1)
    upper = list(low)
    upper[index] += 1
    upper[index + 1:] = [0] * (PARTS - index - 1)
    return low <= version < tuple(upper)


def match_token(version, token):
    """Проверить один точный, масочный или сравнительный диапазон."""
    if token.startswith(("^", "~")):
        return compatible(version, token)
    found = re.fullmatch(r"(>=|<=|>|<|=)?(.+)", token)
    operator, value = found.groups()
    low, high, exact = partial(value)
    if operator and operator != "=":
        return match_comparator(version, operator, low, high, exact)
    return version == low if exact else version >= low and (
        high is None or version < high)


def match_comparator(version, operator, low, high, exact):
    """Сравнить неполную границу по правилам диапазонов npm."""
    if exact or operator in {">=", "<"}:
        return compare(version, operator, low)
    if high is None:
        return operator == "<="
    return version >= high if operator == ">" else version < high


def matches(value, expression):
    """Поддержать OR, пересечение, дефисный интервал и маски."""
    version = numbers(value)
    for group in expression.split("||"):
        group = group.strip() or "*"
        if " - " in group:
            left, right = group.split(" - ", 1)
            low = partial(left)[0]
            end, high, exact = partial(right)
            if version >= low and (version <= end if exact
                                   else high is None or version < high):
                return True
        else:
            group = re.sub(r"([<>=~^]+)\s+", r"\1", group)
            if all(match_token(version, token) for token in group.split()):
                return True
    return False


def select_version(versions, expression, tags=None):
    """Выбрать максимальную стабильную версию; точные prerelease допустимы."""
    expression = (tags or {}).get(expression, expression)
    if expression in versions:
        return expression
    candidates = [value for value in versions if "-" not in value]
    suitable = [value for value in candidates if matches(value, expression)]
    if not suitable:
        raise AppError(f"Нет версии для диапазона {expression}")
    return max(suitable, key=numbers)
