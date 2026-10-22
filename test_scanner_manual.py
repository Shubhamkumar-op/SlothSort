
from pathlib import Path
from src.scanner import scan_folder


folder = Path("sample_data/test_files").resolve()
files = scan_folder(str(folder))

print("\nSCANNER RESULTS")
print("-" * 40)

for file in files:
    print(file["relative_path"])

print("-" * 40)

assert all(
    file["name"] != "slothsort_audit.jsonl"
    for file in files
), "Audit log should not be scanned"

assert all(
    Path(file["relative_path"]).parts[0]
    not in {"Code", "Documents", "Images", "Archives",
            "Videos", "Audio", "Other"}
    for file in files
), "Organized folders should not be scanned"

print("SUCCESS: Internal files and organized folders are skipped.")
