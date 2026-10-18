import pandas as pd
import pytest
from app.pipeline import read_csv_bytes, quality_report, transform_frame

def test_read_csv_and_profile():
    df = read_csv_bytes(b"name,amount\n Alice ,10\nBob,\n")
    report = quality_report(df)
    assert report["row_count"] == 2
    assert report["column_count"] == 2
    assert report["null_cells"] == 1

def test_transform_normalizes_trims_and_deduplicates():
    df = pd.DataFrame({"Customer Name": [" Alice ", " Alice "], "Amount": [10, 10]})
    out, applied = transform_frame(df, {
        "operations": ["normalize_columns", "trim_strings"],
        "drop_duplicates": True, "missing_strategy": "keep"
    })
    assert list(out.columns) == ["customer_name", "amount"]
    assert len(out) == 1
    assert out.iloc[0]["customer_name"] == "Alice"
    assert len(applied) >= 3

def test_bad_operation_rejected():
    with pytest.raises(ValueError):
        transform_frame(pd.DataFrame({"a": [1]}), {"operations": ["execute_shell"]})

def test_duplicate_normalized_names_rejected():
    with pytest.raises(ValueError):
        transform_frame(pd.DataFrame({"A B": [1], "A-B": [2]}), {"operations": ["normalize_columns"]})
