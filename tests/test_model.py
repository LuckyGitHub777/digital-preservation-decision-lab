import unittest
from src.decision_lab import (ArchiveEvidence, DeviceEvidence, judge, build_archive_72, build_device_72)

class SyntheticDecisionTests(unittest.TestCase):
    def test_model_population(self):
        self.assertEqual(len(build_archive_72()),72)
        self.assertEqual(len(build_device_72()),72)
    def test_holds_without_verified_backup(self):
        from dataclasses import replace
        a=replace(ArchiveEvidence(),second_copy_verified=False)
        good, blockers=judge(a,DeviceEvidence())
        self.assertFalse(good)
        self.assertIn("ARCHIVE:second_copy_verified",blockers)
    def test_uncontrolled_drive_never_passes(self):
        from dataclasses import replace
        d=replace(DeviceEvidence(),drive_retained=False,qualified_purge_attested=False)
        good,blockers=judge(ArchiveEvidence(),d)
        self.assertFalse(good)
        self.assertIn("DEVICE:uncontrolled_original_drive",blockers)
