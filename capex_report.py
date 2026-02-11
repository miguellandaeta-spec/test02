"""
capex_report.py

Reads a CSV file and generates a CAPEX report based on the `capex` column.

Usage:
    python capex_report.py --input data.csv --output report.csv [--group-by project]

If `--group-by` is provided, the script will aggregate CAPEX sums and counts per group.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Generate CAPEX report from CSV")
    parser.add_argument('--input', '-i', required=True, help='Input CSV file path')
    parser.add_argument('--output', '-o', default='capex_report.csv', help='Output CSV file path')
    parser.add_argument('--group-by', '-g', default=None, help='Optional column name to group by (e.g., project, department)')
    parser.add_argument('--capex-column', '-c', default='capex', help='Name of the CAPEX column (default: capex)')
    parser.add_argument('--capex-threshold', '-t', type=float, default=0.0, help='Numeric threshold: values > threshold considered CAPEX (default: 0.0)')
    return parser.parse_args()


def normalize_capex(series):
    """Return a numeric series where CAPEX amounts are parsed as floats when possible,
    and boolean/text values are mapped to 1/0."""
    # Try to coerce to numeric; non-numeric become NaN
    numeric = pd.to_numeric(series, errors='coerce')

    # For non-numeric, map common truthy strings to 1
    mask_non_numeric = numeric.isna()
    text = series[mask_non_numeric].astype(str).str.strip().str.lower()
    truthy = text.isin(['yes', 'y', 'true', 't', '1'])

    numeric.loc[mask_non_numeric & truthy] = 1.0
    numeric.loc[mask_non_numeric & ~truthy] = 0.0

    # Fill remaining NaNs with 0
    numeric = numeric.fillna(0.0)
    return numeric


def generate_report(df, capex_col='capex', group_by=None, capex_threshold=0.0):
    if capex_col not in df.columns:
        raise KeyError(f"CAPEX column '{capex_col}' not found in input CSV")

    df['_capex_amount'] = normalize_capex(df[capex_col])

    # Consider rows with capex amount > threshold as CAPEX
    df['_is_capex'] = df['_capex_amount'] > capex_threshold

    # Overall summary
    total_capex_amount = float(df.loc[df['_is_capex'], '_capex_amount'].sum())
    total_capex_count = int(df['_is_capex'].sum())
    total_rows = len(df)

    summary = {
        'total_rows': total_rows,
        'capex_rows': total_capex_count,
        'total_capex_amount': total_capex_amount,
    }

    if group_by and group_by in df.columns:
        grouped = df.groupby(group_by).agg(
            capex_count=pd.NamedAgg(column='_is_capex', aggfunc='sum'),
            capex_amount=pd.NamedAgg(column='_capex_amount', aggfunc=lambda s: s[df.loc[s.index, '_is_capex']].sum()),
            total_count=pd.NamedAgg(column='_capex_amount', aggfunc='count'),
        ).reset_index()
        # Ensure integers where appropriate
        grouped['capex_count'] = grouped['capex_count'].astype(int)
        report_df = grouped
    else:
        # Return a small dataframe with overall totals
        report_df = pd.DataFrame([{
            'total_rows': summary['total_rows'],
            'capex_rows': summary['capex_rows'],
            'total_capex_amount': summary['total_capex_amount']
        }])

    return summary, report_df


def main():
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        sys.exit(2)

    df = pd.read_csv(input_path)

    try:
        summary, report_df = generate_report(df, capex_col=args.capex_column, group_by=args.group_by, capex_threshold=args.capex_threshold)
    except KeyError as e:
        print(f"Error: {e}")
        sys.exit(2)

    # Save report
    out_path = Path(args.output)
    report_df.to_csv(out_path, index=False)

    # Print quick summary
    print(f"Processed {summary['total_rows']} rows")
    print(f"CAPEX rows: {summary['capex_rows']}")
    print(f"Total CAPEX amount: {summary['total_capex_amount']}")
    print(f"Report written to: {out_path}")


if __name__ == '__main__':
    main()
