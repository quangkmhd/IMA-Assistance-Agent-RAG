from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from iqmeet_graphrag.security import ACLGuard, ACLViolation


class ACLTests(unittest.TestCase):
    def test_workspace_isolation_violation(self) -> None:
        guard = ACLGuard(allowed_workspaces={"ws_allowed"})
        with self.assertRaises(ACLViolation):
            guard.enforce("ws_other")


if __name__ == "__main__":
    unittest.main()
