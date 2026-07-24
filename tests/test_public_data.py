from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_results import validate


class PublicEvidenceTests(unittest.TestCase):
    def test_public_evidence_tables(self) -> None:
        messages = validate()
        self.assertTrue(any("pressure drop" in message for message in messages))
        self.assertTrue(any("T_sigma" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
