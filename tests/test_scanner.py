
import pytest
from pathlib import Path

from src.scanner import scan_folder, calculate_file_hash


def test_scan_folder_finds_files(tmp_path):
    (tmp_path / "notes.txt").write_text("Hello")
    (tmp_path / "code.cpp").write_text("int main() {}")

    results = scan_folder(str(tmp_path))

    assert len(results) == 2
    assert {item["name"] for item in results} == {
        "notes.txt",
        "code.cpp",
    }


def test_scan_folder_reads_file_metadata(tmp_path):
    (tmp_path / "report.txt").write_text("Sample report")

    results = scan_folder(str(tmp_path))
    file_info = results[0]

    assert file_info["extension"] == ".txt"
    assert file_info["relative_path"] == "report.txt"
    assert file_info["size_bytes"] == len("Sample report")


def test_hash_is_same_for_identical_content(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"

    file_a.write_text("Same content")
    file_b.write_text("Same content")

    assert calculate_file_hash(file_a) == calculate_file_hash(file_b)


def test_hash_differs_for_different_content(tmp_path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"

    file_a.write_text("First file")
    file_b.write_text("Second file")

    assert calculate_file_hash(file_a) != calculate_file_hash(file_b)


def test_nonexistent_folder_raises_error(tmp_path):
    missing_folder = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        scan_folder(str(missing_folder))
