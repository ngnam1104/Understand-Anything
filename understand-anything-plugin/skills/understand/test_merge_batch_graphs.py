#!/usr/bin/env python3
"""
test_merge_batch_graphs.py — Tests for the deterministic tested_by linker.

Run from this directory:
    python -m unittest test_merge_batch_graphs.py -v
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


# ── Module loader ─────────────────────────────────────────────────────────
# `merge-batch-graphs.py` has a hyphen in its name, so we cannot `import` it
# directly. Load it via importlib so we can call its module-level helpers.

_HERE = Path(__file__).resolve().parent
_MODULE_PATH = _HERE / "merge-batch-graphs.py"


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("merge_batch_graphs", _MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["merge_batch_graphs"] = module
    spec.loader.exec_module(module)
    return module


mbg = _load_module()


# ── Helpers ───────────────────────────────────────────────────────────────

def _file_node(path: str, **extra: Any) -> dict[str, Any]:
    """Build a minimal file node with the given relative path."""
    node: dict[str, Any] = {
        "id": f"file:{path}",
        "type": "file",
        "name": path.rsplit("/", 1)[-1],
        "filePath": path,
        "summary": "",
        "tags": [],
        "complexity": "simple",
    }
    node.update(extra)
    return node


# ── is_test_path ──────────────────────────────────────────────────────────

class IsTestPathTests(unittest.TestCase):
    """Path classification: production vs. test."""

    def test_js_ts_sibling_test_extensions(self) -> None:
        for path in [
            "src/foo.test.ts",
            "src/foo.test.tsx",
            "src/foo.test.js",
            "src/foo.test.jsx",
            "src/foo.test.mjs",
            "src/foo.test.cjs",
            "src/Component.test.vue",
            "src/foo.spec.ts",
            "src/foo.spec.tsx",
            "src/foo.spec.js",
            "src/Component.spec.vue",
        ]:
            with self.subTest(path=path):
                self.assertTrue(mbg.is_test_path(path), f"{path} should be a test")

    def test_underscore_test_dir_with_test_extension(self) -> None:
        self.assertTrue(mbg.is_test_path("src/__tests__/foo.test.js"))
        self.assertTrue(mbg.is_test_path("src/__tests__/foo.test.ts"))

    def test_tests_directory_with_test_extension(self) -> None:
        self.assertTrue(mbg.is_test_path("tests/foo/X.test.ts"))
        self.assertTrue(mbg.is_test_path("test/foo/X.test.ts"))
        self.assertTrue(mbg.is_test_path("spec/foo/X.spec.ts"))

    def test_go_test_files(self) -> None:
        self.assertTrue(mbg.is_test_path("internal/bar_test.go"))
        self.assertTrue(mbg.is_test_path("bar_test.go"))

    def test_python_test_files(self) -> None:
        self.assertTrue(mbg.is_test_path("tests/test_bar.py"))
        self.assertTrue(mbg.is_test_path("bar_test.py"))
        self.assertTrue(mbg.is_test_path("test_bar.py"))

    def test_java_test_files(self) -> None:
        self.assertTrue(mbg.is_test_path("src/test/java/com/foo/BarTest.java"))
        self.assertTrue(mbg.is_test_path("src/test/java/com/foo/BarTests.java"))
        self.assertTrue(mbg.is_test_path("src/test/java/com/foo/BarIT.java"))

    def test_kotlin_test_files(self) -> None:
        self.assertTrue(mbg.is_test_path("src/test/kotlin/com/foo/BarTest.kt"))
        self.assertTrue(mbg.is_test_path("src/test/kotlin/com/foo/BarTests.kt"))

    def test_csharp_test_files(self) -> None:
        self.assertTrue(mbg.is_test_path("Foo.Tests/BarTests.cs"))
        self.assertTrue(mbg.is_test_path("Foo.Tests/BarTest.cs"))

    def test_c_cpp_test_files(self) -> None:
        self.assertTrue(mbg.is_test_path("test/bar_test.c"))
        self.assertTrue(mbg.is_test_path("test/test_bar.c"))
        self.assertTrue(mbg.is_test_path("test/bar_test.cpp"))
        self.assertTrue(mbg.is_test_path("test/bar_test.cc"))
        self.assertTrue(mbg.is_test_path("test/test_bar.cpp"))

    def test_production_files_rejected(self) -> None:
        for path in [
            "src/foo.ts",
            "src/foo.tsx",
            "internal/bar.go",
            "src/index.tsx",
            "README.md",
            "docs/guide.md",
            "main.py",
            "src/foo/bar.js",
            "Foo.cs",
            "Bar.kt",
            "Bar.java",
        ]:
            with self.subTest(path=path):
                self.assertFalse(mbg.is_test_path(path), f"{path} should be production")

    def test_helper_in_tests_dir_without_test_extension_is_not_test(self) -> None:
        # Files that live inside a __tests__ directory but don't carry a test
        # extension are treated as helpers, not tests. We only count code files
        # whose basename matches a test pattern. Assets/non-code files in
        # tests/ are not flagged.
        self.assertFalse(mbg.is_test_path("src/__tests__/helpers.ts"))
        self.assertFalse(mbg.is_test_path("tests/fixtures/data.json"))


# ── production_candidates ─────────────────────────────────────────────────

class ProductionCandidatesTests(unittest.TestCase):
    """For each test path, what production paths should we try?"""

    def test_js_ts_sibling(self) -> None:
        cands = mbg.production_candidates("src/foo/X.test.ts")
        # Sibling de-infix should be in the candidate list, with .ts as the
        # most natural target. Several extensions are tried because a .test.ts
        # file might test a .tsx file.
        self.assertIn("src/foo/X.ts", cands)
        self.assertIn("src/foo/X.tsx", cands)

    def test_js_ts_spec_sibling(self) -> None:
        cands = mbg.production_candidates("src/foo/X.spec.tsx")
        self.assertIn("src/foo/X.tsx", cands)
        self.assertIn("src/foo/X.ts", cands)

    def test_underscore_tests_dir(self) -> None:
        cands = mbg.production_candidates("src/foo/__tests__/X.test.ts")
        # Walking out of __tests__/ should produce src/foo/X.ts
        self.assertIn("src/foo/X.ts", cands)

    def test_mirrored_tests_tree(self) -> None:
        cands = mbg.production_candidates("tests/foo/X.test.ts")
        # Should try src/foo/X.ts, app/foo/X.ts, lib/foo/X.ts, foo/X.ts
        self.assertIn("src/foo/X.ts", cands)
        self.assertIn("foo/X.ts", cands)

    def test_go_sibling(self) -> None:
        cands = mbg.production_candidates("internal/bar_test.go")
        self.assertIn("internal/bar.go", cands)

    def test_python_test_prefix(self) -> None:
        cands = mbg.production_candidates("tests/test_bar.py")
        self.assertIn("tests/bar.py", cands)
        # Also try mirrored layout
        self.assertIn("bar.py", cands)
        self.assertIn("src/bar.py", cands)

    def test_python_test_suffix(self) -> None:
        cands = mbg.production_candidates("foo/bar_test.py")
        self.assertIn("foo/bar.py", cands)

    def test_java_maven_layout(self) -> None:
        cands = mbg.production_candidates("src/test/java/com/foo/BarTest.java")
        self.assertIn("src/main/java/com/foo/Bar.java", cands)

    def test_java_tests_suffix(self) -> None:
        cands = mbg.production_candidates("src/test/java/com/foo/BarTests.java")
        self.assertIn("src/main/java/com/foo/Bar.java", cands)

    def test_java_it_suffix(self) -> None:
        cands = mbg.production_candidates("src/test/java/com/foo/BarIT.java")
        self.assertIn("src/main/java/com/foo/Bar.java", cands)

    def test_kotlin_maven_layout(self) -> None:
        cands = mbg.production_candidates("src/test/kotlin/com/foo/BarTest.kt")
        self.assertIn("src/main/kotlin/com/foo/Bar.kt", cands)


# ── link_tests (end-to-end) ───────────────────────────────────────────────

class LinkTestsTests(unittest.TestCase):
    """End-to-end behaviour of the linker against a node/edge set."""

    def test_basic_pairing_emits_forward_edge(self) -> None:
        nodes_by_id = {
            "file:src/foo.ts": _file_node("src/foo.ts"),
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
        }
        edges: list[dict[str, Any]] = []

        added, dropped, tagged = mbg.link_tests(nodes_by_id, edges)

        self.assertEqual(added, 1)
        self.assertEqual(dropped, 0)
        self.assertEqual(tagged, 1)
        self.assertEqual(len(edges), 1)
        edge = edges[0]
        self.assertEqual(edge["source"], "file:src/foo.ts")
        self.assertEqual(edge["target"], "file:src/foo.test.ts")
        self.assertEqual(edge["type"], "tested_by")
        self.assertEqual(edge["direction"], "forward")
        self.assertEqual(edge["weight"], 0.5)
        self.assertIn("tested", nodes_by_id["file:src/foo.ts"]["tags"])
        # Test node is not tagged with "tested"
        self.assertNotIn("tested", nodes_by_id["file:src/foo.test.ts"]["tags"])

    def test_no_production_counterpart_no_edge(self) -> None:
        nodes_by_id = {
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
        }
        edges: list[dict[str, Any]] = []

        added, dropped, tagged = mbg.link_tests(nodes_by_id, edges)

        self.assertEqual(added, 0)
        self.assertEqual(tagged, 0)
        self.assertEqual(len(edges), 0)

    def test_strips_existing_llm_tested_by_edges(self) -> None:
        nodes_by_id = {
            "file:src/foo.ts": _file_node("src/foo.ts"),
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
        }
        # Existing inverted LLM edge: test → production (wrong direction)
        edges: list[dict[str, Any]] = [
            {
                "source": "file:src/foo.test.ts",
                "target": "file:src/foo.ts",
                "type": "tested_by",
                "direction": "forward",
                "weight": 0.5,
                "description": "from LLM",
            },
            # Unrelated edge — should survive untouched
            {
                "source": "file:src/foo.ts",
                "target": "file:src/foo.test.ts",
                "type": "imports",
                "direction": "forward",
                "weight": 0.7,
            },
        ]

        added, dropped, tagged = mbg.link_tests(nodes_by_id, edges)

        self.assertEqual(added, 1)
        self.assertEqual(dropped, 1)
        self.assertEqual(tagged, 1)

        tested_by_edges = [e for e in edges if e["type"] == "tested_by"]
        self.assertEqual(len(tested_by_edges), 1)
        self.assertEqual(tested_by_edges[0]["source"], "file:src/foo.ts")
        self.assertEqual(tested_by_edges[0]["target"], "file:src/foo.test.ts")

        # Imports edge survives
        import_edges = [e for e in edges if e["type"] == "imports"]
        self.assertEqual(len(import_edges), 1)

    def test_direction_always_forward_production_to_test(self) -> None:
        nodes_by_id = {
            "file:src/foo.ts": _file_node("src/foo.ts"),
            "file:src/__tests__/foo.test.ts": _file_node("src/__tests__/foo.test.ts"),
            "file:internal/bar.go": _file_node("internal/bar.go"),
            "file:internal/bar_test.go": _file_node("internal/bar_test.go"),
            "file:src/main/java/com/foo/Bar.java": _file_node("src/main/java/com/foo/Bar.java"),
            "file:src/test/java/com/foo/BarTest.java": _file_node("src/test/java/com/foo/BarTest.java"),
        }
        edges: list[dict[str, Any]] = []

        added, dropped, tagged = mbg.link_tests(nodes_by_id, edges)

        self.assertEqual(added, 3)
        for edge in edges:
            self.assertEqual(edge["type"], "tested_by")
            self.assertEqual(edge["direction"], "forward")
            # Target must be the test file (basename gives it away)
            self.assertTrue(
                mbg.is_test_path(edge["target"][len("file:"):]),
                f"target {edge['target']} should classify as test",
            )
            self.assertFalse(
                mbg.is_test_path(edge["source"][len("file:"):]),
                f"source {edge['source']} should classify as production",
            )

    def test_idempotent(self) -> None:
        nodes_by_id = {
            "file:src/foo.ts": _file_node("src/foo.ts"),
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
        }
        edges: list[dict[str, Any]] = []

        mbg.link_tests(nodes_by_id, edges)
        # Second invocation must not duplicate edges or tags.
        added2, dropped2, tagged2 = mbg.link_tests(nodes_by_id, edges)

        # On the second pass: existing deterministic edge gets stripped (it is
        # a tested_by edge) and re-added; tag is already there. So edge count
        # stays at 1 and tags has exactly one "tested".
        tested_by_edges = [e for e in edges if e["type"] == "tested_by"]
        self.assertEqual(len(tested_by_edges), 1)
        tags = nodes_by_id["file:src/foo.ts"]["tags"]
        self.assertEqual(tags.count("tested"), 1)

    def test_first_matching_candidate_wins(self) -> None:
        # If both src/foo.ts and src/foo.tsx exist, the linker should match
        # exactly one of them (the first candidate). Sibling de-infix yields
        # .ts before .tsx (since the test is named foo.test.ts).
        nodes_by_id = {
            "file:src/foo.ts": _file_node("src/foo.ts"),
            "file:src/foo.tsx": _file_node("src/foo.tsx"),
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
        }
        edges: list[dict[str, Any]] = []

        added, dropped, tagged = mbg.link_tests(nodes_by_id, edges)

        self.assertEqual(added, 1)
        self.assertEqual(tagged, 1)
        # Only one of them gets tagged.
        ts_tagged = "tested" in nodes_by_id["file:src/foo.ts"]["tags"]
        tsx_tagged = "tested" in nodes_by_id["file:src/foo.tsx"]["tags"]
        self.assertTrue(ts_tagged != tsx_tagged, "exactly one should be tagged")
        # The .ts file should win (it matches the test-file extension).
        self.assertTrue(ts_tagged)

    def test_does_not_match_test_to_test(self) -> None:
        # If only test files exist, no edges are produced — we never link a
        # test to another test.
        nodes_by_id = {
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
            "file:src/foo.spec.ts": _file_node("src/foo.spec.ts"),
        }
        edges: list[dict[str, Any]] = []

        added, dropped, tagged = mbg.link_tests(nodes_by_id, edges)

        self.assertEqual(added, 0)
        self.assertEqual(tagged, 0)

    def test_does_not_duplicate_existing_tag(self) -> None:
        # Production node already carries the "tested" tag — linker should
        # not duplicate it.
        nodes_by_id = {
            "file:src/foo.ts": _file_node("src/foo.ts", tags=["tested", "core"]),
            "file:src/foo.test.ts": _file_node("src/foo.test.ts"),
        }
        edges: list[dict[str, Any]] = []

        mbg.link_tests(nodes_by_id, edges)

        tags = nodes_by_id["file:src/foo.ts"]["tags"]
        self.assertEqual(tags.count("tested"), 1)
        self.assertIn("core", tags)


# ── merge_and_normalize integration ───────────────────────────────────────

class MergeIntegrationTests(unittest.TestCase):
    """Verify the linker is wired into merge_and_normalize correctly."""

    def test_linker_runs_during_merge(self) -> None:
        batch = {
            "nodes": [
                {
                    "id": "file:src/foo.ts",
                    "type": "file",
                    "name": "foo.ts",
                    "filePath": "src/foo.ts",
                    "summary": "",
                    "tags": [],
                    "complexity": "simple",
                },
                {
                    "id": "file:src/foo.test.ts",
                    "type": "file",
                    "name": "foo.test.ts",
                    "filePath": "src/foo.test.ts",
                    "summary": "",
                    "tags": [],
                    "complexity": "simple",
                },
            ],
            "edges": [
                # An LLM-emitted (inverted) tested_by edge — should be dropped
                {
                    "source": "file:src/foo.test.ts",
                    "target": "file:src/foo.ts",
                    "type": "tested_by",
                    "direction": "forward",
                    "weight": 0.5,
                },
            ],
        }

        assembled, report = mbg.merge_and_normalize([batch])

        # Output should have exactly one tested_by edge with canonical direction
        tested_by_edges = [e for e in assembled["edges"] if e["type"] == "tested_by"]
        self.assertEqual(len(tested_by_edges), 1)
        self.assertEqual(tested_by_edges[0]["source"], "file:src/foo.ts")
        self.assertEqual(tested_by_edges[0]["target"], "file:src/foo.test.ts")

        # Production node tagged
        prod_node = next(n for n in assembled["nodes"] if n["id"] == "file:src/foo.ts")
        self.assertIn("tested", prod_node["tags"])

        # Report mentions the linker
        report_text = "\n".join(report)
        self.assertIn("tested_by", report_text.lower())


if __name__ == "__main__":
    unittest.main()
