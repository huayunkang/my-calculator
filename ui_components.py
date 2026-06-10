"""Reusable Streamlit input components."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime
import re

import streamlit as st
import sympy as sp

from calculator_core import (
    InputParseError,
    analyze_formula,
    normalize_math_input,
    parse_math_expr,
)
from units_core import from_si, to_si, unit_names


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

SMART_EDITOR_HTML = """
<div class="smart-editor">
  <label></label>
  <textarea rows="1" spellcheck="false"></textarea>
  <div class="completion-list" role="listbox"></div>
  <div class="editor-status" aria-live="polite"></div>
</div>
"""

SMART_EDITOR_CSS = """
.smart-editor { position: relative; font-family: inherit; }
.smart-editor label { display:block; margin-bottom:.4rem; font-weight:600; }
.smart-editor textarea {
  box-sizing:border-box; width:100%; min-height:44px; resize:vertical;
  padding:.7rem .8rem; border:1px solid rgba(128,128,128,.45);
  border-radius:.6rem; color:inherit; background:var(--st-secondary-background-color);
  font:inherit; line-height:1.45;
}
.smart-editor textarea:focus { outline:3px solid rgba(0,188,212,.45); border-color:#00a6b8; }
.completion-list { display:flex; flex-wrap:wrap; gap:.35rem; margin-top:.4rem; }
.completion-list button {
  border:1px solid rgba(128,128,128,.35); border-radius:999px; padding:.25rem .55rem;
  background:var(--st-secondary-background-color); color:inherit; cursor:pointer;
}
.editor-status { min-height:1.25rem; margin-top:.35rem; font-size:.85rem; opacity:.85; }
.editor-status.error { color:#d32f2f; }
.editor-status.ok { color:#16803c; }
"""

SMART_EDITOR_JS = """
export default function(component) {
  const { setStateValue, parentElement, data } = component;
  const label = parentElement.querySelector("label");
  const input = parentElement.querySelector("textarea");
  const list = parentElement.querySelector(".completion-list");
  const status = parentElement.querySelector(".editor-status");
  label.textContent = data.label ?? "";
  input.rows = data.multiline ? 4 : 1;
  input.placeholder = data.placeholder ?? "";

  if (input.value !== (data.value ?? "")) {
    input.value = data.value ?? "";
  }

  list.replaceChildren();
  (data.completions ?? []).forEach((name) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = name;
    button.onclick = () => {
      const prefix = input.value.match(/[A-Za-z_]\\w*$/)?.[0] ?? "";
      input.value = input.value.slice(0, input.value.length - prefix.length) + name;
      setStateValue("value", input.value);
      input.focus();
    };
    list.appendChild(button);
  });

  status.className = "editor-status " + (data.valid ? "ok" : "error");
  status.textContent = data.status ?? "";

  let timer;
  input.oninput = () => {
    clearTimeout(timer);
    timer = setTimeout(() => setStateValue("value", input.value), 250);
  };
  input.onblur = () => {
    clearTimeout(timer);
    setStateValue("value", input.value);
  };
  input.onkeydown = (event) => {
    if (event.key === "Tab" && (data.completions ?? []).length) {
      event.preventDefault();
      const prefix = input.value.match(/[A-Za-z_]\\w*$/)?.[0] ?? "";
      input.value = input.value.slice(0, input.value.length - prefix.length) + data.completions[0];
      setStateValue("value", input.value);
    }
  };
}
"""

try:
    SMART_FORMULA_COMPONENT = st.components.v2.component(
        "smart_formula_editor",
        html=SMART_EDITOR_HTML,
        css=SMART_EDITOR_CSS,
        js=SMART_EDITOR_JS,
    )
except (AttributeError, RuntimeError):
    SMART_FORMULA_COMPONENT = None


def _append_value(key: str, value: str) -> None:
    _set_value(key, f"{_get_value(key)}{value}")


def _backspace_value(key: str) -> None:
    _set_value(key, _get_value(key)[:-1])


def _clear_value(key: str) -> None:
    _set_value(key, "")


def _set_value(key: str, value: str) -> None:
    current = st.session_state.get(key)
    if isinstance(current, Mapping):
        st.session_state[key] = {**current, "value": value}
    else:
        st.session_state[key] = value


def _get_value(key: str, default: str = "") -> str:
    current = st.session_state.get(key, default)
    if isinstance(current, Mapping):
        return str(current.get("value", default))
    return str(current)


def _remember_undo(key: str, value: str) -> None:
    stack_key = f"{key}_undo"
    stack = st.session_state.setdefault(stack_key, [])
    if not stack or stack[-1] != value:
        stack.append(value)
        del stack[:-20]


def _undo_value(key: str) -> None:
    stack = st.session_state.get(f"{key}_undo", [])
    if stack:
        _set_value(key, stack.pop())


def _apply_repair(key: str, repaired: str) -> None:
    _remember_undo(key, _get_value(key))
    _set_value(key, repaired)


def render_smart_formula_input(
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
    numeric_only: bool = False,
) -> str:
    """Render a debounced formula editor with repair feedback and fallback."""
    if key not in st.session_state:
        st.session_state[key] = {"value": default} if SMART_FORMULA_COMPONENT else default

    value = _get_value(key, default)
    analysis = analyze_formula(value, allowed_symbols, numeric_only=numeric_only)
    auto_source_key = f"{key}_last_auto_source"
    if (
        analysis.automatic_changes
        and analysis.repaired != value
        and st.session_state.get(auto_source_key) != value
    ):
        _remember_undo(key, value)
        _set_value(key, analysis.repaired)
        st.session_state[auto_source_key] = value
        st.session_state[f"{key}_repair_notice"] = (
            value,
            analysis.repaired,
            analysis.automatic_changes,
        )
        st.rerun()

    repair_notice = st.session_state.get(f"{key}_repair_notice")
    if repair_notice:
        original, repaired, changes = repair_notice
        notice_col, undo_col = st.columns([4, 1])
        notice_col.success(
            f"已自动修复：`{original}` → `{repaired}`（{'；'.join(changes)}）"
        )
        undo_col.button(
            "撤销",
            key=f"{key}_undo_auto",
            on_click=_undo_value,
            args=(key,),
        )
        st.session_state.pop(f"{key}_repair_notice", None)
        value = _get_value(key, default)
        analysis = analyze_formula(value, allowed_symbols, numeric_only=numeric_only)

    status = "公式有效" if analysis.valid else (analysis.error_message or "")
    if analysis.error_position is not None:
        status += f"（约在第 {analysis.error_position + 1} 个字符）"
    if analysis.automatic_changes:
        status = "可自动修复：" + "；".join(analysis.automatic_changes)

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
            _remember_undo(key, value)
            _set_value(key, selected)
            st.session_state[f"{key}_loaded_example"] = selected
            st.rerun()

    component_failed = False
    if SMART_FORMULA_COMPONENT is not None:
        try:
            SMART_FORMULA_COMPONENT(
                data={
                    "label": label,
                    "value": value,
                    "multiline": multiline,
                    "placeholder": help_text or "",
                    "completions": list(analysis.completions),
                    "valid": analysis.valid,
                    "status": status,
                },
                default={"value": value},
                key=key,
                on_value_change=lambda: None,
            )
        except (AttributeError, KeyError, RuntimeError, TypeError):
            component_failed = True
    else:
        component_failed = True

    if component_failed:
        if multiline:
            value = st.text_area(label, value=value, key=f"{key}_fallback", help=help_text)
        else:
            value = st.text_input(label, value=value, key=f"{key}_fallback", help=help_text)
        _set_value(key, value)

    analysis = analyze_formula(value, allowed_symbols, numeric_only=numeric_only)
    for index, suggestion in enumerate(analysis.suggestions):
        suggestion_col, action_col = st.columns([4, 1])
        suggestion_col.warning(suggestion, icon="💡")
        match = re.match(r"“(.+)”是否应为“(.+)”？", suggestion)
        if match:
            source, target = match.groups()
            suggested_value = re.sub(
                rf"\b{re.escape(source)}\b",
                target,
                value,
                count=1,
            )
            action_col.button(
                "确认替换",
                key=f"{key}_suggestion_{index}",
                on_click=_apply_repair,
                args=(key, suggested_value),
            )

    if preview and analysis.valid:
        try:
            expression = parse_math_expr(analysis.repaired, allowed_symbols, numeric_only)
            st.caption("实时公式预览")
            st.latex(sp.latex(expression))
        except InputParseError:
            pass

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
                        on_click=_append_value_smart,
                        args=(key, token),
                    )

            backspace, clear = st.columns(2)
            backspace.button(
                "退格",
                key=f"{key}_backspace",
                use_container_width=True,
                on_click=_backspace_value_smart,
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


def _append_value_smart(key: str, value: str) -> None:
    _set_value(key, f"{_get_value(key)}{value}")


def _backspace_value_smart(key: str) -> None:
    _set_value(key, _get_value(key)[:-1])


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
    return render_smart_formula_input(
        label,
        key=key,
        default=default,
        allowed_symbols=allowed_symbols,
        examples=examples,
        multiline=multiline,
        help_text=help_text,
        show_keypad=show_keypad,
        preview=preview,
        extra_tokens=extra_tokens,
    )


def render_quantity_input(
    label: str,
    *,
    key: str,
    default: float,
    quantity: str | None,
    default_unit: str,
) -> tuple[float, str]:
    """Render a numeric input with a unit selector and return SI value."""
    if quantity is None:
        value = st.number_input(label, value=float(default), key=f"{key}_value")
        st.caption(default_unit)
        return float(value), default_unit

    units = unit_names(quantity)
    unit_index = units.index(default_unit) if default_unit in units else 0
    value_col, unit_col = st.columns([2, 1])
    value = value_col.number_input(label, value=float(default), key=f"{key}_value")
    unit = unit_col.selectbox("单位", units, index=unit_index, key=f"{key}_unit")
    return to_si(float(value), quantity, unit), unit


def format_quantity(value_si: float, quantity: str | None, unit: str) -> float:
    return from_si(value_si, quantity, unit) if quantity else value_si


def add_calculation_history(
    tool: str,
    expression: str,
    result: str,
    *,
    input_key: str | None = None,
) -> None:
    history = st.session_state.setdefault("calculation_history", [])
    item = {
        "tool": tool,
        "expression": expression,
        "result": result,
        "input_key": input_key,
        "time": datetime.now().strftime("%H:%M:%S"),
    }
    if not history or history[0] != item:
        history.insert(0, item)
    del history[20:]


def render_history_panel() -> None:
    history = st.session_state.setdefault("calculation_history", [])
    with st.expander(f"最近计算 ({len(history)}/20)"):
        if not history:
            st.caption("暂无计算记录。")
            return
        if st.button("清空记录", key="clear_calculation_history"):
            history.clear()
            st.rerun()
        for index, item in enumerate(history):
            st.markdown(
                f"**{item['tool']}** · {item['time']}  \n"
                f"`{item['expression']}` → {item['result']}"
            )
            if item.get("input_key") and st.button(
                "重新载入",
                key=f"reload_history_{index}",
            ):
                _set_value(item["input_key"], item["expression"])
                st.rerun()
