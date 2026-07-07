import json
from pathlib import Path

import streamlit as st

from utils.annotation import (
    DEMO_FILENAME,
    current_label,
    filter_for_annotator,
    go_to,
    list_raw_json_files,
    load_json,
    matching_annotator_letter,
    pending_indices,
    record_annotation,
    reset_annotations,
    restore_progress,
    to_list,
)

st.set_page_config(page_title="Annotation Tool", page_icon="🏷️", layout="wide")


def _load_css(path: str) -> None:
    css = Path(path).read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_load_css("assets/styles.css")

for _k, _v in [
    ("df", None),
    ("filename", None),
    ("display_name", None),
    ("current_idx", None),
    ("instructions_ack", False),
    ("annotator_id", None),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


def _start_annotating(df, filename, display_name) -> None:
    annotator_id = st.session_state.annotator_id
    df = filter_for_annotator(df, annotator_id)
    df = restore_progress(df, filename, annotator_id)
    st.session_state.df = df
    st.session_state.filename = filename
    st.session_state.display_name = display_name
    pending = pending_indices(df, annotator_id)
    st.session_state.current_idx = pending[0] if pending else (df.index[0] if len(df) else None)
    st.rerun()


def _dataset_labels(paths: list[Path]) -> dict[Path, str]:
    return {
        p: (f"Mock contrast set" if p.name == DEMO_FILENAME else p.name)
        for p in paths
    }


def _reset_to_login() -> None:
    st.session_state.annotator_id = None
    st.session_state.df = None
    st.session_state.filename = None
    st.session_state.display_name = None
    st.session_state.current_idx = None


def _reset_to_dataset_selection() -> None:
    st.session_state.df = None
    st.session_state.filename = None
    st.session_state.display_name = None
    st.session_state.current_idx = None


# ── Instructions screen ─────────────────────────────────────────────────────────
if not st.session_state.instructions_ack:
    instructions_path = Path("instructions.md")
    instructions_text = instructions_path.read_text().strip()
    if instructions_text:
        st.markdown(instructions_text)
    else:
        st.title("🏷️ Annotation Tool — Instructions")
        st.warning("instructions.md is empty. Add annotation guidelines there before annotators start.")
    ack = st.checkbox("I have read and understood the instructions above.")
    if st.button("Continue to annotation tool ➜"):
        if ack:
            st.session_state.instructions_ack = True
            st.rerun()
        else:
            st.error("Please check the box above to confirm you've read the instructions.")
    st.stop()


# ── Login screen ────────────────────────────────────────────────────────────────
if not st.session_state.annotator_id:
    st.title("🏷️ Annotation Tool")
    name = st.text_input("Enter your annotator name (A, B, C, or D)").strip().upper()
    if st.button("Continue ➜"):
        if name in {"A", "B", "C", "D"}:
            st.session_state.annotator_id = name
            st.rerun()
        else:
            st.error("Enter one of A, B, C, or D.")
    st.stop()


# ── Dataset selection screen ────────────────────────────────────────────────────
if st.session_state.df is None:
    top_l, top_r = st.columns([4, 1])
    with top_l:
        st.title("🏷️ Annotation Tool")
        st.caption(f"Logged in as **{st.session_state.annotator_id}**")
    with top_r:
        if st.button("Not you? Change annotator"):
            _reset_to_login()
            st.rerun()

    st.markdown("Choose a dataset below to start annotating, or upload your own file.")

    raw_files = list_raw_json_files()
    if raw_files:
        labels = _dataset_labels(raw_files)
        choice = st.selectbox("Available datasets", raw_files, format_func=lambda p: labels[p])
        if st.button("📂 Load selected dataset"):
            try:
                df = load_json(choice)
            except ValueError as e:
                st.error(str(e))
            else:
                _start_annotating(df, choice.name, labels[choice])
    else:
        st.info("No datasets are available right now.")

    st.markdown("---")
    uploaded = st.file_uploader("Or upload a .json file", type=["json"])
    if uploaded:
        expected_letter = matching_annotator_letter(uploaded.name)
        if expected_letter and expected_letter != st.session_state.annotator_id:
            st.error(
                f"This file is {uploaded.name} but you're logged in as "
                f"{st.session_state.annotator_id}."
            )
        else:
            try:
                df = load_json(uploaded)
            except ValueError as e:
                st.error(str(e))
            else:
                _start_annotating(df, uploaded.name, uploaded.name)

    st.stop()


# ── Annotation screen ──────────────────────────────────────────────────────────
df = st.session_state.df
annotator_id = st.session_state.annotator_id
total = len(df)
done_count = total - len(pending_indices(df, annotator_id))

# Top bar — title + action buttons
col_title, col_actions = st.columns([3, 2])
with col_title:
    st.title("🏷️ Annotation Tool")
    st.caption(f"📄 {st.session_state.display_name} · Annotator: **{annotator_id}**")

with col_actions:
    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
    btn_dl, btn_reset, btn_new = st.columns(3)
    with btn_dl:
        payload = json.dumps(to_list(df), indent=2).encode()
        download_name = f"{Path(st.session_state.filename).stem}_annotator_{annotator_id}.json"
        st.download_button(
            label="💾 Download annotations",
            data=payload,
            file_name=download_name,
            mime="application/json",
            use_container_width=True,
        )
    with btn_reset:
        if st.button("🔄 Start over", use_container_width=True):
            reset_annotations()
            st.rerun()
    with btn_new:
        if st.button("⬅ Back to dataset selection", use_container_width=True):
            _reset_to_dataset_selection()
            st.rerun()

st.caption("💾 Progress is autosaved as you annotate — reopening this dataset resumes where you left off. Still download your file when finished.")
if st.button("Not you? Change annotator", key="change_annotator_annotate"):
    _reset_to_login()
    st.rerun()

st.progress(done_count / total if total else 0)
st.markdown(f"**{done_count} / {total}** rows annotated")

if total == 0:
    st.warning(f"No rows in this dataset are assigned to annotator {annotator_id}.")
    st.stop()

if done_count == total:
    st.success("🎉 All rows annotated! Download your file with the button above.")
    st.stop()

# ── Active row ─────────────────────────────────────────────────────────────────
idx = st.session_state.current_idx
row = df.loc[idx]
pos = df.index.get_loc(idx)

st.markdown("---")

nav_prev, nav_pos, nav_next = st.columns([1, 3, 1])
with nav_prev:
    if st.button("⬅ Previous", use_container_width=True, disabled=pos == 0):
        go_to(-1)
        st.rerun()
with nav_pos:
    st.markdown(
        f"<div style='text-align:center'>Row {pos + 1} of {total}</div>",
        unsafe_allow_html=True,
    )
with nav_next:
    if st.button("Next ➡", use_container_width=True, disabled=pos == total - 1):
        go_to(1)
        st.rerun()

label = current_label(row, annotator_id)
st.markdown(f"**Question:** `{row.get('question') or '—'}`")
st.markdown(f"**Answer:** `{row.get('answer') or '—'}`")
st.markdown(f"**Current label:** {label or '_not yet annotated_'}")

st.markdown("---")

# Texts
left, right = st.columns(2)
with left:
    st.markdown("**📄 Original Evidence**")
    st.info(str(row.get("source_text") or ""))
with right:
    st.markdown("**✏️ Perturbed Evidence**")
    st.warning(str(row.get("perturbed_text") or ""))

st.markdown("---")
st.markdown("#### Annotate this row")

# Annotation buttons — MUST stay as the last st.columns call on the page
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("✅  Preserve", use_container_width=True):
        record_annotation("preserved")
        st.rerun()
with b2:
    if st.button("❌  Alter", use_container_width=True):
        record_annotation("altered")
        st.rerun()
with b3:
    if st.button("⚠️  Malformed", use_container_width=True):
        record_annotation("malformed")
        st.rerun()
with b4:
    if st.button("❓  Not Sure", use_container_width=True):
        record_annotation("not_sure")
        st.rerun()
