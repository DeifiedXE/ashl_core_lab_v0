import unittest

from ashl_core.expression import build_expression_package
from ashl_core.guard import guard_output


class ExpressionGuardTests(unittest.TestCase):
    def test_forbidden_output_falls_back(self):
        package = build_expression_package("refocus", "跑題了，拉回來", {})
        result = guard_output("收到，回到主線，但順便談另一題。", package)

        self.assertFalse(result["passed"])
        self.assertEqual(result["final_output"], "收到，拉回主線。")

    def test_must_include_is_checked(self):
        package = build_expression_package("unknown_need_tool", "證明黎曼假設", {})
        result = guard_output("需要正式工具或嚴格推導。", package)

        self.assertFalse(result["passed"])
        self.assertIn("不能靠直覺硬答", result["final_output"])


if __name__ == "__main__":
    unittest.main()
