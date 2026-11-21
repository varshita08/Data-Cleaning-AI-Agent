# Data Cleaning AI Agent

## About the project
This is a small Python-based data cleaning agent for CSV files. It checks the data and applies suitable cleaning rules automatically.

## Features
- Removes duplicate rows.
- Removes extra spaces from text.
- Fills missing numeric values using the median.
- Fills missing text values using the most common value.
- Standardises text capitalization.
- Standardises columns whose names contain `date`.
- Saves a cleaned CSV file and a cleaning report.

## Requirements
- Python 3.9 or later
- pandas

Install the library:
```bash
pip install -r requirements.txt
```

## Run the project
Keep your CSV file in this folder and run:
```bash
python data_cleaning_agent.py sample_input.csv
```

The program creates:
- `cleaned_output.csv`
- `cleaning_report.txt`

## Note
This is a beginner-friendly rule-based intelligent agent. It selects cleaning actions by inspecting the column type and the values present. It does not use a paid AI API or train a machine-learning model.
