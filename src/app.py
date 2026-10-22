
import streamlit as st
from pathlib import Path

from src.scanner import scan_folder
from src.ai_planner import plan_file
from src.executor import (
    build_organization_plan,
    execute_organization_plan,
)


st.set_page_config(
    page_title="SlothSort AI",
    page_icon="🦥",
    layout="wide",
)

st.title("🦥 SlothSort AI")
st.caption(
    "Local AI-powered file organization with human approval."
)

st.info(
    "Files are analyzed using local Ollama. "
    "No files are moved until you explicitly approve the plan."
)

# MVP safety boundary: operate only on the sample folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FOLDER = (
    PROJECT_ROOT / "sample_data" / "test_files"
).resolve()

st.subheader("1. Selected folder")
st.code(str(SAMPLE_FOLDER))

if not SAMPLE_FOLDER.is_dir():
    st.error("Sample folder does not exist.")
    st.stop()


if st.button("Scan and Generate Plan", type="primary"):
    # Always discard an old plan before generating a new one.
    st.session_state.pop("slothsort_preview", None)
    st.session_state.pop("slothsort_root", None)

    try:
        with st.spinner("Scanning files and asking local Gemma..."):
            files = scan_folder(str(SAMPLE_FOLDER))

            usable_files = [
                item for item in files
                if "error" not in item
            ]

            if not usable_files:
                st.warning(
                    "No eligible files found. "
                    "Place a new test file directly in "
                    "sample_data/test_files and scan again."
                )
                st.stop()

            plans = []

            progress = st.progress(0)

            for index, file_info in enumerate(usable_files):
                plans.append(plan_file(file_info))
                progress.progress(
                    (index + 1) / len(usable_files)
                )

            preview = build_organization_plan(
                str(SAMPLE_FOLDER),
                usable_files,
                plans,
            )

            st.session_state["slothsort_preview"] = preview
            st.session_state["slothsort_root"] = str(
                SAMPLE_FOLDER
            )

            progress.empty()

    except Exception as error:
        st.error(f"Could not generate plan: {error}")


preview = st.session_state.get("slothsort_preview")

if preview:
    st.subheader("2. Review the organization plan")

    st.warning(
        "Review every source and destination carefully. "
        "Existing destinations are conflicts and must not "
        "be overwritten."
    )

    table_rows = []

    for item in preview:
        try:
            destination_display = str(
                Path(item["destination"]).relative_to(SAMPLE_FOLDER)
            )
        except ValueError:
            destination_display = item["destination"]

        table_rows.append({
            "Source": str(
                Path(item["source"]).relative_to(SAMPLE_FOLDER)
            ),
            "Destination": destination_display,
            "Category": item["category"],
            "Status": item["status"],
            "Reason": item["reason"],
        })

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )

    ready_items = [
        item for item in preview
        if item["status"] == "ready_for_review"
    ]

    conflicts = [
        item for item in preview
        if item["status"] == "conflict"
    ]

    already_in_place = [
        item for item in preview
        if item["status"] == "already_in_place"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric("Ready for review", len(ready_items))
    col2.metric("Conflicts", len(conflicts))
    col3.metric("Already organized", len(already_in_place))

    if conflicts:
        st.error(
            "Conflicts detected. No organization will be allowed "
            "until the conflicts are resolved and a fresh plan "
            "is generated."
        )

    if already_in_place:
        st.info(
            "Some files are already at their suggested destination "
            "and will not be moved."
        )

    confirmed = st.checkbox(
        "I reviewed the complete plan and approve moving "
        "the eligible files inside sample_data/test_files."
    )

    can_execute = (
        confirmed
        and bool(ready_items)
        and not conflicts
    )

    if st.button(
        "Approve and Organize",
        type="primary",
        disabled=not can_execute,
    ):
        try:
            with st.spinner(
                "Revalidating and organizing files..."
            ):
                result = execute_organization_plan(
                    st.session_state["slothsort_root"],
                    preview,
                    approved=True,
                )

            st.session_state.pop("slothsort_preview", None)
            st.session_state.pop("slothsort_root", None)

            if result["status"] == "completed":
                st.success(
                    f"Organization complete! "
                    f"{len(result['moved'])} file(s) moved."
                )
            else:
                st.warning(
                    f"Execution finished with status: "
                    f"{result['status']}"
                )

            if result["errors"]:
                st.subheader("Execution errors")
                st.json(result["errors"])

            if result["moved"]:
                st.subheader("Successful moves")
                st.json(result["moved"])

            st.rerun()

        except Exception as error:
            st.error(f"Execution failed: {error}")

    if st.button("Discard Preview"):
        st.session_state.pop("slothsort_preview", None)
        st.session_state.pop("slothsort_root", None)
        st.rerun()


st.divider()

st.caption(
    "SlothSort MVP · Local Gemma · Human-approved file operations"
)
