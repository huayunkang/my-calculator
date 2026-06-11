"""Safe parsing and validation helpers for the calculator UI."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from difflib import get_close_matches
from tokenize import TokenError
import unicodedata

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
        "；": ";",
        "：": ":",
        "＝": "=",
        "＋": "+",
        "－": "-",
        "＊": "*",
        "／": "/",
        "＾": "^",
        "．": ".",
        "　": " ",
        "【": "(",
        "】": ")",
        "｛": "(",
        "｝": ")",
        "［": "(",
        "］": ")",
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

_KNOWN_NAMES = tuple(
    sorted({*DEFAULT_SYMBOLS, *SAFE_FUNCTIONS, *SAFE_CONSTANTS})
)


class InputParseError(ValueError):
    """An input error with a message suitable for display to end users."""


@dataclass(frozen=True)
class InputChange:
    original: str
    replacement: str
    position: int
    reason: str
    requires_confirmation: bool = False


@dataclass(frozen=True)
class RepairResult:
    original: str
    repaired: str
    automatic_changes: tuple[str, ...] = ()
    suggestions: tuple[str, ...] = ()
    changes: tuple[InputChange, ...] = ()

    @property
    def changed(self) -> bool:
        return self.original != self.repaired


@dataclass(frozen=True)
class FormulaAnalysis:
    original: str
    normalized: str
    repaired: str
    valid: bool
    error_message: str | None
    error_position: int | None
    completions: tuple[str, ...]
    automatic_changes: tuple[str, ...]
    suggestions: tuple[str, ...]
    changes: tuple[InputChange, ...] = ()


def _normalize_character(character: str) -> str:
    translated = character.translate(_TRANSLATION_TABLE)
    if translated != character:
        return translated
    normalized = unicodedata.normalize("NFKC", character)
    return normalized if normalized != character else character


def normalize_math_input(text: str, context: str = "expression") -> str:
    """Convert common mathematical symbols to SymPy-compatible syntax."""
    if text is None:
        return ""

    normalized = "".join(_normalize_character(char) for char in str(text)).strip()
    if context == "equations":
        normalized = normalized.replace(";", "\n")
    elif context == "matrix":
        normalized = normalized.replace(";", "\n")
    elif context not in {"expression", "vector", "numeric"}:
        raise ValueError(f"Unsupported input context: {context}")

    normalized = re.sub(r"(?<=\d)[。](?=\d)", ".", normalized)
    normalized = re.sub(r"(?<![A-Za-z0-9_)])[。](?=\d)", ".", normalized)
    normalized = re.sub(r"(?<!\*)\^(?!\*)", "**", normalized)
    normalized = re.sub(r"√\s*\(([^()]*)\)", r"sqrt(\1)", normalized)
    normalized = re.sub(
        r"√\s*([A-Za-z0-9_.]+)",
        r"sqrt(\1)",
        normalized,
    )
    return normalized


def repair_math_input(
    text: str,
    allowed_symbols: Mapping[str, sp.Symbol] | Iterable[str | sp.Symbol] | None = None,
    context: str = "expression",
) -> RepairResult:
    """Apply deterministic repairs and return ambiguous suggestions separately."""
    original = "" if text is None else str(text)
    normalized_chars: list[str] = []
    input_changes: list[InputChange] = []
    for position, character in enumerate(original):
        replacement = _normalize_character(character)
        if replacement != character:
            input_changes.append(
                InputChange(
                    character,
                    replacement,
                    position,
                    "转换中文或全角字符",
                )
            )
        normalized_chars.append(replacement)

    for match in re.finditer(
        r"(?:(?<=\d)|(?<![A-Za-z0-9_)]))。(?=\d)",
        original,
    ):
        input_changes.append(
            InputChange("。", ".", match.start(), "将数字之间的中文句号作为小数点")
        )

    repaired = normalize_math_input("".join(normalized_chars), context=context)
    changes: list[str] = list(
        dict.fromkeys(
            item.reason for item in input_changes if not item.requires_confirmation
        )
    )
    suggestions: list[str] = []

    def apply(pattern: str, replacement: str, message: str) -> None:
        nonlocal repaired
        match = re.search(pattern, repaired)
        updated = re.sub(pattern, replacement, repaired)
        if updated != repaired:
            if match:
                input_changes.append(
                    InputChange(
                        match.group(0),
                        re.sub(pattern, replacement, match.group(0)),
                        match.start(),
                        message,
                    )
                )
            repaired = updated
            changes.append(message)

    apply(r"(?<![\d.])\.(\d)", r"0.\1", "补全小数点前的 0")
    apply(
        r"(\d|\))\s*(?=(?![eE][+-]?\d)[A-Za-z_(])",
        r"\1*",
        "补全省略的乘号",
    )
    apply(
        r"([A-DF-Za-df-z_]\w*|\))\s*(?=\d)",
        r"\1*",
        "补全省略的乘号",
    )
    apply(r"(?<!\*)\+\s*\+", "+", "合并重复的加号")

    function_names = "|".join(
        sorted((re.escape(name) for name in SAFE_FUNCTIONS), key=len, reverse=True)
    )
    repaired = re.sub(
        rf"\b({function_names})\s*\*\s*\(",
        r"\1(",
        repaired,
    )
    repaired = re.sub(
        rf"\b({function_names})\s+([A-Za-z0-9_.]+)",
        r"\1(\2)",
        repaired,
    )

    symbols = _symbol_dict(allowed_symbols)
    allowed_names = {*symbols, *SAFE_FUNCTIONS, *SAFE_CONSTANTS}
    identifier_source = _SCIENTIFIC_NUMBER_RE.sub("0", repaired)
    for name in sorted(set(_IDENTIFIER_RE.findall(identifier_source)) - allowed_names):
        matches = get_close_matches(name, allowed_names, n=2, cutoff=0.62)
        if matches:
            suggestions.append(f"“{name}”是否应为“{matches[0]}”？")
            input_changes.append(
                InputChange(
                    name,
                    matches[0],
                    repaired.find(name),
                    "函数或变量名称可能拼写错误",
                    True,
                )
            )

    if "。" in repaired:
        position = repaired.find("。")
        suggestions.append("检测到中文句号；如果它表示小数点，请确认替换为“.”。")
        input_changes.append(
            InputChange("。", ".", position, "中文句号可能是小数点", True)
        )

    balance = repaired.count("(") - repaired.count(")")
    if balance > 0:
        input_changes.append(
            InputChange("", ")" * balance, len(repaired), f"补全 {balance} 个右括号")
        )
        repaired += ")" * balance
        changes.append(f"补全 {balance} 个右括号")

    return RepairResult(
        original=original,
        repaired=repaired,
        automatic_changes=tuple(dict.fromkeys(changes)),
        suggestions=tuple(dict.fromkeys(suggestions)),
        changes=tuple(input_changes),
    )


def analyze_formula(
    text: str,
    allowed_symbols: Mapping[str, sp.Symbol] | Iterable[str | sp.Symbol] | None = None,
    numeric_only: bool = False,
    context: str = "expression",
) -> FormulaAnalysis:
    """Analyze an expression for live editor feedback."""
    repair = repair_math_input(text, allowed_symbols, context=context)
    error_message = None
    error_position = None
    valid = False
    try:
        if context == "equations":
            parse_equations(repair.repaired, allowed_symbols)
        elif context == "matrix":
            parse_matrix(repair.repaired)
        elif context == "vector":
            parse_vector(repair.repaired)
        else:
            parse_math_expr(
                repair.repaired,
                allowed_symbols,
                numeric_only=numeric_only,
                context=context,
            )
        valid = True
    except InputParseError as exc:
        error_message = str(exc)
        unknown = re.search(r"不支持的变量或函数：([^。]+)", error_message)
        if unknown:
            error_position = repair.repaired.find(unknown.group(1).split("、")[0])
        elif repair.repaired.count(")") > repair.repaired.count("("):
            error_position = repair.repaired.rfind(")")

    prefix_match = re.search(
        r"([A-Za-z_]\w*)$",
        normalize_math_input(text, context=context),
    )
    completions: tuple[str, ...] = ()
    if prefix_match:
        prefix = prefix_match.group(1)
        names = sorted(
            {
                *_KNOWN_NAMES,
                *_symbol_dict(allowed_symbols),
            }
        )
        completions = tuple(
            name for name in names if name.startswith(prefix) and name != prefix
        )[:8]

    return FormulaAnalysis(
        original="" if text is None else str(text),
        normalized=normalize_math_input(text, context=context),
        repaired=repair.repaired,
        valid=valid,
        error_message=error_message,
        error_position=error_position,
        completions=completions,
        automatic_changes=repair.automatic_changes,
        suggestions=repair.suggestions,
        changes=repair.changes,
    )


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
    context: str = "expression",
) -> sp.Expr:
    """Parse a restricted mathematical expression.

    The parser accepts only known variables, a small function allow-list, and
    arithmetic syntax. It rejects Python attributes, strings, containers, and
    unknown names before SymPy receives the expression.
    """
    normalized = repair_math_input(
        text,
        allowed_symbols,
        context=context,
    ).repaired
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
        raise InputParseError(
            "公式语法有误，请检查括号，并确认数字、变量或括号之间有乘号。"
        ) from exc
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
    expression = parse_math_expr(
        text,
        allowed_symbols={},
        numeric_only=True,
        context="numeric",
    )
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
    normalized = normalize_math_input(text, context="equations")
    chunks = _split_top_level(normalized, separators={",", "\n"})
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


def _split_top_level(text: str, separators: set[str]) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    depth = 0
    for character in text:
        if character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
        if character in separators and depth == 0:
            chunk = "".join(current).strip()
            if chunk:
                chunks.append(chunk)
            current = []
        else:
            current.append(character)
    chunk = "".join(current).strip()
    if chunk:
        chunks.append(chunk)
    return chunks


def parse_matrix(text: str) -> sp.Matrix:
    """Parse rows separated by newlines and entries separated by spaces/commas."""
    if not text or not text.strip():
        raise InputParseError("请输入矩阵。")

    normalized = normalize_math_input(text, context="matrix").strip()
    if normalized.startswith("(") and normalized.endswith(")"):
        normalized = normalized[1:-1].strip()

    rows: list[list[sp.Expr]] = []
    for row_number, row_text in enumerate(normalized.splitlines(), start=1):
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
    normalized = normalize_math_input(text or "", context="vector").strip()
    if normalized.startswith("(") and normalized.endswith(")"):
        normalized = normalized[1:-1].strip()
    entries = [entry for entry in re.split(r"[\s,]+", normalized) if entry]
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
    if isinstance(error, OverflowError):
        return "数值过大，已超出当前计算或绘图范围。"
    if isinstance(error, ValueError) and "domain" in str(error).lower():
        return "输入超出函数定义域，请检查根号、对数或分母中的数值。"
    return fallback
