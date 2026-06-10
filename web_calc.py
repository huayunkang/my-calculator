import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit.components.v1 as components
import os
import urllib.request
from urllib.error import URLError

from calculator_core import (
    InputParseError,
    parse_equations,
    parse_math_expr,
    parse_matrix,
    parse_numeric,
    parse_vector,
    user_error_message,
)
from tool_pages import (
    render_complex_calculator,
    render_function_analysis,
    render_physics_toolbox,
    render_statistics_probability,
    render_unit_converter,
)
from ui_components import (
    add_calculation_history,
    render_formula_input,
    render_history_panel,
)

# ==========================================
# 🌟 1. 终极中文字体守护引擎 (解决云端乱码)
# ==========================================
@st.cache_resource
def get_font_path():
    """全自动获取或下载字体文件"""
    local_path = "SimHei.ttf"
    if not os.path.exists(local_path):
        url = "https://cdn.jsdelivr.net/gh/StellarCN/scp_zh@master/fonts/SimHei.ttf"
        try:
            urllib.request.urlretrieve(url, local_path)
        except (OSError, URLError):
            pass
    return local_path if os.path.exists(local_path) else None

def apply_chinese_font():
    """在每次绘图前强制注入中文支持"""
    f_path = get_font_path()
    if f_path:
        fm.fontManager.addfont(f_path)
        prop = fm.FontProperties(fname=f_path)
        plt.rcParams['font.sans-serif'] = [prop.get_name(), 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False 


apply_chinese_font()

# --- 基础配置 ---
st.set_page_config(page_title="Ultra Max 计算器 Quantum", page_icon="🧮", layout="centered")

# ==========================================
# 🧚‍♀️ 2. 萌物召唤模块：全屏可拖拽的看板小猫 (📱 移动端霸体追踪版)
# ==========================================
def summon_mascot():
    mascot_code = """
    <script>
    const parentDoc = window.parent.document;
    const parentWindow = window.parent;
    
    // 🔪 斩杀旧猫：防止热更新后旧的事件监听器残留在内存里卡死页面
    let oldCat = parentDoc.getElementById("cute-mascot");
    if (oldCat) oldCat.remove();

    const mascot = parentDoc.createElement("div");
    mascot.id = "cute-mascot";
    mascot.style.position = "fixed";
    const compactMode = parentWindow.matchMedia("(max-width: 768px)").matches;
    const mascotSize = compactMode ? 72 : 120;
    mascot.style.bottom = compactMode ? "12px" : "30px";
    mascot.style.right = compactMode ? "12px" : "30px";
    mascot.style.zIndex = "999999";
    mascot.style.cursor = compactMode ? "default" : "grab";
    mascot.style.userSelect = "none";
    mascot.style.touchAction = compactMode ? "pan-y" : "none";
    mascot.style.pointerEvents = compactMode ? "none" : "auto";
    
    mascot.innerHTML = `<img draggable="false" src="https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif" width="${mascotSize}px" height="${mascotSize}px" style="pointer-events: none; border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 3px solid #FF4B2B;"/>`;
    parentDoc.body.appendChild(mascot);

    let isDragging = false;
    let startX, startY, initialLeft, initialTop;

    // 🎯 核心逻辑：计算相对偏移，防止跳动
    function startDrag(clientX, clientY) {
        isDragging = true;
        const rect = mascot.getBoundingClientRect();
        startX = clientX;
        startY = clientY;
        initialLeft = rect.left;
        initialTop = rect.top;
        mascot.style.bottom = "auto";
        mascot.style.right = "auto";
        mascot.style.left = initialLeft + "px";
        mascot.style.top = initialTop + "px";
        mascot.style.cursor = "grabbing";
    }

    function moveDrag(clientX, clientY) {
        if (!isDragging) return;
        const dx = clientX - startX;
        const dy = clientY - startY;
        const maxLeft = Math.max(0, parentWindow.innerWidth - mascot.offsetWidth);
        const maxTop = Math.max(0, parentWindow.innerHeight - mascot.offsetHeight);
        mascot.style.left = Math.min(maxLeft, Math.max(0, initialLeft + dx)) + "px";
        mascot.style.top = Math.min(maxTop, Math.max(0, initialTop + dy)) + "px";
    }

    // 手机端让触摸穿透，避免挂件阻止页面滚动或挡住输入。
    if (!compactMode) {
        mascot.addEventListener('touchstart', function(e) {
            e.preventDefault(); e.stopPropagation();
            startDrag(e.touches[0].clientX, e.touches[0].clientY);
        }, {passive: false});

        mascot.addEventListener('touchmove', function(e) {
            e.preventDefault(); e.stopPropagation();
            moveDrag(e.touches[0].clientX, e.touches[0].clientY);
        }, {passive: false});

        mascot.addEventListener('touchend', () => { isDragging = false; });
    }

    // 💻 电脑鼠标神经
    mascot.addEventListener('mousedown', (e) => { e.preventDefault(); startDrag(e.clientX, e.clientY); });
    parentDoc.addEventListener('mousemove', (e) => { if(isDragging) moveDrag(e.clientX, e.clientY); });
    parentDoc.addEventListener('mouseup', () => { isDragging = false; });

    </script>
    """
    components.html(mascot_code, height=0, width=0)

summon_mascot()

# ==========================================
# 3. 页面标题
# ==========================================
TOOL_GROUPS = {
    "数学工具": [
        "📚 微积分",
        "🔍 解方程",
        "➕ 级数",
        "🌀 多重积分",
        "🧮 线性代数",
        "📐 向量",
        "🏺 旋转面",
        "〰️ 曲线积分",
        "📈 函数分析",
        "📊 统计概率",
        "🌀 复数计算",
    ],
    "实用工具": ["🔁 单位换算", "💻 程序员"],
    "物理工具": ["🧪 物理工具箱", "🌌 高级物理演示"],
}

if "active_tool" not in st.session_state:
    st.session_state.active_tool = TOOL_GROUPS["数学工具"][0]


def select_tool(tool_name):
    st.session_state.active_tool = tool_name


with st.sidebar:
    st.markdown("## 🧮 功能导航")
    for group_name, tools in TOOL_GROUPS.items():
        st.markdown(f"### {group_name}")
        for tool_name in tools:
            st.button(
                tool_name,
                key=f"nav_{tool_name}",
                type="primary" if st.session_state.active_tool == tool_name else "secondary",
                use_container_width=True,
                on_click=select_tool,
                args=(tool_name,),
            )
    st.markdown("---")
    dark_mode = st.toggle("🌙 星空夜景模式", key="dark_mode")
    st.caption("支持 ^、×、÷、√、π 等常用数学符号。")
    render_history_panel()

selected_tool = st.session_state.active_tool

st.markdown('<div class="title-text">🧮 Ultra Max 计算器 Quantum</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">超级微积分神器 • 风景赛博版</div>', unsafe_allow_html=True)

# ==========================================
# 🎨 4. 视觉引擎：动态 CSS 注入 (📱 彻底修复平板滑动卡死)
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
    /* ----- 1. 核心背景与滑动修复 ----- */
    .stApp {{
        background-image: url("{current_bg}");
        background-size: cover; background-position: center; 
        background-attachment: fixed; /* 电脑端视差 */
        transition: background-image 0.5s ease-in-out;
    }}
    
    /* 🚨 移动端/平板 终极救命补丁：必须解除 fixed 锁定，否则 iPad 会假死 */
    @media screen and (max-width: 1100px), (hover: none) and (pointer: coarse) {{
        .stApp {{
            background-attachment: scroll !important;
            overflow-y: auto !important;
        }}
        .block-container {{
            backdrop-filter: none !important; /* 解除渲染压力 */
            -webkit-backdrop-filter: none !important;
        }}
        html, body, [data-testid="stAppViewContainer"] {{
            overflow: auto !important;
            height: auto !important;
        }}
        .block-container {{
            padding: 20px 14px 96px !important;
            border-radius: 14px;
        }}
        .title-text {{ font-size: 30px; line-height: 1.2; }}
        .subtitle-text {{ margin-bottom: 18px; }}
        div.stButton > button {{
            min-height: 46px;
            padding: 8px 10px;
            touch-action: manipulation;
        }}
        div.stTextInput input, div.stTextArea textarea {{
            font-size: 16px !important;
        }}
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

    /* ----- 2. 文字与按钮风格 ----- */
    .title-text {{
        background: -webkit-linear-gradient(45deg, #FF416C, #FF4B2B, #7b2ff7, #2f9eff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 42px; font-weight: 900; text-align: center; margin-bottom: 0px; padding-bottom: 10px;
    }}
    .subtitle-text {{ text-align: center; color: #888; font-size: 16px; margin-bottom: 30px; }}
    
    div.stButton > button {{
        border-radius: 12px; border: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
        min-height: 42px;
        cursor: pointer;
    }}
    div.stButton > button[kind="primary"] {{
        box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.55), 0 6px 16px rgba(79, 70, 229, 0.3);
        font-weight: 700;
    }}
    div.stTextInput > div > div > input {{ background-color: {input_bg}; color: {text_color}; }}
    div.stTextArea textarea {{ background-color: {input_bg}; color: {text_color}; }}
    p, span, label, div[data-testid="stMarkdownContainer"] {{ color: {text_color} !important; }}
    div[data-testid="stSidebar"] {{
        background-color: {card_bg};
        backdrop-filter: blur(12px);
    }}
    *:focus-visible {{ outline: 3px solid #00bcd4 !important; outline-offset: 2px; }}
</style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# ==========================================
# 5. 状态机与变量定义
# ==========================================
x, y, z, n, i, k, t = sp.symbols('x y z n i k t')
ALL_SYMBOLS = {"x": x, "y": y, "z": z, "n": n, "i": i, "k": k, "t": t}

# ==========================================
# 📈 6. 统一绘图函数
# ==========================================
def plot_graph(func, fill_a=None, fill_b=None):
    if dark_mode: plt.style.use('dark_background')
    else: plt.style.use('default')
    
    apply_chinese_font() 
    line_color = '#00ffcc' if dark_mode else '#FF4B2B' 
        
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)

    f_np = sp.lambdify(x, func, 'numpy')
    plot_min, plot_max = (min(fill_a, fill_b) - 2, max(fill_a, fill_b) + 2) if fill_a is not None and fill_b is not None else (-10, 10)
        
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

    ax.axhline(0, color='gray', linewidth=1); ax.axvline(0, color='gray', linewidth=1)
    ax.grid(True, linestyle='--', alpha=0.3)
    st.pyplot(fig)
# ------------------------------------------
# 第一页：微积分 
# ------------------------------------------
if selected_tool == "📚 微积分":
    st.markdown("### 📚 微积分计算")
    expr_str = render_formula_input(
        "请输入算式",
        key="math_expr",
        default="x^2 - 5×x + 6",
        allowed_symbols={"x": x},
        examples=("x^2 - 5*x + 6", "sin(x)^2 + cos(x)^2", "√(x^2 + 1)"),
        help_text="支持 ^、×、÷、√、π；变量使用 x。",
        extra_tokens=(("x", "x"), ("e", "E"), ("exp", "exp(")),
    )
    
    st.markdown("**(可选) 定积分上下限设置：**")
    col_a, col_b = st.columns(2)
    lower_limit_str = col_a.text_input("积分下限 a:", value="0")
    upper_limit_str = col_b.text_input("积分上限 b:", value="2")

    col1, col2, col3, col4 = st.columns(4)

    if col1.button("🟰 普通计算"):
        try:
            expr = parse_math_expr(expr_str, {"x": x})
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
            add_calculation_history(
                "普通计算",
                expr_str,
                str(simplified),
                input_key="math_expr",
            )
        except Exception as error:
            st.error(user_error_message(error, "公式计算失败，请检查输入。"))

    if col2.button("📈 求导数"):
        try:
            func = parse_math_expr(expr_str, {"x": x})
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
            add_calculation_history(
                "求导",
                expr_str,
                str(result),
                input_key="math_expr",
            )
        except Exception as error:
            st.error(user_error_message(error, "求导失败，请检查公式定义域。"))

    if col3.button("📉 不定积分"):
        try:
            func = parse_math_expr(expr_str, {"x": x})
            result = sp.integrate(func, x)
            st.success("不定积分成功！")
            with st.expander("👀 查看积分详细过程", expanded=True):
                st.markdown("**1. 构建不定积分式:**")
                st.latex(f"\\int \\left( {sp.latex(func)} \\right) dx")
                st.markdown("**2. 求解反导数:**")
                st.latex(f"= {sp.latex(result)} + C")
            plot_graph(result)
            add_calculation_history(
                "不定积分",
                expr_str,
                str(result),
                input_key="math_expr",
            )
        except Exception as error:
            st.error(user_error_message(error, "不定积分失败，请检查公式。"))

    if col4.button("📊 定积分"):
        try:
            func = parse_math_expr(expr_str, {"x": x})
            a = parse_math_expr(lower_limit_str, {}, numeric_only=True)
            b = parse_math_expr(upper_limit_str, {}, numeric_only=True)
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
            add_calculation_history(
                "定积分",
                f"{expr_str}; {a}→{b}",
                str(result),
                input_key="math_expr",
            )
        except Exception as error:
            st.error(user_error_message(error, "定积分失败，请检查上下限和公式。"))

# ------------------------------------------
# 第二页：解方程
# ------------------------------------------
if selected_tool == "🔍 解方程":
    st.markdown("### 🔍 智能方程求解器")
    eq_str = render_formula_input(
        "请输入方程（每行一个，也可用逗号分隔）",
        key="eq_expr",
        default="x^2 - 5*x + 6 = 0",
        allowed_symbols={"x": x, "y": y, "z": z},
        examples=("x^2 - 5*x + 6 = 0", "x + y = 3\nx - y = 1"),
        multiline=True,
        preview=False,
        help_text="例如：x+y=3，换行后输入 x-y=1。",
        extra_tokens=(("x", "x"), ("y", "y"), ("z", "z"), ("=", "="), ("换行", "\n")),
    )
    
    if st.button("🚀 解方程并查看过程"):
        try:
            eq_list, standard_forms = parse_equations(
                eq_str,
                {"x": x, "y": y, "z": z},
            )
                    
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
                        except (TypeError, ValueError, sp.PolynomialError):
                            pass
                    st.markdown("**最终解集:**")
                    for idx, sol in enumerate(solution):
                        sol_latex = ", \\quad ".join([f"{sp.latex(var)} = {sp.latex(val)}" for var, val in sol.items()])
                        st.latex(f"\\text{{解 }} {idx + 1}: \\quad {sol_latex}")
                add_calculation_history(
                    "解方程",
                    eq_str,
                    str(solution),
                    input_key="eq_expr",
                )
        except Exception as error:
            st.error(user_error_message(error, "方程求解失败，请检查方程格式。"))
# ------------------------------------------
# 第三页：级数求和
# ------------------------------------------
if selected_tool == "➕ 级数":
    st.markdown("### ➕ 西格玛 (Σ) 求和神器")
    sum_expr_str = render_formula_input(
        "求和通项公式",
        key="sum_expr",
        default="n^2",
        allowed_symbols={"n": n, "i": i, "k": k},
        examples=("n^2", "1/n^2", "2^n"),
        help_text="变量可使用 n、i 或 k。",
        extra_tokens=(("n", "n"), ("i", "i"), ("k", "k"), ("∞", "∞")),
    )
    
    col_s1, col_s2 = st.columns(2)
    sum_lower_str = col_s1.text_input("求和下限:", value="1")
    sum_upper_str = col_s2.text_input("求和上限 (如 oo):", value="10")
    
    if st.button("🧮 计算级数求和"):
        try:
            func_sum = parse_math_expr(sum_expr_str, {"n": n, "i": i, "k": k})
            free_vars = func_sum.free_symbols
            var = n if n in free_vars else (i if i in free_vars else (k if k in free_vars else x))
            if not func_sum.free_symbols: var = n 
            lower = parse_math_expr(sum_lower_str, {}, numeric_only=True)
            upper = parse_math_expr(sum_upper_str, {}, numeric_only=True)
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
            add_calculation_history(
                "级数求和",
                sum_expr_str,
                str(result),
                input_key="sum_expr",
            )
        except Exception as error:
            st.error(user_error_message(error, "级数求和失败，请检查范围和通项。"))

# ------------------------------------------
# 第四页：多重积分
# ------------------------------------------
if selected_tool == "🌀 多重积分":
    st.markdown("### 🌀 空间多重积分求解")
    int_type = st.radio("请选择积分维度:", ["∬ 二重积分", "∭ 三重积分"], horizontal=True)
    is_triple = "三重" in int_type
    
    multi_expr = render_formula_input(
        "被积函数 f(x,y,z)",
        key="multi_expr",
        default="x × y",
        allowed_symbols={"x": x, "y": y, "z": z},
        examples=("x*y", "x^2 + y^2", "sin(x)*cos(y)"),
        help_text="二重积分使用 x、y；三重积分还可使用 z。",
        extra_tokens=(("x", "x"), ("y", "y"), ("z", "z")),
    )
    
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
        except (TypeError, ValueError, OverflowError):
            st.warning("⚠️ 当前边界无法转换为可绘制的有限数值，已跳过 3D 图。")

    if st.button("🌀 发动多重积分魔法 "):
        try:
            f = parse_math_expr(multi_expr, {"x": x, "y": y, "z": z})
            xl = parse_math_expr(xl_str, {}, numeric_only=True)
            xu = parse_math_expr(xu_str, {}, numeric_only=True)
            yl = parse_math_expr(yl_str, {"x": x})
            yu = parse_math_expr(yu_str, {"x": x})
            
            if is_triple:
                zl = parse_math_expr(zl_str, {"x": x, "y": y})
                zu = parse_math_expr(zu_str, {"x": x, "y": y})
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
        except Exception as error:
            st.error(user_error_message(error, "多重积分失败，请检查积分顺序和边界。"))
# ------------------------------------------
# 第五页：线性代数与矩阵
# ------------------------------------------
if selected_tool == "🧮 线性代数":
    st.markdown("### 🧮 智能矩阵运算中心")
    col_m1, col_m2 = st.columns(2)
    mat_A_str = col_m1.text_area("输入矩阵 A:", value="1 2\n3 4", height=120)
    mat_B_str = col_m2.text_area("输入矩阵 B (可选):", value="5 6\n7 8", height=120)

    btn1, btn2, btn3, btn4, btn5 = st.columns(5)
    
    if btn1.button("A + B (求和)"):
        try:
            A, B = parse_matrix(mat_A_str), parse_matrix(mat_B_str)
            st.latex(f"{sp.latex(A)} + {sp.latex(B)} = {sp.latex(A + B)}")
        except Exception as error:
            st.error(user_error_message(error, "矩阵加法失败，请确认 A、B 维度一致。"))

    if btn2.button("A × B (相乘)"):
        try:
            A, B = parse_matrix(mat_A_str), parse_matrix(mat_B_str)
            result = A * B
            st.success("✅ 矩阵乘法计算成功！")
            with st.expander("👀 查看矩阵相乘形态", expanded=True):
                st.latex(f"{sp.latex(A)} \\times {sp.latex(B)} = {sp.latex(result)}")
        except Exception as error:
            st.error(user_error_message(error, "矩阵乘法失败，请确认 A 的列数等于 B 的行数。"))

    if btn3.button("| A | (行列式)"):
        try:
            A = parse_matrix(mat_A_str)
            st.latex(f"\\det({sp.latex(A)}) = {sp.latex(A.det())}")
        except Exception as error:
            st.error(user_error_message(error, "行列式仅适用于方阵。"))

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
        except Exception as error:
            st.error(user_error_message(error, "矩阵不可逆，请确认它是行列式非零的方阵。"))
        
    if btn5.button("Aᵀ (转置)"):
        try:
            A = parse_matrix(mat_A_str)
            st.latex(f"{sp.latex(A)}^T = {sp.latex(A.T)}")
        except Exception as error:
            st.error(user_error_message(error, "矩阵解析失败。"))

# ------------------------------------------
# 第六页：程序员(进制)
# ------------------------------------------
if selected_tool == "💻 程序员":
    st.markdown("### 🔢 实时进制转换")
    prog_expr = st.text_input("请输入整数或算式:", value="255", key="prog_input")
    if prog_expr:
        try:
            val_expr = parse_math_expr(prog_expr, {}, numeric_only=True)
            if val_expr.is_integer:
                val = int(val_expr)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(label="十进制 (DEC)", value=str(val))
                c2.metric(label="二进制 (BIN)", value=bin(val))
                c3.metric(label="八进制 (OCT)", value=oct(val))
                c4.metric(label="十六进制 (HEX)", value=hex(val))
            else:
                st.info("请输入结果为整数的算式，例如 2^8 - 1。")
        except Exception as error:
            st.error(user_error_message(error, "无法转换该输入。"))

# ------------------------------------------
# 第七页：向量计算
# ------------------------------------------
if selected_tool == "📐 向量":
    st.markdown("### 📐 空间向量计算器")
    vc1, vc2 = st.columns(2)
    vecA_str = vc1.text_input("向量 $\\vec{A}$:", value="1, 2, 3")
    vecB_str = vc2.text_input("向量 $\\vec{B}$:", value="4, 5, 6")
    
    vb1, vb2, vb3, vb4 = st.columns(4)
    if vb1.button("$\\vec{A} + \\vec{B}$"):
        try:
            A, B = parse_vector(vecA_str), parse_vector(vecB_str)
            st.latex(f"\\vec{{A}} + \\vec{{B}} = {sp.latex(A + B)}")
        except Exception as error:
            st.error(user_error_message(error, "向量相加失败，请确认维度一致。"))
            
    if vb2.button("内积 (点乘)"):
        try:
            A, B = parse_vector(vecA_str), parse_vector(vecB_str)
            result = A.dot(B)
            st.success("✅ 点乘计算完成")
            with st.expander("👀 查看内积公式", expanded=True):
                st.latex(f"\\vec{{A}} \\cdot \\vec{{B}} = ({sp.latex(A.T)}) \\cdot ({sp.latex(B.T)})")
                st.latex(f"= {sp.latex(result)}")
        except Exception as error:
            st.error(user_error_message(error, "点乘失败，请确认两个向量维度一致。"))
            
    if vb3.button("外积 (叉乘)"):
        try:
            A, B = parse_vector(vecA_str), parse_vector(vecB_str)
            if len(A) != 3 or len(B) != 3: st.warning("⚠️ 叉乘主要适用于三维向量！")
            else:
                result = A.cross(B)
                st.success("✅ 叉乘计算完成")
                with st.expander("👀 查看外积公式", expanded=True):
                    st.latex(f"\\vec{{A}} \\times \\vec{{B}} = {sp.latex(result)}")
        except Exception as error:
            st.error(user_error_message(error, "叉乘失败，请输入两个三维向量。"))
            
    if vb4.button("求模长 $|\\vec{A}|$"):
        try:
            A = parse_vector(vecA_str)
            st.latex(f"|\\vec{{A}}| = {sp.latex(A.norm())}")
        except Exception as error:
            st.error(user_error_message(error, "向量解析失败。"))

# ------------------------------------------
# 第八页：旋转面方程
# ------------------------------------------
if selected_tool == "🏺 旋转面":
    st.markdown("### 🏺 旋转曲面生成器")
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        curve_str = render_formula_input(
            "输入平面曲线表达式",
            key="surface_curve",
            default="x^2",
            allowed_symbols={"x": x, "y": y},
            examples=("x^2", "sin(x)", "√(x)"),
            help_text="绕 x 轴时通常输入关于 x 的表达式；绕 y 轴时输入关于 y 的表达式。",
            extra_tokens=(("x", "x"), ("y", "y")),
        )
    axis = sc2.radio("绕哪个轴旋转?", ["x轴", "y轴"], horizontal=True)
    
    st.markdown("**3D 渲染范围设置：**")
    sc3, sc4 = st.columns(2)
    plot_start = sc3.text_input("参数起点 (如 -2):", value="-2")
    plot_end = sc4.text_input("参数终点 (如 2):", value="2")
    
    if st.button("✨ 自动推导 & 3D渲染"):
        try:
            f = parse_math_expr(curve_str, {"x": x, "y": y})
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

            plot_start_value = parse_numeric(plot_start)
            plot_end_value = parse_numeric(plot_end)
            if plot_start_value >= plot_end_value:
                raise InputParseError("参数起点必须小于终点。")
            v_vals = np.linspace(plot_start_value, plot_end_value, 100)
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
        except Exception as error:
            st.error(user_error_message(error, "旋转面生成失败，请检查公式和绘图范围。"))

# ------------------------------------------
# 第九页：曲线积分
# ------------------------------------------
if selected_tool == "〰️ 曲线积分":
    st.markdown("### 〰️ 第二类曲线积分 (力场做功)")
    lc1, lc2 = st.columns(2)
    with lc1:
        P_str = render_formula_input(
            "向量场 P(x, y)",
            key="line_p",
            default="y",
            allowed_symbols={"x": x, "y": y},
            show_keypad=False,
        )
    with lc2:
        Q_str = render_formula_input(
            "向量场 Q(x, y)",
            key="line_q",
            default="x^2",
            allowed_symbols={"x": x, "y": y},
            show_keypad=False,
        )
    lc3, lc4 = st.columns(2)
    with lc3:
        xt_str = render_formula_input(
            "曲线参数 x(t)",
            key="line_xt",
            default="t",
            allowed_symbols={"t": t},
            show_keypad=False,
        )
    with lc4:
        yt_str = render_formula_input(
            "曲线参数 y(t)",
            key="line_yt",
            default="t^2",
            allowed_symbols={"t": t},
            show_keypad=False,
        )
    lc5, lc6 = st.columns(2)
    t_start_str = lc5.text_input("参数 $t$ 起点:", value="0")
    t_end_str = lc6.text_input("参数 $t$ 终点:", value="1")
    
    if st.button("🚀 计算做功积分并看步骤"):
        try:
            P = parse_math_expr(P_str, {"x": x, "y": y})
            Q = parse_math_expr(Q_str, {"x": x, "y": y})
            x_t = parse_math_expr(xt_str, {"t": t})
            y_t = parse_math_expr(yt_str, {"t": t})
            t_start = parse_math_expr(t_start_str, {}, numeric_only=True)
            t_end = parse_math_expr(t_end_str, {}, numeric_only=True)
            
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
        except Exception as error:
            st.error(user_error_message(error, "曲线积分失败，请确保参数方程只使用变量 t。"))

# ------------------------------------------
# 新增实用工具
# ------------------------------------------
if selected_tool == "📈 函数分析":
    render_function_analysis(dark_mode)

if selected_tool == "📊 统计概率":
    render_statistics_probability(dark_mode)

if selected_tool == "🌀 复数计算":
    render_complex_calculator(dark_mode)

if selected_tool == "🔁 单位换算":
    render_unit_converter()

if selected_tool == "🧪 物理工具箱":
    render_physics_toolbox(dark_mode)

# ==========================================
# 第十页：物理引擎 (量子与宇宙终极法则 Ultra 版)
# ==========================================
if selected_tool == "🌌 高级物理演示":
    st.markdown("### 🌌 宇宙真理解析引擎 (Physics Engine Quantum Plus)")
    
    # 一级菜单：选择物理学分支
    domain = st.selectbox("📚 请选择物理学领域:", [
        "🍎 经典力学 (Classical Mechanics)", 
        "🔥 热力学与统计物理 (Thermodynamics & Statistical)", 
        "⚡ 电磁学 (Electromagnetism)", 
        "🚀 近代物理 & 量子力学 (Modern & Quantum)"
    ])
    
    st.markdown("---")

# ==========================================
    # 🍎 经典力学 (含流体力学)
    # ==========================================
    if "经典力学" in domain:
        mech_sub = st.radio("⚙️ 选择定律分类:", [
            "动力学基础 (Newton/Hooke)",
            "抛体运动轨迹 (可视化作图)",
            "【纳维-斯托克斯】流体力学方程" # 🌟 新增：NS 方程概念展示
        ], horizontal=True)

        if "动力学" in mech_sub:
            creator = st.selectbox("🧑‍🔬 选择定律与提出者:", [
                "【牛顿】万有引力", "【牛顿】牛顿第二定律", "【胡克】胡克定律", "【阿蒙顿】滑动摩擦力"
            ])
            
            if "万有引力" in creator:
                st.info("公式: $F = G \\frac{m_1 m_2}{r^2}$")
                c1, c2, c3 = st.columns(3)
                m1_str, m2_str, r_str = c1.text_input("质量 $m_1$ (kg):", value="5.97e24", key="g_m1"), c2.text_input("质量 $m_2$ (kg):", value="70", key="g_m2"), c3.text_input("距离 $r$ (m):", value="6.371e6", key="g_r")
                if st.button("🚀 计算万有引力", key="btn_g"):
                    try:
                        m1 = parse_numeric(m1_str, non_negative=True)
                        m2 = parse_numeric(m2_str, non_negative=True)
                        radius = parse_numeric(r_str, positive=True)
                        F = 6.6743e-11 * m1 * m2 / radius**2
                        st.latex(f"F = {F:.6e} \\text{{ N}}")
                    except Exception as error:
                        st.error(user_error_message(error, "万有引力计算失败。"))
            elif "第二定律" in creator:
                st.info("公式: $F = m a$")
                c1, c2 = st.columns(2)
                m_str, a_str = c1.text_input("质量 $m$ (kg):", value="10", key="n2_m"), c2.text_input("加速度 $a$ (m/s²):", value="9.8", key="n2_a")
                if st.button("🚀 计算合外力", key="btn_n2"):
                    try:
                        F = parse_numeric(m_str, non_negative=True) * parse_numeric(a_str)
                        st.latex(f"F = {F:.6g} \\text{{ N}}")
                    except Exception as error:
                        st.error(user_error_message(error, "合外力计算失败。"))
            elif "胡克" in creator:
                st.info("公式: $F = -k x$")
                c1, c2 = st.columns(2)
                k_str, x_str = c1.text_input("劲度系数 $k$ (N/m):", value="500", key="hk_k"), c2.text_input("形变量 $x$ (m):", value="0.2", key="hk_x")
                if st.button("🚀 计算弹力", key="btn_hk"):
                    try:
                        force = parse_numeric(k_str, non_negative=True) * abs(parse_numeric(x_str))
                        st.latex(f"|F| = {force:.6g} \\text{{ N}}")
                    except Exception as error:
                        st.error(user_error_message(error, "弹力计算失败。"))
            elif "摩擦力" in creator:
                st.info("公式: $f = \\mu F_N$")
                c1, c2 = st.columns(2)
                mu_str, fn_str = c1.text_input("摩擦因数 $\\mu$:", value="0.3", key="fr_mu"), c2.text_input("正压力 $F_N$ (N):", value="98", key="fr_fn")
                if st.button("🚀 计算摩擦力", key="btn_fr"):
                    try:
                        friction = parse_numeric(mu_str, non_negative=True) * parse_numeric(fn_str, non_negative=True)
                        st.latex(f"f = {friction:.6g} \\text{{ N}}")
                    except Exception as error:
                        st.error(user_error_message(error, "摩擦力计算失败。"))

        elif "抛体运动" in mech_sub:
            st.markdown("#### ☄️ 抛体运动可视化引擎")
            st.info("公式: $x(t) = v_0 \\cos(\\theta) t, \\quad y(t) = v_0 \\sin(\\theta) t - \\frac{1}{2}gt^2$")
            pc1, pc2, pc3 = st.columns(3)
            v0_s, t_s, g_s = pc1.text_input("初速度 $v_0$ (m/s):", value="20", key="pr_v0"), pc2.text_input("发射角 $\\theta$ (°):", value="45", key="pr_theta"), pc3.text_input("重力加速 $g$:", value="9.8", key="pr_g")
            if st.button("☄️ 绘制轨迹", key="btn_pr"):
                try:
                    v0 = parse_numeric(v0_s, non_negative=True)
                    theta = parse_numeric(t_s)
                    g_v = parse_numeric(g_s, positive=True)
                    if not 0 <= theta <= 90:
                        raise InputParseError("发射角应在 0° 到 90° 之间。")
                    theta_rad = np.radians(theta)
                    t_flight = 2 * v0 * np.sin(theta_rad) / g_v
                    if dark_mode: plt.style.use('dark_background'); line_color = '#00ffcc'
                    else: plt.style.use('default'); line_color = '#FF4B2B'
                    
                    apply_chinese_font() # 👈 强制注入中文字体
                    
                    fig, ax = plt.subplots(figsize=(8, 4)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0); t_vals = np.linspace(0, t_flight, 200)
                    x_v, y_v = v0 * np.cos(theta_rad) * t_vals, v0 * np.sin(theta_rad) * t_vals - 0.5 * g_v * t_vals**2
                    ax.plot(x_v, y_v, color=line_color, lw=3); ax.fill_between(x_v, y_v, alpha=0.2, color=line_color); ax.set_xlabel("水平距离 X (m)", color=line_color); ax.set_ylabel("竖直高度 Y (m)", color=line_color); ax.set_ylim(bottom=0); ax.grid(True, linestyle='--', alpha=0.3)
                    st.pyplot(fig); st.info(f"射程: `{x_v[-1]:.2f} 米`, 最大高度: `{np.max(y_v):.2f} 米`")
                except Exception as error:
                    st.error(user_error_message(error, "抛体轨迹绘制失败。"))

        elif "纳维" in mech_sub:
            st.markdown("#### 🌊 纳维-斯托克斯方程 (Navier-Stokes Equations)")
            st.warning("⚠️ 这是千禧年七大数学难题之一，本模块仅用于展示其矢量形式，目前人类尚无通用代数解。")
            st.markdown("**对于不可压缩流体:**")
            st.latex("\\rho \\left( \\frac{\\partial \\mathbf{u}}{\\partial t} + (\\mathbf{u} \\cdot \\nabla) \\mathbf{u} \\right) = -\\nabla p + \\mu \\nabla^2 \\mathbf{u} + \\mathbf{f}")
            with st.expander("👀 解析方程各项的物理含义"):
                st.markdown("**左边**：惯性力。其中 $\\rho$ 是流体密度，$\\partial \\mathbf{u}/\\partial t$ 是局部加速度，$(\\mathbf{u} \\cdot \\nabla) \\mathbf{u}$ 是平流（对流）加速度。")
                st.markdown("**右边**：作用在流体上的外力。其中 $-\\nabla p$ 是压力梯度力（流体从高压流向低压），$\\mu \\nabla^2 \\mathbf{u}$ 是粘滞力（流体的摩擦力，$\\mu$ 为粘度），$\\mathbf{f}$ 是体积力（如重力）。")

    # ==========================================
    # 🔥 热力学与统计物理 (含熵增可视化)
    # ==========================================
    elif "热力学" in domain:
        creator = st.radio("🧑‍🔬 选择定律:", [
            "【克拉珀龙】理想气体状态方程", 
            "【斯特藩-玻尔兹曼】黑体辐射定律",
            "【克劳修斯】热力学第二定律 (熵增)" # 🌟 新增：熵增作图
        ], horizontal=True)
        
        if "理想气体" in creator:
            st.info("公式: $P = \\frac{nRT}{V}$")
            col1, col2, col3 = st.columns(3)
            n_str, T_str, V_str = col1.text_input("物质的量 $n$ (mol):", value="1", key="ig_n"), col2.text_input("绝对温度 $T$ (K):", value="298.15", key="ig_T"), col3.text_input("体积 $V$ (m³):", value="0.0224", key="ig_V")
            if st.button("🔥 计算压强", key="btn_ig"):
                try:
                    amount = parse_numeric(n_str, non_negative=True)
                    temperature = parse_numeric(T_str, positive=True)
                    volume = parse_numeric(V_str, positive=True)
                    pressure = amount * 8.314 * temperature / volume
                    st.latex(f"P = {pressure:.6e} \\text{{ Pa}}")
                except Exception as error:
                    st.error(user_error_message(error, "压强计算失败。"))
        elif "黑体" in creator:
            st.info("公式: $j^{\\star} = \\sigma T^4$")
            T_str = st.text_input("绝对温度 $T$ (K):", value="5778", key="sb_T") 
            if st.button("🔥 计算辐射出射度", key="btn_sb"):
                try:
                    temperature = parse_numeric(T_str, positive=True)
                    radiation = 5.67037e-8 * temperature**4
                    st.latex(f"j^{{\\star}} \\approx {radiation:.4e} \\text{{ W/m}}^2")
                except Exception as error:
                    st.error(user_error_message(error, "辐射出射度计算失败。"))
                
        elif "熵增" in creator:
            st.markdown("#### 🔥 热力学第二定律 (The Second Law: Entropy Increase)")
            st.info("克劳修斯表述: 热量不能自发地从低温物体传递到高温物体。孤立系统的熵总是趋于增加：$\\Delta S \\ge 0$")
            st.markdown("**熵增过程可视化 (模拟绝热膨胀/混合):**")
            n_atoms = st.slider("选择孤立系统中粒子数量:", 20, 200, 50, key="ent_atoms")
            if st.button("📊 发动熵增魔法 (作图)", key="btn_ent"):
                if dark_mode: plt.style.use('dark_background'); line_color = '#FF4B2B'; fill_color = '#7B2FF7'
                else: plt.style.use('default'); line_color = '#FF7F0e'; fill_color = '#1f77b4'
                
                apply_chinese_font() # 👈 强制注入中文字体
                
                fig, ax = plt.subplots(figsize=(8, 4)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                # 模拟粒子扩散过程中的统计熵 (S = k*ln(W))
                time_steps = 100
                particles = np.random.rand(n_atoms, 2) # 初始粒子堆积在左侧
                particles[:, 0] *= 0.1 # 初始化x范围在0-0.1
                entropy_vals = []
                # 统计每一步粒子在左右两半的分布，计算状态数W和熵S
                bins = np.array([0.0, 0.5, 1.0])
                kB = 1.38065e-23
                for t in range(time_steps):
                    particles[:, 0] += np.random.randn(n_atoms) * 0.01 + 0.005 # 向右扩散
                    particles[:, 0] = np.clip(particles[:, 0], 0, 1) # 限制在容器内
                    particles[:, 1] += np.random.randn(n_atoms) * 0.01 
                    particles[:, 1] = np.clip(particles[:, 1], 0, 1)
                    # 统计左右粒子数
                    n_left = np.sum(particles[:, 0] < 0.5)
                    n_right = n_atoms - n_left
                    # 状态数W = n! / (nL! * nR!)
                    W = sp.factorial(n_atoms) / (sp.factorial(n_left) * sp.factorial(n_right))
                    S = kB * np.log(float(W)) # 这里由于W太大了，需要特殊处理
                    entropy_vals.append(float(S))
                ax.plot(np.arange(time_steps), entropy_vals, color=line_color, lw=3, label="系统统计熵 $S(t)$")
                ax.fill_between(np.arange(time_steps), entropy_vals, alpha=0.2, color=fill_color)
                ax.set_xlabel("系统演化时间 $t$", color=line_color); ax.set_ylabel("系统统计熵 $S$ (J/K)", color=line_color); ax.grid(True, linestyle='--', alpha=0.3); ax.legend()
                st.pyplot(fig)
                st.success(f"模拟完成！初始熵: {entropy_vals[0]:.2e}, 最终熵: {entropy_vals[-1]:.2e}，系统自发由有序变为无序。")

    # ==========================================
    # ⚡ 电磁学 (带物理曲线可视化)
    # ==========================================
    elif "电磁" in domain:
        creator = st.radio("🧑‍🔬 选择定律:", ["【库仑】库仑定律", "【安培】安培力公式", "【法拉第】电磁感应定律"], horizontal=True)
        
        if "库仑" in creator:
            st.info("公式: $F = k_e \\frac{q_1 q_2}{r^2}$")
            col1, col2, col3 = st.columns(3)
            q1_s, q2_s, r_s = col1.text_input("电荷 $q_1$ (C):", value="1e-6", key="cb_q1"), col2.text_input("电荷 $q_2$ (C):", value="1e-6", key="cb_q2"), col3.text_input("距离 $r$ (m):", value="0.1", key="cb_r")
            if st.button("⚡ 计算库仑力并作图", key="btn_cb"):
                try:
                    q1_v = parse_numeric(q1_s)
                    q2_v = parse_numeric(q2_s)
                    r_v = parse_numeric(r_s, positive=True)
                    k_e = 8.98755e9
                    F_val = k_e * (q1_v * q2_v) / (r_v**2)
                    st.success("推导完成！")
                    st.latex(f"F \\approx {F_val:.4e} \\text{{ N}}")
                    
                    # 🌟 库仑力平方反比曲线图
                    if dark_mode: plt.style.use('dark_background'); c_line = '#00FFFF'
                    else: plt.style.use('default'); c_line = '#FF4B2B'
                    
                    apply_chinese_font() # 👈 强制注入中文字体
                    
                    fig, ax = plt.subplots(figsize=(6, 3)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                    r_vals = np.linspace(r_v * 0.2, r_v * 4, 100)
                    F_vals = k_e * (q1_v * q2_v) / (r_vals**2)
                    ax.plot(r_vals, np.abs(F_vals), color=c_line, lw=2, label=r"$F \propto 1/r^2$")
                    ax.scatter([r_v], [np.abs(F_val)], color='#FF00FF', s=100, zorder=5, label="当前位置")
                    ax.set_xlabel("距离 r (m)", color=c_line); ax.set_ylabel("受力大小 |F| (N)", color=c_line)
                    ax.grid(True, linestyle='--', alpha=0.3); ax.legend()
                    st.pyplot(fig)
                except Exception as error:
                    st.error(user_error_message(error, "库仑力计算失败。"))
                
        elif "安培" in creator:
            st.info("公式: $F = B I L \\sin(\\theta)$")
            c1, c2, c3, c4 = st.columns(4)
            B_s, I_s, L_s, t_s = c1.text_input("磁场 $B$ (T):", value="0.5", key="am_B"), c2.text_input("电流 $I$ (A):", value="2", key="am_I"), c3.text_input("长度 $L$ (m):", value="1", key="am_L"), c4.text_input("夹角 $\\theta$ (°):", value="90", key="am_t")
            if st.button("⚡ 计算安培力并作图", key="btn_am"):
                try:
                    B_v = parse_numeric(B_s, non_negative=True)
                    I_v = parse_numeric(I_s)
                    L_v = parse_numeric(L_s, non_negative=True)
                    t_v = parse_numeric(t_s)
                    if not 0 <= t_v <= 180:
                        raise InputParseError("夹角应在 0° 到 180° 之间。")
                    F_val = B_v * I_v * L_v * np.sin(np.radians(t_v))
                    st.success("推导完成！")
                    st.latex(f"F = {F_val:.4f} \\text{{ N}}")
                    
                    # 🌟 安培力角度正弦图
                    if dark_mode: plt.style.use('dark_background'); c_line = '#FF00FF'
                    else: plt.style.use('default'); c_line = '#1f77b4'
                    
                    apply_chinese_font() # 👈 强制注入中文字体
                    
                    fig, ax = plt.subplots(figsize=(6, 3)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                    thetas = np.linspace(0, 180, 100)
                    Fs = B_v * I_v * L_v * np.sin(np.radians(thetas))
                    ax.plot(thetas, Fs, color=c_line, lw=2, label="力随夹角变化 $F(\\theta)$")
                    ax.scatter([t_v], [F_val], color='#00FFFF', s=100, zorder=5, label="当前角度")
                    ax.set_xlabel("夹角 $\\theta$ (度)", color=c_line); ax.set_ylabel("安培力 F (N)", color=c_line)
                    ax.grid(True, linestyle='--', alpha=0.3); ax.legend()
                    st.pyplot(fig)
                except Exception as error:
                    st.error(user_error_message(error, "安培力计算失败。"))
                
        elif "法拉第" in creator:
            st.info("公式: $\\mathcal{E} = -N \\frac{\\Delta \\Phi}{\\Delta t}$")
            c1, c2, c3 = st.columns(3)
            N_s, dp_s, dt_s = c1.text_input("线圈匝数 $N$:", value="100", key="fa_N"), c2.text_input("磁通变化 $\\Delta \\Phi$ (Wb):", value="0.05", key="fa_dPhi"), c3.text_input("时间 $\\Delta t$ (s):", value="0.1", key="fa_dt")
            if st.button("⚡ 计算电动势", key="btn_fa"):
                try:
                    N_v = parse_numeric(N_s, positive=True)
                    dp_v = parse_numeric(dp_s)
                    dt_v = parse_numeric(dt_s, positive=True)
                    E_val = N_v * (dp_v / dt_v)
                    st.success("推导完成！")
                    st.latex(f"|\\mathcal{{E}}| = {E_val:.4f} \\text{{ V}}")
                except Exception as error:
                    st.error(user_error_message(error, "电动势计算失败。"))
    # ==========================================
    # 🚀 近代物理 & 量子力学 (终极带图版)
    # ==========================================
    elif "近代物理" in domain:
        creator = st.radio("🧑‍🔬 选择定律:", ["【爱因斯坦】质能等价", "【普朗克】光子能量", "【海森堡】不确定性原理", "【霍金】黑洞熵"], horizontal=True)

        if "爱因斯坦" in creator:
            st.markdown("#### ⚛️ 质能方程 (Mass-Energy Equivalence)")
            st.info("公式: $E = m c^2$")
            m_s = st.text_input("湮灭质量 $m$ (kg):", value="1", key="emc_m")
            if st.button("🚀 计算能量当量可视化", key="btn_emc"):
                try:
                    m_v = parse_numeric(m_s, non_negative=True)
                    c = 299792458
                    E_val = m_v * (c**2)
                    st.success("推导完成！")
                    st.latex(f"E \\approx {E_val:.4e} \\text{{ J}}")
                    
                    # 🌟 能量当量柱状图对比 (1吨TNT = 4.184e9 焦耳)
                    tnt_tons = E_val / 4.184e9
                    hiroshima_bombs = tnt_tons / 15000 # 广岛原子弹约1.5万吨TNT当量
                    
                    if dark_mode: plt.style.use('dark_background'); text_c = 'white'
                    else: plt.style.use('default'); text_c = 'black'
                    
                    apply_chinese_font() # 👈 强制注入中文字体
                    
                    fig, ax = plt.subplots(figsize=(8, 3)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                    labels = ['你的质量包含的能量', '小男孩原子弹 (作对比)']
                    values = [hiroshima_bombs, 1]
                    ax.barh(labels, values, color=['#FF00FF', '#00FFFF'], alpha=0.8)
                    ax.set_xlabel("等效广岛原子弹数量 (枚)", color=text_c)
                    ax.set_xscale('log') # 使用对数坐标
                    st.pyplot(fig)
                    st.caption(f"💥 **直观感受:** 你输入的质量完全湮灭，相当于 `{hiroshima_bombs:.2e}` 枚广岛原子弹爆炸的能量！")
                except Exception as error:
                    st.error(user_error_message(error, "质能换算失败。"))

        elif "普朗克" in creator:
            st.markdown("#### ⚡ 普朗克-爱因斯坦关系 (Planck-Einstein Relation)")
            st.info("公式: $E = h \\nu$")
            nu_str = st.text_input("请输入光子频率 $\\nu$ (Hz) [可见光约 5e14]:", value="5e14", key="pe_nu")
            if st.button("⚡ 计算光子能量", key="btn_pe"):
                try:
                    nu_v = parse_numeric(nu_str, positive=True)
                    h = 6.62607e-34
                    E_val = h * nu_v
                    st.success("推导完成！")
                    st.latex(f"E \\approx {E_val:.4e} \\text{{ J}}")
                    
                    # 🌟 E-nu 线性正比关系图
                    if dark_mode: plt.style.use('dark_background'); c_line = '#00FFFF'
                    else: plt.style.use('default'); c_line = '#FF7F0e'
                    
                    apply_chinese_font() # 👈 强制注入中文字体
                    
                    fig, ax = plt.subplots(figsize=(6, 3)); fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0)
                    nu_vals = np.linspace(nu_v * 0.1, nu_v * 3, 100)
                    E_vals = h * nu_vals
                    ax.plot(nu_vals, E_vals, color=c_line, lw=2, label="能量-频率 关系 $E=h\\nu$")
                    ax.scatter([nu_v], [E_val], color='#FF00FF', s=100, zorder=5, label="当前光子")
                    ax.set_xlabel("频率 $\\nu$ (Hz)", color=c_line); ax.set_ylabel("能量 E (J)", color=c_line)
                    ax.grid(True, linestyle='--', alpha=0.3); ax.legend()
                    st.pyplot(fig)
                except Exception as error:
                    st.error(user_error_message(error, "光子能量计算失败。"))

        elif "海森堡" in creator:
            st.markdown("#### 🌀 海森堡不确定性原理 (Heisenberg Uncertainty Principle)")
            st.info(r"公式: $\Delta x \Delta p \ge \frac{\hbar}{2}$")
            dx_str = st.text_input("预设位置不确定性 $\\Delta x$ (m) [例: 1e-10]:", value="1e-10", key="unc_dx")
            
            if st.button("🌀 发动量子仿真 (无惧刻度崩溃版)", key="btn_unc"):
                try:
                    dx = parse_numeric(dx_str, positive=True)
                    hbar = 1.05457e-34 
                    dp_min = hbar / (2 * dx) 
                    st.success(f"计算完成！最小动量不确定性 $\\Delta p_{{min}}$: `{dp_min:.2e} kg·m/s`")
                    
                    if dark_mode:
                        plt.style.use('dark_background')
                        c_x, c_p, c_glow = '#00FFFF', '#FF00FF', '#7B2FF7' 
                        text_c = 'white'
                    else:
                        plt.style.use('default')
                        c_x, c_p, c_glow = '#1f77b4', '#ff7f0e', '#7b2ff7' 
                        text_c = 'black'
                        
                    apply_chinese_font() # 👈 强制注入中文字体
                        
                    fig = plt.figure(figsize=(10, 6))
                    fig.patch.set_alpha(0.0) 
                    
                    # 🌟 修复版：使用归一化坐标轴防止 matplotlib 在 1e-25 时崩溃
                    norm_vals = np.linspace(-3, 3, 500) # 统一用 -3 到 +3 的比例尺画图
                    
                    ax1 = fig.add_subplot(211)
                    ax1.patch.set_alpha(0.0); ax1.grid(True, linestyle='--', alpha=0.3)
                    wave_x = np.exp(-(norm_vals**2) / 4) * np.cos(10 * norm_vals)
                    ax1.plot(norm_vals, wave_x, color=c_x, lw=2, label="粒子波包 $\\Psi(x)$")
                    ax1.fill_between(norm_vals, -1, 1, where=np.abs(norm_vals) < 1, color=c_glow, alpha=0.1)
                    ax1.axvline(1, color=c_glow, linestyle='--'); ax1.axvline(-1, color=c_glow, linestyle='--')
                    ax1.set_xlabel(f"位置 X (单位: $\\Delta x$ = {dx:.2e} m)", color=text_c)
                    ax1.set_ylabel("振幅 $\\Psi(x)$", color=text_c); ax1.legend()

                    ax2 = fig.add_subplot(212)
                    ax2.patch.set_alpha(0.0); ax2.grid(True, linestyle='--', alpha=0.3)
                    wave_p = np.exp(-(norm_vals**2) / 4) # 动量空间没有高频震荡
                    ax2.plot(norm_vals, wave_p, color=c_p, lw=2, label="动量分布 $\\Phi(p)$")
                    ax2.fill_between(norm_vals, -1, 1, where=np.abs(norm_vals) < 1, color=c_glow, alpha=0.1)
                    ax2.axvline(1, color=c_glow, linestyle='--'); ax2.axvline(-1, color=c_glow, linestyle='--')
                    ax2.set_xlabel(f"动量 P (单位: $\\Delta p_{{min}}$ = {dp_min:.2e} kg·m/s)", color=text_c)
                    ax2.set_ylabel("振幅 $\\Phi(p)$", color=text_c); ax2.legend()
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                except Exception as error:
                    st.error(user_error_message(error, "不确定性仿真失败。"))

        elif "霍金" in creator:
            st.markdown("#### 🏺 贝肯斯坦-霍金熵公式 (Bekenstein-Hawking Entropy Formula)")
            st.info("公式: $S = \\frac{k_B c^3 A}{4G\\hbar}$")
            col_1, col_2 = st.columns([2, 1])
            input_mode = col_2.radio("选择输入方式:", ["已知视界面积 A", "已知黑洞质量 M (例: 太阳)"])
            
            if "面积" in input_mode:
                A_str = col_1.text_input("请输入视界面积 $A$ (m²):", value="1.3e9", key="bh_A") 
            else:
                M_str = col_1.text_input("请输入黑洞质量 $M$ (kg):", value="1.989e30", key="bh_M") 
            
            if st.button("🏺 开启终极真理解析", key="btn_bh"):
                try:
                    kB, c, hbar, G = 1.38065e-23, 299792458, 1.05457e-34, 6.6743e-11
                    if "面积" in input_mode:
                        A = parse_numeric(A_str, positive=True)
                        M = (c**2) * np.sqrt(A / (16 * np.pi * G**2))
                    else:
                        M = parse_numeric(M_str, positive=True)
                        A = 16 * np.pi * (G**2) * (M**2) / (c**4)
                        st.info(f"推导视界面积 $A \\approx$ `{A:.4e}` m²")

                    S_hawking = (kB * c**3 * A) / (4 * G * hbar)
                    st.success("终极解析完成！")
                    st.warning(f"**爆表熵值:** `{S_hawking:.4e} J/K`")

                    # 史瓦西黑洞 3D 渲染引擎
                    Rs_val = 2 * G * M / (c**2)
                    if dark_mode: plt.style.use('dark_background'); disk_cmap = 'magma'
                    else: plt.style.use('default'); disk_cmap = 'plasma'
                    
                    apply_chinese_font() # 👈 强制注入中文字体
                        
                    fig = plt.figure(figsize=(6, 6))
                    ax = fig.add_subplot(111, projection='3d')
                    fig.patch.set_alpha(0.0); ax.patch.set_alpha(0.0); ax.axis('off') 
                    
                    u, v = np.linspace(0, 2 * np.pi, 50), np.linspace(0, np.pi, 50)
                    U, V = np.meshgrid(u, v)
                    X_bh, Y_bh, Z_bh = Rs_val * np.cos(U) * np.sin(V), Rs_val * np.sin(U) * np.sin(V), Rs_val * np.cos(V)
                    ax.plot_surface(X_bh, Y_bh, Z_bh, color='black', alpha=1.0)
                    
                    rad, theta = np.linspace(Rs_val * 1.2, Rs_val * 3, 30), np.linspace(0, 2 * np.pi, 60)
                    R_disk, Theta_disk = np.meshgrid(rad, theta)
                    X_disk, Y_disk, Z_disk = R_disk * np.cos(Theta_disk), R_disk * np.sin(Theta_disk), np.zeros_like(R_disk)
                    
                    Intensity = 1 / (R_disk**1.5)
                    colors = plt.get_cmap(disk_cmap)(Intensity / np.max(Intensity))
                    ax.plot_surface(X_disk, Y_disk, Z_disk, facecolors=colors, alpha=0.7, shade=False)
                    
                    ax.set_xlim([-Rs_val*3, Rs_val*3]); ax.set_ylim([-Rs_val*3, Rs_val*3]); ax.set_zlim([-Rs_val*3, Rs_val*3])
                    st.pyplot(fig)
                except Exception as error:
                    st.error(user_error_message(error, "黑洞熵计算或绘图失败，数值可能超出范围。"))

