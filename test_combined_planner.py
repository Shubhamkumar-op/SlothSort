
from src.scanner import scan_folder
from src.ai_planner import plan_file


FOLDER = "sample_data/test_files"


def main():
    files = scan_folder(FOLDER)

    print(f"\nFiles found: {len(files)}")
    print("-" * 60)

    for file_info in files:
        if "error" in file_info:
            print(f"Skipped {file_info['name']}: {file_info['error']}")
            continue

        print(f"\nPlanning: {file_info['name']}")

        try:
            plan = plan_file(file_info)

            print(f"Category: {plan['category']}")
            print(f"Suggested name: {plan['suggested_name']}")
            print(f"Suggested folder: {plan['suggested_folder']}")
            print(f"Reason: {plan['reason']}")

        except Exception as error:
            print(f"Planning failed: {error}")

    print("\nPlanning finished. No files were modified.")


if __name__ == "__main__":
    main()
