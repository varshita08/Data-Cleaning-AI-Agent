"""
Data Cleaning AI Agent
A small Python agent that checks a CSV file, chooses suitable cleaning
steps from the data it finds, and saves a cleaned file plus a report.

Run:
    python data_cleaning_agent.py sample_input.csv
"""

import sys
from pathlib import Path
import pandas as pd


class DataCleaningAgent:
    def __init__(self, input_file):
        self.input_file = Path(input_file)
        self.actions = []

    def load_data(self):
        """Read the CSV file and show a useful error if it cannot be opened."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"File not found: {self.input_file}")
        data = pd.read_csv(self.input_file)
        if data.empty:
            raise ValueError("The input CSV file has no rows.")
        return data

    def clean_data(self, data):
        """Inspect columns and apply cleaning rules based on their data type."""
        cleaned = data.copy()

        # 1. Remove fully repeated rows.
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates()
        removed = before - len(cleaned)
        if removed:
            self.actions.append(f"Removed {removed} duplicate row(s).")

        # 2. Remove extra spaces and standardise text.
        for column in cleaned.select_dtypes(include=["object"]).columns:
            cleaned[column] = cleaned[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )
            cleaned[column] = cleaned[column].replace("", pd.NA)

        # 3. Detect missing values and fill them using a simple column-based rule.
        for column in cleaned.columns:
            missing = int(cleaned[column].isna().sum())
            if missing == 0:
                continue

            if pd.api.types.is_numeric_dtype(cleaned[column]):
                fill_value = cleaned[column].median()
                if pd.isna(fill_value):
                    fill_value = 0
                cleaned[column] = cleaned[column].fillna(fill_value)
                self.actions.append(
                    f"Filled {missing} missing value(s) in '{column}' "
                    f"with the median ({fill_value})."
                )
            else:
                mode_values = cleaned[column].mode(dropna=True)
                fill_value = mode_values.iloc[0] if not mode_values.empty else "Unknown"
                cleaned[column] = cleaned[column].fillna(fill_value)
                self.actions.append(
                    f"Filled {missing} missing value(s) in '{column}' "
                    f"with the most common value ('{fill_value}')."
                )

        # 4. Standardise common text categories (case and surrounding spaces).
        for column in cleaned.select_dtypes(include=["object"]).columns:
            cleaned[column] = cleaned[column].apply(
                lambda value: value.title() if isinstance(value, str) else value
            )

        # 5. Convert columns that look like dates.
        for column in cleaned.columns:
            if "date" in column.lower():
                def parse_date(value):
                    if pd.isna(value) or str(value).strip() == "":
                        return pd.NaT
                    value = str(value).strip()
                    for date_format in ("%Y/%m/%d", "%Y-%m-%d", "%d-%m-%Y"):
                        try:
                            return pd.to_datetime(value, format=date_format)
                        except (ValueError, TypeError):
                            pass
                    return pd.NaT

                converted = cleaned[column].apply(parse_date)
                if converted.notna().any():
                    cleaned[column] = converted.dt.strftime("%Y-%m-%d").fillna("Unknown")
                    self.actions.append(f"Standardised date format in '{column}'.")

        if not self.actions:
            self.actions.append("No cleaning was needed. The data already looks clean.")

        return cleaned

    def create_report(self, original, cleaned, output_file):
        """Save a text report describing the work done by the agent."""
        report_file = Path(output_file).with_name("cleaning_report.txt")
        lines = [
            "DATA CLEANING AGENT - REPORT",
            "=" * 34,
            f"Input file: {self.input_file.name}",
            f"Original rows: {len(original)}",
            f"Cleaned rows: {len(cleaned)}",
            f"Number of columns: {len(cleaned.columns)}",
            "",
            "Actions performed:"
        ]
        lines.extend(f"- {action}" for action in self.actions)
        lines += ["", "Missing values after cleaning:"]
        lines.extend(
            f"- {column}: {int(cleaned[column].isna().sum())}"
            for column in cleaned.columns
        )
        report_file.write_text("\n".join(lines), encoding="utf-8")
        return report_file

    def run(self):
        original = self.load_data()
        cleaned = self.clean_data(original)

        output_file = self.input_file.with_name("cleaned_output.csv")
        cleaned.to_csv(output_file, index=False)

        report_file = self.create_report(original, cleaned, output_file)

        print("\nDATA CLEANING AGENT")
        print("-------------------")
        print(f"Input rows : {len(original)}")
        print(f"Output rows: {len(cleaned)}")
        print("\nActions performed:")
        for action in self.actions:
            print(f"- {action}")
        print(f"\nCleaned file saved as: {output_file}")
        print(f"Report saved as      : {report_file}")
        print("\nPreview of cleaned data:")
        print(cleaned.to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python data_cleaning_agent.py <input_csv_file>")
        sys.exit(1)

    try:
        agent = DataCleaningAgent(sys.argv[1])
        agent.run()
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)
