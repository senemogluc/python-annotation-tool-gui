import json
from pathlib import Path

import pandas as pd
import streamlit as st

ANNOT_COL = "annotations"
RAW_DIR = Path("data/raw")
ANNOTATED_DIR = Path("data/annotated")


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


def resolve_load(filename: str, raw_source) -> tuple[pd.DataFrame, str, dict | None]:
    """Load annotations from data/annotated/<filename> if present (resume),
    otherwise load fresh from raw_source (path or uploaded file-like)."""
    annotated_path = ANNOTATED_DIR / filename
    if annotated_path.exists():
        df, summary = load_json(annotated_path)
    else:
        df, summary = load_json(raw_source)
    return df, filename, summary


def pending_indices(df: pd.DataFrame) -> list[int]:
    return df[df[ANNOT_COL].isna()].index.tolist()


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


def save_annotated(df: pd.DataFrame, filename: str, summary: dict | None) -> None:
    ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
    (ANNOTATED_DIR / filename).write_text(json.dumps(to_nested(df, summary), indent=2))


def record_annotation(value: int) -> None:
    df = st.session_state.df
    df.at[st.session_state.current_idx, ANNOT_COL] = value
    save_annotated(df, st.session_state.filename, st.session_state.summary)
    remaining = pending_indices(df)
    st.session_state.current_idx = remaining[0] if remaining else None
