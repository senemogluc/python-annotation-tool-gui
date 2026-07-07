import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

RAW_DIR = Path("data/raw")
AUTOSAVE_DIR = Path("data/autosave")
DEMO_FILENAME = "demo_sample_for_annotators.json"

ANNOTATOR_FILE_RE = re.compile(r"annotator_([ABCD])\.json")

LABELS = {
    "preserved": "✅ Preserve",
    "altered": "❌ Alter",
    "malformed": "⚠️ Malformed",
    "not_sure": "❓ Not Sure",
}


def list_raw_json_files() -> list[Path]:
    if not RAW_DIR.exists():
        return []
    return sorted(RAW_DIR.glob("*.json"))


def matching_annotator_letter(filename: str) -> str | None:
    """Return the letter encoded in an `annotator_<LETTER>.json` filename, if any."""
    match = ANNOTATOR_FILE_RE.fullmatch(filename)
    return match.group(1) if match else None


def load_json(source) -> pd.DataFrame:
    """Read a JSON file (path or uploaded file-like) into a DataFrame."""
    if isinstance(source, (str, Path)):
        data = json.loads(Path(source).read_text())
    else:
        data = json.load(source)
    if not isinstance(data, list):
        raise ValueError(
            "Unsupported file format — expected a JSON array of items "
            "(old grouped-dict files are no longer supported)."
        )
    return pd.DataFrame(data)


def filter_for_annotator(df: pd.DataFrame, annotator_id: str) -> pd.DataFrame:
    """Keep only rows this annotator is assigned to."""
    mask = df["assigned_pair"].apply(lambda pair: annotator_id in (pair or []))
    return df[mask]


def pending_indices(df: pd.DataFrame, annotator_id: str) -> list[int]:
    return df[df[f"annotator_{annotator_id}"].isna()].index.tolist()


def current_label(row, annotator_id: str) -> str | None:
    return LABELS.get(row.get(f"annotator_{annotator_id}"))


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


def to_list(df: pd.DataFrame) -> list[dict]:
    """Convert the DataFrame back to a plain list of item dicts, in row order."""
    return [{k: _to_native(v) for k, v in row.items()} for _, row in df.iterrows()]


def _autosave_path(filename: str, annotator_id: str) -> Path:
    stem = Path(filename).stem
    return AUTOSAVE_DIR / f"{stem}__annotator_{annotator_id}.json"


def restore_progress(df: pd.DataFrame, filename: str, annotator_id: str) -> pd.DataFrame:
    """Fill in this annotator's labels from a previous autosave, matched by item_id."""
    path = _autosave_path(filename, annotator_id)
    if not path.exists():
        return df
    saved = json.loads(path.read_text())
    col = f"annotator_{annotator_id}"
    saved_labels = {item["item_id"]: item.get(col) for item in saved if item.get(col) is not None}
    if saved_labels:
        mapped = df["item_id"].map(saved_labels)
        df[col] = mapped.where(mapped.notna(), df[col])
    return df


def save_progress() -> None:
    """Persist the current annotator's progress to disk so it survives a restart."""
    df = st.session_state.df
    filename = st.session_state.filename
    annotator_id = st.session_state.annotator_id
    if df is None or not filename or not annotator_id:
        return
    AUTOSAVE_DIR.mkdir(parents=True, exist_ok=True)
    _autosave_path(filename, annotator_id).write_text(json.dumps(to_list(df), indent=2))


def clear_progress(filename: str, annotator_id: str) -> None:
    _autosave_path(filename, annotator_id).unlink(missing_ok=True)


def record_annotation(label: str) -> None:
    """Label the current row and advance to the next one, if any."""
    df = st.session_state.df
    idx = st.session_state.current_idx
    annotator_id = st.session_state.annotator_id
    row = df.loc[idx]
    if annotator_id not in (row.get("assigned_pair") or []):
        st.error("This row isn't assigned to you — refusing to record the label.")
        return
    df.at[idx, f"annotator_{annotator_id}"] = label
    if idx < df.index[-1]:
        st.session_state.current_idx = df.index[df.index.get_loc(idx) + 1]
    save_progress()


def go_to(delta: int) -> None:
    """Move current_idx forward/backward by delta, clamped to the dataframe's bounds."""
    df = st.session_state.df
    pos = df.index.get_loc(st.session_state.current_idx) + delta
    pos = max(0, min(len(df) - 1, pos))
    st.session_state.current_idx = df.index[pos]


def reset_annotations() -> None:
    """Clear this annotator's own labels for the currently loaded file and restart from row 1."""
    df = st.session_state.df
    annotator_id = st.session_state.annotator_id
    df[f"annotator_{annotator_id}"] = None
    st.session_state.current_idx = df.index[0] if len(df) else None
    if st.session_state.filename:
        clear_progress(st.session_state.filename, annotator_id)
