# Digital Preservation — Decision Lab

An offline, **synthetic-only** decision model for thinking through archive-evidence and device-readiness requirements. It explores 72 fabricated archive scenarios × 72 fabricated device scenarios = 5,184 modeled decisions.

Run `python src/decision_lab.py synthetic-output` in a new output directory to generate CSV and JSON model evidence. Or run `python -m unittest discover -s tests -v` to check the model boundaries. The two blank inventory/receipt templates in `docs/` are intended for **local use only**; never commit completed personal records.

**What this does not establish:** It does not inspect a real device, restore a backup, certify erasure, confirm encryption, or establish transfer/donation safety. Human evaluation of all physical storage, account removal, independent backups, restores and supported operating-system security remains necessary.

**License/attribution:** Existing Apache License 2.0 and `NOTICE` are preserved unchanged. This public learning subset omits original private history, actual backup tooling, system access and private records. `MANIFEST.sha256` records exact released bytes. No background monitoring or personal-data collection is provided.
