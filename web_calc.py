import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="全能微积分计算器", page_icon="🧮")

st.title("🧮 手机全能计算器")
st.markdown("输入你的数学公式，一键计算、求导或求定/不定积分！")

x = sp.Symbol('x')

# --- 1. 基础公式输入 ---
expr_str = st.text_input("请输入算式 (例如: sin(x) + x**2):", value="x**2 + 2*x")

# --- 2. 新增：定积分的上下限输入框 (放在一行) ---
st.markdown("**(可选) 定积分上下限设置：**")
col_a, col_b = st.columns(2)
lower_limit_str = col_a.text_input("积分下限 a (可填 pi 等):", value="0")
upper_limit_str = col_b.text_input("积分上限 b (可填 pi 等):", value="2")

# --- 3. 按钮布局 ---
col1, col2, col3, col4 = st.columns(4)

def plot_graph(func, fill_a=None, fill_b=None):
    """通用的画图函数，如果传入了 a 和 b，就会给面积涂色！"""
    fig, ax = plt.subplots(figsize=(6, 4))
    f_np = sp.lambdify(x, func, 'numpy')
    
    # 智能决定画图的X轴范围
    if fill_a is not None and fill_b is not None:
        plot_min, plot_max = min(fill_a, fill_b) - 2, max(fill_a, fill_b) + 2
    else:
        plot_min, plot_max = -10, 10
        
    x_vals = np.linspace(plot_min, plot_max, 400)
    y_vals = f_np(x_vals)
    if isinstance(y_vals, (int, float)): y_vals = np.full_like(x_vals, y_vals)
        
    ax.plot(x_vals, y_vals, color='#1f77b4', linewidth=2)
    
    # --- 新增：涂色魔法 ---
    if fill_a is not None and fill_b is not None:
        fill_x = np.linspace(fill_a, fill_b, 100)
        fill_y = f_np(fill_x)
        if isinstance(fill_y, (int, float)): fill_y = np.full_like(fill_x, fill_y)
        # 用半透明的橙色涂满面积！
        ax.fill_between(fill_x, fill_y, alpha=0.4, color='orange', label="定积分面积")
        ax.legend()

    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig) 

# --- 按钮逻辑 ---
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

# --- 新增：定积分专属按钮 ---
if col4.button("📊 定积分"):
    try:
        func = sp.sympify(expr_str)
        a = sp.sympify(lower_limit_str)
        b = sp.sympify(upper_limit_str)
        
        # 1. 计算定积分 (带上下限)
        result = sp.integrate(func, (x, a, b))
        st.success("定积分计算成功！")
        
        # 2. 渲染带上下限的完美 LaTeX 公式
        st.latex(f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} ({sp.latex(func)}) dx = {sp.latex(result)}")
        
        # 如果结果里有 pi 或分数，额外显示一个小数近似值
        st.info(f"**近似数值:** `{result.evalf():.4f}`")
        
        # 3. 画图并涂色 (将 sympy 的常数转换为 float)
        plot_graph(func, float(a.evalf()), float(b.evalf()))
    except Exception as e:
        st.error("计算失败，请检查公式或上下限格式！")
