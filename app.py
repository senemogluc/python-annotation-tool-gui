import io
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.annotation import (
    ANNOT_COL,
    find_bert_col,
    find_confidence_col,
    load_uploaded_file,
    pending_indices,
    record_annotation,
)

st.set_page_config(page_title="Annotation Tool", page_icon="🏷️", layout="wide")


def _load_css(path: str) -> None:
    css = Path(path).read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


_load_css("assets/styles.css")

for _k, _v in [("df", None), ("filename", None), ("current_idx", None)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ── Upload screen ──────────────────────────────────────────────────────────────
if st.session_state.df is None:
    st.title("🏷️ Annotation Tool")
    st.markdown("Upload an Excel file to start annotating rows.")

    uploaded = st.file_uploader("Choose an .xlsx file", type=["xlsx"])
    if uploaded:
        df, filename = load_uploaded_file(uploaded)
        if df is None:
            st.error("File must contain a `bertscore_f1` or `bertscore` column.")
            st.stop()

        pending = pending_indices(df)
        st.session_state.df = df
        st.session_state.filename = filename
        st.session_state.current_idx = pending[0] if pending else None
        st.rerun()

    st.stop()


# ── Annotation screen ──────────────────────────────────────────────────────────
df = st.session_state.df
bert_col = find_bert_col(df)
conf_col = find_confidence_col(df)
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
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        st.download_button(
            label="💾 Download annotations",
            data=buf.getvalue(),
            file_name=st.session_state.filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with btn_new:
        if st.button("📂 Load a new file", use_container_width=True):
            st.session_state.df = None
            st.session_state.filename = None
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

# Perturbation type — full text, no truncation
pert_type = row.get("perturbation_type") or "—"
st.markdown(f"**Perturbation Type:** `{pert_type}`")

# Numeric metadata
m1, m2, m3 = st.columns(3)
with m1:
    raw_bert = row.get(bert_col) if bert_col else None
    st.metric("BERTScore F1", f"{float(raw_bert):.4f}" if pd.notna(raw_bert) else "—")
with m2:
    raw_conf = row.get(conf_col) if conf_col else None
    st.metric("Confidence Score", f"{float(raw_conf):.4f}" if conf_col and pd.notna(raw_conf) else "—")
with m3:
    st.metric("NLI Label", row.get("nli_label") or "—")

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
