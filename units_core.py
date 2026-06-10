"""Unit conversion helpers using SI as the internal representation."""

from __future__ import annotations

from dataclasses import dataclass


class UnitConversionError(ValueError):
    pass


@dataclass(frozen=True)
class UnitDefinition:
    factor: float
    offset: float = 0.0

    def to_si(self, value: float) -> float:
        return (value + self.offset) * self.factor

    def from_si(self, value: float) -> float:
        return value / self.factor - self.offset


UNIT_CATEGORIES: dict[str, dict[str, UnitDefinition]] = {
    "长度": {
        "m": UnitDefinition(1),
        "km": UnitDefinition(1000),
        "cm": UnitDefinition(0.01),
        "mm": UnitDefinition(0.001),
        "μm": UnitDefinition(1e-6),
        "nm": UnitDefinition(1e-9),
        "in": UnitDefinition(0.0254),
        "ft": UnitDefinition(0.3048),
        "yd": UnitDefinition(0.9144),
        "mile": UnitDefinition(1609.344),
    },
    "面积": {
        "m²": UnitDefinition(1),
        "km²": UnitDefinition(1e6),
        "cm²": UnitDefinition(1e-4),
        "ha": UnitDefinition(1e4),
        "acre": UnitDefinition(4046.8564224),
        "ft²": UnitDefinition(0.09290304),
    },
    "体积": {
        "m³": UnitDefinition(1),
        "L": UnitDefinition(1e-3),
        "mL": UnitDefinition(1e-6),
        "cm³": UnitDefinition(1e-6),
        "gal(US)": UnitDefinition(0.003785411784),
        "ft³": UnitDefinition(0.028316846592),
    },
    "质量": {
        "kg": UnitDefinition(1),
        "g": UnitDefinition(1e-3),
        "mg": UnitDefinition(1e-6),
        "t": UnitDefinition(1000),
        "lb": UnitDefinition(0.45359237),
        "oz": UnitDefinition(0.028349523125),
    },
    "时间": {
        "s": UnitDefinition(1),
        "ms": UnitDefinition(1e-3),
        "min": UnitDefinition(60),
        "h": UnitDefinition(3600),
        "day": UnitDefinition(86400),
    },
    "速度": {
        "m/s": UnitDefinition(1),
        "km/h": UnitDefinition(1 / 3.6),
        "mph": UnitDefinition(0.44704),
        "knot": UnitDefinition(0.5144444444),
    },
    "温度": {
        "K": UnitDefinition(1),
        "℃": UnitDefinition(1, 273.15),
        "℉": UnitDefinition(5 / 9, 459.67),
    },
    "压力": {
        "Pa": UnitDefinition(1),
        "kPa": UnitDefinition(1000),
        "MPa": UnitDefinition(1e6),
        "bar": UnitDefinition(1e5),
        "atm": UnitDefinition(101325),
        "mmHg": UnitDefinition(133.322387415),
        "psi": UnitDefinition(6894.757293),
    },
    "能量": {
        "J": UnitDefinition(1),
        "kJ": UnitDefinition(1000),
        "MJ": UnitDefinition(1e6),
        "Wh": UnitDefinition(3600),
        "kWh": UnitDefinition(3.6e6),
        "cal": UnitDefinition(4.184),
        "kcal": UnitDefinition(4184),
        "eV": UnitDefinition(1.602176634e-19),
    },
    "功率": {
        "W": UnitDefinition(1),
        "kW": UnitDefinition(1000),
        "MW": UnitDefinition(1e6),
        "hp": UnitDefinition(745.699871582),
    },
    "频率": {
        "Hz": UnitDefinition(1),
        "kHz": UnitDefinition(1000),
        "MHz": UnitDefinition(1e6),
        "GHz": UnitDefinition(1e9),
        "rpm": UnitDefinition(1 / 60),
    },
    "电压": {
        "V": UnitDefinition(1),
        "mV": UnitDefinition(1e-3),
        "kV": UnitDefinition(1000),
    },
    "电流": {
        "A": UnitDefinition(1),
        "mA": UnitDefinition(1e-3),
        "μA": UnitDefinition(1e-6),
    },
    "电阻": {
        "Ω": UnitDefinition(1),
        "kΩ": UnitDefinition(1000),
        "MΩ": UnitDefinition(1e6),
    },
    "电荷": {
        "C": UnitDefinition(1),
        "mC": UnitDefinition(1e-3),
        "μC": UnitDefinition(1e-6),
        "nC": UnitDefinition(1e-9),
    },
    "电容": {
        "F": UnitDefinition(1),
        "mF": UnitDefinition(1e-3),
        "μF": UnitDefinition(1e-6),
        "nF": UnitDefinition(1e-9),
        "pF": UnitDefinition(1e-12),
    },
}


def unit_names(quantity: str) -> tuple[str, ...]:
    try:
        return tuple(UNIT_CATEGORIES[quantity])
    except KeyError as exc:
        raise UnitConversionError(f"不支持的单位类别：{quantity}") from exc


def convert_value(value: float, quantity: str, from_unit: str, to_unit: str) -> float:
    try:
        category = UNIT_CATEGORIES[quantity]
        source = category[from_unit]
        target = category[to_unit]
    except KeyError as exc:
        raise UnitConversionError("单位类别或单位名称无效。") from exc
    return target.from_si(source.to_si(float(value)))


def to_si(value: float, quantity: str, unit: str) -> float:
    try:
        return UNIT_CATEGORIES[quantity][unit].to_si(float(value))
    except KeyError as exc:
        raise UnitConversionError(f"不支持单位：{unit}") from exc


def from_si(value: float, quantity: str, unit: str) -> float:
    try:
        return UNIT_CATEGORIES[quantity][unit].from_si(float(value))
    except KeyError as exc:
        raise UnitConversionError(f"不支持单位：{unit}") from exc
