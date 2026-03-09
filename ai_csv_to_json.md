# AI-Augmented Task — CSV to JSON Converter with Auto Delimiter Detection

---

## 1. Prompt Used

"Write a Python script that reads a CSV file, automatically detects the
delimiter (comma, tab, semicolon, or pipe), and converts the CSV into a
properly formatted JSON file."

---

## 2. AI-Generated Output
```python
import csv
import json

def csv_to_json(csv_filepath, json_filepath):
    with open(csv_filepath, 'r') as f:
        sample = f.read(1024)
        dialect = csv.Sniffer().sniff(sample)
        f.seek(0)
        reader = csv.DictReader(f, dialect=dialect)
        rows = list(reader)
    
    with open(json_filepath, 'w') as f:
        json.dump(rows, f, indent=2)
    
    print(f"Converted {len(rows)} rows to {json_filepath}")

csv_to_json("data.csv", "output.json")
```

---

## 3. Testing the AI Code

### Test 1 — comma delimited (data1.csv)
Input:
```
date,product,qty,price
2026-03-01,Laptop,2,65000
2026-03-01,Mouse,5,800
```
Result: Detected comma correctly, JSON output was valid.

### Test 2 — pipe delimited (data_pipe.csv)
Input:
```
date|product|qty|price
2026-03-01|Laptop|2|65000
2026-03-01|Mouse|5|800
```
Result: csv.Sniffer() detected pipe correctly, JSON output was valid.

---

## 4. Critical Evaluation (200 words)

The AI solution correctly used csv.Sniffer() to auto-detect the delimiter,
which is the right approach. DictReader was also a good choice as it maps
each row to a dict automatically, producing clean JSON output. For simple,
well-formed CSV files the script works reliably.

However several weaknesses exist. The script does not specify encoding,
which causes crashes on files containing non-ASCII characters such as
accented names or currency symbols. Both open() calls are missing
newline="" which can produce blank rows on Windows. There is no edge case
handling — an empty file causes DictReader to return no rows silently with
no warning to the user. If csv.Sniffer() cannot detect the delimiter it
raises a csv.Error exception that is never caught, crashing the script
without a helpful message. The output JSON contains all values as strings
since CSV has no type information — numeric fields like qty and price are
not converted to integers or floats, reducing the usefulness of the JSON.
Finally there are no type hints or docstrings, making the code hard to
maintain or extend.

The improved version below addresses all of these issues.

---

## 5. Improved Version
```python
import csv
import json
from pathlib import Path


FALLBACK_DELIMITER = ","
NUMERIC_FIELDS     = {"qty", "price"}


def detect_delimiter(file_path: Path) -> str:
    """
    Detects the delimiter of a CSV file using csv.Sniffer().
    Falls back to comma if detection fails.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Single character delimiter string.
    """
    with open(file_path, "r", newline="", encoding="utf-8") as f:
        sample = f.read(2048)
    try:
        dialect = csv.Sniffer().sniff(
            sample,
            delimiters=",\t;|"
        )
        return dialect.delimiter
    except csv.Error:
        print(f"  Could not detect delimiter, falling back to '{FALLBACK_DELIMITER}'.")
        return FALLBACK_DELIMITER


def cast_row(row: dict) -> dict:
    """
    Converts numeric string values to int or float where appropriate.

    Args:
        row: A dict representing one CSV row.

    Returns:
        Row dict with numeric fields cast to correct types.
    """
    result = {}
    for key, value in row.items():
        if key in NUMERIC_FIELDS:
            try:
                result[key] = int(value)
            except ValueError:
                try:
                    result[key] = float(value)
                except ValueError:
                    result[key] = value
        else:
            result[key] = value
    return result


def csv_to_json(csv_path: str, json_path: str) -> int:
    """
    Reads a CSV file with auto-detected delimiter and writes it as JSON.

    Args:
        csv_path: Path to the input CSV file.
        json_path: Path to write the output JSON file.

    Returns:
        Number of rows written to the JSON file.
        Returns 0 if the file is empty or does not exist.

    Raises:
        FileNotFoundError: If the CSV file does not exist.

    Example:
        >>> csv_to_json("data/data1.csv", "output/data1.json")
        8
    """
    source = Path(csv_path)

    if not source.exists():
        raise FileNotFoundError(f"CSV file not found: '{csv_path}'")

    delimiter = detect_delimiter(source)
    print(f"  Detected delimiter: '{delimiter}'")

    with open(source, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows   = [cast_row(row) for row in reader]

    if not rows:
        print(f"  Warning: '{csv_path}' contains no data rows.")
        return 0

    output = Path(json_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"  Converted {len(rows)} rows from '{source.name}' -> '{output.name}'")
    return len(rows)


if __name__ == "__main__":
    csv_to_json("data/data1.csv", "output/data1.json")
    csv_to_json("data/data2.csv", "output/data2.json")
```

---

## 6. Improvements Summary

| Issue | AI Code | Improved Version |
|-------|---------|-----------------|
| Encoding | Not specified, crashes on non-ASCII | utf-8 specified on all open() calls |
| newline= | Missing, blank rows on Windows | newline="" on all CSV open() calls |
| Sniffer failure | Unhandled csv.Error crash | try/except with comma fallback |
| Empty file | Silent, no warning | Explicit warning returned to caller |
| Numeric types | All values stay as strings | cast_row() converts qty and price |
| Missing file | Unhandled crash | FileNotFoundError raised with message |
| Type hints | None | Full type hints on all functions |
| Docstrings | None | Google-style docstrings throughout |
