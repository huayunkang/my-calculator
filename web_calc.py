import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# 1. 设置网页的标题和手机浏览器标签页上的小图标
st.set_page_config(page_title="全能微积分计算器", page_icon="🧮")

# 2. 网页的大标题和描述
st.title("🧮 手机全能计算器")
st.markdown("输入你的数学公式，点击按钮一键计算、求导或积分！")

x = sp.Symbol('x')

# 3. 手机屏幕上的输入框 (天生带有漂亮 UI)
expr_str = st.text_input("请输入算式 (例如: sin(x) + x**2):", value="x**2 + 2*x")

# 4. 把按钮横向排列，分成三列（就像手机 App 底部的菜单）
col1, col2, col3 = st.columns(3)

# --- 提取一个画图的通用函数 ---
def plot_graph(func):
    fig, ax = plt.subplots(figsize=(6, 4))
    f_np = sp.lambdify(x, func, 'numpy')
    x_vals = np.linspace(-10, 10, 400)
    y_vals = f_np(x_vals)
    if isinstance(y_vals, (int, float)):
        y_vals = np.full_like(x_vals, y_vals)
        
    ax.plot(x_vals, y_vals, color='#1f77b4', linewidth=2)
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # 【魔法命令】直接把图表贴到网页上！
    st.pyplot(fig) 

# --- 按钮逻辑 ---
if col1.button("🟰 普通计算"):
    try:
        result = sp.sympify(expr_str)
        st.success("计算成功！")
        # 【魔法命令】在网页上完美渲染极其漂亮的 LaTeX 印刷体数学公式
        st.latex(f"= {sp.latex(result)}") 
    except:
        st.error("公式格式有误，请检查输入！")

if col2.button("📈 求导数"):
    try:
        func = sp.sympify(expr_str)
        result = sp.diff(func, x)
        st.success("求导成功！")
        st.latex(f"\\frac{{d}}{{dx}}({sp.latex(func)}) = {sp.latex(result)}")
        plot_graph(result)
    except:
        st.error("求导失败，请确保输入了合法的带 x 函数！")

if col3.button("📉 求积分"):
    try:
        func = sp.sympify(expr_str)
        result = sp.integrate(func, x)
        st.success("积分成功！")
        st.latex(f"\\int ({sp.latex(func)}) dx = {sp.latex(result)}")
        plot_graph(result)
    except:
        st.error("积分失败，请确保输入了合法的带 x 函数！")
