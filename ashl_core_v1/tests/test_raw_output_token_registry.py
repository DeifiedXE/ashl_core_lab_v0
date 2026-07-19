import unittest

from ashl_core_v1.runtime.raw_output_token_registry import (
    build_raw_output_token_registry,
    validate_raw_output_tokens,
)


class RawOutputTokenRegistryTests(unittest.TestCase):
    def test_t00_through_t15_exist_without_meaning(self) -> None:
        tokens = build_raw_output_token_registry()
        self.assertEqual(tuple(token.token_code for token in tokens), tuple(f"T{index:02d}" for index in range(16)))
        self.assertTrue(all(token.semantic_label is None for token in tokens))
        self.assertTrue(all(token.predefined_meaning is None for token in tokens))
        self.assertTrue(all(token.enabled for token in tokens))

    def test_invalid_token_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_raw_output_tokens(("T03", "T16"))


if __name__ == "__main__":
    unittest.main()
