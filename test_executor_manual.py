
from pathlib import Path

from src.scanner import scan_folder
from src.ai_planner import plan_file
from src.executor import (
    build_organization_plan,
    execute_organization_plan,
)


folder = Path("sample_data/test_files").resolve()

files = scan_folder(str(folder))
plans = []

for file_info in files:
    if "error" in file_info:
        raise RuntimeError(f"Scanner error: {file_info}")

    plans.append(plan_file(file_info))

preview = build_organization_plan(
    str(folder),
    files,
    plans,
)

print("\nORGANIZATION PREVIEW")
for item in preview:
    print(
        f"{item['source']} -> {item['destination']} "
        f"[{item['status']}]"
    )

# Verify that execution is blocked without approval.
blocked = execute_organization_plan(
    str(folder),
    preview,
    approved=False,
)

print("\nWithout approval:", blocked["status"])

if blocked["status"] != "approval_required":
    raise AssertionError("Executor should require approval")

print("\nThis test will move files only inside sample_data/test_files.")
approval = input("Type YES to approve these moves: ").strip()

if approval != "YES":
    print("Cancelled. No files were moved.")
else:
    result = execute_organization_plan(
        str(folder),
        preview,
        approved=True,
    )

    print("\nExecution result:", result["status"])
    print("Files moved:", len(result["moved"]))
    print("Errors:", result["errors"])
    print("Audit log:", folder / "slothsort_audit.jsonl")
