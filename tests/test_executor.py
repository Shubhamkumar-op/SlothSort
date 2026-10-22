
from pathlib import Path

import pytest

from src.executor import (
    build_organization_plan,
    execute_organization_plan,
)


def test_execution_requires_approval(tmp_path):
    source = tmp_path / "notes.txt"
    source.write_text("Hello SlothSort")

    result = execute_organization_plan(
        str(tmp_path),
        [],
        approved=False,
    )

    assert result["status"] == "approval_required"
    assert result["moved"] == []
    assert source.exists()


def test_preview_marks_existing_destination_as_conflict(tmp_path):
    source = tmp_path / "notes.txt"
    source.write_text("Hello")

    documents = tmp_path / "Documents"
    documents.mkdir()

    destination = documents / "notes.txt"
    destination.write_text("Keep this file")

    files = [{
        "name": "notes.txt",
        "extension": ".txt",
        "relative_path": "notes.txt",
        "size_bytes": 5,
    }]

    plans = [{
        "category": "Documents",
        "suggested_folder": "Documents",
        "suggested_name": "notes.txt",
        "reason": "Text document",
    }]

    preview = build_organization_plan(
        str(tmp_path),
        files,
        plans,
    )

    assert len(preview) == 1
    assert preview[0]["status"] == "conflict"
    assert destination.read_text() == "Keep this file"
    assert source.exists()


def test_invalid_category_is_rejected(tmp_path):
    source = tmp_path / "notes.txt"
    source.write_text("Hello")

    files = [{
        "name": "notes.txt",
        "extension": ".txt",
        "relative_path": "notes.txt",
        "size_bytes": 5,
    }]

    plans = [{
        "category": "../outside",
        "suggested_folder": "../outside",
        "suggested_name": "notes.txt",
        "reason": "Invalid test",
    }]

    with pytest.raises(ValueError):
        build_organization_plan(
            str(tmp_path),
            files,
            plans,
        )


def test_successful_move_after_approval_in_sample_folder(
    tmp_path, monkeypatch
):
    project_root = tmp_path / "project"
    sample_folder = project_root / "sample_data" / "test_files"
    sample_folder.mkdir(parents=True)

    source = sample_folder / "notes.txt"
    source.write_text("Hello SlothSort")

    destination = sample_folder / "Documents" / "notes.txt"

    monkeypatch.chdir(project_root)

    preview = [{
        "source": str(source),
        "destination": str(destination),
        "category": "Documents",
        "reason": "Text document",
        "status": "ready_for_review",
    }]

    result = execute_organization_plan(
        str(sample_folder),
        preview,
        approved=True,
    )

    assert result["status"] == "completed"
    assert len(result["moved"]) == 1
    assert not source.exists()
    assert destination.read_text() == "Hello SlothSort"
    assert (sample_folder / "slothsort_audit.jsonl").exists()


def test_preview_rejects_path_traversal(tmp_path):
    source = tmp_path / "notes.txt"
    source.write_text("Hello")

    files = [{
        "name": "notes.txt",
        "extension": ".txt",
        "relative_path": "../notes.txt",
        "size_bytes": 5,
    }]

    plans = [{
        "category": "Documents",
        "suggested_folder": "Documents",
        "suggested_name": "notes.txt",
        "reason": "Text document",
    }]

    with pytest.raises(ValueError):
        build_organization_plan(
            str(tmp_path),
            files,
            plans,
        )
