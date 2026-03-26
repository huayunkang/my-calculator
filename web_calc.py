import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="全能微积分计算器", page_icon="🧮", layout="centered")

st.title("🧮 手机全能计算器 Pro Max")
st.markdown("微积分神器 & 程序员工具箱")

dark_mode = st.toggle("🌙 开启暗黑图表模式")

# ==========================================
# 🌟 网页记忆魔法：让按钮能自动输入文字！
# ==========================================
# 1. 如果网页刚打开，先在记忆里存一个初始公式
if "math_expr" not in st.session_state:
    st.session_state.math_expr = "x**2 + 2*x"

# 2. 定义打字机函数：点按钮就把字加进去
def add_to_expr(text):
    st.session_state.math_expr += text

# 3. 定义清空函数
def clear_expr():
    st.session_state.math_expr = ""

# ==========================================

tab_math, tab_prog = st.tabs(["📚 微积分运算", "💻 程序员(进制转换)"])
x = sp.Symbol('x')

# ------------------------------------------
# 第一页：微积分专属页面
# ------------------------------------------
with tab_math:
    
    # 🌟 新增：超级酷炫的折叠科学键盘！
    with st.expander("🎹 点击展开科学计算快捷键盘"):
        b1, b2, b3, b4 = st.columns(4)
        b1.button("sin(", on_click=add_to_expr, args=("sin(",))
        b2.button("cos(", on_click=add_to_expr, args=("cos(",))
        b3.button("tan(", on_click=add_to_expr, args=("tan(",))
        b4.button("pi", on_click=add_to_expr, args=("pi",))

        b5, b6, b7, b8 = st.columns(4)
        b5.button("log(", on_click=add_to_expr, args=("log(",))
        b6.button("exp(", on_click=add_to_expr, args=("exp(",))
        b7.button("sqrt(", on_click=add_to_expr, args=("sqrt(",))
        b8.button("E", on_click=add_to_expr, args=("E",))

        b9, b10, b11, b12 = st.columns(4)
        b9.button("x", on_click=add_to_expr, args=("x",))
        b10.button("** (乘方)", on_click=add_to_expr, args=("**",))
        b11.button(")", on_click=add_to_expr, args=(")",))
        b12.button("🗑️ 清空", on_click=clear_expr)

    # 🌟 输入框现在直接绑定了名为 "math_expr" 的记忆！
    expr_str = st.text_input("请输入算式:", key="math_expr")

    st.markdown("**(可选) 定积分上下限设置：**")
    col_a, col_b = st.columns(2)
    lower_limit_str = col_a.text_input("积分下限 a (可填 pi 等):", value="0")
    upper_limit_str = col_b.text_input("积分上限 b (可填 pi 等):", value="2")

    col1, col2, col3, col4 = st.columns(4)

    def plot_graph(func, fill_a=None, fill_b=None):
        if dark_mode:
            plt.style.use('dark_background')
            line_color = '#00ffcc' 
        else:
            plt.style.use('default')
            line_color = '#1f77b4' 
            
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)

        f_np = sp.lambdify(x, func, 'numpy')
        
        if fill_a is not None and fill_b is not None:
            plot_min, plot_max = min(fill_a, fill_b) - 2, max(fill_a, fill_b) + 2
        else:
            plot_min, plot_max = -10, 10
            
        x_vals = np.linspace(plot_min, plot_max, 400)
        y_vals = f_np(x_vals)
        if isinstance(y_vals, (int, float)): y_vals = np.full_like(x_vals, y_vals)
            
        ax.plot(x_vals, y_vals, color=line_color, linewidth=2)
        
        if fill_a is not None and fill_b is not None:
            fill_x = np.linspace(fill_a, fill_b, 100)
            fill_y = f_np(fill_x)
            if isinstance(fill_y, (int, float)): fill_y = np.full_like(fill_x, fill_y)
            ax.fill_between(fill_x, fill_y, alpha=0.4, color='orange', label="定积分面积")
            ax.legend()

        ax.axhline(0, color='gray', linewidth=1)
        ax.axvline(0, color='gray', linewidth=1)
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig) 

    if col1.button("🟰 计算"):
        try:
            result = sp.sympify(expr_str)
            st.success("计算成功！")
            st.latex(f"= {sp.latex(result)}") 
        except:
            st.error("公式格式有误！")

    if col2.button("📈 求导数"):
        try:
            func = sp.sympify(expr_str)
            result = sp.diff(func, x)
            st.success("求导成功！")
            st.latex(f"\\frac{{d}}{{dx}}({sp.latex(func)}) = {sp.latex(result)}")
            plot_graph(result)
        except:
            st.error("求导失败！")

    if col3.button("📉 不定积分"):
        try:
            func = sp.sympify(expr_str)
            result = sp.integrate(func, x)
            st.success("不定积分成功！")
            st.latex(f"\\int ({sp.latex(func)}) dx = {sp.latex(result)}")
            plot_graph(result)
        except:
            st.error("不定积分失败！")

    if col4.button("📊 定积分"):
        try:
            func = sp.sympify(expr_str)
            a = sp.sympify(lower_limit_str)
            b = sp.sympify(upper_limit_str)
            result = sp.integrate(func, (x, a, b))
            st.success("定积分计算成功！")
            st.latex(f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} ({sp.latex(func)}) dx = {sp.latex(result)}")
            st.info(f"**近似数值:** `{result.evalf():.4f}`")
            plot_graph(func, float(a.evalf()), float(b.evalf()))
        except Exception:
            st.error("计算失败，请检查公式或上下限格式！")

# ------------------------------------------
# 第二页：程序员(进制转换)页面
# ------------------------------------------
with tab_prog:
    st.markdown("### 🔢 实时进制转换引擎")
    st.info("💡 提示：支持直接输入数学算式（如 `255` 或 `10 + 5 * 2`），程序会自动计算并转换！")
    
    prog_expr = st.text_input("请输入整数或算式:", value="255", key="prog_input")
    
    if prog_expr:
        try:
            val_expr = sp.sympify(prog_expr)
            if val_expr.is_integer:
                val = int(val_expr)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(label="十进制 (DEC)", value=str(val))
                c2.metric(label="二进制 (BIN)", value=bin(val))
                c3.metric(label="八进制 (OCT)", value=oct(val))
                c4.metric(label="十六进制 (HEX)", value=hex(val))
            else:
                st.warning("⚠️ 进制转换目前仅支持整数计算哦！")
        except Exception:
            st.error("❌ 无法识别的输入，请检查格式。")
