import math
import unittest
from datetime import date

import sympy as sp

from beginner_tools import (
    common_denominator,
    date_difference,
    geometry_value,
    percentage_change,
    scientific_notation,
    search_tools,
    solve_quadratic,
)
from calculator_core import (
    analyze_formula,
    normalize_math_input,
    parse_equations,
    parse_math_expr,
    parse_matrix,
    parse_vector,
    repair_math_input,
)
from physics_core import PHYSICS_TOOLS, calculate_physics
from units_core import convert_value, to_si


class FormulaRepairTests(unittest.TestCase):
    def test_repairs_implicit_multiplication_and_parentheses(self):
        result = repair_math_input("2x + 3(x+1", {"x": None})
        self.assertEqual(result.repaired, "2*x + 3*(x+1)")
        self.assertTrue(result.automatic_changes)

    def test_repairs_function_argument_and_decimal(self):
        result = repair_math_input("sin x + .5", {"x": None})
        self.assertEqual(result.repaired, "sin(x) + 0.5")

    def test_typo_is_suggestion_not_automatic_rewrite(self):
        result = repair_math_input("sni(x)", {"x": None})
        self.assertEqual(result.repaired, "sni(x)")
        self.assertTrue(result.suggestions)

    def test_analysis_completions(self):
        analysis = analyze_formula("sq", {"x": None})
        self.assertIn("sqrt", analysis.completions)

    def test_fullwidth_and_chinese_punctuation(self):
        self.assertEqual(
            normalize_math_input("１２．５＋３（x－１）"),
            "12.5+3(x-1)",
        )
        repaired = repair_math_input("２（x＋１）＋３π", {"x": sp.Symbol("x")})
        self.assertEqual(repaired.repaired, "2*(x+1)+3*pi")
        self.assertTrue(repaired.changes)

    def test_context_aware_chinese_commas(self):
        x, y = sp.symbols("x y")
        self.assertEqual(parse_math_expr("log（8，2）"), 3)
        equations, _ = parse_equations(
            "x＋y＝3，x－y＝1",
            {"x": x, "y": y},
        )
        self.assertEqual(len(equations), 2)
        equations_with_function, _ = parse_equations(
            "log（8，2）＝3，x＝1",
            {"x": x},
        )
        self.assertEqual(len(equations_with_function), 2)

    def test_chinese_matrix_vector_and_decimal(self):
        self.assertEqual(parse_matrix("【１，２；３，４】"), sp.Matrix([[1, 2], [3, 4]]))
        self.assertEqual(parse_vector("（１，２，３）"), sp.Matrix([1, 2, 3]))
        self.assertEqual(repair_math_input("３。１４＋。５").repaired, "3.14+0.5")

    def test_ambiguous_chinese_period_requires_confirmation(self):
        result = repair_math_input("x。5", {"x": sp.Symbol("x")})
        self.assertIn("。", result.repaired)
        self.assertTrue(result.suggestions)
        self.assertTrue(any(change.requires_confirmation for change in result.changes))


class UnitConversionTests(unittest.TestCase):
    def test_speed_temperature_energy(self):
        self.assertAlmostEqual(convert_value(36, "速度", "km/h", "m/s"), 10)
        self.assertAlmostEqual(convert_value(0, "温度", "℃", "K"), 273.15)
        self.assertAlmostEqual(convert_value(1, "能量", "kWh", "J"), 3.6e6)

    def test_round_trip(self):
        mph = convert_value(100, "速度", "km/h", "mph")
        self.assertAlmostEqual(convert_value(mph, "速度", "mph", "km/h"), 100)


class PhysicsRegistryTests(unittest.TestCase):
    def test_all_default_tools_return_finite_results(self):
        for tool in PHYSICS_TOOLS:
            with self.subTest(tool=tool.name):
                values = {}
                for input_spec in tool.inputs:
                    if input_spec.quantity:
                        values[input_spec.key] = to_si(
                            input_spec.default,
                            input_spec.quantity,
                            input_spec.unit,
                        )
                    else:
                        values[input_spec.key] = input_spec.default
                results = calculate_physics(tool, values)
                self.assertTrue(results)
                self.assertTrue(all(math.isfinite(result.value_si) for result in results))

    def test_known_ohm_result(self):
        tool = next(tool for tool in PHYSICS_TOOLS if tool.name == "欧姆定律与电功率")
        results = calculate_physics(tool, {"voltage": 12, "resistance": 6})
        self.assertAlmostEqual(results[0].value_si, 2)
        self.assertAlmostEqual(results[1].value_si, 24)


class BeginnerToolTests(unittest.TestCase):
    def test_search_routes_natural_chinese_queries(self):
        self.assertEqual(search_tools("帮我求导")[0].target, "📚 微积分")
        self.assertEqual(search_tools("怎么算电费")[0].target, "🧪 物理工具箱")
        self.assertEqual(search_tools("分数通分")[0].target, "🧰 新手实用工具")

    def test_fraction_percentage_and_quadratic(self):
        fractions, denominator, numerators = common_denominator("1/2，2/3")
        self.assertEqual([str(value) for value in fractions], ["1/2", "2/3"])
        self.assertEqual((denominator, numerators), (6, [3, 4]))
        self.assertAlmostEqual(percentage_change(80, 100), 25)
        discriminant, roots = solve_quadratic(1, -5, 6)
        self.assertEqual(discriminant, 1)
        self.assertEqual(set(roots), {sp.Integer(2), sp.Integer(3)})

    def test_geometry_scientific_notation_and_dates(self):
        _, area, unit = geometry_value("圆面积", {"radius": 2})
        self.assertAlmostEqual(area, 4 * math.pi)
        self.assertEqual(unit, "m²")
        coefficient, exponent, notation = scientific_notation("０。００００１２３")
        self.assertAlmostEqual(coefficient, 1.23)
        self.assertEqual(exponent, -5)
        self.assertIn("e-5", notation)
        self.assertEqual(date_difference(date(2026, 1, 1), date(2026, 1, 11)), (10, 1))


if __name__ == "__main__":
    unittest.main()
