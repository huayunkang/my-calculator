import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="全能微积分计算器", page_icon="🧮", layout="centered")

st.title("🧮 手机全能计算器 Pro Max")
st.markdown("微积分神器 | 智能解方程 | 程序员工具箱")

dark_mode = st.toggle("🌙 开启暗黑图表模式")

# 1. 如果网页刚打开，先在记忆里存一个初始公式
if "math_expr" not in st.session_state:
    st.session_state.math_expr = "x**2 + 2*x"

def add_to_expr(text):
    st.session_state.math_expr += text

def clear_expr():
    st.session_state.math_expr = ""

# ==========================================
# 🌟 核心升级：一次性初始化 x, y, z 三个符号！
# ==========================================
x, y, z = sp.symbols('x y z')

# 新增了第三个标签页！
tab_math, tab_eq, tab_prog = st.tabs(["📚 微积分运算", "🔍 解多元方程", "💻 程序员(进制)"])

# ------------------------------------------
# 第一页：微积分专属页面 (保持不变)
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
# 第二页：全新！智能解方程页面
# ------------------------------------------
with tab_eq:
    st.markdown("### 🔍 智能方程求解器")
    st.info("💡 提示：支持一元、二元甚至三元方程！如果有多个方程，请用 **英文逗号 (,)** 隔开。可以直接输入 `=` 号！")
    
    eq_str = st.text_input("请输入方程组:", value="x + y + z = 6, x - y = 1, 2*x + y - z = 1")
    
    if st.button("🚀 一键求解方程"):
        try:
            # 1. 智能解析输入的字符串
            eq_list = []
            # 按照逗号拆分多个方程
            for eq in eq_str.split(','):
                eq = eq.strip()
                if not eq: continue
                
                # 如果用户输入了 '='，比如 x + y = 5，自动帮它转换成数学等式
                if '=' in eq:
                    left, right = eq.split('=')
                    eq_list.append(sp.Eq(sp.sympify(left), sp.sympify(right)))
                else:
                    # 如果没写等号，默认这个式子等于 0
                    eq_list.append(sp.sympify(eq))
            
            # 2. 召唤 SymPy 的求解魔法
            solution = sp.solve(eq_list, dict=True)
            
            # 3. 完美展示结果
            if not solution:
                st.warning("⚠️ 该方程组无解，或者输入格式有误。")
            else:
                st.success("🎉 求解成功！")
                for idx, sol in enumerate(solution):
                    st.markdown(f"**可能解 {idx + 1}:**")
                    # 将字典结果拼接成漂亮的 LaTeX 格式展示
                    sol_latex = ", \\quad ".join([f"{sp.latex(var)} = {sp.latex(val)}" for var, val in sol.items()])
                    st.latex(sol_latex)
        except Exception as e:
            st.error("解析失败，请确保格式正确 (比如 2x 要写成 2*x)。")

# ------------------------------------------
# 第三页：程序员(进制转换)页面
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
            pass # 没输完时不显示报错
