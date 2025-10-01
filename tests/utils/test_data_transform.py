"""
Tests for data transformation utilities.
"""

import pytest
import pandas as pd

from colombian_grid.utils.data_transform import (
    wide_to_long_timeseries,
    long_to_wide_timeseries,
    add_timestamp_to_hourly_data,
)


def test_wide_to_long_hourly_basic():
    """Test basic wide to long transformation for hourly data."""
    # Create sample wide format data
    wide_df = pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-02"],
            "Code": ["TBST", "TBST"],
            "Hour01": [100.0, 105.0],
            "Hour02": [110.0, 115.0],
            "Hour03": [120.0, 125.0],
        }
    )

    result = wide_to_long_timeseries(wide_df, id_columns=["Code"])

    # Check shape
    assert len(result) == 6  # 2 days * 3 hours
    assert list(result.columns) == ["Code", "timestamp", "value"]

    # Check first row
    assert result.iloc[0]["Code"] == "TBST"
    assert result.iloc[0]["timestamp"] == pd.Timestamp("2024-01-01 00:00:00")
    assert result.iloc[0]["value"] == 100.0

    # Check last row
    assert result.iloc[-1]["Code"] == "TBST"
    assert result.iloc[-1]["timestamp"] == pd.Timestamp("2024-01-02 02:00:00")
    assert result.iloc[-1]["value"] == 125.0


def test_wide_to_long_multiple_ids():
    """Test wide to long with multiple ID columns."""
    wide_df = pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-01"],
            "Plant": ["TBST", "GVIO"],
            "Type": ["Hydro", "Hydro"],
            "Hour01": [100.0, 200.0],
            "Hour02": [110.0, 210.0],
        }
    )

    result = wide_to_long_timeseries(wide_df, id_columns=["Plant", "Type"])

    assert len(result) == 4  # 2 plants * 2 hours
    assert list(result.columns) == ["Plant", "Type", "timestamp", "value"]

    # Check different plants
    tbst_data = result[result["Plant"] == "TBST"]
    gvio_data = result[result["Plant"] == "GVIO"]

    assert len(tbst_data) == 2
    assert len(gvio_data) == 2
    assert tbst_data.iloc[0]["value"] == 100.0
    assert gvio_data.iloc[0]["value"] == 200.0


def test_wide_to_long_auto_detect_ids():
    """Test automatic ID column detection."""
    wide_df = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Code": ["TBST"],
            "Name": ["Termobarranca"],
            "Hour01": [100.0],
            "Hour02": [110.0],
        }
    )

    # Don't specify id_columns - should auto-detect
    result = wide_to_long_timeseries(wide_df, id_columns=None)

    assert "Code" in result.columns
    assert "Name" in result.columns
    assert "timestamp" in result.columns
    assert "value" in result.columns


def test_wide_to_long_with_nan_values():
    """Test handling of NaN values."""
    wide_df = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Code": ["TBST"],
            "Hour01": [100.0],
            "Hour02": [None],
            "Hour03": [120.0],
        }
    )

    result = wide_to_long_timeseries(wide_df, id_columns=["Code"])

    # NaN values should be dropped
    assert len(result) == 2  # Only 2 non-NaN values


def test_long_to_wide_hourly_basic():
    """Test basic long to wide transformation for hourly data."""
    # Create sample long format data (Hour01=00:00, Hour02=01:00)
    long_df = pd.DataFrame(
        {
            "Code": ["TBST", "TBST", "TBST", "TBST"],
            "timestamp": pd.to_datetime(
                [
                    "2024-01-01 00:00:00",
                    "2024-01-01 01:00:00",
                    "2024-01-02 00:00:00",
                    "2024-01-02 01:00:00",
                ]
            ),
            "value": [100.0, 110.0, 105.0, 115.0],
        }
    )

    result = long_to_wide_timeseries(long_df, id_columns=["Code"])

    # Check shape
    assert len(result) == 2  # 2 days
    assert "Code" in result.columns
    assert "Date" in result.columns
    assert "Hour01" in result.columns
    assert "Hour02" in result.columns

    # Check values
    day1 = result[result["Date"] == pd.Timestamp("2024-01-01")].iloc[0]
    assert day1["Code"] == "TBST"
    assert day1["Hour01"] == 100.0
    assert day1["Hour02"] == 110.0

    day2 = result[result["Date"] == pd.Timestamp("2024-01-02")].iloc[0]
    assert day2["Hour01"] == 105.0
    assert day2["Hour02"] == 115.0


def test_roundtrip_conversion():
    """Test that wide -> long -> wide produces the same result."""
    # Original wide format
    original = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Code": ["TBST", "TBST"],
            "Hour01": [100.0, 105.0],
            "Hour02": [110.0, 115.0],
            "Hour03": [120.0, 125.0],
        }
    )

    # Wide -> Long
    long_format = wide_to_long_timeseries(original, id_columns=["Code"])

    # Long -> Wide
    wide_again = long_to_wide_timeseries(long_format, id_columns=["Code"])

    # Compare (order of columns may differ)
    assert set(wide_again.columns) == set(original.columns)
    assert len(wide_again) == len(original)

    # Check values match
    for col in ["Hour01", "Hour02", "Hour03"]:
        assert wide_again[col].tolist() == original[col].tolist()


def test_add_timestamp_to_hourly_data():
    """Test convenience function for hourly data."""
    df = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Code": ["TBST"],
            "Name": ["Termobarranca"],
            "Hour01": [100.0],
            "Hour02": [110.0],
        }
    )

    result = add_timestamp_to_hourly_data(df)

    assert "timestamp" in result.columns
    assert "value" in result.columns
    assert "Code" in result.columns
    assert "Name" in result.columns
    assert len(result) == 2


def test_wide_to_long_empty_dataframe():
    """Test handling of empty DataFrame."""
    empty_df = pd.DataFrame()

    result = wide_to_long_timeseries(empty_df)

    assert result.empty
    assert "timestamp" in result.columns
    assert "value" in result.columns


def test_wide_to_long_missing_date_column():
    """Test error handling for missing date column."""
    df = pd.DataFrame(
        {
            "Code": ["TBST"],
            "Hour01": [100.0],
        }
    )

    with pytest.raises(ValueError, match="Date column 'Date' not found"):
        wide_to_long_timeseries(df)


def test_wide_to_long_missing_value_columns():
    """Test error handling for missing value columns."""
    df = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Code": ["TBST"],
        }
    )

    with pytest.raises(ValueError, match="No columns found with prefix"):
        wide_to_long_timeseries(df)


def test_wide_to_long_invalid_id_columns():
    """Test error handling for invalid ID columns."""
    df = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Code": ["TBST"],
            "Hour01": [100.0],
        }
    )

    with pytest.raises(ValueError, match="ID columns not found"):
        wide_to_long_timeseries(df, id_columns=["InvalidColumn"])


def test_wide_to_long_24_hours():
    """Test transformation with full 24-hour day."""
    # Create data with all 24 hours
    data = {"Date": ["2024-01-01"], "Code": ["TBST"]}
    for hour in range(1, 25):
        data[f"Hour{hour:02d}"] = [float(100 + hour)]

    wide_df = pd.DataFrame(data)
    result = wide_to_long_timeseries(wide_df, id_columns=["Code"])

    assert len(result) == 24

    # Hour01 = 00:00 (midnight), Hour24 = 23:00
    assert result.iloc[0]["timestamp"] == pd.Timestamp("2024-01-01 00:00:00")
    assert result.iloc[-1]["timestamp"] == pd.Timestamp("2024-01-01 23:00:00")


def test_long_to_wide_empty_dataframe():
    """Test handling of empty DataFrame in long to wide conversion."""
    empty_df = pd.DataFrame()

    result = long_to_wide_timeseries(empty_df)

    assert result.empty


def test_long_to_wide_missing_timestamp_column():
    """Test error handling for missing timestamp column."""
    df = pd.DataFrame(
        {
            "Code": ["TBST"],
            "value": [100.0],
        }
    )

    with pytest.raises(ValueError, match="Timestamp column 'timestamp' not found"):
        long_to_wide_timeseries(df)


def test_long_to_wide_missing_value_column():
    """Test error handling for missing value column."""
    df = pd.DataFrame(
        {
            "Code": ["TBST"],
            "timestamp": [pd.Timestamp("2024-01-01 01:00:00")],
        }
    )

    with pytest.raises(ValueError, match="Value column 'value' not found"):
        long_to_wide_timeseries(df)
