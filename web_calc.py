import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="全能微积分计算器", page_icon="🧮", layout="centered")

st.title("🧮 手机全能计算器 Ultra Max")
st.markdown("微积分 | 解方程 | 级数 | 多重积分 | 线性代数 | 程序员")

dark_mode = st.toggle("🌙 开启暗黑图表模式")

if "math_expr" not in st.session_state:
    st.session_state.math_expr = "x**2 + 2*x"

def add_to_expr(text): st.session_state.math_expr += text
def clear_expr(): st.session_state.math_expr = ""

x, y, z, n, i, k = sp.symbols('x y z n i k')

# 🌟 震撼升级：六大顶级标签页！
tab_math, tab_eq, tab_sum, tab_multi, tab_linalg, tab_prog = st.tabs(
    ["📚 微积分", "🔍 解方程", "➕ 级数", "🌀 多重积分", "🧮 线性代数", "💻 程序员"]
)

# ------------------------------------------
# 第一页：微积分
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
    lower_limit_str = col_a.text_input("积分下限 a:", value="0")
    upper_limit_str = col_b.text_input("积分上限 b:", value="2")

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
        except: st.error("公式格式有误！")

    if col2.button("📈 求导数"):
        try:
            func = sp.sympify(expr_str)
            result = sp.diff(func, x)
            st.success("求导成功！")
            st.latex(f"\\frac{{d}}{{dx}}({sp.latex(func)}) = {sp.latex(result)}")
            plot_graph(result)
        except: st.error("求导失败！")

    if col3.button("📉 不定积分"):
        try:
            func = sp.sympify(expr_str)
            result = sp.integrate(func, x)
            st.success("不定积分成功！")
            st.latex(f"\\int ({sp.latex(func)}) dx = {sp.latex(result)}")
            plot_graph(result)
        except: st.error("不定积分失败！")

    if col4.button("📊 定积分"):
        try:
            func = sp.sympify(expr_str)
            a, b = sp.sympify(lower_limit_str), sp.sympify(upper_limit_str)
            result = sp.integrate(func, (x, a, b))
            st.success("定积分计算成功！")
            st.latex(f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} ({sp.latex(func)}) dx = {sp.latex(result)}")
            st.info(f"**近似数值:** `{result.evalf():.4f}`")
            plot_graph(func, float(a.evalf()), float(b.evalf()))
        except: st.error("计算失败！")

# ------------------------------------------
# 第二页：解方程
# ------------------------------------------
with tab_eq:
    st.markdown("### 🔍 智能方程求解器")
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
            if not solution: st.warning("⚠️ 无解或格式有误。")
            else:
                st.success("🎉 求解成功！")
                for idx, sol in enumerate(solution):
                    st.markdown(f"**可能解 {idx + 1}:**")
                    sol_latex = ", \\quad ".join([f"{sp.latex(var)} = {sp.latex(val)}" for var, val in sol.items()])
                    st.latex(sol_latex)
        except: st.error("解析失败！")

# ------------------------------------------
# 第三页：级数求和
# ------------------------------------------
with tab_sum:
    st.markdown("### ➕ 西格玛 (Σ) 求和神器")
    sum_expr_str = st.text_input("求和通项公式 (如: n**2):", value="n")
    col_s1, col_s2 = st.columns(2)
    sum_lower_str = col_s1.text_input("求和下限:", value="1")
    sum_upper_str = col_s2.text_input("求和上限 (如 oo):", value="100")
    if st.button("🧮 计算级数求和"):
        try:
            func_sum = sp.sympify(sum_expr_str)
            free_vars = func_sum.free_symbols
            var = n if n in free_vars else (i if i in free_vars else (k if k in free_vars else x))
            if not func_sum.free_symbols: var = n 
            lower, upper = sp.sympify(sum_lower_str), sp.sympify(sum_upper_str)
            sum_obj = sp.Sum(func_sum, (var, lower, upper))
            result = sum_obj.doit()
            st.success("🎉 求和计算成功！")
            st.latex(f"{sp.latex(sum_obj)} = {sp.latex(result)}")
            if result.is_number and not result.has(sp.oo):
                st.info(f"**近似数值:** `{result.evalf():.6f}`")
        except: st.error("计算失败！")

# ------------------------------------------
# 第四页：多重积分 (带3D)
# ------------------------------------------
with tab_multi:
    st.markdown("### 🌀 空间多重积分求解")
    int_type = st.radio("请选择积分维度:", ["∬ 二重积分", "∭ 三重积分"], horizontal=True)
    is_triple = "三重" in int_type
    multi_expr = st.text_input("被积函数 f(x,y,z):", value="x * y * z" if is_triple else "sin(x) * cos(y)")
    
    st.markdown("**最外层积分 (dx):**")
    c_x1, c_x2 = st.columns(2)
    xl_str, xu_str = c_x1.text_input("x 下限:", value="-2"), c_x2.text_input("x 上限:", value="2")
    
    st.markdown("**中层/内层积分 (dy):**")
    c_y1, c_y2 = st.columns(2)
    yl_str, yu_str = c_y1.text_input("y 下限:", value="-2"), c_y2.text_input("y 上限:", value="2")
    
    if is_triple:
        st.markdown("**最内层积分 (dz):**")
        c_z1, c_z2 = st.columns(2)
        zl_str, zu_str = c_z1.text_input("z 下限:", value="0"), c_z2.text_input("z 上限:", value="x + y")

    def plot_3d_integral(func_expr, xl_val, xu_val, yl_func, yu_func):
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        if dark_mode:
            plt.style.use('dark_background')
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))
            cmap_hl = 'cool'
        else:
            plt.style.use('default')
            cmap_hl = 'plasma'

        try:
            x_n = np.linspace(float(xl_val.evalf()), float(xu_val.evalf()), 40)
            f_yl, f_yu = sp.lambdify(x, yl_func, 'numpy'), sp.lambdify(x, yu_func, 'numpy')
            y_min_arr, y_max_arr = f_yl(x_n), f_yu(x_n)
            if isinstance(y_min_arr, (int, float)): y_min_arr = np.full_like(x_n, y_min_arr)
            if isinstance(y_max_arr, (int, float)): y_max_arr = np.full_like(x_n, y_max_arr)
            y_n = np.linspace(np.min(y_min_arr), np.max(y_max_arr), 40)
            X, Y = np.meshgrid(x_n, y_n)
            f_np = sp.lambdify((x, y), func_expr, 'numpy')
            Z = f_np(X, Y)
            if isinstance(Z, (int, float)): Z = np.full_like(X, Z)
            ax.plot_surface(X, Y, Z, alpha=0.8, cmap=cmap_hl, edgecolor='none')
            st.pyplot(fig)
        except: st.warning("⚠️ 3D 渲染跳过 (边界过于复杂)")

    if st.button("🌀 发动多重积分魔法"):
        try:
            f, xl, xu, yl, yu = sp.sympify(multi_expr), sp.sympify(xl_str), sp.sympify(xu_str), sp.sympify(yl_str), sp.sympify(yu_str)
            if is_triple:
                zl, zu = sp.sympify(zl_str), sp.sympify(zu_str)
                result = sp.integrate(f, (z, zl, zu), (y, yl, yu), (x, xl, xu))
                st.success("🎉 三重积分计算成功！")
                st.latex(f"\\iiint ({sp.latex(f)}) \\, dz \\, dy \\, dx = {sp.latex(result)}")
            else:
                result = sp.integrate(f, (y, yl, yu), (x, xl, xu))
                st.success("🎉 二重积分计算成功！")
                st.latex(f"\\iint ({sp.latex(f)}) \\, dy \\, dx = {sp.latex(result)}")
                plot_3d_integral(f, xl, xu, yl, yu)
            if result.is_number and not result.has(sp.oo): st.info(f"**近似数值:** `{result.evalf():.6f}`")
        except: st.error("计算失败！")

# ------------------------------------------
# 第五页：全新！🧮 线性代数与矩阵
# ------------------------------------------
with tab_linalg:
    st.markdown("### 🧮 智能矩阵运算中心")
    st.info("💡 **输入规则：** 同一行的数字用**空格或逗号**隔开，按 **回车键 (Enter)** 换行输入下一行。支持输入分数或未知数 $x$！")
    
    col_m1, col_m2 = st.columns(2)
    mat_A_str = col_m1.text_area("输入矩阵 A:", value="1 2\n3 4", height=120)
    mat_B_str = col_m2.text_area("输入矩阵 B (可选):", value="5 6\n7 8", height=120)

    def parse_matrix(matrix_string):
        if not matrix_string.strip(): return None
        rows = matrix_string.strip().split('\n')
        matrix_data = []
        for row in rows:
            elements = row.replace(',', ' ').split()
            if elements:
                matrix_data.append([sp.sympify(e) for e in elements])
        return sp.Matrix(matrix_data)

    st.markdown("**选择矩阵运算：**")
    btn1, btn2, btn3, btn4, btn5 = st.columns(5)
    
    if btn1.button("A + B (求和)"):
        try:
            A, B = parse_matrix(mat_A_str), parse_matrix(mat_B_str)
            result = A + B
            st.success("✅ 矩阵加法计算成功！")
            st.latex(f"{sp.latex(A)} + {sp.latex(B)} = {sp.latex(result)}")
        except Exception: st.error("❌ 计算失败，请确保 A 和 B 的行数列数完全一致！")

    if btn2.button("A × B (相乘)"):
        try:
            A, B = parse_matrix(mat_A_str), parse_matrix(mat_B_str)
            result = A * B
            st.success("✅ 矩阵乘法计算成功！")
            st.latex(f"{sp.latex(A)} \\times {sp.latex(B)} = {sp.latex(result)}")
        except Exception: st.error("❌ 计算失败，请确保 A 的列数等于 B 的行数！")

    if btn3.button("| A | (行列式)"):
        try:
            A = parse_matrix(mat_A_str)
            result = A.det()
            st.success("✅ 行列式计算成功！")
            st.latex(f"\\det({sp.latex(A)}) = {sp.latex(result)}")
        except Exception: st.error("❌ 计算失败，求行列式必须是方阵（行数=列数）！")

    if btn4.button("A⁻¹ (求逆)"):
        try:
            A = parse_matrix(mat_A_str)
            result = A.inv()
            st.success("✅ 逆矩阵计算成功！")
            st.latex(f"{sp.latex(A)}^{{-1}} = {sp.latex(result)}")
        except Exception: st.error("❌ 计算失败，该矩阵不可逆（行列式为0）或不是方阵！")
        
    if btn5.button("Aᵀ (转置)"):
        try:
            A = parse_matrix(mat_A_str)
            result = A.T
            st.success("✅ 矩阵转置成功！")
            st.latex(f"{sp.latex(A)}^T = {sp.latex(result)}")
        except Exception: st.error("❌ 解析失败！")

# ------------------------------------------
# 第六页：程序员(进制)
# ------------------------------------------
with tab_prog:
    st.markdown("### 🔢 实时进制转换")
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
        except Exception: pass
