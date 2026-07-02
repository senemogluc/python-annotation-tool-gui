import json
from pathlib import Path

import streamlit as st

from utils.annotation import (
    list_raw_json_files,
    pending_indices,
    record_annotation,
    resolve_load,
    to_nested,
)

st.set_page_config(page_title="Annotation Tool", page_icon="🏷️", layout="wide")


def _load_css(path: str) -> None:
    css = Path(path).read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_load_css("assets/styles.css")

for _k, _v in [
    ("df", None),
    ("filename", None),
    ("current_idx", None),
    ("summary", None),
    ("instructions_ack", False),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


def _start_annotating(df, filename, summary) -> None:
    pending = pending_indices(df)
    st.session_state.df = df
    st.session_state.filename = filename
    st.session_state.summary = summary
    st.session_state.current_idx = pending[0] if pending else None
    st.rerun()


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
    if st.button("Continue to annotation tool ➜", disabled=not ack):
        st.session_state.instructions_ack = True
        st.rerun()
    st.stop()


# ── Upload screen ──────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.title("🏷️ Annotation Tool")
    st.markdown("Pick a JSON file from `data/raw/` or upload one to start annotating.")

    raw_files = list_raw_json_files()
    if raw_files:
        choice = st.selectbox("Files in data/raw/", raw_files, format_func=lambda p: p.name)
        if st.button("📂 Load selected file"):
            df, filename, summary = resolve_load(choice.name, choice)
            _start_annotating(df, filename, summary)
    else:
        st.info("No JSON files found in `data/raw/`.")

    st.markdown("---")
    uploaded = st.file_uploader("Or upload a .json file", type=["json"])
    if uploaded:
        df, filename, summary = resolve_load(uploaded.name, uploaded)
        _start_annotating(df, filename, summary)

    st.stop()


# ── Annotation screen ──────────────────────────────────────────────────────────
df = st.session_state.df
pending = pending_indices(df)
total = len(df)
done_count = total - len(pending)

# Top bar — title + action buttons
col_title, col_actions = st.columns([3, 2])
with col_title:
    st.title("🏷️ Annotation Tool")
    st.caption(f"📄 {st.session_state.filename}")

with col_actions:
    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
    btn_dl, btn_new = st.columns(2)
    with btn_dl:
        payload = json.dumps(to_nested(df, st.session_state.summary), indent=2).encode()
        download_name = f"{Path(st.session_state.filename).stem}_annotated.json"
        st.download_button(
            label="💾 Download annotations",
            data=payload,
            file_name=download_name,
            mime="application/json",
            use_container_width=True,
        )
    with btn_new:
        if st.button("📂 Load a new file", use_container_width=True):
            st.session_state.df = None
            st.session_state.filename = None
            st.session_state.summary = None
            st.session_state.current_idx = None
            st.rerun()

st.progress(done_count / total if total else 0)
st.markdown(f"**{done_count} / {total}** rows annotated")

# ── All done ───────────────────────────────────────────────────────────────────
if st.session_state.current_idx is None:
    st.success("🎉 All rows annotated! Download your file with the button above.")
    st.stop()

# ── Active row ─────────────────────────────────────────────────────────────────
idx = st.session_state.current_idx
row = df.loc[idx]

st.markdown("---")
st.markdown(
    f"## Row {idx + 1} &nbsp;·&nbsp; "
    f"<span style='color:gray;font-size:1rem'>{done_count}/{total} annotated</span>",
    unsafe_allow_html=True,
)

st.markdown(
    f"**Question Type:** `{row.get('question_type') or '—'}` &nbsp;&nbsp; "
    f"**Perturbation Type:** `{row.get('perturbation_type') or '—'}`"
)

st.markdown("---")

# Texts
left, right = st.columns(2)
with left:
    st.markdown("**📄 Original Text**")
    st.info(str(row.get("source_text") or ""))
with right:
    st.markdown("**✏️ Perturbed Text**")
    st.warning(str(row.get("perturbed_text") or ""))

st.markdown("---")
st.markdown("#### Annotate this row")

# Annotation buttons — MUST stay as the last st.columns call on the page
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("✅  Preserve  (1)", use_container_width=True):
        record_annotation(1)
        st.rerun()
with b2:
    if st.button("❌  Alter  (0)", use_container_width=True):
        record_annotation(0)
        st.rerun()
with b3:
    if st.button("❓  Not Sure  (-1)", use_container_width=True):
        record_annotation(-1)
        st.rerun()
