"""Safe parsing and validation helpers for the calculator UI."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from tokenize import TokenError

import sympy as sp


MAX_EXPRESSION_LENGTH = 500

DEFAULT_SYMBOLS = {
    name: symbol
    for name, symbol in zip(
        ("x", "y", "z", "n", "i", "k", "t"),
        sp.symbols("x y z n i k t"),
    )
}

SAFE_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "Abs": sp.Abs,
    "abs": sp.Abs,
    "factorial": sp.factorial,
    "floor": sp.floor,
    "ceiling": sp.ceiling,
}

SAFE_CONSTANTS = {
    "pi": sp.pi,
    "E": sp.E,
    "oo": sp.oo,
    "I": sp.I,
}

_TRANSLATION_TABLE = str.maketrans(
    {
        "×": "*",
        "·": "*",
        "÷": "/",
        "−": "-",
        "–": "-",
        "—": "-",
        "π": "pi",
        "∞": "oo",
        "（": "(",
        "）": ")",
        "，": ",",
        "【": "(",
        "】": ")",
    }
)

_IDENTIFIER_RE = re.compile(r"[A-Za-z_]\w*")
_SCIENTIFIC_NUMBER_RE = re.compile(
    r"(?<![A-Za-z_])(?:\d+(?:\.\d*)?|\.\d+)[eE][+-]?\d+"
)
_ALLOWED_CHARS_RE = re.compile(r"^[0-9A-Za-z_+\-*/().,\s]*$")
_DANGEROUS_PATTERNS = (
    "__",
    "lambda",
    "import",
    "eval",
    "exec",
    "open",
    "compile",
    "globals",
    "locals",
    "getattr",
    "setattr",
    "delattr",
)


class InputParseError(ValueError):
    """An input error with a message suitable for display to end users."""


def normalize_math_input(text: str) -> str:
    """Convert common mathematical symbols to SymPy-compatible syntax."""
    if text is None:
        return ""

    normalized = str(text).strip().translate(_TRANSLATION_TABLE)
    normalized = re.sub(r"(?<!\*)\^(?!\*)", "**", normalized)
    normalized = re.sub(r"√\s*\(([^()]*)\)", r"sqrt(\1)", normalized)
    normalized = re.sub(
        r"√\s*([A-Za-z0-9_.]+)",
        r"sqrt(\1)",
        normalized,
    )
    return normalized


def _symbol_dict(
    allowed_symbols: Mapping[str, sp.Symbol] | Iterable[str | sp.Symbol] | None,
) -> dict[str, sp.Symbol]:
    if allowed_symbols is None:
        return dict(DEFAULT_SYMBOLS)
    if isinstance(allowed_symbols, Mapping):
        return dict(allowed_symbols)

    symbols: dict[str, sp.Symbol] = {}
    for item in allowed_symbols:
        if isinstance(item, sp.Symbol):
            symbols[str(item)] = item
        else:
            name = str(item)
            symbols[name] = DEFAULT_SYMBOLS.get(name, sp.Symbol(name))
    return symbols


def parse_math_expr(
    text: str,
    allowed_symbols: Mapping[str, sp.Symbol] | Iterable[str | sp.Symbol] | None = None,
    numeric_only: bool = False,
) -> sp.Expr:
    """Parse a restricted mathematical expression.

    The parser accepts only known variables, a small function allow-list, and
    arithmetic syntax. It rejects Python attributes, strings, containers, and
    unknown names before SymPy receives the expression.
    """
    normalized = normalize_math_input(text)
    if not normalized:
        raise InputParseError("请输入公式或数值。")
    if len(normalized) > MAX_EXPRESSION_LENGTH:
        raise InputParseError(f"输入过长，请控制在 {MAX_EXPRESSION_LENGTH} 个字符以内。")

    lowered = normalized.lower()
    if any(pattern in lowered for pattern in _DANGEROUS_PATTERNS):
        raise InputParseError("输入包含不允许的名称或操作。")
    if not _ALLOWED_CHARS_RE.fullmatch(normalized):
        raise InputParseError("输入含有无法识别的字符，请使用数字、变量和常见运算符。")
    if "[" in normalized or "]" in normalized or "{" in normalized or "}" in normalized:
        raise InputParseError("公式中不支持列表或字典语法。")
    if normalized.count("(") != normalized.count(")"):
        raise InputParseError("左右括号数量不一致。")

    symbols = _symbol_dict(allowed_symbols)
    local_dict = {
        **symbols,
        **SAFE_FUNCTIONS,
        **SAFE_CONSTANTS,
    }
    allowed_names = set(local_dict)
    identifier_source = _SCIENTIFIC_NUMBER_RE.sub("0", normalized)
    unknown_names = sorted(set(_IDENTIFIER_RE.findall(identifier_source)) - allowed_names)
    if unknown_names:
        names = "、".join(unknown_names[:4])
        raise InputParseError(f"不支持的变量或函数：{names}。")

    try:
        expression = sp.sympify(normalized, locals=local_dict, evaluate=True)
    except (TypeError, ValueError, SyntaxError, TokenError) as exc:
        raise InputParseError("公式语法有误，请检查运算符和括号。") from exc
    except Exception as exc:
        raise InputParseError("公式无法解析，请检查输入格式。") from exc

    if not isinstance(expression, sp.Expr):
        raise InputParseError("请输入一个可计算的数学表达式。")
    if numeric_only and expression.free_symbols:
        names = "、".join(sorted(str(symbol) for symbol in expression.free_symbols))
        raise InputParseError(f"这里需要具体数值，不能包含变量：{names}。")
    if numeric_only and expression.has(sp.zoo, sp.nan):
        raise InputParseError("数值未定义，请检查是否存在除以零。")
    return expression


def parse_numeric(
    text: str,
    *,
    positive: bool = False,
    non_negative: bool = False,
    non_zero: bool = False,
) -> float:
    """Parse a finite real number and apply common range constraints."""
    expression = parse_math_expr(text, allowed_symbols={}, numeric_only=True)
    if expression.has(sp.oo, -sp.oo, sp.zoo, sp.nan) or expression.is_real is False:
        raise InputParseError("请输入有限实数。")
    try:
        value = float(expression.evalf())
    except (TypeError, ValueError, OverflowError) as exc:
        raise InputParseError("该数值无法转换为有限小数。") from exc

    if positive and value <= 0:
        raise InputParseError("该数值必须大于 0。")
    if non_negative and value < 0:
        raise InputParseError("该数值不能小于 0。")
    if non_zero and value == 0:
        raise InputParseError("该数值不能为 0。")
    return value


def parse_equations(
    text: str,
    allowed_symbols: Mapping[str, sp.Symbol] | Iterable[str | sp.Symbol] | None = None,
) -> tuple[list[sp.Expr | sp.Equality], list[sp.Expr]]:
    """Parse equations separated by newlines, semicolons, or commas."""
    normalized = normalize_math_input(text).replace(";", "\n")
    chunks = [
        chunk.strip()
        for line in normalized.splitlines()
        for chunk in line.split(",")
        if chunk.strip()
    ]
    if not chunks:
        raise InputParseError("请至少输入一个方程。")

    equations: list[sp.Expr | sp.Equality] = []
    standard_forms: list[sp.Expr] = []
    for chunk in chunks:
        if chunk.count("=") > 1:
            raise InputParseError(f"方程“{chunk}”包含多个等号。")
        if "=" in chunk:
            left_text, right_text = chunk.split("=", 1)
            left = parse_math_expr(left_text, allowed_symbols)
            right = parse_math_expr(right_text, allowed_symbols)
            equations.append(sp.Eq(left, right))
            standard_forms.append(sp.simplify(left - right))
        else:
            expression = parse_math_expr(chunk, allowed_symbols)
            equations.append(expression)
            standard_forms.append(expression)
    return equations, standard_forms


def parse_matrix(text: str) -> sp.Matrix:
    """Parse rows separated by newlines and entries separated by spaces/commas."""
    if not text or not text.strip():
        raise InputParseError("请输入矩阵。")

    rows: list[list[sp.Expr]] = []
    for row_number, row_text in enumerate(text.strip().splitlines(), start=1):
        entries = [entry for entry in re.split(r"[\s,]+", row_text.strip()) if entry]
        if not entries:
            continue
        try:
            rows.append([parse_math_expr(entry) for entry in entries])
        except InputParseError as exc:
            raise InputParseError(f"矩阵第 {row_number} 行：{exc}") from exc

    if not rows:
        raise InputParseError("请输入矩阵。")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise InputParseError("矩阵每一行必须有相同数量的元素。")
    return sp.Matrix(rows)


def parse_vector(text: str) -> sp.Matrix:
    """Parse a comma or whitespace separated vector."""
    entries = [entry for entry in re.split(r"[\s,]+", (text or "").strip()) if entry]
    if not entries:
        raise InputParseError("请输入向量。")
    return sp.Matrix([parse_math_expr(entry) for entry in entries])


def user_error_message(error: Exception, fallback: str = "计算失败。") -> str:
    """Return a concise user-facing message without exposing internals."""
    if isinstance(error, InputParseError):
        return str(error)
    if isinstance(error, ZeroDivisionError):
        return "计算中出现除以零，请检查输入范围。"
    if isinstance(error, (sp.ShapeError, sp.NonSquareMatrixError)):
        return f"矩阵维度不符合要求：{error}"
    return fallback
