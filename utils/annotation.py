import pandas as pd
import streamlit as st

ANNOT_COL = "annotations"


def find_bert_col(df: pd.DataFrame) -> str | None:
    if "bertscore_f1" in df.columns:
        return "bertscore_f1"
    if "bertscore" in df.columns:
        return "bertscore"
    return None


def find_confidence_col(df: pd.DataFrame) -> str | None:
    for col in ("confidence_score", "confidence"):
        if col in df.columns:
            return col
    return None


def pending_indices(df: pd.DataFrame) -> list[int]:
    return df[df[ANNOT_COL].isna()].index.tolist()


def record_annotation(value: int) -> None:
    df = st.session_state.df
    df.at[st.session_state.current_idx, ANNOT_COL] = value
    remaining = pending_indices(df)
    st.session_state.current_idx = remaining[0] if remaining else None


def load_uploaded_file(uploaded) -> tuple[pd.DataFrame, str] | tuple[None, None]:
    """Read an uploaded xlsx, add annotations column if missing. Returns (df, filename) or (None, None) on error."""
    df = pd.read_excel(uploaded)
    if find_bert_col(df) is None:
        return None, None
    if ANNOT_COL not in df.columns:
        df[ANNOT_COL] = pd.NA
    return df, uploaded.name
