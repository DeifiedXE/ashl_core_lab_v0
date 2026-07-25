import unittest

from ashl_core_v1.runtime.package_124_milestone_cli import build_parser


class Package124CliTests(unittest.TestCase):
    def test_parser_accepts_required_commands(self):
        parser = build_parser()
        for argv in (
            ["inspect-source", "--state-dir", "s", "--expected-commit", "8c38918"],
            ["audit-source", "--state-dir", "s"],
            ["create-archive", "--state-dir", "s", "--archive-root", "a", "--expected-commit", "8c38918", "--confirm"],
            ["verify-archive", "--archive-dir", "a"],
            ["show-certificate", "--archive-dir", "a"],
            ["show-provenance", "--archive-dir", "a"],
            ["show-boundaries", "--archive-dir", "a"],
            ["audit-archive-and-certify", "--state-dir", "s", "--archive-root", "a", "--confirm"],
        ):
            parsed = parser.parse_args(argv)
            self.assertIsNotNone(parsed.command)


if __name__ == "__main__":
    unittest.main()
