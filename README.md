# 🧮 全能微积分与线性代数计算器 (Ultra Max)

🎉 **在线体验地址:** https://my-calculator-cpkuuuvhgppes5959gpwfp.streamlit.app/

这不仅是一个计算器，这是一个基于 Python (`Streamlit` + `SymPy` + `Matplotlib`) 打造的**全能数学神器**！它完美适配手机与电脑端，能够极速解决从初等代数到大学高等数学的各种复杂运算，并提供精美的可视化图表。

## ✨ 核心功能 (Features)

### 1. 📚 微积分 (Calculus)
* 支持导数、不定积分、定积分。
* 具备函数自动绘图功能，定积分区域自动高亮填充。

### 2. 🔍 智能解方程 (Equation Solver)
* 支持一元/多元方程组、非线性方程。
* 具备**自动移项**与**因式分解**（十字相乘等）步骤展示。

### 3. 🌀 空间多重积分 (Multiple Integrals)
* 首创**“剥洋葱”降维推导法**。
* 完整展示三重/二重积分如何一步步降阶为一重定积分。

### 4. 🧮 线性代数 (Linear Algebra)
* 矩阵加减乘、求逆、行列式、转置。
* 允许输入未知数 $x, y$ 进行**符号矩阵**运算。

### 5. 📐 空间向量 (Vector Calculus)
* 实时计算点乘 (Dot Product)、叉乘 (Cross Product) 及模长。
* 支持三维空间逻辑推导。

### 6. 🏺 旋转曲面 (Surface of Revolution)
* 输入平面方程，自动推导三维空间曲面方程。
* **实时渲染 3D 交互模型**，空间想象力瞬间拉满。

### 7. 〰️ 曲线积分 (Line Integrals)
* 计算第二类曲线积分（力场做功）。
* 自动完成 $x(t), y(t)$ 参数化代换与求导步骤。

### 8. ➕ 级数求和 (Series)
* 完美支持 $\sum$ 西格玛求和，支持求极限（无限级数）。

### 9. 💻 程序员模式 (Binary)
* DEC/BIN/OCT/HEX 四大进制实时转换，内置整数算式解析。

## 🛠️ 技术栈
* **符号计算引擎**: [SymPy](https://www.sympy.org/)
* **Web 框架**: [Streamlit](https://streamlit.io/)
* **数值计算**: [NumPy](https://numpy.org/)
* **图形渲染**: [Matplotlib](https://matplotlib.org/) (2D & 3D Engine)
* **前端增强**: JavaScript Snippets & CSS Injection
### 🎨 赛博朋克视觉交互
* **动态风景壁纸**：内置**日间雪山**与**夜间星空**双重滤镜，随暗黑模式开关自动切换。
* **毛玻璃 UI**：基于 CSS 注入的现代 Glassmorphism 设计，卡片半透明度动态呼吸。
* **全屏拖拽萌物**：右下角常驻一只“狂敲键盘的小猫”吉祥物，鼠标可全屏自由拖拽。
## 🚀 本地运行指南 (Local Setup)
如果你想在自己的电脑上运行此项目：
1. 克隆此仓库到本地。
2. 安装依赖库：`pip install -r requirements.txt`
3. 启动应用：`streamlit run web_calc.py`

---
*If you like this project, please give it a ⭐! (如果你喜欢这个项目，请给我点一个免费的 Star 吧！)*
