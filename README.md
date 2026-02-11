# test02 - CAPEX Report

This repository contains a small Python script to generate a CAPEX report from a CSV file.

Usage:

```bash
python capex_report.py --input data.csv --output capex_report.csv --group-by project
```

Arguments:
- `--input` / `-i`: Path to input CSV (required)
- `--output` / `-o`: Path to output report CSV (default: `capex_report.csv`)
- `--group-by` / `-g`: Optional column to group results by (e.g., `project`, `department`)
- `--capex-column` / `-c`: Name of the capex column (default: `capex`)
- `--capex-threshold` / `-t`: Numeric threshold; values greater than the threshold are considered CAPEX (default: `0.0`)

The script uses `pandas` to parse values and supports both numeric CAPEX amounts and truthy text values ("yes", "true", "1").
