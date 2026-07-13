import unittest
from dataclasses import FrozenInstanceError

from ashl_core_v1.runtime.bounded_embodied_session_runtime import BoundedEmbodiedSessionRuntime
from ashl_core_v1.runtime.runtime_capability_profile import (
    build_verified_runtime_capability_profile,
    validate_runtime_capability_profile,
)


class RuntimeCapabilityProfileTests(unittest.TestCase):
    def test_runtime_capability_profile_builds_once_and_is_immutable(self):
        profile = build_verified_runtime_capability_profile()
        validation = validate_runtime_capability_profile(profile)
        self.assertTrue(validation["valid"])
        self.assertTrue(profile.immutable_profile)
        self.assertTrue(profile.fixture_only)
        self.assertTrue(profile.profile_sha256)
        with self.assertRaises(FrozenInstanceError):
            profile.fixture_only = False  # type: ignore[misc]

    def test_bounded_runtime_stores_profile_id_and_hash(self):
        profile = build_verified_runtime_capability_profile()
        runtime = BoundedEmbodiedSessionRuntime(capability_profile=profile)
        state = runtime.create_session()
        self.assertEqual(state.runtime_capability_profile_id, profile.profile_id)
        self.assertEqual(state.runtime_capability_profile_sha256, profile.profile_sha256)


if __name__ == "__main__":
    unittest.main()

