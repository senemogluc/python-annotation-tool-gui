import json
from pathlib import Path

import pandas as pd
import streamlit as st

ANNOT_COL = "annotations"
RAW_DIR = Path("data/raw")
DEMO_FILENAME = "demo_sample_for_annotators.json"

LABELS = {1: "✅ Preserve", 0: "❌ Alter", -1: "❓ Not Sure"}


def list_raw_json_files() -> list[Path]:
    if not RAW_DIR.exists():
        return []
    return sorted(RAW_DIR.glob("*.json"))


def _flatten(data: dict) -> pd.DataFrame:
    rows = []
    for group_key, items in data.items():
        if group_key == "_summary":
            continue
        for item_idx, item in enumerate(items):
            row = dict(item)
            row["group_key"] = group_key
            row["item_idx"] = item_idx
            row[ANNOT_COL] = row.pop("annotation", pd.NA)
            if row[ANNOT_COL] is None:
                row[ANNOT_COL] = pd.NA
            rows.append(row)
    return pd.DataFrame(rows)


def load_json(source) -> tuple[pd.DataFrame, dict | None]:
    """Read a JSON file (path or uploaded file-like) into (df, summary)."""
    if isinstance(source, (str, Path)):
        data = json.loads(Path(source).read_text())
    else:
        data = json.load(source)
    summary = data.get("_summary")
    return _flatten(data), summary


def pending_indices(df: pd.DataFrame) -> list[int]:
    return df[df[ANNOT_COL].isna()].index.tolist()


def current_label(row) -> str | None:
    return LABELS.get(row.get(ANNOT_COL))


def _to_native(value):
    """Convert numpy/pandas scalar types to plain Python types for JSON serialization."""
    if isinstance(value, (list, dict)):
        return value
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value.item() if hasattr(value, "item") else value


def to_nested(df: pd.DataFrame, summary: dict | None) -> dict:
    nested: dict = {}
    for group_key, group in df.groupby("group_key", sort=False):
        items = []
        for _, row in group.sort_values("item_idx").iterrows():
            item = row.drop(labels=["group_key", "item_idx"]).to_dict()
            annotation = item.pop(ANNOT_COL)
            item = {k: _to_native(v) for k, v in item.items()}
            item["annotation"] = _to_native(annotation)
            items.append(item)
        nested[group_key] = items
    if summary is not None:
        nested["_summary"] = summary
    return nested


def record_annotation(value: int) -> None:
    """Label the current row and advance to the next one, if any."""
    df = st.session_state.df
    idx = st.session_state.current_idx
    df.at[idx, ANNOT_COL] = value
    if idx < df.index[-1]:
        st.session_state.current_idx = df.index[df.index.get_loc(idx) + 1]


def go_to(delta: int) -> None:
    """Move current_idx forward/backward by delta, clamped to the dataframe's bounds."""
    df = st.session_state.df
    pos = df.index.get_loc(st.session_state.current_idx) + delta
    pos = max(0, min(len(df) - 1, pos))
    st.session_state.current_idx = df.index[pos]


def reset_annotations() -> None:
    """Clear all annotations for the currently loaded file and restart from row 1."""
    df = st.session_state.df
    df[ANNOT_COL] = pd.NA
    st.session_state.current_idx = df.index[0] if len(df) else None
