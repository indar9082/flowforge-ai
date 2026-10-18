import json
import re
from io import BytesIO
from time import perf_counter
import pandas as pd

ALLOWED_OPERATIONS = {"trim_strings", "normalize_columns", "drop_empty_columns", "convert_numeric"}

def read_csv_bytes(data: bytes) -> pd.DataFrame:
    if not data:
        raise ValueError("The uploaded file is empty.")
    try:
        frame = pd.read_csv(BytesIO(data), encoding="utf-8-sig")
    except UnicodeDecodeError:
        frame = pd.read_csv(BytesIO(data), encoding="latin-1")
    except Exception as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc
    if frame.empty and len(frame.columns) == 0:
        raise ValueError("CSV has no readable columns.")
    if len(frame.columns) > 250:
        raise ValueError("CSV has too many columns (maximum 250).")
    return frame

def quality_report(df: pd.DataFrame) -> dict:
    total = int(len(df))
    nulls = {str(c): int(df[c].isna().sum()) for c in df.columns}
    dtypes = {str(c): str(df[c].dtype) for c in df.columns}
    duplicates = int(df.duplicated().sum()) if total else 0
    return {
        "row_count": total,
        "column_count": int(len(df.columns)),
        "duplicate_rows": duplicates,
        "null_cells": int(sum(nulls.values())),
        "nulls_by_column": nulls,
        "dtypes": dtypes,
        "memory_kb": round(float(df.memory_usage(deep=True).sum()) / 1024, 2),
    }

def transform_frame(df: pd.DataFrame, options: dict) -> tuple[pd.DataFrame, list[str]]:
    result = df.copy()
    applied = []
    for operation in options.get("operations", []):
        if operation not in ALLOWED_OPERATIONS:
            raise ValueError(f"Unsupported operation: {operation}")
        if operation == "trim_strings":
            for col in result.select_dtypes(include=["object", "string"]).columns:
                result[col] = result[col].map(lambda x: x.strip() if isinstance(x, str) else x)
            applied.append("Trim whitespace in text fields")
        elif operation == "normalize_columns":
            names = []
            for col in result.columns:
                name = re.sub(r"[^a-zA-Z0-9]+", "_", str(col).strip().lower()).strip("_")
                names.append(name or "column")
            if len(set(names)) != len(names):
                raise ValueError("Column normalization would create duplicate column names.")
            result.columns = names
            applied.append("Normalize column names")
        elif operation == "drop_empty_columns":
            empty = [c for c in result.columns if result[c].isna().all()]
            result = result.drop(columns=empty)
            applied.append(f"Drop {len(empty)} fully empty columns")
        elif operation == "convert_numeric":
            converted = []
            for col in result.select_dtypes(include=["object", "string"]).columns:
                candidate = pd.to_numeric(result[col], errors="coerce")
                valid_original = result[col].notna().sum()
                if valid_original and candidate.notna().sum() / valid_original >= 0.85:
                    result[col] = candidate
                    converted.append(str(col))
            applied.append("Convert numeric-like fields" + (f": {', '.join(converted)}" if converted else ": no fields matched"))
    if options.get("drop_duplicates", True):
        before = len(result)
        result = result.drop_duplicates()
        removed = before - len(result)
        if removed:
            applied.append(f"Remove {removed} duplicate rows")
    strategy = options.get("missing_strategy", "keep")
    if strategy == "drop_rows":
        before = len(result)
        result = result.dropna()
        applied.append(f"Drop {before - len(result)} rows containing missing values")
    elif strategy == "fill_empty":
        text_cols = result.select_dtypes(include=["object", "string"]).columns
        for col in text_cols:
            result[col] = result[col].fillna("")
        applied.append("Fill missing text values with empty strings")
    filter_column = options.get("filter_column")
    filter_contains = options.get("filter_contains")
    if filter_column and filter_contains is not None:
        if filter_column not in result.columns:
            raise ValueError(f"Filter column '{filter_column}' does not exist in the transformed data.")
        before = len(result)
        result = result[result[filter_column].astype(str).str.contains(str(filter_contains), case=False, na=False, regex=False)]
        applied.append(f"Filter rows where {filter_column} contains '{filter_contains}' ({before - len(result)} removed)")
    return result, applied

def dataframe_preview(df: pd.DataFrame, limit: int = 12) -> list[dict]:
    clean = df.head(limit).astype(object).where(pd.notna(df.head(limit)), None)
    return clean.to_dict(orient="records")

def execute_pipeline(data: bytes, options: dict):
    start = perf_counter()
    source = read_csv_bytes(data)
    report_before = quality_report(source)
    output, applied = transform_frame(source, options)
    report_after = quality_report(output)
    duration = round((perf_counter() - start) * 1000, 2)
    return {
        "source": source,
        "output": output,
        "rows_in": len(source),
        "rows_out": len(output),
        "duration_ms": duration,
        "applied": applied,
        "quality_before": report_before,
        "quality_after": report_after,
    }
