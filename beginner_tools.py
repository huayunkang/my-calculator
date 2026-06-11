"""Beginner-oriented calculations and natural-language tool search."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from fractions import Fraction
import math
import re

import sympy as sp

from calculator_core import InputParseError, normalize_math_input, parse_numeric


@dataclass(frozen=True)
class ToolMatch:
    target: str
    title: str
    reason: str
    example: str | None = None
    input_key: str | None = None


@dataclass(frozen=True)
class ToolDefinition:
    target: str
    title: str
    keywords: tuple[str, ...]
    example: str | None = None
    input_key: str | None = None


TOOL_SEARCH_CATALOG: tuple[ToolDefinition, ...] = (
    ToolDefinition("📚 微积分", "求导与积分", ("求导", "导数", "微分", "积分", "定积分"), "x^3-3*x", "math_expr"),
    ToolDefinition("🔍 解方程", "解方程", ("方程", "二元方程", "未知数", "解x"), "x+y=3\nx-y=1", "eq_expr"),
    ToolDefinition("➕ 级数", "级数求和", ("级数", "数列", "求和", "西格玛"), "n^2", "sum_expr"),
    ToolDefinition("📈 函数分析", "函数分析与绘图", ("函数", "画图", "零点", "极值", "切线"), "x^3-3*x", "function_analysis_expr"),
    ToolDefinition("📊 统计概率", "统计与概率", ("平均数", "中位数", "方差", "回归", "概率", "正态分布")),
    ToolDefinition("🔁 单位换算", "单位换算", ("公里转英里", "单位", "换算", "温度", "速度", "英里")),
    ToolDefinition("🧪 物理工具箱", "物理工具箱", ("算电费", "欧姆定律", "电路", "速度", "功率", "热量", "压强")),
    ToolDefinition("🧰 新手实用工具", "分数、百分比和几何", ("分数", "通分", "百分比", "二次方程", "面积", "体积", "几何", "科学计数法", "常数", "日期差")),
)


def search_tools(query: str) -> list[ToolMatch]:
    normalized = re.sub(r"\s+", "", (query or "").lower())
    if not normalized:
        return []

    ranked: list[tuple[int, ToolDefinition, str]] = []
    for tool in TOOL_SEARCH_CATALOG:
        title = tool.title.lower()
        matched_keywords = [keyword for keyword in tool.keywords if keyword.lower() in normalized]
        score = 0
        reason = ""
        if normalized in title or title in normalized:
            score = 100
            reason = f"与“{tool.title}”直接匹配"
        elif matched_keywords:
            longest = max(matched_keywords, key=len)
            score = 60 + len(longest)
            reason = f"匹配关键词“{longest}”"
        else:
            query_chars = set(normalized)
            overlap = len(query_chars & set(title))
            if overlap >= 2:
                score = overlap
                reason = "名称相近"
        if score:
            ranked.append((score, tool, reason))

    ranked.sort(key=lambda item: (-item[0], item[1].title))
    return [
        ToolMatch(
            target=tool.target,
            title=tool.title,
            reason=reason,
            example=tool.example,
            input_key=tool.input_key,
        )
        for _, tool, reason in ranked[:5]
    ]


def parse_fraction(text: str) -> Fraction:
    normalized = normalize_math_input(text, context="numeric")
    if not normalized:
        raise InputParseError("请输入分数，例如 6/8。")
    try:
        return Fraction(normalized)
    except (ValueError, ZeroDivisionError) as exc:
        raise InputParseError("分数格式有误，请使用 3/4、2 或 0.25。") from exc


def common_denominator(text: str) -> tuple[list[Fraction], int, list[int]]:
    normalized = normalize_math_input(text, context="vector")
    entries = [item for item in re.split(r"[\s,;]+", normalized) if item]
    if len(entries) < 2:
        raise InputParseError("请至少输入两个分数，例如 1/2，2/3。")
    fractions = [parse_fraction(item) for item in entries]
    denominator = math.lcm(*(item.denominator for item in fractions))
    numerators = [item.numerator * (denominator // item.denominator) for item in fractions]
    return fractions, denominator, numerators


def percentage_value(base: float, percent: float) -> float:
    return float(base) * float(percent) / 100


def percentage_change(original: float, current: float) -> float:
    if original == 0:
        raise InputParseError("原数值不能为 0，否则无法计算变化率。")
    return (float(current) - float(original)) / float(original) * 100


def solve_quadratic(a: float, b: float, c: float) -> tuple[sp.Expr, tuple[sp.Expr, ...]]:
    if a == 0:
        raise InputParseError("二次项系数 a 不能为 0。")
    discriminant = sp.simplify(b**2 - 4 * a * c)
    roots = (
        sp.simplify((-b + sp.sqrt(discriminant)) / (2 * a)),
        sp.simplify((-b - sp.sqrt(discriminant)) / (2 * a)),
    )
    return discriminant, roots


def geometry_value(shape: str, values: dict[str, float]) -> tuple[str, float, str]:
    if any(value < 0 for value in values.values()):
        raise InputParseError("长度、半径和高度不能为负数。")
    if shape == "矩形面积":
        return "面积", values["length"] * values["width"], "m²"
    if shape == "三角形面积":
        return "面积", values["base"] * values["height"] / 2, "m²"
    if shape == "圆面积":
        return "面积", math.pi * values["radius"] ** 2, "m²"
    if shape == "长方体体积":
        return "体积", values["length"] * values["width"] * values["height"], "m³"
    if shape == "圆柱体积":
        return "体积", math.pi * values["radius"] ** 2 * values["height"], "m³"
    if shape == "球体积":
        return "体积", 4 * math.pi * values["radius"] ** 3 / 3, "m³"
    raise InputParseError(f"暂不支持该几何图形：{shape}")


def scientific_notation(text: str) -> tuple[float, int, str]:
    value = parse_numeric(text)
    if value == 0:
        return 0.0, 0, "0"
    exponent = math.floor(math.log10(abs(value)))
    coefficient = value / (10**exponent)
    return coefficient, exponent, f"{coefficient:.10g}e{exponent:+d}"


MATH_CONSTANTS: dict[str, tuple[sp.Expr, str]] = {
    "圆周率 π": (sp.pi, "圆周长与直径的比值"),
    "自然常数 e": (sp.E, "自然对数的底"),
    "黄金比例 φ": ((1 + sp.sqrt(5)) / 2, "常见于比例、几何和数列"),
    "根号 2": (sp.sqrt(2), "边长为 1 的正方形对角线长度"),
    "光速 c": (sp.Integer(299792458), "真空光速，单位 m/s"),
    "标准重力 g": (sp.Float("9.80665"), "标准重力加速度，单位 m/s²"),
}


def date_difference(start: date, end: date) -> tuple[int, int]:
    days = (end - start).days
    return days, abs(days) // 7
