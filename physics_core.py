"""Physics calculation registry for the Streamlit toolbox."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable


G = 6.67430e-11
C = 299_792_458.0
H = 6.62607015e-34
HBAR = 1.054571817e-34
E_CHARGE = 1.602176634e-19
K_B = 1.380649e-23
R_GAS = 8.314462618


class PhysicsCalculationError(ValueError):
    pass


@dataclass(frozen=True)
class PhysicsInput:
    key: str
    label: str
    default: float
    quantity: str | None
    unit: str
    positive: bool = False
    non_negative: bool = False


@dataclass(frozen=True)
class PhysicsResult:
    label: str
    value_si: float
    quantity: str | None
    unit: str


@dataclass(frozen=True)
class PhysicsTool:
    category: str
    name: str
    formula: str
    inputs: tuple[PhysicsInput, ...]
    calculate: Callable[[dict[str, float]], tuple[PhysicsResult, ...]]
    description: str = ""
    plot_input: str | None = None


def _result(label: str, value: float, quantity: str | None, unit: str) -> PhysicsResult:
    if not math.isfinite(value):
        raise PhysicsCalculationError("计算结果不是有限数值，请检查输入。")
    return PhysicsResult(label, value, quantity, unit)


def _kinematics(v: dict[str, float]) -> tuple[PhysicsResult, ...]:
    velocity = v["v0"] + v["a"] * v["t"]
    displacement = v["v0"] * v["t"] + 0.5 * v["a"] * v["t"] ** 2
    return (
        _result("末速度", velocity, "速度", "m/s"),
        _result("位移", displacement, "长度", "m"),
    )


def _work_energy(v):
    work = v["force"] * v["distance"] * math.cos(math.radians(v["angle"]))
    return (_result("功", work, "能量", "J"),)


def _power(v):
    return (_result("平均功率", v["work"] / v["time"], "功率", "W"),)


def _momentum(v):
    return (
        _result("动量", v["mass"] * v["velocity"], None, "kg·m/s"),
        _result("冲量", v["force"] * v["time"], None, "N·s"),
    )


def _collision(v):
    denominator = v["m1"] + v["m2"]
    if denominator == 0:
        raise PhysicsCalculationError("总质量不能为 0。")
    velocity = (v["m1"] * v["u1"] + v["m2"] * v["u2"]) / denominator
    return (_result("完全非弹性碰撞共同速度", velocity, "速度", "m/s"),)


def _circular(v):
    acceleration = v["velocity"] ** 2 / v["radius"]
    force = v["mass"] * acceleration
    return (
        _result("向心加速度", acceleration, None, "m/s²"),
        _result("向心力", force, None, "N"),
    )


def _orbit(v):
    orbit = math.sqrt(G * v["mass"] / v["radius"])
    escape = math.sqrt(2) * orbit
    return (
        _result("圆轨道速度", orbit, "速度", "m/s"),
        _result("逃逸速度", escape, "速度", "m/s"),
    )


def _ohm(v):
    current = v["voltage"] / v["resistance"]
    power = v["voltage"] * current
    return (
        _result("电流", current, "电流", "A"),
        _result("电功率", power, "功率", "W"),
    )


def _series_parallel(v):
    series = v["r1"] + v["r2"]
    parallel = 1 / (1 / v["r1"] + 1 / v["r2"])
    return (
        _result("串联等效电阻", series, "电阻", "Ω"),
        _result("并联等效电阻", parallel, "电阻", "Ω"),
    )


def _electric_cost(v):
    energy_kwh = v["power"] * v["hours"] / 3.6e6
    return (
        _result("耗电量", energy_kwh * 3.6e6, "能量", "J"),
        _result("电费", energy_kwh * v["price"], None, "元"),
    )


def _capacitor(v):
    energy = 0.5 * v["capacitance"] * v["voltage"] ** 2
    charge = v["capacitance"] * v["voltage"]
    return (
        _result("储能", energy, "能量", "J"),
        _result("电荷量", charge, "电荷", "C"),
    )


def _rc(v):
    tau = v["resistance"] * v["capacitance"]
    voltage = v["source"] * (1 - math.exp(-v["time"] / tau))
    return (
        _result("时间常数", tau, "时间", "s"),
        _result("充电电压", voltage, "电压", "V"),
    )


def _heat(v):
    return (_result("吸收或放出热量", v["mass"] * v["specific_heat"] * v["delta_t"], "能量", "J"),)


def _phase(v):
    return (_result("相变热量", v["mass"] * v["latent_heat"], "能量", "J"),)


def _mixing(v):
    denominator = v["m1"] * v["c1"] + v["m2"] * v["c2"]
    temperature = (
        v["m1"] * v["c1"] * v["t1"] + v["m2"] * v["c2"] * v["t2"]
    ) / denominator
    return (_result("平衡温度", temperature, "温度", "K"),)


def _ideal_gas(v):
    return (_result("压强", v["amount"] * R_GAS * v["temperature"] / v["volume"], "压力", "Pa"),)


def _fluid_pressure(v):
    return (_result("液体压强", v["density"] * v["gravity"] * v["depth"], "压力", "Pa"),)


def _buoyancy(v):
    return (_result("浮力", v["density"] * v["gravity"] * v["volume"], None, "N"),)


def _continuity(v):
    return (_result("出口流速", v["area1"] * v["velocity1"] / v["area2"], "速度", "m/s"),)


def _bernoulli(v):
    pressure2 = (
        v["pressure1"]
        + 0.5 * v["density"] * (v["velocity1"] ** 2 - v["velocity2"] ** 2)
        + v["density"] * v["gravity"] * (v["height1"] - v["height2"])
    )
    return (_result("位置 2 压强", pressure2, "压力", "Pa"),)


def _wave(v):
    return (_result("波速", v["frequency"] * v["wavelength"], "速度", "m/s"),)


def _decibel(v):
    if v["intensity"] <= 0:
        raise PhysicsCalculationError("声强必须大于 0。")
    return (_result("声强级", 10 * math.log10(v["intensity"] / 1e-12), None, "dB"),)


def _doppler(v):
    denominator = v["wave_speed"] - v["source_speed"]
    if denominator <= 0:
        raise PhysicsCalculationError("声源速度必须小于波速。")
    observed = v["frequency"] * (v["wave_speed"] + v["observer_speed"]) / denominator
    return (_result("观测频率", observed, "频率", "Hz"),)


def _refraction(v):
    ratio = v["n1"] * math.sin(math.radians(v["angle1"])) / v["n2"]
    if abs(ratio) > 1:
        raise PhysicsCalculationError("该条件发生全反射，没有实数折射角。")
    return (_result("折射角", math.degrees(math.asin(ratio)), None, "°"),)


def _lens(v):
    denominator = 1 / v["focal"] - 1 / v["object_distance"]
    if denominator == 0:
        raise PhysicsCalculationError("物距位于焦点，像距趋于无穷。")
    image_distance = 1 / denominator
    magnification = -image_distance / v["object_distance"]
    return (
        _result("像距", image_distance, "长度", "m"),
        _result("放大率", magnification, None, "倍"),
    )


def _relativity(v):
    beta2 = (v["velocity"] / C) ** 2
    if beta2 >= 1:
        raise PhysicsCalculationError("速度必须小于光速。")
    gamma = 1 / math.sqrt(1 - beta2)
    return (
        _result("洛伦兹因子", gamma, None, ""),
        _result("膨胀后的时间", gamma * v["proper_time"], "时间", "s"),
        _result("收缩后的长度", v["proper_length"] / gamma, "长度", "m"),
    )


def _de_broglie(v):
    return (_result("德布罗意波长", H / (v["mass"] * v["velocity"]), "长度", "m"),)


def _photoelectric(v):
    photon = H * v["frequency"]
    kinetic = photon - v["work_function"]
    if kinetic < 0:
        kinetic = 0.0
    return (
        _result("光子能量", photon, "能量", "J"),
        _result("最大动能", kinetic, "能量", "J"),
    )


def _input(key, label, default, quantity, unit, positive=False, non_negative=False):
    return PhysicsInput(key, label, default, quantity, unit, positive, non_negative)


PHYSICS_TOOLS: tuple[PhysicsTool, ...] = (
    PhysicsTool("力学", "匀变速运动", r"v=v_0+at,\ s=v_0t+\frac12at^2", (
        _input("v0", "初速度", 0, "速度", "m/s"),
        _input("a", "加速度", 9.8, None, "m/s²"),
        _input("t", "时间", 2, "时间", "s", positive=True),
    ), _kinematics, plot_input="t"),
    PhysicsTool("力学", "功与能", r"W=Fs\cos\theta", (
        _input("force", "力", 10, None, "N"),
        _input("distance", "位移", 5, "长度", "m", non_negative=True),
        _input("angle", "夹角", 0, None, "°"),
    ), _work_energy),
    PhysicsTool("力学", "平均功率", r"P=W/t", (
        _input("work", "功", 1000, "能量", "J"),
        _input("time", "时间", 10, "时间", "s", positive=True),
    ), _power),
    PhysicsTool("力学", "动量与冲量", r"p=mv,\ J=Ft", (
        _input("mass", "质量", 2, "质量", "kg", non_negative=True),
        _input("velocity", "速度", 5, "速度", "m/s"),
        _input("force", "力", 10, None, "N"),
        _input("time", "作用时间", 1, "时间", "s", non_negative=True),
    ), _momentum),
    PhysicsTool("力学", "一维完全非弹性碰撞", r"v=\frac{m_1u_1+m_2u_2}{m_1+m_2}", (
        _input("m1", "物体 1 质量", 2, "质量", "kg", non_negative=True),
        _input("u1", "物体 1 初速度", 5, "速度", "m/s"),
        _input("m2", "物体 2 质量", 3, "质量", "kg", non_negative=True),
        _input("u2", "物体 2 初速度", 0, "速度", "m/s"),
    ), _collision),
    PhysicsTool("力学", "圆周运动", r"a_c=v^2/r,\ F_c=mv^2/r", (
        _input("mass", "质量", 1, "质量", "kg", non_negative=True),
        _input("velocity", "线速度", 10, "速度", "m/s"),
        _input("radius", "半径", 2, "长度", "m", positive=True),
    ), _circular, plot_input="velocity"),
    PhysicsTool("力学", "轨道与逃逸速度", r"v_o=\sqrt{GM/r},\ v_e=\sqrt{2GM/r}", (
        _input("mass", "天体质量", 5.972e24, "质量", "kg", positive=True),
        _input("radius", "距天体中心距离", 6.371e6, "长度", "m", positive=True),
    ), _orbit, plot_input="radius"),
    PhysicsTool("电学与电路", "欧姆定律与电功率", r"I=U/R,\ P=UI", (
        _input("voltage", "电压", 220, "电压", "V"),
        _input("resistance", "电阻", 100, "电阻", "Ω", positive=True),
    ), _ohm, plot_input="voltage"),
    PhysicsTool("电学与电路", "串并联电阻", r"R_s=R_1+R_2,\ R_p=(1/R_1+1/R_2)^{-1}", (
        _input("r1", "电阻 R1", 100, "电阻", "Ω", positive=True),
        _input("r2", "电阻 R2", 200, "电阻", "Ω", positive=True),
    ), _series_parallel),
    PhysicsTool("电学与电路", "用电量与电费", r"E=Pt,\ Cost=E_{kWh}\times Price", (
        _input("power", "电器功率", 1000, "功率", "W", non_negative=True),
        _input("hours", "使用时间", 8, "时间", "h", non_negative=True),
        _input("price", "每千瓦时电价", 0.6, None, "元/kWh", non_negative=True),
    ), _electric_cost),
    PhysicsTool("电学与电路", "电容储能", r"E=\frac12CU^2,\ Q=CU", (
        _input("capacitance", "电容", 100, "电容", "μF", non_negative=True),
        _input("voltage", "电压", 12, "电压", "V"),
    ), _capacitor, plot_input="voltage"),
    PhysicsTool("电学与电路", "RC 充电", r"\tau=RC,\ U_C=U_0(1-e^{-t/\tau})", (
        _input("resistance", "电阻", 10, "电阻", "kΩ", positive=True),
        _input("capacitance", "电容", 100, "电容", "μF", positive=True),
        _input("source", "电源电压", 5, "电压", "V"),
        _input("time", "充电时间", 1, "时间", "s", non_negative=True),
    ), _rc, plot_input="time"),
    PhysicsTool("热学与流体", "比热容计算", r"Q=mc\Delta T", (
        _input("mass", "质量", 1, "质量", "kg", non_negative=True),
        _input("specific_heat", "比热容", 4200, None, "J/(kg·K)", non_negative=True),
        _input("delta_t", "温度变化", 20, None, "K"),
    ), _heat),
    PhysicsTool("热学与流体", "相变热", r"Q=mL", (
        _input("mass", "质量", 1, "质量", "kg", non_negative=True),
        _input("latent_heat", "比潜热", 334000, None, "J/kg", non_negative=True),
    ), _phase),
    PhysicsTool("热学与流体", "混合量热", r"T=\frac{m_1c_1T_1+m_2c_2T_2}{m_1c_1+m_2c_2}", (
        _input("m1", "物体 1 质量", 1, "质量", "kg", positive=True),
        _input("c1", "物体 1 比热容", 4200, None, "J/(kg·K)", positive=True),
        _input("t1", "物体 1 温度", 353.15, "温度", "K"),
        _input("m2", "物体 2 质量", 1, "质量", "kg", positive=True),
        _input("c2", "物体 2 比热容", 4200, None, "J/(kg·K)", positive=True),
        _input("t2", "物体 2 温度", 293.15, "温度", "K"),
    ), _mixing),
    PhysicsTool("热学与流体", "理想气体", r"P=nRT/V", (
        _input("amount", "物质的量", 1, None, "mol", non_negative=True),
        _input("temperature", "绝对温度", 298.15, "温度", "K", positive=True),
        _input("volume", "体积", 0.0224, "体积", "m³", positive=True),
    ), _ideal_gas),
    PhysicsTool("热学与流体", "液体压强", r"P=\rho gh", (
        _input("density", "液体密度", 1000, None, "kg/m³", positive=True),
        _input("gravity", "重力加速度", 9.8, None, "m/s²", positive=True),
        _input("depth", "深度", 10, "长度", "m", non_negative=True),
    ), _fluid_pressure, plot_input="depth"),
    PhysicsTool("热学与流体", "阿基米德浮力", r"F_b=\rho gV", (
        _input("density", "流体密度", 1000, None, "kg/m³", positive=True),
        _input("gravity", "重力加速度", 9.8, None, "m/s²", positive=True),
        _input("volume", "排开体积", 0.01, "体积", "m³", non_negative=True),
    ), _buoyancy),
    PhysicsTool("热学与流体", "连续性方程", r"A_1v_1=A_2v_2", (
        _input("area1", "入口面积", 0.02, "面积", "m²", positive=True),
        _input("velocity1", "入口流速", 2, "速度", "m/s"),
        _input("area2", "出口面积", 0.01, "面积", "m²", positive=True),
    ), _continuity),
    PhysicsTool("热学与流体", "伯努利方程", r"P+\frac12\rho v^2+\rho gh=const", (
        _input("pressure1", "位置 1 压强", 101325, "压力", "Pa"),
        _input("density", "流体密度", 1000, None, "kg/m³", positive=True),
        _input("velocity1", "位置 1 流速", 1, "速度", "m/s"),
        _input("velocity2", "位置 2 流速", 3, "速度", "m/s"),
        _input("height1", "位置 1 高度", 2, "长度", "m"),
        _input("height2", "位置 2 高度", 0, "长度", "m"),
        _input("gravity", "重力加速度", 9.8, None, "m/s²", positive=True),
    ), _bernoulli),
    PhysicsTool("波与光学", "波速关系", r"v=f\lambda", (
        _input("frequency", "频率", 440, "频率", "Hz", non_negative=True),
        _input("wavelength", "波长", 0.78, "长度", "m", non_negative=True),
    ), _wave),
    PhysicsTool("波与光学", "分贝", r"L=10\log_{10}(I/I_0)", (
        _input("intensity", "声强", 1e-6, None, "W/m²", positive=True),
    ), _decibel),
    PhysicsTool("波与光学", "多普勒效应", r"f'=f\frac{v+v_o}{v-v_s}", (
        _input("frequency", "声源频率", 440, "频率", "Hz", positive=True),
        _input("wave_speed", "波速", 343, "速度", "m/s", positive=True),
        _input("observer_speed", "观察者迎向声源速度", 0, "速度", "m/s"),
        _input("source_speed", "声源迎向观察者速度", 20, "速度", "m/s"),
    ), _doppler),
    PhysicsTool("波与光学", "折射定律", r"n_1\sin\theta_1=n_2\sin\theta_2", (
        _input("n1", "介质 1 折射率", 1, None, "", positive=True),
        _input("angle1", "入射角", 45, None, "°"),
        _input("n2", "介质 2 折射率", 1.5, None, "", positive=True),
    ), _refraction),
    PhysicsTool("波与光学", "薄透镜与球面镜", r"\frac1f=\frac1u+\frac1v", (
        _input("focal", "焦距", 0.1, "长度", "m"),
        _input("object_distance", "物距", 0.3, "长度", "m"),
    ), _lens),
    PhysicsTool("近代与天体", "狭义相对论", r"\gamma=(1-v^2/c^2)^{-1/2}", (
        _input("velocity", "相对速度", 1.5e8, "速度", "m/s", non_negative=True),
        _input("proper_time", "固有时间", 1, "时间", "s", non_negative=True),
        _input("proper_length", "固有长度", 1, "长度", "m", non_negative=True),
    ), _relativity, plot_input="velocity"),
    PhysicsTool("近代与天体", "德布罗意波长", r"\lambda=h/(mv)", (
        _input("mass", "粒子质量", 9.109e-31, "质量", "kg", positive=True),
        _input("velocity", "粒子速度", 1e6, "速度", "m/s", positive=True),
    ), _de_broglie),
    PhysicsTool("近代与天体", "光电效应", r"K_{max}=h\nu-\phi", (
        _input("frequency", "光频率", 8e14, "频率", "Hz", positive=True),
        _input("work_function", "逸出功", 2, "能量", "eV", non_negative=True),
    ), _photoelectric, plot_input="frequency"),
)


def categories() -> tuple[str, ...]:
    return tuple(dict.fromkeys(tool.category for tool in PHYSICS_TOOLS))


def tools_for_category(category: str) -> tuple[PhysicsTool, ...]:
    return tuple(tool for tool in PHYSICS_TOOLS if tool.category == category)


def calculate_physics(tool: PhysicsTool, values_si: dict[str, float]) -> tuple[PhysicsResult, ...]:
    for input_spec in tool.inputs:
        value = values_si[input_spec.key]
        if input_spec.positive and value <= 0:
            raise PhysicsCalculationError(f"{input_spec.label}必须大于 0。")
        if input_spec.non_negative and value < 0:
            raise PhysicsCalculationError(f"{input_spec.label}不能小于 0。")
    return tool.calculate(values_si)
