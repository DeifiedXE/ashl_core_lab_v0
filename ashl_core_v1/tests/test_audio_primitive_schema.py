import unittest

from ashl_core_v1.perception.audio_primitive_schema import (
    AUDIO_PRIMITIVE_SCHEMA_VERSION,
    AudioPrimitiveRecord,
    build_empty_audio_primitive_schema_demo,
    validate_audio_primitive_record,
)


class AudioPrimitiveSchemaTests(unittest.TestCase):
    def test_observed_expected_roles_share_schema(self) -> None:
        observed = build_empty_audio_primitive_schema_demo(primitive_role="observed")
        expected = build_empty_audio_primitive_schema_demo(primitive_role="expected")

        self.assertEqual(observed.schema_version, AUDIO_PRIMITIVE_SCHEMA_VERSION)
        self.assertEqual(expected.schema_version, AUDIO_PRIMITIVE_SCHEMA_VERSION)
        self.assertIsNone(observed.semantic_label)
        self.assertIsNone(observed.speech_content)
        self.assertIsNone(observed.speaker_identity)
        self.assertIsNone(observed.emotion_label)
        self.assertTrue(validate_audio_primitive_record(observed)["valid"])
        self.assertTrue(validate_audio_primitive_record(expected)["valid"])

    def test_semantic_fields_are_forced_null(self) -> None:
        payload = build_empty_audio_primitive_schema_demo().to_dict()
        payload["audio_primitive_id"] = "audio_primitive:bad"
        payload["semantic_label"] = "anger"

        with self.assertRaises(ValueError):
            AudioPrimitiveRecord(**payload)


if __name__ == "__main__":
    unittest.main()
