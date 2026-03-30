import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import streamlit.components.v1 as components  

st.set_page_config(page_title="Ultra Max 计算器 Quantum", page_icon="🧮", layout="centered")

# ==========================================
# 🧚‍♀️ 萌物召唤模块：全屏可拖拽的看板小猫
# ==========================================
def summon_mascot():
    mascot_code = """
    <script>
    const parentDoc = window.parent.document;
    if (!parentDoc.getElementById("cute-mascot")) {
        const mascot = parentDoc.createElement("div");
        mascot.id = "cute-mascot";
        mascot.style.position = "fixed";
        mascot.style.bottom = "30px";
        mascot.style.right = "30px";
        mascot.style.zIndex = "999999";
        mascot.style.cursor = "grab";
        mascot.style.userSelect = "none";
        
        // 键盘猫 GIF
        mascot.innerHTML = '<img src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="120px" style="pointer-events: none; border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 3px solid #FF4B2B;"/>';
        parentDoc.body.appendChild(mascot);

        let isDragging = false;
        let offsetX, offsetY;
        mascot.onmousedown = function(e) {
            isDragging = true;
            offsetX = e.clientX - mascot.getBoundingClientRect().left;
            offsetY = e.clientY - mascot.getBoundingClientRect().top;
            mascot.style.cursor = "grabbing";
        };
        parentDoc.onmousemove = function(e) {
            if (isDragging) {
                mascot.style.left = (e.clientX - offsetX) + "px";
                mascot.style.top = (e.clientY - offsetY) + "px";
                mascot.style.bottom = "auto";
                mascot.style.right = "auto";
            }
        };
        parentDoc.onmouseup = function() {
            isDragging = false;
            mascot.style.cursor = "grab";
        };
    }
    </script>
    """
    components.html(mascot_code, height=0, width=0)

summon_mascot()

# ==========================================
# 页面标题与统一开关
# ==========================================
st.markdown('<div class="title-text">🧮 Ultra Max 计算器 Quantum</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">超级微积分神器 • 风景赛博版</div>', unsafe_allow_html=True)

# 🌟 全局统一的暗黑模式开关
dark_mode = st.toggle("🌙 一键开启星空夜景模式 (全局生效)")

# ==========================================
# 🎨 核心视觉升级：动态 CSS 注入 (融合赛博朋克边界)
# ==========================================
day_bg_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?q=80&w=2070" 
night_bg_url = "https://images.unsplash.com/photo-1500417148159-68083bd7333a?q=80&w=2070" 

current_bg = night_bg_url if dark_mode else day_bg_url
mask_bg = "rgba(0, 0, 0, 0.65)" if dark_mode else "rgba(255, 255, 255, 0.3)"
card_bg = "rgba(25, 25, 25, 0.8)" if dark_mode else "rgba(255, 255, 255, 0.8)"
input_bg = "rgba(50, 50, 50, 0.9)" if dark_mode else "rgba(255, 255, 255, 0.9)"
text_color = "#ffffff" if dark_mode else "#31333F"

custom_style = f"""
<style>
    /* ----- 1. 唯美风景背景引擎 ----- */
    .stApp {{
        background-image: url("{current_bg}");
        background-size: cover; background-position: center; background-attachment: fixed;
        transition: background-image 0.5s ease-in-out;
    }}
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: {mask_bg}; backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
        z-index: -1; transition: background-color 0.5s ease-in-out;
    }}
    .block-container {{
        background-color: {card_bg}; padding: 40px !important; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3); backdrop-filter: blur(10px); color: {text_color};
        transition: all 0.5s ease-in-out;
    }}

    /* ----- 2. 基础文字与按钮排版 ----- */
    .title-text {{
        background: -webkit-linear-gradient(45deg, #FF416C, #FF4B2B, #7b2ff7, #2f9eff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 900; text-align: center; margin-bottom: 0px; padding-bottom: 10px;
        text-shadow: 0 2px 10px rgba(255,75,43,0.2);
    }}
    .subtitle-text {{
        text-align: center; color: #888; font-size: 16px; letter-spacing: 2px; margin-bottom: 30px;
    }}
    div.stButton > button {{
        border-radius: 12px; border: none; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
    }}
    div.stButton > button:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(118, 75, 162, 0.4); }}
    div.stTextInput > div > div > input, div.stTextArea > div > div > textarea {{
        border-radius: 10px; background-color: {input_bg}; color: {text_color}; transition: all 0.5s ease-in-out;
    }}
    p, span, label, div[data-testid="stMarkdownContainer"] {{ color: {text_color} !important; }}
    
    /* ----- 3. 🌟 修复与重塑：极简高级玻璃态导航栏 ----- */
    
    /* 🚨 抹除上个版本的灾难色块，所有标签恢复透明本色 */
    div[data-baseweb="tab-list"] > button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        transform: none !important;
        width: auto !important;
        opacity: 0.6 !important;
        transition: all 0.3s ease;
    }}
    
    /* ✨ 真正的赛博高级感：仅选中的标签底部亮起青色霓虹剑，文字发光 */
    div[data-baseweb="tab-list"] > button[aria-selected="true"] {{
        opacity: 1 !important;
        border-bottom: 3px solid #00FFFF !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8) !important;
    }}

    /* 🚀 彻底抹杀左右滑动的黑边/渐变边遮罩，让它变得像玻璃一样无感 */
    div[data-baseweb="tab-list"] > div > div {{
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        backdrop-filter: none !important;
    }}

    /* 微调左右滑动的小箭头（平时半透明，鼠标放上去变青色发光） */
    div[data-baseweb="tab-list"] svg {{
        fill: {text_color} !important;
        opacity: 0.5;
        transition: all 0.3s;
    }}
    div[data-baseweb="tab-list"] button[aria-hidden="true"]:hover svg {{
        fill: #00FFFF !important;
        filter: drop-shadow(0px 0px 5px #00FFFF) !important;
        opacity: 1;
    }}

    /* 导航栏底部加一条淡淡的透明分界线 */
    div[data-baseweb="tab-list"] {{
        border-bottom: 1px solid rgba(128, 128, 128, 0.2) !important;
    }}
</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

if "math_expr" not in st.session_state:
    st.session_state.math_expr = "x**2 - 5*x + 6"

def add_to_expr(text): st.session_state.math_expr += text
def clear_expr(): st.session_state.math_expr = ""

x, y, z, n, i, k, t = sp.symbols('x y z n i k t')

tab_math, tab_eq, tab_sum, tab_multi, tab_linalg, tab_prog, tab_vector, tab_surface, tab_line = st.tabs(
    ["📚 微积分", "🔍 解方程", "➕ 级数", "🌀 多重积分", "🧮 线性代数", "💻 程序员", "📐 向量", "🏺 旋转面", "〰️ 曲线积分"]
)

def plot_graph(func, fill_a=None, fill_b=None):
    if dark_mode:
        plt.style.use('dark_background')
        line_color = '#00ffcc' 
    else:
        plt.style.use('default')
        line_color = '#FF4B2B' 
        
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
        ax.fill_between(fill_x, fill_y, alpha=0.3, color='#7b2ff7', label="积分面积")
        ax.legend()

    ax.axhline(0, color='gray', linewidth=1)
    ax.axvline(0, color='gray', linewidth=1)
    ax.grid(True, linestyle='--', alpha=0.3)
    st.pyplot(fig) 

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

    if col1.button("🟰 普通计算"):
        try:
            expr = sp.sympify(expr_str)
            simplified = sp.simplify(expr)
            expanded = sp.expand(expr)
            st.success("计算成功！")
            with st.expander("👀 查看计算/化简过程", expanded=True):
                st.markdown("**1. 原始解析表达式:**")
                st.latex(sp.latex(expr))
                if expr != expanded and expanded != simplified:
                    st.markdown("**2. 展开多项式:**")
                    st.latex(sp.latex(expanded))
                if expr != simplified:
                    st.markdown("**3. 最简代数形式:**")
                    st.latex(sp.latex(simplified))
                st.markdown("**4. 最终答案:**")
                st.latex(f"= {sp.latex(simplified)}")
            if simplified.is_number and not simplified.has(sp.oo):
                st.info(f"**近似数值:** `{simplified.evalf():.6f}`")
        except: st.error("公式格式有误！")

    if col2.button("📈 求导数"):
        try:
            func = sp.sympify(expr_str)
            result = sp.diff(func, x)
            st.success("求导成功！")
            with st.expander("👀 查看求导详细过程", expanded=True):
                st.markdown("**1. 设定原函数:**")
                st.latex(f"f(x) = {sp.latex(func)}")
                st.markdown("**2. 应用求导算子:**")
                st.latex(f"\\frac{{d}}{{dx}} \\left[ {sp.latex(func)} \\right]")
                st.markdown("**3. 得出导函数:**")
                st.latex(f"f'(x) = {sp.latex(result)}")
            plot_graph(result)
        except: st.error("求导失败！")

    if col3.button("📉 不定积分"):
        try:
            func = sp.sympify(expr_str)
            result = sp.integrate(func, x)
            st.success("不定积分成功！")
            with st.expander("👀 查看积分详细过程", expanded=True):
                st.markdown("**1. 构建不定积分式:**")
                st.latex(f"\\int \\left( {sp.latex(func)} \\right) dx")
                st.markdown("**2. 求解反导数:**")
                st.latex(f"= {sp.latex(result)} + C")
            plot_graph(result)
        except: st.error("不定积分失败！")

    if col4.button("📊 定积分"):
        try:
            func = sp.sympify(expr_str)
            a, b = sp.sympify(lower_limit_str), sp.sympify(upper_limit_str)
            result = sp.integrate(func, (x, a, b))
            anti_deriv = sp.integrate(func, x) 
            st.success("定积分计算成功！")
            with st.expander("👀 查看牛顿-莱布尼茨公式推导", expanded=True):
                st.markdown("**1. 构建定积分:**")
                st.latex(f"\\int_{{{sp.latex(a)}}}^{{{sp.latex(b)}}} \\left( {sp.latex(func)} \\right) dx")
                st.markdown("**2. 求解原函数:**")
                st.latex(f"F(x) = {sp.latex(anti_deriv)}")
                st.markdown("**3. 代入上下限 $F(b) - F(a)$:**")
                st.latex(f"\\left[ {sp.latex(anti_deriv)} \\right]_{{{sp.latex(a)}}}^{{{sp.latex(b)}}}")
                st.markdown("**4. 得出确切值:**")
                st.latex(f"= {sp.latex(result)}")
            st.info(f"**近似数值:** `{result.evalf():.4f}`")
            plot_graph(func, float(a.evalf()), float(b.evalf()))
        except: st.error("计算失败！")

# ------------------------------------------
# 第二页：解方程
# ------------------------------------------
with tab_eq:
    st.markdown("### 🔍 智能方程求解器")
    eq_str = st.text_input("请输入方程 (用逗号隔开):", value="x**2 - 5*x + 6 = 0")
    if st.button("🚀 解方程并查看过程"):
        try:
            eq_list, standard_forms = [], []
            for eq in eq_str.split(','):
                eq = eq.strip()
                if not eq: continue
                if '=' in eq:
                    left, right = eq.split('=')
                    eq_list.append(sp.Eq(sp.sympify(left), sp.sympify(right)))
                    standard_forms.append(sp.sympify(left) - sp.sympify(right))
                else:
                    eq_list.append(sp.sympify(eq))
                    standard_forms.append(sp.sympify(eq))
                    
            solution = sp.solve(eq_list, dict=True)
            if not solution: st.warning("⚠️ 无解或格式有误。")
            else:
                st.success("🎉 求解成功！")
                with st.expander("👀 查看方程推导与变形过程", expanded=True):
                    st.markdown("**第一步：提取原始方程**")
                    for eq in eq_list:
                        st.latex(sp.latex(eq) if isinstance(eq, sp.Eq) else f"{sp.latex(eq)} = 0")
                    st.markdown("**第二步：化为标准形式 ($f(x)=0$)**")
                    for sf in standard_forms:
                        st.latex(f"{sp.latex(sf)} = 0")
                    if len(standard_forms) == 1 and len(standard_forms[0].free_symbols) == 1:
                        try:
                            factored = sp.factor(standard_forms[0])
                            if factored != standard_forms[0]:
                                st.markdown("**第三步：多项式因式分解**")
                                st.latex(f"{sp.latex(factored)} = 0")
                        except: pass
                    st.markdown("**最终解集:**")
                    for idx, sol in enumerate(solution):
                        sol_latex = ", \\quad ".join([f"{sp.latex(var)} = {sp.latex(val)}" for var, val in sol.items()])
                        st.latex(f"\\text{{解 }} {idx + 1}: \\quad {sol_latex}")
        except: st.error("解析失败！")

# ------------------------------------------
# 第三页：级数求和
# ------------------------------------------
with tab_sum:
    st.markdown("### ➕ 西格玛 (Σ) 求和神器")
    sum_expr_str = st.text_input("求和通项公式 (如: n**2):", value="n")
    col_s1, col_s2 = st.columns(2)
    sum_lower_str = col_s1.text_input("求和下限:", value="1")
    sum_upper_str = col_s2.text_input("求和上限 (如 oo):", value="10")
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
            with st.expander("👀 查看级数求和展示", expanded=True):
                st.markdown("**1. 级数表达式:**")
                st.latex(sp.latex(sum_obj))
                st.markdown("**2. 展开求和结果:**")
                st.latex(f"= {sp.latex(result)}")
            if result.is_number and not result.has(sp.oo):
                st.info(f"**近似数值:** `{result.evalf():.6f}`")
        except: st.error("计算失败！")

# ------------------------------------------
# 第四页：多重积分
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
        # 🌟 已经修复这里的暗黑模式变量名
        if dark_mode:
            plt.style.use('dark_background')
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))
            cmap_hl = 'cool'
        else:
            plt.style.use('default')
            cmap_hl = 'magma'
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
            ax.plot_surface(X, Y, Z, alpha=0.9, cmap=cmap_hl, edgecolor='none')
            st.pyplot(fig)
        except: st.warning("⚠️ 3D 渲染跳过 (边界过于复杂)")

    if st.button("🌀 发动多重积分魔法 "):
        try:
            f = sp.sympify(multi_expr)
            xl, xu = sp.sympify(xl_str), sp.sympify(xu_str)
            yl, yu = sp.sympify(yl_str), sp.sympify(yu_str)
            
            if is_triple:
                zl, zu = sp.sympify(zl_str), sp.sympify(zu_str)
                step1 = sp.integrate(f, (z, zl, zu))
                step2 = sp.integrate(step1, (y, yl, yu))
                result = sp.integrate(step2, (x, xl, xu))
                st.success("🎉 三重积分计算成功！")
                with st.expander("👀 查看三重积分『剥洋葱』降维过程", expanded=True):
                    st.markdown("**1. 原始三重积分:**")
                    st.latex(f"\\int_{{{sp.latex(xl)}}}^{{{sp.latex(xu)}}} dx \\int_{{{sp.latex(yl)}}}^{{{sp.latex(yu)}}} dy \\int_{{{sp.latex(zl)}}}^{{{sp.latex(zu)}}} \\left( {sp.latex(f)} \\right) dz")
                    st.markdown("**2. 对最内层 $z$ 积分并代入上下限:**")
                    st.latex(f"\\int_{{{sp.latex(xl)}}}^{{{sp.latex(xu)}}} dx \\int_{{{sp.latex(yl)}}}^{{{sp.latex(yu)}}} \\left( {sp.latex(step1)} \\right) dy")
                    st.markdown("**3. 对中间层 $y$ 积分并代入上下限:**")
                    st.latex(f"\\int_{{{sp.latex(xl)}}}^{{{sp.latex(xu)}}} \\left( {sp.latex(step2)} \\right) dx")
                    st.markdown("**4. 对最外层 $x$ 积分得出最终结果:**")
                    st.latex(f"= {sp.latex(result)}")
            else:
                step1 = sp.integrate(f, (y, yl, yu))
                result = sp.integrate(step1, (x, xl, xu))
                st.success("🎉 二重积分计算成功！")
                with st.expander("👀 查看二重积分『剥洋葱』降维过程", expanded=True):
                    st.markdown("**1. 原始二重积分:**")
                    st.latex(f"\\int_{{{sp.latex(xl)}}}^{{{sp.latex(xu)}}} dx \\int_{{{sp.latex(yl)}}}^{{{sp.latex(yu)}}} \\left( {sp.latex(f)} \\right) dy")
                    st.markdown("**2. 对内层 $y$ 积分并代入上下限:**")
                    st.latex(f"\\int_{{{sp.latex(xl)}}}^{{{sp.latex(xu)}}} \\left( {sp.latex(step1)} \\right) dx")
                    st.markdown("**3. 对外层 $x$ 积分得出最终结果:**")
                    st.latex(f"= {sp.latex(result)}")
                plot_3d_integral(f, xl, xu, yl, yu)
            if result.is_number and not result.has(sp.oo): 
                st.info(f"**近似数值:** `{result.evalf():.6f}`")
        except: st.error("计算失败！")

# ------------------------------------------
# 第五页：线性代数与矩阵
# ------------------------------------------
with tab_linalg:
    st.markdown("### 🧮 智能矩阵运算中心")
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

    btn1, btn2, btn3, btn4, btn5 = st.columns(5)
    
    if btn1.button("A + B (求和)"):
        try:
            A, B = parse_matrix(mat_A_str), parse_matrix(mat_B_str)
            st.latex(f"{sp.latex(A)} + {sp.latex(B)} = {sp.latex(A + B)}")
        except Exception: st.error("❌ 计算失败！")

    if btn2.button("A × B (相乘)"):
        try:
            A, B = parse_matrix(mat_A_str), parse_matrix(mat_B_str)
            result = A * B
            st.success("✅ 矩阵乘法计算成功！")
            with st.expander("👀 查看矩阵相乘形态", expanded=True):
                st.latex(f"{sp.latex(A)} \\times {sp.latex(B)} = {sp.latex(result)}")
        except Exception: st.error("❌ 计算失败！")

    if btn3.button("| A | (行列式)"):
        try:
            A = parse_matrix(mat_A_str)
            st.latex(f"\\det({sp.latex(A)}) = {sp.latex(A.det())}")
        except Exception: st.error("❌ 计算失败！")

    if btn4.button("A⁻¹ (求逆)"):
        try:
            A = parse_matrix(mat_A_str)
            result = A.inv()
            st.success("✅ 逆矩阵计算成功！")
            with st.expander("👀 查看求逆过程与行列式", expanded=True):
                st.markdown("**1. 原矩阵:**")
                st.latex(f"A = {sp.latex(A)}")
                st.markdown("**2. 计算行列式 $|A|$:**")
                st.latex(f"|A| = {sp.latex(A.det())}")
                st.markdown("**3. 逆矩阵 $A^{-1}$:**")
                st.latex(f"A^{{-1}} = {sp.latex(result)}")
        except Exception: st.error("❌ 计算失败，不可逆或非方阵！")
        
    if btn5.button("Aᵀ (转置)"):
        try:
            A = parse_matrix(mat_A_str)
            st.latex(f"{sp.latex(A)}^T = {sp.latex(A.T)}")
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

# ------------------------------------------
# 第七页：向量计算
# ------------------------------------------
with tab_vector:
    st.markdown("### 📐 空间向量计算器")
    vc1, vc2 = st.columns(2)
    vecA_str = vc1.text_input("向量 $\\vec{A}$:", value="1, 2, 3")
    vecB_str = vc2.text_input("向量 $\\vec{B}$:", value="4, 5, 6")
    
    def parse_vec(v_str):
        return sp.Matrix([sp.sympify(e) for e in v_str.split(',')])

    vb1, vb2, vb3, vb4 = st.columns(4)
    if vb1.button("$\\vec{A} + \\vec{B}$"):
        try:
            A, B = parse_vec(vecA_str), parse_vec(vecB_str)
            st.latex(f"\\vec{{A}} + \\vec{{B}} = {sp.latex(A + B)}")
        except: st.error("格式错误！")
            
    if vb2.button("内积 (点乘)"):
        try:
            A, B = parse_vec(vecA_str), parse_vec(vecB_str)
            result = A.dot(B)
            st.success("✅ 点乘计算完成")
            with st.expander("👀 查看内积公式", expanded=True):
                st.latex(f"\\vec{{A}} \\cdot \\vec{{B}} = ({sp.latex(A.T)}) \\cdot ({sp.latex(B.T)})")
                st.latex(f"= {sp.latex(result)}")
        except: st.error("格式或维度错误！")
            
    if vb3.button("外积 (叉乘)"):
        try:
            A, B = parse_vec(vecA_str), parse_vec(vecB_str)
            if len(A) != 3 or len(B) != 3: st.warning("⚠️ 叉乘主要适用于三维向量！")
            else:
                result = A.cross(B)
                st.success("✅ 叉乘计算完成")
                with st.expander("👀 查看外积公式", expanded=True):
                    st.latex(f"\\vec{{A}} \\times \\vec{{B}} = {sp.latex(result)}")
        except: st.error("格式错误！")
            
    if vb4.button("求模长 $|\\vec{A}|$"):
        try:
            A = parse_vec(vecA_str)
            st.latex(f"|\\vec{{A}}| = {sp.latex(A.norm())}")
        except: st.error("格式错误！")

# ------------------------------------------
# 第八页：旋转面方程
# ------------------------------------------
with tab_surface:
    st.markdown("### 🏺 旋转曲面生成器")
    sc1, sc2 = st.columns([2, 1])
    curve_str = sc1.text_input("输入平面曲线方程 (如表示 $y=x^2$，输入 $x**2$):", value="x**2")
    axis = sc2.radio("绕哪个轴旋转?", ["x轴", "y轴"], horizontal=True)
    
    st.markdown("**3D 渲染范围设置：**")
    sc3, sc4 = st.columns(2)
    plot_start = sc3.text_input("参数起点 (如 -2):", value="-2")
    plot_end = sc4.text_input("参数终点 (如 2):", value="2")
    
    if st.button("✨ 自动推导 & 3D渲染"):
        try:
            f = sp.sympify(curve_str)
            free_vars = f.free_symbols
            var = list(free_vars)[0] if free_vars else x
            
            if "x" in axis:
                surface_eq = sp.Eq(y**2 + z**2, f**2)
                st.success(f"假设原曲线为 $y = {sp.latex(f)}$，绕 $x$ 轴旋转：")
            else:
                surface_eq = sp.Eq(x**2 + z**2, f**2)
                st.success(f"假设原曲线为 $x = {sp.latex(f)}$，绕 $y$ 轴旋转：")
            st.latex(sp.latex(surface_eq))
            
            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            # 🌟 修复关键点：所有的画图现在都统一听全局暗黑开关的指挥！
            if dark_mode:
                plt.style.use('dark_background')
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)
                ax.xaxis.set_pane_color((0,0,0,0)); ax.yaxis.set_pane_color((0,0,0,0)); ax.zaxis.set_pane_color((0,0,0,0))
                cmap_color = 'cool'
            else:
                plt.style.use('default')
                cmap_color = 'plasma'

            v_vals = np.linspace(float(sp.sympify(plot_start).evalf()), float(sp.sympify(plot_end).evalf()), 100)
            theta_vals = np.linspace(0, 2 * np.pi, 100)
            V, Theta = np.meshgrid(v_vals, theta_vals)
            
            f_lambdify = sp.lambdify(var, f, 'numpy')
            R = f_lambdify(V)
            if isinstance(R, (int, float)): R = np.full_like(V, R)

            if "x" in axis: X, Y, Z = V, R * np.cos(Theta), R * np.sin(Theta)
            else: X, Y, Z = R * np.cos(Theta), V, R * np.sin(Theta)

            ax.plot_surface(X, Y, Z, cmap=cmap_color, alpha=0.9, edgecolor='none')
            ax.set_xlabel('X Axis'); ax.set_ylabel('Y Axis'); ax.set_zlabel('Z Axis')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"解析失败！请检查数学表达式。")

# ------------------------------------------
# 第九页：曲线积分
# ------------------------------------------
with tab_line:
    st.markdown("### 〰️ 第二类曲线积分 (力场做功)")
    lc1, lc2 = st.columns(2)
    P_str = lc1.text_input("向量场 $P(x, y)$:", value="y")
    Q_str = lc2.text_input("向量场 $Q(x, y)$:", value="x**2")
    lc3, lc4 = st.columns(2)
    xt_str = lc3.text_input("曲线参数 $x(t)$:", value="t")
    yt_str = lc4.text_input("曲线参数 $y(t)$:", value="t**2")
    lc5, lc6 = st.columns(2)
    t_start_str = lc5.text_input("参数 $t$ 起点:", value="0")
    t_end_str = lc6.text_input("参数 $t$ 终点:", value="1")
    
    if st.button("🚀 计算做功积分并看步骤"):
        try:
            P, Q = sp.sympify(P_str), sp.sympify(Q_str)
            x_t, y_t = sp.sympify(xt_str), sp.sympify(yt_str)
            t_start, t_end = sp.sympify(t_start_str), sp.sympify(t_end_str)
            
            P_t, Q_t = P.subs({x: x_t, y: y_t}), Q.subs({x: x_t, y: y_t})
            dx_dt, dy_dt = sp.diff(x_t, t), sp.diff(y_t, t)
            
            integrand = P_t * dx_dt + Q_t * dy_dt
            result = sp.integrate(integrand, (t, t_start, t_end))
            
            st.success("🎉 曲线积分计算成功！")
            with st.expander("👀 查看极度舒适的微积分代换过程", expanded=True):
                st.markdown("**1. 原始第二类曲线积分式:**")
                st.latex(f"\\int_L ({sp.latex(P)})dx + ({sp.latex(Q)})dy")
                st.markdown("**2. 将 $x(t), y(t)$ 代入向量场得到 $P(t), Q(t)$:**")
                st.latex(f"P(t) = {sp.latex(P_t)}, \\quad Q(t) = {sp.latex(Q_t)}")
                st.markdown("**3. 对参数方程求导得到微分项 $dx, dy$:**")
                st.latex(f"dx = ({sp.latex(dx_dt)})dt, \\quad dy = ({sp.latex(dy_dt)})dt")
                st.markdown("**4. 组装为关于 $t$ 的一元定积分:**")
                st.latex(f"\\int_{{{sp.latex(t_start)}}}^{{{sp.latex(t_end)}}} \\left[ ({sp.latex(P_t)})({sp.latex(dx_dt)}) + ({sp.latex(Q_t)})({sp.latex(dy_dt)}) \\right] dt")
                st.markdown("**5. 化简被积函数:**")
                st.latex(f"\\int_{{{sp.latex(t_start)}}}^{{{sp.latex(t_end)}}} \\left( {sp.latex(sp.simplify(integrand))} \\right) dt")
                st.markdown("**6. 最终计算结果:**")
                st.latex(f"= {sp.latex(result)}")
        except:
            st.error("计算失败！请确保参数使用了变量 t。")
