#!/usr/bin/env python3
"""Deterministic 72-by-72 synthetic release-gate simulator (no device access).

Purpose: evaluate workflow logic and failure gates, NOT validate actual laptop security.
All evidence records and scenarios are invented for testing and clearly synthetic.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, replace, asdict
from itertools import product
from pathlib import Path
import csv
import json
import sys

@dataclass(frozen=True)
class ArchiveEvidence:
    complete_captures: bool = True
    original_scope_reviewed: bool = True
    hashes_verified: bool = True
    second_copy_verified: bool = True
    encrypted_archive: bool = True
    recovery_key_tested: bool = True
    no_unresolved_file_errors: bool = True
    cloud_and_profiles_reviewed: bool = True
    original_sources_stable: bool = True
    malware_clear_or_quarantined: bool = True
    catalog_complete: bool = False  # Not an irreversible donation gate.

@dataclass(frozen=True)
class DeviceEvidence:
    drive_retained: bool = True
    qualified_purge_attested: bool = False
    clean_install: bool = True
    support_mode: str = "supported"  # supported | esu_verified | offline_only | unsupported_online
    offline_disclosed: bool = False
    expected_online_use: bool = True
    activated_if_windows: bool = True
    private_accounts_removed: bool = True
    wifi_and_browser_cleared: bool = True
    hardware_tested: bool = True
    charger_present: bool = True
    recipient_ready: bool = True
    all_data_storage_accounted: bool = True
    firmware_management_cleared: bool = True

ARCHIVE_REQUIREMENTS = (
    "complete_captures", "original_scope_reviewed", "hashes_verified", "second_copy_verified",
    "encrypted_archive", "recovery_key_tested", "no_unresolved_file_errors", "cloud_and_profiles_reviewed",
    "original_sources_stable", "malware_clear_or_quarantined"
)
DEVICE_REQUIREMENTS = (
    "clean_install", "activated_if_windows", "private_accounts_removed", "wifi_and_browser_cleared",
    "hardware_tested", "charger_present", "recipient_ready", "all_data_storage_accounted", "firmware_management_cleared"
)


def judge(a: ArchiveEvidence, d: DeviceEvidence):
    blockers = ["ARCHIVE:"+f for f in ARCHIVE_REQUIREMENTS if not getattr(a,f)]
    blockers += ["DEVICE:"+f for f in DEVICE_REQUIREMENTS if not getattr(d,f)]
    if not (d.drive_retained or d.qualified_purge_attested):
        blockers.append("DEVICE:uncontrolled_original_drive")
    if d.support_mode not in ("supported", "esu_verified", "offline_only"):
        blockers.append("DEVICE:unsupported_online_os")
    if d.support_mode == "offline_only" and (d.expected_online_use or not d.offline_disclosed):
        blockers.append("DEVICE:offline_only_use_not_enforced_or_disclosed")
    return not blockers, blockers


def build_archive_72():
    # 9 baseline evidence families x 8 operational variants = 72 distinct scenarios.
    families = [
        ("archive_valid", {}),
        ("missing_backup", {"second_copy_verified": False}),
        ("hash_conflict", {"hashes_verified": False}),
        ("capture_incomplete", {"complete_captures": False}),
        ("cloud_unresolved", {"cloud_and_profiles_reviewed": False}),
        ("unknown_scope", {"original_scope_reviewed": False}),
        ("archive_unencrypted", {"encrypted_archive": False}),
        ("recovery_key_unknown", {"recovery_key_tested": False}),
        ("malware_unresolved", {"malware_clear_or_quarantined": False}),
    ]
    variants = [
        ("default", {}),
        ("catalog_pending", {"catalog_complete": False}),
        ("catalog_complete", {"catalog_complete": True}),
        ("source_changed", {"original_sources_stable": False}),
        ("unresolved_read_error", {"no_unresolved_file_errors": False}),
        ("key_test_failed", {"recovery_key_tested": False}),
        ("second_copy_unverified", {"second_copy_verified": False}),
        ("profiles_missing", {"cloud_and_profiles_reviewed": False}),
    ]
    out=[]
    for i,(fam,base) in enumerate(families):
        for j,(var,overrides) in enumerate(variants):
            out.append((f"A{i*8+j+1:02d}",fam+"__"+var,replace(ArchiveEvidence(),**{**base,**overrides})))
    assert len(out)==72
    return out


def build_device_72():
    families = [
        ("fresh_storage_supported", {"drive_retained":True,"support_mode":"supported"}),
        ("attested_purge_supported", {"drive_retained":False,"qualified_purge_attested":True,"support_mode":"supported"}),
        ("valid_esu", {"support_mode":"esu_verified"}),
        ("offline_fully_disclosed", {"support_mode":"offline_only","offline_disclosed":True,"expected_online_use":False}),
        ("windows_reset_only", {"drive_retained":False,"qualified_purge_attested":False}),
        ("old_drive_uncontrolled", {"drive_retained":False,"qualified_purge_attested":False,"clean_install":True}),
        ("unsupported_online", {"support_mode":"unsupported_online"}),
        ("activation_undetermined", {"activated_if_windows":False}),
        ("hardware_fault", {"hardware_tested":False}),
    ]
    variants = [
        ("ready", {}),
        ("old_wifi_profile", {"wifi_and_browser_cleared":False}),
        ("recipient_not_ready", {"recipient_ready":False}),
        ("charger_missing", {"charger_present":False}),
        ("private_accounts", {"private_accounts_removed":False}),
        ("installation_unverified", {"clean_install":False}),
        ("recipient_needs_internet", {"expected_online_use":True}),
        ("overlooked_secondary_storage", {"all_data_storage_accounted":False}),
    ]
    out=[]
    for i,(fam,base) in enumerate(families):
        for j,(var,overrides) in enumerate(variants):
            out.append((f"D{i*8+j+1:02d}",fam+"__"+var,replace(DeviceEvidence(),**{**base,**overrides})))
    assert len(out)==72
    return out


def simulate(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios=build_archive_72()
    variants=build_device_72()
    lines=[]
    blockers_count=Counter()
    allowed=[]
    for (aid,alabel,a),(did,dlabel,d) in product(scenarios,variants):
        approved,blockers=judge(a,d)
        if approved:
            allowed.append((aid,did))
            # Explicit invariants for every APPROVE outcome.
            assert all(getattr(a,x) for x in ARCHIVE_REQUIREMENTS)
            assert all(getattr(d,x) for x in DEVICE_REQUIREMENTS)
            assert d.drive_retained or d.qualified_purge_attested
            assert d.support_mode in ("supported", "esu_verified", "offline_only")
            assert d.support_mode != "offline_only" or (d.offline_disclosed and not d.expected_online_use)
        else:
            assert blockers
        blockers_count.update(blockers)
        lines.append({"archive_id":aid,"archive_case":alabel,"device_id":did,"device_case":dlabel,
                      "result":"ELIGIBLE_ON_SYNTHETIC_EVIDENCE" if approved else "BLOCKED",
                      "blockers":" | ".join(blockers)})
    assert len(lines)==5184
    assert len(allowed)>0 and len(allowed)<5184
    with (output_dir/"decision_matrix_5184.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=lines[0].keys());w.writeheader();w.writerows(lines)
    with (output_dir/"archive_scenarios_72.csv").open("w",newline="",encoding="utf-8-sig") as f:
        cols=["id","label",*asdict(scenarios[0][2]).keys()]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for id,label,o in scenarios: w.writerow({"id":id,"label":label,**asdict(o)})
    with (output_dir/"device_scenarios_72.csv").open("w",newline="",encoding="utf-8-sig") as f:
        cols=["id","label",*asdict(variants[0][2]).keys()]
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for id,label,o in variants:w.writerow({"id":id,"label":label,**asdict(o)})
    summary={"simulated_only":True,"total_cases":len(lines),"archive_scenarios":72,"device_scenarios":72,
             "eligible_in_model":len(allowed),"blocked_in_model":len(lines)-len(allowed),
             "eligible_percent":round(len(allowed)*100/len(lines),2),
             "most_common_blockers":blockers_count.most_common(),"first_eligible":allowed[:8],
             "not_proof_of_real_security": "These are synthetic logical conditions. No real files were audited, no laptop booted, no drive sanitized, no OS installed."}
    (output_dir/"simulation_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    return summary

if __name__=="__main__":
    print(json.dumps(simulate(Path(sys.argv[1]) if len(sys.argv)>1 else Path("simulation")),indent=2))
