import unittest

from ashl_core_v1.runtime.windows_bounded_window_capture_source import (
    WindowsBoundedWindowCaptureSource,
    luminance_mean_from_bgra8,
    visual_contrast_distinguishable,
)


class WindowsBoundedWindowCaptureSourceTests(unittest.TestCase):
    def test_luminance_contrast_uses_bgra8_bytes(self):
        black = bytes([0, 0, 0, 255] * 4)
        white = bytes([255, 255, 255, 255] * 4)
        self.assertLess(luminance_mean_from_bgra8(black), 0.01)
        self.assertGreater(luminance_mean_from_bgra8(white), 0.99)
        self.assertTrue(visual_contrast_distinguishable(black, white))

    def test_missing_window_does_not_capture_or_fallback_to_fixture(self):
        source = WindowsBoundedWindowCaptureSource()
        binding = source.bind_by_title(
            experiment_run_id="experiment:test",
            window_title="ASHL Package 123 definitely missing window",
        )
        self.assertIn(binding.binding_status, {"window_not_found", "capture_failed"})
        self.assertNotEqual(binding.binding_status, "bound")


if __name__ == "__main__":
    unittest.main()
