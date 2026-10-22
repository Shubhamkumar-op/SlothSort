# 🦥 SlothSort — Local AI File Organizer

SlothSort is a local AI-powered file organization tool that helps users classify files and preview suggested destinations before moving them. It uses a locally running Ollama model and requires human approval before file operations.

## ✨ Features

- **File scanning:** Detects eligible files and collects metadata such as filename, extension, size, and modification time.
- **SHA-256 hashing:** Calculates file hashes without loading the entire file into memory.
- **Local AI classification:** Uses Ollama with the `gemma3:4b` model to suggest file categories and filenames.
- **Organization preview:** Shows proposed source and destination paths before any move.
- **Human approval:** Requires explicit approval before executing file operations.
- **Conflict detection:** Identifies existing destinations rather than intentionally overwriting them.
- **Path validation:** Rejects invalid categories and unsafe relative paths.
- **Audit logging:** Records file operation outcomes in a JSON Lines audit log.
- **Streamlit dashboard:** Provides a simple interface for reviewing organization plans.
- **Automated tests:** Includes scanner and executor tests using `pytest`.

## 🧰 Tech Stack

- Python 3.13
- Streamlit
- Ollama
- Gemma 3 (`gemma3:4b`)
- Requests
- Pytest

## 🏗️ Project Structure

```text
SlothSort/
├── src/
│   ├── app.py
│   ├── scanner.py
│   ├── ai_planner.py
│   └── executor.py
├── tests/
│   ├── test_scanner.py
│   └── test_executor.py
├── sample_data/
│   └── test_files/
├── test_scanner_manual.py
├── test_ai_planner_manual.py
├── test_combined_planner.py
├── test_executor_manual.py
├── .gitignore
├── LICENSE
└── README.md
```

## ⚙️ Prerequisites

Install Python and [Ollama](https://ollama.com/). You need the Gemma model available locally.

Pull the model:

```powershell
ollama pull gemma3:4b
```

Ensure Ollama is running before using AI classification.

## 🚀 Installation

Clone the repository and enter its directory:

```powershell
git clone YOUR_REPOSITORY_URL
cd SlothSort
```

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install streamlit requests pytest
```

## ▶️ Run the Dashboard

From the project root, run:

```powershell
python -m streamlit run src/app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

The current MVP operates only on `sample_data/test_files`.

## 🧪 Run Tests

Run the automated test suite:

```powershell
python -m pytest tests/ -v
```

The current test suite contains 10 tests covering scanner behavior, hashing, approval requirements, destination conflicts, category validation, path traversal rejection, and an approved move in a temporary test directory.

## 🔒 Safety Design

- The dashboard is restricted to the sample-data directory.
- The AI receives file metadata rather than file contents.
- Suggested categories and filenames are validated.
- Existing destinations are treated as conflicts.
- Execution requires explicit approval.
- Tests use temporary directories for isolated file-movement checks.

**Important:** This is an MVP. Review every proposed operation before approving it. File-operation safeguards should be tested further before using the tool on important personal data.

## 🛣️ Future Improvements

- Add more executor security tests.
- Improve error handling and recovery for interrupted file operations.
- Add configurable folder selection with clear safety boundaries.
- Improve the dashboard with filters and richer file metadata.
- Add CI with automated tests on every pull request.

## 👨‍💻 Project Status

SlothSort is an actively developed portfolio project focused on local AI, file-system automation, and human-in-the-loop safety.

## 📄 License

See the repository's `LICENSE` file for license terms.
