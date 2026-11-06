# Digital Preservation — Decision Lab

An offline decision model built from **synthetic scenarios**: 72 illustrative archive-evidence cases × 72 illustrative device-readiness cases = **5,184 modeled decisions**.

## Explore

```bash
python src/decision_lab.py synthetic-output
python -m unittest discover -s tests -v
```

Use a new output directory for generated CSV and JSON results. The blank templates in `docs/` are for local use only; never commit completed personal device records.

## Limits

The model does **not** inspect hardware, restore backups, verify encryption, certify erasure, or establish real-world donation safety. Those outcomes require separately verified physical storage, privacy, backup and device checks. Results are illustrative, not field assurance.

**License:** Apache License 2.0 ([LICENSE](LICENSE)); the existing attribution is preserved in [NOTICE](NOTICE). [MANIFEST.sha256](MANIFEST.sha256) records the released files.
