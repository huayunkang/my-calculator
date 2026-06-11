"""Additional calculator pages kept separate from the main Streamlit entrypoint."""

from __future__ import annotations

import math
import re
from datetime import date
from statistics import NormalDist

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import sympy as sp

from beginner_tools import (
    MATH_CONSTANTS,
    common_denominator,
    date_difference,
    geometry_value,
    parse_fraction,
    percentage_change,
    percentage_value,
    scientific_notation,
    solve_quadratic,
)
from calculator_core import (
    InputParseError,
    parse_math_expr,
    parse_numeric,
    repair_math_input,
    user_error_message,
)
from physics_core import (
    PhysicsCalculationError,
    calculate_physics,
    categories,
    tools_for_category,
)
from ui_components import (
    add_calculation_history,
    format_quantity,
    render_formula_input,
    render_quantity_input,
)
from units_core import UNIT_CATEGORIES, convert_value, unit_names


X = sp.Symbol("x", real=True)


def _style_plot(dark_mode: bool):
    plt.style.use("dark_background" if dark_mode else "default")


def _beginner_intro(message: str) -> None:
    if st.session_state.get("beginner_mode", True):
        st.info(message, icon="🧭")


def render_function_analysis(dark_mode: bool) -> None:
    st.markdown("### 📈 函数分析实验室")
    _beginner_intro("输入一个关于 x 的函数，可以一次看到图像、导数、零点、驻点和指定位置的切线。")
    expression_text = render_formula_input(
        "函数 f(x)",
        key="function_analysis_expr",
        default="x^3 - 3x",
        allowed_symbols={"x": X},
        examples=("x^3 - 3*x", "sin(x)", "exp(-x^2)", "1/(x-1)"),
        extra_tokens=(("x", "x"), ("exp", "exp(")),
    )
    range_left, range_right, tangent_col = st.columns(3)
    start = range_left.number_input("绘图区间起点", value=-5.0)
    end = range_right.number_input("绘图区间终点", value=5.0)
    tangent_x = tangent_col.number_input("切点 x₀", value=1.0)

    if st.button("分析函数", key="analyze_function"):
        try:
            if start >= end:
                raise InputParseError("绘图区间起点必须小于终点。")
            function = parse_math_expr(expression_text, {"x": X})
            derivative = sp.simplify(sp.diff(function, X))
            antiderivative = sp.integrate(function, X)
            zeros = sp.solve(sp.Eq(function, 0), X)
            critical_points = sp.solve(sp.Eq(derivative, 0), X)
            try:
                domain = sp.calculus.util.continuous_domain(function, X, sp.S.Reals)
            except (NotImplementedError, ValueError):
                domain = "无法自动判定"

            tangent_value = sp.simplify(function.subs(X, tangent_x))
            tangent_slope = sp.simplify(derivative.subs(X, tangent_x))
            tangent = sp.expand(tangent_slope * (X - tangent_x) + tangent_value)

            st.success("分析完成")
            result_cols = st.columns(3)
            result_cols[0].metric("实数零点数量", len([z for z in zeros if z.is_real is not False]))
            result_cols[1].metric("驻点数量", len(critical_points))
            result_cols[2].metric("切线斜率", f"{float(sp.N(tangent_slope)):.6g}")
            st.latex(f"f'(x)={sp.latex(derivative)}")
            st.latex(f"F(x)={sp.latex(antiderivative)}+C")
            st.latex(f"y_{{tangent}}={sp.latex(tangent)}")
            st.write("**连续定义域：**", domain)
            st.write("**零点：**", zeros or "未找到解析零点")
            st.write("**驻点：**", critical_points or "未找到解析驻点")

            values = np.linspace(start, end, 800)
            function_np = sp.lambdify(X, function, "numpy")
            derivative_np = sp.lambdify(X, derivative, "numpy")
            with np.errstate(all="ignore"):
                y_values = np.asarray(function_np(values), dtype=float)
                dy_values = np.asarray(derivative_np(values), dtype=float)
            if y_values.ndim == 0:
                y_values = np.full_like(values, float(y_values))
            if dy_values.ndim == 0:
                dy_values = np.full_like(values, float(dy_values))
            y_values[~np.isfinite(y_values)] = np.nan
            dy_values[~np.isfinite(dy_values)] = np.nan

            _style_plot(dark_mode)
            fig, ax = plt.subplots(figsize=(8, 4.5))
            ax.plot(values, y_values, label="f(x)", linewidth=2)
            ax.plot(values, dy_values, label="f'(x)", linestyle="--")
            tangent_np = sp.lambdify(X, tangent, "numpy")
            tangent_values = np.asarray(tangent_np(values), dtype=float)
            if tangent_values.ndim == 0:
                tangent_values = np.full_like(values, float(tangent_values))
            ax.plot(values, tangent_values, label="切线", alpha=0.75)
            ax.axhline(0, color="gray", linewidth=1)
            ax.axvline(0, color="gray", linewidth=1)
            ax.set_xlim(start, end)
            ax.grid(alpha=0.25)
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)
            add_calculation_history(
                "函数分析",
                expression_text,
                f"f'(x)={derivative}",
                input_key="function_analysis_expr",
            )
        except Exception as error:
            st.error(user_error_message(error, "函数分析失败，请检查表达式和绘图区间。"))


def _parse_number_list(text: str) -> np.ndarray:
    entries = [entry for entry in re.split(r"[\s,，;；]+", text.strip()) if entry]
    if not entries:
        raise InputParseError("请输入至少一个数值。")
    return np.array([parse_numeric(entry) for entry in entries], dtype=float)


def render_statistics_probability(dark_mode: bool) -> None:
    st.markdown("### 📊 统计与概率")
    _beginner_intro("先选择任务，再按示例输入数据。数据之间可以使用空格、英文逗号或中文逗号。")
    mode = st.selectbox("选择工具", ["描述统计", "线性回归", "排列组合", "二项分布", "正态分布"])

    if mode == "描述统计":
        text = st.text_area("输入数据（逗号、空格或换行分隔）", "1, 2, 2, 3, 4, 5, 8")
        if st.button("计算统计量"):
            try:
                data = _parse_number_list(text)
                unique, counts = np.unique(data, return_counts=True)
                modes = unique[counts == counts.max()]
                q1, median, q3 = np.percentile(data, [25, 50, 75])
                metrics = st.columns(4)
                metrics[0].metric("样本数", len(data))
                metrics[1].metric("均值", f"{np.mean(data):.6g}")
                metrics[2].metric("中位数", f"{median:.6g}")
                metrics[3].metric("标准差", f"{np.std(data, ddof=1) if len(data)>1 else 0:.6g}")
                st.write(f"众数：{', '.join(f'{v:g}' for v in modes)}")
                st.write(f"方差：{np.var(data, ddof=1) if len(data)>1 else 0:.6g}")
                st.write(f"四分位数：Q1={q1:.6g}，Q2={median:.6g}，Q3={q3:.6g}")
                _style_plot(dark_mode)
                fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
                axes[0].hist(data, bins="auto", alpha=0.8)
                axes[0].set_title("直方图")
                axes[1].boxplot(data, vert=True)
                axes[1].set_title("箱线图")
                st.pyplot(fig)
                plt.close(fig)
                add_calculation_history("描述统计", text, f"均值={np.mean(data):.6g}")
            except Exception as error:
                st.error(user_error_message(error, "数据解析失败。"))

    elif mode == "线性回归":
        c1, c2 = st.columns(2)
        x_text = c1.text_area("X 数据", "1,2,3,4,5")
        y_text = c2.text_area("Y 数据", "2.1,4.2,5.9,8.2,10.1")
        if st.button("拟合直线"):
            try:
                xs, ys = _parse_number_list(x_text), _parse_number_list(y_text)
                if len(xs) != len(ys) or len(xs) < 2:
                    raise InputParseError("X、Y 数据必须等长且至少有两个点。")
                slope, intercept = np.polyfit(xs, ys, 1)
                correlation = np.corrcoef(xs, ys)[0, 1]
                st.latex(f"y={slope:.6g}x+({intercept:.6g})")
                st.metric("决定系数 R²", f"{correlation**2:.6f}")
                _style_plot(dark_mode)
                fig, ax = plt.subplots(figsize=(7, 4))
                ax.scatter(xs, ys, label="数据")
                line_x = np.linspace(xs.min(), xs.max(), 100)
                ax.plot(line_x, slope * line_x + intercept, label="回归线")
                ax.grid(alpha=0.25)
                ax.legend()
                st.pyplot(fig)
                plt.close(fig)
            except Exception as error:
                st.error(user_error_message(error, "线性回归失败。"))

    elif mode == "排列组合":
        c1, c2 = st.columns(2)
        n_value = c1.number_input("n", min_value=0, value=10, step=1)
        r_value = c2.number_input("r", min_value=0, value=3, step=1)
        if r_value <= n_value:
            permutation = math.factorial(n_value) // math.factorial(n_value - r_value)
            combination = math.comb(n_value, r_value)
            st.latex(f"P({n_value},{r_value})={permutation}")
            st.latex(f"C({n_value},{r_value})={combination}")
        else:
            st.warning("r 不能大于 n。")

    elif mode == "二项分布":
        c1, c2, c3 = st.columns(3)
        trials = c1.number_input("试验次数 n", min_value=1, value=10, step=1)
        probability = c2.number_input("成功概率 p", min_value=0.0, max_value=1.0, value=0.5)
        successes = c3.number_input("成功次数 k", min_value=0, value=5, step=1)
        if successes <= trials:
            exact = math.comb(trials, successes) * probability**successes * (1-probability)**(trials-successes)
            st.latex(rf"P(X={successes})={exact:.8g}")
            st.write(f"期望：{trials*probability:.6g}，方差：{trials*probability*(1-probability):.6g}")
        else:
            st.warning("k 不能大于 n。")

    else:
        c1, c2, c3 = st.columns(3)
        mean = c1.number_input("均值 μ", value=0.0)
        std = c2.number_input("标准差 σ", min_value=1e-12, value=1.0)
        value = c3.number_input("上界 x", value=1.96)
        distribution = NormalDist(mean, std)
        probability = distribution.cdf(value)
        st.latex(rf"P(X\le {value:g})={probability:.8g}")
        st.write(f"右尾概率：{1-probability:.8g}")


def _parse_complex(text: str) -> complex:
    normalized = text.replace("j", "I").replace("i", "I")
    repaired = repair_math_input(normalized, {}).repaired
    expression = parse_math_expr(repaired, {}, numeric_only=True)
    return complex(expression.evalf())


def render_complex_calculator(dark_mode: bool) -> None:
    st.markdown("### 🌀 复数计算")
    _beginner_intro("复数可以写成 3+4i。这里能完成四则运算、求模、辐角、共轭和复数根。")
    c1, c2 = st.columns(2)
    a_text = c1.text_input("复数 A", "3+4i")
    b_text = c2.text_input("复数 B", "1-2i")
    operation = st.selectbox("运算", ["A+B", "A-B", "A×B", "A÷B", "分析 A", "A 的 n 次根"])
    root_n = st.number_input("根次数 n", min_value=1, value=3, step=1) if "n 次根" in operation else 1
    if st.button("计算复数"):
        try:
            a, b = _parse_complex(a_text), _parse_complex(b_text)
            if operation == "A+B":
                results = [a + b]
            elif operation == "A-B":
                results = [a - b]
            elif operation == "A×B":
                results = [a * b]
            elif operation == "A÷B":
                if b == 0:
                    raise InputParseError("除数 B 不能为 0。")
                results = [a / b]
            elif operation == "A 的 n 次根":
                radius, angle = abs(a), math.atan2(a.imag, a.real)
                results = [
                    radius ** (1 / root_n) * np.exp(1j * (angle + 2 * math.pi * k) / root_n)
                    for k in range(root_n)
                ]
            else:
                results = [a]

            for index, value in enumerate(results, start=1):
                label = f"结果 {index}" if len(results) > 1 else "结果"
                st.write(f"**{label}：** `{value.real:.8g} {value.imag:+.8g}i`")
                st.write(f"模：`{abs(value):.8g}`，辐角：`{math.degrees(math.atan2(value.imag, value.real)):.8g}°`")
                st.latex(
                    rf"{abs(value):.6g}\left(\cos({math.atan2(value.imag,value.real):.6g})"
                    rf"+i\sin({math.atan2(value.imag,value.real):.6g})\right)"
                )
            st.write(f"A 的共轭：`{a.conjugate().real:.8g} {a.conjugate().imag:+.8g}i`")
            _style_plot(dark_mode)
            fig, ax = plt.subplots(figsize=(5, 5))
            for index, value in enumerate(results):
                ax.arrow(0, 0, value.real, value.imag, head_width=max(abs(value)*0.04, 0.05), length_includes_head=True)
                ax.text(value.real, value.imag, f" z{index+1}")
            ax.axhline(0, color="gray")
            ax.axvline(0, color="gray")
            ax.set_aspect("equal", adjustable="datalim")
            ax.grid(alpha=0.25)
            ax.set_xlabel("实部")
            ax.set_ylabel("虚部")
            st.pyplot(fig)
            plt.close(fig)
            add_calculation_history("复数", f"{operation}: {a_text}, {b_text}", str(results[0]))
        except Exception as error:
            st.error(user_error_message(error, "复数格式错误，请使用 3+4i 这类格式。"))


def render_unit_converter() -> None:
    st.markdown("### 🔁 单位换算")
    _beginner_intro("选择物理量、原单位和目标单位，结果会自动按统一的国际单位换算。")
    category = st.selectbox("物理量", tuple(UNIT_CATEGORIES))
    units = unit_names(category)
    c1, c2, c3 = st.columns([2, 1, 1])
    value = c1.number_input("数值", value=1.0)
    from_unit = c2.selectbox("从", units, key="unit_from")
    to_unit = c3.selectbox("换算到", units, index=min(1, len(units)-1), key="unit_to")
    result = convert_value(value, category, from_unit, to_unit)
    st.metric("换算结果", f"{result:.12g} {to_unit}")
    st.latex(rf"{value:g}\ {from_unit}={result:.12g}\ {to_unit}")
    if st.button("保存本次换算"):
        add_calculation_history("单位换算", f"{value:g} {from_unit}", f"{result:.8g} {to_unit}")
        st.success("已加入最近计算。")


def render_physics_toolbox(dark_mode: bool) -> None:
    st.markdown("### 🧪 实用物理工具箱")
    _beginner_intro("先选物理分类和公式，再输入带单位的已知量。计算器会展示公式代入步骤。")
    category = st.selectbox("物理分类", categories(), key="physics_tool_category")
    tools = tools_for_category(category)
    tool = st.selectbox("计算工具", tools, format_func=lambda item: item.name, key="physics_tool")
    st.info(tool.description or f"公式：${tool.formula}$")
    st.latex(tool.formula)

    values_si: dict[str, float] = {}
    input_units: dict[str, str] = {}
    for input_spec in tool.inputs:
        value_si, selected_unit = render_quantity_input(
            input_spec.label,
            key=f"physics_{tool.name}_{input_spec.key}",
            default=input_spec.default,
            quantity=input_spec.quantity,
            default_unit=input_spec.unit,
        )
        values_si[input_spec.key] = value_si
        input_units[input_spec.key] = selected_unit

    if st.button("计算并显示步骤", key=f"calculate_{tool.name}"):
        try:
            results = calculate_physics(tool, values_si)
            st.success("计算完成")
            with st.expander("公式代入步骤", expanded=True):
                st.latex(tool.formula)
                values_text = ", ".join(
                    f"{item.label}={values_si[item.key]:.8g} {item.unit}"
                    for item in tool.inputs
                )
                st.write("统一换算为 SI 后：", values_text)

            result_strings = []
            for index, result in enumerate(results):
                if result.quantity:
                    output_units = unit_names(result.quantity)
                    default_index = output_units.index(result.unit) if result.unit in output_units else 0
                    output_unit = st.selectbox(
                        f"{result.label}输出单位",
                        output_units,
                        index=default_index,
                        key=f"output_{tool.name}_{index}",
                    )
                    display_value = format_quantity(result.value_si, result.quantity, output_unit)
                else:
                    output_unit = result.unit
                    display_value = result.value_si
                st.metric(result.label, f"{display_value:.10g} {output_unit}")
                result_strings.append(f"{result.label}={display_value:.6g}{output_unit}")

            if tool.plot_input and results:
                base_value = values_si[tool.plot_input]
                if base_value != 0:
                    x_values = np.linspace(base_value * 0.5, base_value * 1.5, 100)
                else:
                    x_values = np.linspace(0, 1, 100)
                y_values = []
                for x_value in x_values:
                    sample = dict(values_si)
                    sample[tool.plot_input] = x_value
                    try:
                        y_values.append(calculate_physics(tool, sample)[0].value_si)
                    except (PhysicsCalculationError, ValueError, ZeroDivisionError):
                        y_values.append(np.nan)
                _style_plot(dark_mode)
                fig, ax = plt.subplots(figsize=(7, 3.8))
                ax.plot(x_values, y_values)
                ax.scatter([base_value], [results[0].value_si], zorder=3)
                ax.set_xlabel(next(item.label for item in tool.inputs if item.key == tool.plot_input))
                ax.set_ylabel(results[0].label)
                ax.grid(alpha=0.25)
                st.pyplot(fig)
                plt.close(fig)

            add_calculation_history(
                f"物理-{tool.name}",
                ", ".join(f"{key}={value:.5g}" for key, value in values_si.items()),
                "；".join(result_strings),
            )
        except (PhysicsCalculationError, InputParseError, ValueError, ZeroDivisionError) as error:
            st.error(str(error))


def render_beginner_toolkit() -> None:
    st.markdown("### 🧰 新手实用工具")
    _beginner_intro("这里集中放置生活计算和中学数学工具。选择任务后，只需填写当前出现的输入框。")
    tool = st.selectbox(
        "我想计算",
        (
            "分数化简与通分",
            "比例与百分比",
            "二次方程",
            "平面与立体几何",
            "科学计数法",
            "常数查询",
            "日期时间差",
        ),
        key="beginner_tool_choice",
    )

    if tool == "分数化简与通分":
        operation = st.radio("选择操作", ("化简一个分数", "多个分数通分"), horizontal=True)
        if operation == "化简一个分数":
            text = st.text_input("分数", "18/24", help="可以使用中文或英文斜杠输入。")
            if st.button("化简分数", key="simplify_fraction"):
                try:
                    result = parse_fraction(text)
                    st.success(f"最简分数：{result.numerator}/{result.denominator}")
                    st.latex(
                        rf"{text}=\frac{{{result.numerator}}}{{{result.denominator}}}"
                    )
                    add_calculation_history("分数化简", text, str(result))
                except InputParseError as error:
                    st.error(str(error))
        else:
            text = st.text_input("输入多个分数", "1/2，2/3，5/6")
            if st.button("开始通分", key="common_denominator"):
                try:
                    fractions, denominator, numerators = common_denominator(text)
                    converted = [
                        f"{numerator}/{denominator}" for numerator in numerators
                    ]
                    st.success("通分结果：" + "，".join(converted))
                    st.write("原分数：", "，".join(str(item) for item in fractions))
                    add_calculation_history("分数通分", text, "，".join(converted))
                except InputParseError as error:
                    st.error(str(error))

    elif tool == "比例与百分比":
        operation = st.radio(
            "选择问题",
            ("求一个数的百分比", "计算增长或下降百分比"),
            horizontal=True,
        )
        first, second = st.columns(2)
        if operation == "求一个数的百分比":
            base = first.number_input("原数值", value=200.0)
            percent = second.number_input("百分比 (%)", value=15.0)
            result = percentage_value(base, percent)
            st.metric("结果", f"{result:.10g}")
            st.caption(f"{base:g} × {percent:g}% = {result:g}")
        else:
            original = first.number_input("原数值", value=80.0)
            current = second.number_input("新数值", value=100.0)
            try:
                change = percentage_change(original, current)
                direction = "增长" if change >= 0 else "下降"
                st.metric(f"{direction}百分比", f"{abs(change):.6g}%")
            except InputParseError as error:
                st.error(str(error))

    elif tool == "二次方程":
        _beginner_intro("对应方程 ax²+bx+c=0。先计算判别式 Δ=b²-4ac，再代入求根公式。")
        col_a, col_b, col_c = st.columns(3)
        a = col_a.number_input("a", value=1.0)
        b = col_b.number_input("b", value=-5.0)
        c = col_c.number_input("c", value=6.0)
        if st.button("求解二次方程", key="solve_quadratic"):
            try:
                discriminant, roots = solve_quadratic(a, b, c)
                st.latex(rf"{a:g}x^2+({b:g})x+({c:g})=0")
                st.latex(rf"\Delta=b^2-4ac={sp.latex(discriminant)}")
                st.latex(
                    rf"x=\frac{{-b\pm\sqrt{{\Delta}}}}{{2a}}"
                    rf"\Rightarrow x_1={sp.latex(roots[0])},\ x_2={sp.latex(roots[1])}"
                )
                add_calculation_history(
                    "二次方程",
                    f"{a}x²+{b}x+{c}=0",
                    str(roots),
                )
            except InputParseError as error:
                st.error(str(error))

    elif tool == "平面与立体几何":
        shape = st.selectbox(
            "选择图形",
            ("矩形面积", "三角形面积", "圆面积", "长方体体积", "圆柱体积", "球体积"),
        )
        values: dict[str, float] = {}
        if shape in {"矩形面积", "长方体体积"}:
            values["length"] = st.number_input("长度 (m)", min_value=0.0, value=5.0)
            values["width"] = st.number_input("宽度 (m)", min_value=0.0, value=3.0)
        if shape == "三角形面积":
            values["base"] = st.number_input("底边 (m)", min_value=0.0, value=5.0)
        if shape in {"三角形面积", "长方体体积", "圆柱体积"}:
            values["height"] = st.number_input("高度 (m)", min_value=0.0, value=2.0)
        if shape in {"圆面积", "圆柱体积", "球体积"}:
            values["radius"] = st.number_input("半径 (m)", min_value=0.0, value=2.0)
        label, result, unit = geometry_value(shape, values)
        st.metric(label, f"{result:.10g} {unit}")

    elif tool == "科学计数法":
        text = st.text_input("输入数值", "0.0000123")
        if st.button("转换科学计数法", key="scientific_notation"):
            try:
                coefficient, exponent, notation = scientific_notation(text)
                st.latex(rf"{coefficient:.10g}\times10^{{{exponent}}}")
                st.code(notation)
            except InputParseError as error:
                st.error(str(error))

    elif tool == "常数查询":
        name = st.selectbox("选择常数", tuple(MATH_CONSTANTS))
        value, description = MATH_CONSTANTS[name]
        st.metric(name, f"{sp.N(value, 12)}")
        st.info(description)
        st.latex(sp.latex(value))

    else:
        today = date.today()
        first, second = st.columns(2)
        start = first.date_input("开始日期", value=today, key="date_start")
        end = second.date_input("结束日期", value=today, key="date_end")
        days, whole_weeks = date_difference(start, end)
        st.metric("相差天数", f"{abs(days)} 天")
        st.caption(f"约为 {whole_weeks} 个完整星期；方向：{'之后' if days >= 0 else '之前'}。")
