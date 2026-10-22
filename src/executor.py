
from pathlib import Path
import json
import os
import shutil
from datetime import datetime, timezone


ALLOWED_CATEGORIES = {
    "Documents",
    "Images",
    "Code",
    "Archives",
    "Videos",
    "Audio",
    "Other",
}


def build_organization_plan(root_folder, files, plans):
    """Build a read-only organization preview."""

    root = Path(root_folder).resolve(strict=True)

    if not root.is_dir():
        raise NotADirectoryError(str(root))

    if len(files) != len(plans):
        raise ValueError("Each file must have exactly one plan")

    preview = []
    reserved = set()

    for info, plan in zip(files, plans):
        if "error" in info:
            raise ValueError(f"Scan error: {info}")

        relative = Path(info["relative_path"])

        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe source path")

        source = root / relative

        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Invalid source file: {source}")

        source = source.resolve(strict=True)

        if not source.is_relative_to(root):
            raise ValueError("Source outside selected folder")

        category = plan.get("category")
        folder = plan.get("suggested_folder")
        name = plan.get("suggested_name")

        if category not in ALLOWED_CATEGORIES or folder != category:
            raise ValueError("Invalid category or folder")

        if (
            not isinstance(name, str)
            or not name.strip()
            or name in {".", ".."}
            or any(c in name for c in ("/", "\\", ":", "\x00"))
        ):
            raise ValueError("Invalid filename")

        extension = info.get("extension", "")

        if extension not in {"", "[no extension]"}:
            if not name.lower().endswith(extension.lower()):
                raise ValueError("Original extension must be preserved")

        destination = root / folder / name
        destination = destination.parent.resolve() / destination.name

        if not destination.is_relative_to(root):
            raise ValueError("Destination outside selected folder")

        if destination == source:
            status = "already_in_place"
        elif destination.exists() or destination.is_symlink():
            status = "conflict"
        else:
            status = "ready_for_review"

        key = os.path.normcase(str(destination))

        if key in reserved:
            status = "conflict"

        reserved.add(key)

        preview.append({
            "source": str(source),
            "destination": str(destination),
            "category": category,
            "reason": str(plan.get("reason", ""))[:300],
            "status": status,
        })

    return preview


def execute_organization_plan(root_folder, preview, approved=False):
    """Move approved files only within a recognized project test folder."""

    if approved is not True:
        return {
            "status": "approval_required",
            "moved": [],
            "errors": [],
        }

    root = Path(root_folder).resolve(strict=True)
    project_root = Path(__file__).resolve().parent.parent

    allowed_roots = {
        (project_root / "sample_data" / "test_files").resolve(),
        (project_root / "demo_data").resolve(),
    }

    if root not in allowed_roots or not root.is_dir():
        raise ValueError("Execution is restricted to project demo folders")

    moved = []
    errors = []
    audit_path = root / "slothsort_audit.jsonl"

    for item in preview:
        if item.get("status") == "already_in_place":
            continue

        source = Path(item["source"])
        destination = Path(item["destination"])
        created_destination = False
        record = None

        try:
            if item.get("status") != "ready_for_review":
                raise ValueError("Item is not ready for execution")

            if not source.is_relative_to(root):
                raise ValueError("Source outside allowed folder")

            if not destination.is_relative_to(root):
                raise ValueError("Destination outside allowed folder")

            if source.is_symlink() or not source.is_file():
                raise ValueError("Source is missing or invalid")

            if destination.is_symlink() or destination.exists():
                raise FileExistsError(f"Destination exists: {destination}")

            destination.parent.mkdir(parents=True, exist_ok=True)

            fd = os.open(
                destination,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            created_destination = True

            try:
                with os.fdopen(fd, "wb") as target:
                    with source.open("rb") as original:
                        shutil.copyfileobj(original, target)
                    target.flush()
                    os.fsync(target.fileno())

                source.unlink()

            except Exception:
                destination.unlink(missing_ok=True)
                created_destination = False
                raise

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "move",
                "source": str(source),
                "destination": str(destination),
                "result": "success",
            }
            moved.append(record)

        except Exception as error:
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": str(source),
                "destination": str(destination),
                "result": "failed",
                "error": str(error),
            }
            errors.append(record)

            if created_destination and source.exists():
                destination.unlink(missing_ok=True)

        finally:
            if record is not None:
                with audit_path.open("a", encoding="utf-8") as log:
                    log.write(json.dumps(record) + "\n")

    return {
        "status": "completed" if not errors else "completed_with_errors",
        "moved": moved,
        "errors": errors,
    }
