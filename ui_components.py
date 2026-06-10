"""Reusable Streamlit input components."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

import streamlit as st
import sympy as sp

from calculator_core import InputParseError, normalize_math_input, parse_math_expr


DEFAULT_KEYPAD: tuple[tuple[str, str], ...] = (
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("÷", "÷"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("×", "×"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("−", "-"),
    ("0", "0"),
    (".", "."),
    ("(", "("),
    (")", ")"),
    ("+", "+"),
    ("xʸ", "^"),
    ("√", "√("),
    ("π", "π"),
    ("sin", "sin("),
    ("cos", "cos("),
    ("tan", "tan("),
    ("log", "log("),
)


def _append_value(key: str, value: str) -> None:
    st.session_state[key] = f"{st.session_state.get(key, '')}{value}"


def _backspace_value(key: str) -> None:
    st.session_state[key] = st.session_state.get(key, "")[:-1]


def _clear_value(key: str) -> None:
    st.session_state[key] = ""


def _set_value(key: str, value: str) -> None:
    st.session_state[key] = value


def render_formula_input(
    label: str,
    *,
    key: str,
    default: str = "",
    allowed_symbols: Mapping[str, sp.Symbol] | Iterable[str | sp.Symbol] | None = None,
    examples: Sequence[str] = (),
    multiline: bool = False,
    help_text: str | None = None,
    show_keypad: bool = True,
    preview: bool = True,
    extra_tokens: Sequence[tuple[str, str]] = (),
) -> str:
    """Render a formula field with templates, keypad, and live preview."""
    if key not in st.session_state:
        st.session_state[key] = default

    if examples:
        selected = st.selectbox(
            "常用示例",
            ("选择一个示例", *examples),
            key=f"{key}_example",
            label_visibility="collapsed",
        )
        if selected != "选择一个示例" and selected != st.session_state.get(
            f"{key}_loaded_example"
        ):
            st.session_state[key] = selected
            st.session_state[f"{key}_loaded_example"] = selected
            st.rerun()

    if multiline:
        value = st.text_area(label, key=key, help=help_text, height=110)
    else:
        value = st.text_input(label, key=key, help=help_text)

    normalized = normalize_math_input(value)
    if preview and normalized:
        try:
            expression = parse_math_expr(normalized, allowed_symbols)
            st.caption("公式预览")
            st.latex(sp.latex(expression))
        except InputParseError as exc:
            st.caption(f"输入提示：{exc}")

    if show_keypad:
        with st.expander("打开公式快捷键盘"):
            keypad = (*DEFAULT_KEYPAD, *extra_tokens)
            for start in range(0, len(keypad), 4):
                columns = st.columns(4)
                for column, (button_label, token) in zip(
                    columns,
                    keypad[start : start + 4],
                ):
                    column.button(
                        button_label,
                        key=f"{key}_key_{start}_{button_label}",
                        use_container_width=True,
                        on_click=_append_value,
                        args=(key, token),
                    )

            backspace, clear = st.columns(2)
            backspace.button(
                "退格",
                key=f"{key}_backspace",
                use_container_width=True,
                on_click=_backspace_value,
                args=(key,),
            )
            clear.button(
                "清空",
                key=f"{key}_clear",
                use_container_width=True,
                on_click=_clear_value,
                args=(key,),
            )
    return value
