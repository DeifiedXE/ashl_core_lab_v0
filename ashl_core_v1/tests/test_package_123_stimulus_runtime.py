import unittest

from ashl_core_v1.runtime.local_pulse_stimulus_runtime import build_planned_stimulus_transitions
from ashl_core_v1.runtime.package_123_types import EXPERIMENT_ID, STIMULUS_SCHEDULE, build_source_profile


class Package123StimulusRuntimeTests(unittest.TestCase):
    def test_planned_transitions_are_ground_truth_only(self):
        transitions = build_planned_stimulus_transitions("experiment:test")
        self.assertEqual(len(transitions), len(STIMULUS_SCHEDULE))
        self.assertTrue(all(item.stimulus_ground_truth_only for item in transitions))
        self.assertEqual([item.visual_state for item in transitions].count("white"), 4)
        self.assertEqual([item.audio_state for item in transitions].count("tone"), 4)

    def test_source_profile_marks_camera_not_participating_by_design(self):
        profile = build_source_profile(
            experiment_run_id="experiment:test",
            screen_binding_id="binding:test",
            audio_source_descriptor_id="loopback:test",
        )
        self.assertEqual(profile.experiment_id, EXPERIMENT_ID)
        self.assertEqual(profile.screen_lane, "windows_window_capture")
        self.assertEqual(profile.audio_lane, "system_audio_loopback")
        self.assertEqual(profile.host_state_lane, "real_host_state")
        self.assertEqual(profile.camera_lane, "not_participating_by_design")
        self.assertTrue(profile.real_live_capture)
        self.assertFalse(profile.prerecorded_fixture_used)


if __name__ == "__main__":
    unittest.main()
