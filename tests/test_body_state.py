import unittest

from ashl_core.body_state import build_body_state, clamp01, set_body_state, validate_body_state


class BodyStateTests(unittest.TestCase):
    def test_build_body_state_defaults_to_lying(self):
        body = build_body_state()

        self.assertEqual(body["type"], "body_state")
        self.assertEqual(body["state"], "lying")
        self.assertEqual(body["stability"], 0.0)
        self.assertEqual(body["energy"], 1.0)

    def test_validate_body_state_accepts_legal_state(self):
        self.assertTrue(validate_body_state(build_body_state("sitting", stability=0.4, energy=0.8)))

    def test_unknown_state_validation_fails(self):
        body = build_body_state("floating")

        self.assertIsNone(body)
        self.assertFalse(
            validate_body_state(
                {"type": "body_state", "state": "floating", "stability": 0.5, "energy": 0.5, "updated_at": "now"}
            )
        )

    def test_stability_is_clamped(self):
        body = build_body_state("lying", stability=2.0)

        self.assertEqual(body["stability"], 1.0)
        self.assertEqual(clamp01(-3.0), 0.0)

    def test_energy_is_clamped(self):
        body = build_body_state("lying", energy=-1.0)

        self.assertEqual(body["energy"], 0.0)
        self.assertEqual(clamp01(3.0), 1.0)

    def test_set_body_state_updates_known_state(self):
        body = build_body_state("lying")
        updated = set_body_state(body, "sitting")

        self.assertEqual(updated["state"], "sitting")
        self.assertTrue(validate_body_state(updated))


if __name__ == "__main__":
    unittest.main()
