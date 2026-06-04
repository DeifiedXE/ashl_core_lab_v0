import unittest

from ashl_core.senses import (
    build_sensor_event,
    build_visual_concept_candidate,
    validate_sensor_event,
)


class SensesTests(unittest.TestCase):
    def test_build_camera_pointing_teach_event(self):
        event = build_sensor_event(
            "camera",
            "pointing_teach",
            {"label_hint": "蘋果", "region_ref": {"x": 10, "y": 20, "w": 30, "h": 40}},
        )

        self.assertEqual(event["type"], "sensor_event")
        self.assertEqual(event["source"], "camera")
        self.assertEqual(event["event_type"], "pointing_teach")

    def test_build_screen_observation_event(self):
        event = build_sensor_event("screen", "screen_observation", {"window_title": "ASHL Lab"})

        self.assertEqual(event["source"], "screen")
        self.assertEqual(event["event_type"], "screen_observation")

    def test_sensor_event_required_fields(self):
        event = build_sensor_event("camera", "pointing_teach")

        for key in ["id", "type", "source", "event_type", "created_at"]:
            self.assertIn(key, event)

    def test_validate_sensor_event_accepts_valid_event(self):
        event = build_sensor_event("camera", "pointing_teach")

        self.assertTrue(validate_sensor_event(event))

    def test_validate_sensor_event_rejects_invalid_source(self):
        event = build_sensor_event("radar", "pointing_teach")

        self.assertFalse(validate_sensor_event(event))

    def test_validate_sensor_event_rejects_invalid_event_type(self):
        event = build_sensor_event("camera", "object_recognition")

        self.assertFalse(validate_sensor_event(event))

    def test_build_visual_concept_candidate_from_camera_event(self):
        event = build_sensor_event("camera", "pointing_teach")
        candidate = build_visual_concept_candidate(
            event,
            "蘋果",
            region_ref={"x": 10, "y": 20, "w": 30, "h": 40},
            note="user pointed to object",
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["type"], "visual_concept_candidate")
        self.assertEqual(candidate["label"], "蘋果")
        self.assertEqual(candidate["source_event_id"], event["id"])
        self.assertEqual(candidate["source"], "camera")

    def test_visual_concept_candidate_status_and_audit(self):
        event = build_sensor_event("camera", "pointing_teach")
        candidate = build_visual_concept_candidate(event, "蘋果")

        self.assertEqual(candidate["status"], "candidate")
        self.assertTrue(candidate["audit_required"])

    def test_visual_concept_candidate_contains_no_real_image_data(self):
        event = build_sensor_event("camera", "pointing_teach")
        candidate = build_visual_concept_candidate(event, "蘋果")

        forbidden_keys = {"image", "image_data", "pixels", "frame", "raw_image", "screenshot"}
        self.assertTrue(forbidden_keys.isdisjoint(candidate.keys()))

    def test_missing_label_returns_none(self):
        event = build_sensor_event("camera", "pointing_teach")

        self.assertIsNone(build_visual_concept_candidate(event, None))

    def test_missing_source_event_returns_none(self):
        self.assertIsNone(build_visual_concept_candidate(None, "蘋果"))


if __name__ == "__main__":
    unittest.main()
