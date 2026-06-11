import unittest

import sympy as sp

from calculator_core import (
    InputParseError,
    MAX_EXPRESSION_LENGTH,
    normalize_math_input,
    parse_equations,
    parse_math_expr,
    parse_matrix,
    parse_numeric,
    parse_vector,
)


class CalculatorCoreTests(unittest.TestCase):
    def test_normalizes_friendly_symbols(self):
        self.assertEqual(normalize_math_input("√(x^2) + π×2÷4"), "sqrt(x**2) + pi*2/4")

    def test_parses_allowed_expression(self):
        x = sp.Symbol("x")
        result = parse_math_expr("sin(x)^2 + cos(x)^2", {"x": x})
        self.assertEqual(sp.simplify(result), 1)

    def test_rejects_unknown_name(self):
        with self.assertRaisesRegex(InputParseError, "不支持"):
            parse_math_expr("mystery(x)", {"x": sp.Symbol("x")})

    def test_rejects_dangerous_input(self):
        with self.assertRaises(InputParseError):
            parse_math_expr("__import__('os')")

    def test_rejects_empty_and_long_input(self):
        with self.assertRaisesRegex(InputParseError, "请输入"):
            parse_math_expr("")
        with self.assertRaisesRegex(InputParseError, "输入过长"):
            parse_math_expr("1" * (MAX_EXPRESSION_LENGTH + 1))

    def test_numeric_constraints(self):
        self.assertEqual(parse_numeric("2^3"), 8.0)
        self.assertEqual(parse_numeric("5.97e24"), 5.97e24)
        with self.assertRaisesRegex(InputParseError, "大于 0"):
            parse_numeric("0", positive=True)

    def test_equations_accept_lines_and_commas(self):
        x, y = sp.symbols("x y")
        equations, forms = parse_equations("x + y = 3\nx-y=1", {"x": x, "y": y})
        self.assertEqual(len(equations), 2)
        self.assertEqual(len(forms), 2)

    def test_matrix_and_vector_validation(self):
        matrix = parse_matrix("1, 2\n3, 4")
        self.assertEqual(matrix.shape, (2, 2))
        self.assertEqual(parse_vector("1, 2, 3").shape, (3, 1))
        with self.assertRaisesRegex(InputParseError, "相同数量"):
            parse_matrix("1 2\n3")

    def test_representative_calculations(self):
        x, y, n = sp.symbols("x y n")
        function = parse_math_expr("x^2 - 5*x + 6", {"x": x})
        self.assertEqual(sp.diff(function, x), 2 * x - 5)
        self.assertEqual(sp.integrate(function, (x, 0, 2)), sp.Rational(14, 3))

        equations, _ = parse_equations("x+y=3\nx-y=1", {"x": x, "y": y})
        self.assertEqual(sp.solve(equations, (x, y), dict=True), [{x: 2, y: 1}])

        term = parse_math_expr("n^2", {"n": n})
        self.assertEqual(sp.summation(term, (n, 1, 10)), 385)

        integrand = parse_math_expr("x*y", {"x": x, "y": y})
        result = sp.integrate(integrand, (y, 0, 2), (x, 0, 2))
        self.assertEqual(result, 4)


if __name__ == "__main__":
    unittest.main()
