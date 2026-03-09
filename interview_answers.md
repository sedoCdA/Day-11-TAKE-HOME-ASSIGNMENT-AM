# Interview Answers — Day 11 AM (File Handling, CSV, JSON, pathlib)

---

## Q1 — json.load() vs json.loads()

### json.load()
Reads JSON from a **file object**.
Used when your JSON data is stored in a file on disk.
The function reads and parses the file directly.
```python
import json

with open("revenue_summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data["metadata"]["total_revenue"])
```

Real-world use: Reading a config file, loading a saved report,
reading an API response that was saved to disk.

### json.loads()
Parses JSON from a **string** already in memory.
The "s" stands for "string".
Used when you receive JSON as text, not as a file.
```python
import json

response_text = '{"status": "ok", "code": 200}'
data = json.loads(response_text)

print(data["status"])
```

Real-world use: Parsing the body of an HTTP API response,
processing a JSON string received from a message queue or websocket,
or reading JSON that was stored as a string in a database column.

### Summary

| Function | Input | When to use |
|----------|-------|-------------|
| json.load() | File object | JSON is in a file on disk |
| json.loads() | String | JSON is already in memory as text |

---

## Q2 — find_large_files()
```python
from pathlib import Path


def find_large_files(
    directory: str,
    size_mb: float
) -> list[tuple[str, float]]:
    """
    Recursively finds all files larger than size_mb megabytes.

    Args:
        directory: Root directory to search recursively.
        size_mb: Minimum file size threshold in megabytes.

    Returns:
        List of (filename, size_in_mb) tuples sorted by size descending.
        Returns empty list if directory does not exist or no files match.

    Example:
        >>> find_large_files("/home/user/data", 10)
        [("bigfile.csv", 45.2), ("report.json", 12.1)]
    """
    root = Path(directory)

    if not root.exists():
        print(f"Directory '{directory}' does not exist.")
        return []

    threshold_bytes = size_mb * 1024 * 1024

    results = [
        (f.name, round(f.stat().st_size / (1024 * 1024), 2))
        for f in root.rglob("*")
        if f.is_file() and f.stat().st_size > threshold_bytes
    ]

    return sorted(results, key=lambda x: x[1], reverse=True)


# Tests
matches = find_large_files("data", 0.001)
for name, size in matches:
    print(f"  {name}: {size} MB")

print(find_large_files("nonexistent_dir", 10))
```

---

## Q3 — Debug Problem

### Buggy code
```python
def merge_csv_files(file_list):
    all_data = []
    for filename in file_list:
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                all_data.append(row)

    with open("merged.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(all_data)

    return len(all_data)
```

### Bug 1 — Missing import

`csv` is used but never imported.
Python raises a `NameError: name 'csv' is not defined` immediately.

Fix:
```python
import csv
```

### Bug 2 — Missing newline='' on Windows

When opening CSV files without `newline=""`, Python's universal newline
mode adds an extra blank row between every data row on Windows.
The csv module requires direct control over newlines itself.

Fix: add `newline=""` to every `open()` call that reads or writes CSV.
```python
with open(filename, "r", newline="", encoding="utf-8") as f:
```

### Bug 3 — Header row duplicated from every file

`csv.reader` includes the header row as a regular row.
When multiple files are merged, each file contributes its own header,
resulting in the header appearing once per file in the output.

Fix: skip the header for every file after the first one, or use
`csv.DictReader` which handles headers automatically.

### Fully fixed version
```python
import csv


def merge_csv_files(file_list: list[str]) -> int:
    """
    Merges multiple CSV files into a single merged.csv file.
    Skips duplicate header rows from each file after the first.

    Args:
        file_list: List of CSV file paths to merge.

    Returns:
        Total number of data rows written (excluding header).
    """
    all_data = []
    header   = None

    for filename in file_list:
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows   = list(reader)
            if not rows:
                continue
            if header is None:
                header = rows[0]
            all_data.extend(rows[1:])

    with open("merged.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(all_data)

    return len(all_data)
