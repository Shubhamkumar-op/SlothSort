
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
st.caption("Local AI-powered file organization with human approval.")

st.info(
    "SlothSort uses local Ollama AI to classify file metadata. "
    "Review the plan before approving any file movement."
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FOLDERS = {
    "Demo Files": (PROJECT_ROOT / "demo_data").resolve(),
    "Sample Test Files": (
        PROJECT_ROOT / "sample_data" / "test_files"
    ).resolve(),
}

st.subheader("1. Choose a folder")

folder_label = st.selectbox(
    "Folder to scan",
    list(FOLDERS.keys()),
)

selected_folder = FOLDERS[folder_label]

st.code(str(selected_folder))

if not selected_folder.is_dir():
    st.error("Selected folder does not exist.")
    st.stop()

if (
    "slothsort_root" in st.session_state
    and st.session_state["slothsort_root"] != str(selected_folder)
):
    st.session_state.pop("slothsort_preview", None)
    st.session_state.pop("slothsort_root", None)

if st.button("Scan and Generate Plan", type="primary"):
    st.session_state.pop("slothsort_preview", None)
    st.session_state.pop("slothsort_root", None)

    try:
        with st.spinner("Scanning files and asking local Gemma..."):
            files = scan_folder(str(selected_folder))

            usable_files = [
                item for item in files
                if "error" not in item
            ]

            if not usable_files:
                st.warning(
                    "No eligible files found. Add files directly "
                    "inside the selected folder and scan again."
                )
                st.stop()

            plans = []

            progress = st.progress(0)

            for index, file_info in enumerate(usable_files):
                plans.append(plan_file(file_info))
                progress.progress((index + 1) / len(usable_files))

            preview = build_organization_plan(
                str(selected_folder),
                usable_files,
                plans,
            )

            st.session_state["slothsort_preview"] = preview
            st.session_state["slothsort_root"] = str(selected_folder)

            progress.empty()

    except Exception as error:
        st.error(f"Could not generate plan: {error}")


preview = st.session_state.get("slothsort_preview")

if preview and st.session_state.get("slothsort_root") == str(selected_folder):
    st.subheader("2. Review the organization plan")

    st.warning(
        "Review all proposed paths. Existing destinations and "
        "duplicate destinations are treated as conflicts."
    )

    rows = []

    for item in preview:
        rows.append({
            "Source": str(Path(item["source"]).relative_to(selected_folder)),
            "Destination": str(
                Path(item["destination"]).relative_to(selected_folder)
            ),
            "Category": item["category"],
            "Status": item["status"],
            "Reason": item["reason"],
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)

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
        st.error("Resolve all conflicts and generate a fresh plan.")

    confirmed = st.checkbox(
        f"I reviewed the plan and approve moving files only inside "
        f"the {folder_label} folder."
    )

    if st.button(
        "Approve and Organize",
        type="primary",
        disabled=not confirmed or not ready_items or bool(conflicts),
    ):
        try:
            with st.spinner("Revalidating and organizing files..."):
                result = execute_organization_plan(
                    str(selected_folder),
                    preview,
                    approved=True,
                )

            st.session_state.pop("slothsort_preview", None)
            st.session_state.pop("slothsort_root", None)

            if result["status"] == "completed":
                st.success(
                    f"Organization complete! {len(result['moved'])} file(s) moved."
                )
            else:
                st.warning(f"Execution status: {result['status']}")

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
st.caption("SlothSort MVP · Local Gemma · Human-approved file operations")
