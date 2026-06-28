import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = ROOT / "ashl_core_v1" / "docs" / "runtime_architecture_r2.md"


class RuntimeArchitectureR2DocTests(unittest.TestCase):
    def test_runtime_architecture_r2_doc_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_top_level_engines_are_defined(self):
        text = self._read_doc()
        for engine in (
            "Task Engine",
            "State Engine",
            "Memory Engine",
            "Teacher Interface",
            "Sense Interface",
            "Output Interface",
        ):
            with self.subTest(engine=engine):
                self.assertIn(engine, text)

    def test_task_engine_contains_required_runtime_parts(self):
        text = self._read_doc()
        for term in (
            "Task Creation",
            "ActiveTaskFrame",
            "Working Memory",
            "Tick Builder",
            "Bounded Runner",
            "Task Closure",
            "Task Disposition",
            "Suspended Task",
            "Task Resume",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_memory_engine_readback_flow_is_defined(self):
        text = self._read_doc()
        for term in (
            "Learning Candidate",
            "Teacher Review",
            "Reviewed Learning",
            "MemoryLearningTrace",
            "MemoryRoutingTrace",
            "MemoryApplicationData",
            "Readback",
            "Readback Apply",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_runtime_main_circulation_is_task_centered(self):
        text = self._read_doc()
        self.assertIn("Runtime R2 is described as a task circulation", text)
        self.assertIn("Tick is a unit inside Task Engine", text)
        self.assertIn("Task\n↓\nWorking Memory\n↓\nTick", text)

    def test_package_mapping_covers_packages_38_to_55(self):
        text = self._read_doc()
        for package_number in range(38, 56):
            with self.subTest(package_number=package_number):
                self.assertIn(f"| {package_number} |", text)

    def test_refactor_goals_move_future_work_to_engines(self):
        text = self._read_doc()
        self.assertIn("new runtime packages should be named by engine responsibility", text)
        self.assertIn("Task Engine state persistence", text)
        self.assertIn("Memory Engine readback use", text)
        self.assertIn("State Engine session handoff", text)

    def test_scope_boundary_does_not_claim_new_runtime_capability(self):
        text = self._read_doc()
        for forbidden_claim in (
            "new runtime",
            "new tick",
            "new memory write",
            "new loop",
            "scheduler",
            "action execution",
            "free action selection",
            "automatic learning approval",
        ):
            with self.subTest(forbidden_claim=forbidden_claim):
                self.assertIn(f"- {forbidden_claim}", text)

    def test_next_work_is_engine_named_not_tick_named(self):
        text = self._read_doc()
        self.assertIn(
            "ASHL Core v1 State Engine Cradle Persistence Handoff Minimal v0",
            text,
        )
        self.assertNotIn("Package 56 / ASHL Core v1 Tick", text)

    def _read_doc(self) -> str:
        return DOC_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
