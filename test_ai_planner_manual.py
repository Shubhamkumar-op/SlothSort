
from src.ai_planner import plan_file

file_info = {
    "name": "lecture_notes.pdf",
    "extension": ".pdf",
    "relative_path": "lecture_notes.pdf",
    "size_bytes": 20480,
    "modified_time": "2026-10-21T10:00:00",
}

try:
    result = plan_file(file_info)
    print("AI planning successful!")
    print(result)
except Exception as error:
    print("AI planning failed:", error)
