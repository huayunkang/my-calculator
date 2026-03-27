import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="全能微积分计算器", page_icon="🧮", layout="centered")

st.title("🧮 手机全能计算器 Pro Max")
st.markdown("微积分 | 解方程 | 级数求和 | 程序员")

dark_mode = st.toggle("🌙 开启暗黑图表模式")

if "math_expr" not in st.session_state:
    st.session_state.math_expr = "x**2 + 2*x"

def add_to_expr(text):
    st.session_state.math_expr += text

def clear_expr():
    st.session_state.math_expr = ""

# ==========================================
# 🌟 核心升级：增加 n, i, k 作为求和常用的专属变量！
# ==========================================
x, y, z, n, i, k = sp.symbols('x y z n i k')

# 🌟 新增了第四个标签页！
tab_math, tab_eq, tab_sum, tab_prog = st.tabs(["📚 微积分运算", "🔍 解多元方程", "➕ 级数与求和", "💻 程序员(进制)"])

# ------------------------------------------
# 第一页：微积分专属页面
# ------------------------------------------
with tab_math:
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
        b10.button("**", on_click=add_to_expr, args=("**",))
        b11.button(")", on_click=add_to_expr, args=(")",))
        b12.button("🗑️ 清空", on_click=clear_expr)

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
# 第二页：智能解方程页面
# ------------------------------------------
with tab_eq:
    st.markdown("### 🔍 智能方程求解器")
    st.info("💡 提示：支持一元、二元甚至三元方程！如果有多个方程，请用 **英文逗号 (,)** 隔开。")
    
    eq_str = st.text_input("请输入方程组:", value="x + y + z = 6, x - y = 1, 2*x + y - z = 1")
    
    if st.button("🚀 一键求解方程"):
        try:
            eq_list = []
            for eq in eq_str.split(','):
                eq = eq.strip()
                if not eq: continue
                if '=' in eq:
                    left, right = eq.split('=')
                    eq_list.append(sp.Eq(sp.sympify(left), sp.sympify(right)))
                else:
                    eq_list.append(sp.sympify(eq))
            
            solution = sp.solve(eq_list, dict=True)
            
            if not solution:
                st.warning("⚠️ 该方程无解，或者输入格式有误。")
            else:
                st.success("🎉 求解成功！")
                for idx, sol in enumerate(solution):
                    st.markdown(f"**可能解 {idx + 1}:**")
                    sol_latex = ", \\quad ".join([f"{sp.latex(var)} = {sp.latex(val)}" for var, val in sol.items()])
                    st.latex(sol_latex)
        except Exception:
            st.error("解析失败，请确保格式正确 (比如 2x 要写成 2*x)。")

# ------------------------------------------
# 第三页：全新！级数与求和公式
# ------------------------------------------
with tab_sum:
    st.markdown("### ➕ 西格玛 (Σ) 求和神器")
    st.info("💡 **高能提示：** 求和变量默认使用 `n` 或 `i`。如果想算**加到无穷大**，上限请填入两个小写字母 `oo` ！！")
    
    sum_expr_str = st.text_input("请输入求和通项公式 (例如: n**2 或 1/2**n):", value="n")
    
    col_s1, col_s2 = st.columns(2)
    sum_lower_str = col_s1.text_input("求和下限 (如: 1):", value="1")
    sum_upper_str = col_s2.text_input("求和上限 (如: 100 或 oo):", value="100")
    
    if st.button("🧮 计算级数求和"):
        try:
            func_sum = sp.sympify(sum_expr_str)
            
            # 智能探测用户用的是哪个字母(n, i, k, 或者 x)
            free_vars = func_sum.free_symbols
            if n in free_vars: var = n
            elif i in free_vars: var = i
            elif k in free_vars: var = k
            elif x in free_vars: var = x
            else: var = n # 如果输入的是纯数字，默认用 n
            
            lower = sp.sympify(sum_lower_str)
            upper = sp.sympify(sum_upper_str)
            
            # 召唤 SymPy 的求和魔法！
            sum_obj = sp.Sum(func_sum, (var, lower, upper))
            result = sum_obj.doit()
            
            st.success("🎉 求和计算成功！")
            # 完美渲染带上下限的大 Σ 符号公式
            st.latex(f"{sp.latex(sum_obj)} = {sp.latex(result)}")
            
            # 如果结果是具体的数字，且不是无穷大，给个小数提示
            if result.is_number and not result.has(sp.oo):
                st.info(f"**近似数值:** `{result.evalf():.6f}`")
                
        except Exception as e:
            st.error("计算失败，请检查公式中是否正确使用了字母 n 或 i！")

# ------------------------------------------
# 第四页：程序员(进制转换)页面
# ------------------------------------------
with tab_prog:
    st.markdown("### 🔢 实时进制转换引擎")
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
            pass
