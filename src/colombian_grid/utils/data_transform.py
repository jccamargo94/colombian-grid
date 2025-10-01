"""
Data transformation utilities for colombian-grid.

This module provides utilities to transform DataFrames between different formats,
particularly for time series data from the XM API.
"""

import pandas as pd
from datetime import datetime, timedelta


def wide_to_long_timeseries(
    df: pd.DataFrame,
    date_column: str = "Date",
    value_prefix: str = "Hour",
    id_columns: list[str] | None = None,
    frequency: str = "H",
) -> pd.DataFrame:
    """
    Transform wide format time series to long format.

    Converts a DataFrame where each row represents a date and columns contain
    time-based values (e.g., Hour01, Hour02, ..., Hour24) into a long format
    with timestamp and value columns.

    Args:
        df: Input DataFrame in wide format
        date_column: Name of the column containing dates (default: "Date")
        value_prefix: Prefix for time-based columns (default: "Hour")
        id_columns: List of identifier columns to preserve (e.g., ["Id", "Code"])
                   If None, all non-date, non-value columns are used
        frequency: Time frequency for timestamps:
                  - "H" for hourly (default)
                  - "D" for daily
                  - "M" for monthly

    Returns:
        DataFrame in long format with columns: id_columns + ["timestamp", "value"]

    Example:
        >>> # Wide format (hourly data)
        >>> wide_df = pd.DataFrame({
        ...     "Date": ["2024-01-01", "2024-01-02"],
        ...     "Code": ["TBST", "TBST"],
        ...     "Hour01": [100.0, 105.0],
        ...     "Hour02": [110.0, 115.0],
        ... })
        >>> long_df = wide_to_long_timeseries(wide_df, id_columns=["Code"])
        >>> # Result:
        >>> # Code | timestamp           | value
        >>> # TBST | 2024-01-01 00:00:00 | 100.0
        >>> # TBST | 2024-01-01 01:00:00 | 110.0
        >>> # TBST | 2024-01-02 00:00:00 | 105.0
        >>> # TBST | 2024-01-02 01:00:00 | 115.0

        Note:
            Hour numbering: Hour01 = 00:00 (midnight), Hour02 = 01:00, ..., Hour24 = 23:00
    """
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "value"])

    df = df.copy()

    if date_column not in df.columns:
        raise ValueError(f"Date column '{date_column}' not found in DataFrame")

    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])

    # Identify value columns (those starting with value_prefix)
    value_columns = [col for col in df.columns if col.startswith(value_prefix)]

    if not value_columns:
        raise ValueError(
            f"No columns found with prefix '{value_prefix}'. "
            f"Available columns: {df.columns.tolist()}"
        )

    # Determine ID columns
    if id_columns is None:
        id_columns = [
            col for col in df.columns if col not in value_columns and col != date_column
        ]
    else:
        # Validate that id_columns exist
        missing_cols = set(id_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"ID columns not found in DataFrame: {missing_cols}")

    # Extract time periods from column names (e.g., "Hour01" -> 1)
    time_periods = []
    for col in value_columns:
        # Extract number from column name
        period_str = col.replace(value_prefix, "")
        try:
            period = int(period_str)
            time_periods.append(period)
        except ValueError:
            raise ValueError(
                f"Could not extract time period from column '{col}'. "
                f"Expected format: '{value_prefix}XX' where XX is a number."
            )

    # Melt the DataFrame
    id_vars = id_columns + [date_column]
    melted = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_columns,
        var_name="period",
        value_name="value",
    )

    # Extract period number from column name
    melted["period_num"] = melted["period"].str.replace(value_prefix, "").astype(int)

    # Calculate timestamp based on frequency
    if frequency == "H":
        # For hourly: Hour numbering is 1-24 representing hours 0-23 of the day
        # Hour01 = 00:00 (midnight), Hour02 = 01:00, ..., Hour24 = 23:00
        melted["timestamp"] = melted.apply(
            lambda row: row[date_column] + timedelta(hours=row["period_num"] - 1),
            axis=1,
        )
    elif frequency == "D":
        # For daily: day number represents the day of the month
        melted["timestamp"] = melted.apply(
            lambda row: row[date_column] + timedelta(days=row["period_num"] - 1), axis=1
        )
    elif frequency == "M":
        # For monthly: month number represents the month
        melted["timestamp"] = melted.apply(
            lambda row: datetime(
                row[date_column].year, row["period_num"], row[date_column].day
            ),
            axis=1,
        )
    else:
        raise ValueError(
            f"Unsupported frequency: {frequency}. "
            f"Supported values: 'H' (hourly), 'D' (daily), 'M' (monthly)"
        )

    # Select and order final columns
    result_columns = id_columns + ["timestamp", "value"]
    result = melted[result_columns].copy()

    # Sort by id columns and timestamp
    sort_columns = id_columns + ["timestamp"]
    result = result.sort_values(sort_columns).reset_index(drop=True)

    # Drop rows with NaN values (optional, can be configured)
    result = result.dropna(subset=["value"])

    return result


def long_to_wide_timeseries(
    df: pd.DataFrame,
    timestamp_column: str = "timestamp",
    value_column: str = "value",
    id_columns: list[str] | None = None,
    frequency: str = "H",
    value_prefix: str = "Hour",
) -> pd.DataFrame:
    """
    Transform long format time series to wide format.

    Converts a DataFrame with timestamp and value columns into a wide format
    where each row represents a date and columns contain time-based values.

    Args:
        df: Input DataFrame in long format
        timestamp_column: Name of the timestamp column (default: "timestamp")
        value_column: Name of the value column (default: "value")
        id_columns: List of identifier columns (e.g., ["Code"])
        frequency: Time frequency:
                  - "H" for hourly (default)
                  - "D" for daily
                  - "M" for monthly
        value_prefix: Prefix for time-based columns (default: "Hour")

    Returns:
        DataFrame in wide format with date and time-period columns

    Example:
        >>> # Long format
        >>> long_df = pd.DataFrame({
        ...     "Code": ["TBST", "TBST", "TBST", "TBST"],
        ...     "timestamp": [
        ...         "2024-01-01 00:00:00",
        ...         "2024-01-01 01:00:00",
        ...         "2024-01-02 00:00:00",
        ...         "2024-01-02 01:00:00",
        ...     ],
        ...     "value": [100.0, 110.0, 105.0, 115.0],
        ... })
        >>> wide_df = long_to_wide_timeseries(long_df, id_columns=["Code"])
        >>> # Result:
        >>> # Code | Date       | Hour01 | Hour02
        >>> # TBST | 2024-01-01 | 100.0  | 110.0
        >>> # TBST | 2024-01-02 | 105.0  | 115.0

        Note:
            Hour numbering: Hour01 = 00:00 (midnight), Hour02 = 01:00, ..., Hour24 = 23:00
    """
    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    if timestamp_column not in df.columns:
        raise ValueError(f"Timestamp column '{timestamp_column}' not found")

    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_column]):
        df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    # Validate value column exists
    if value_column not in df.columns:
        raise ValueError(f"Value column '{value_column}' not found")

    # Determine ID columns
    if id_columns is None:
        id_columns = [
            col for col in df.columns if col not in [timestamp_column, value_column]
        ]

    # Extract date and period based on frequency
    if frequency == "H":
        df["Date"] = df[timestamp_column].dt.date
        # Hour numbering: 00:00 = Hour01, 01:00 = Hour02, ..., 23:00 = Hour24
        df["period_num"] = df[timestamp_column].dt.hour + 1
    elif frequency == "D":
        df["Date"] = df[timestamp_column].dt.to_period("M").dt.to_timestamp()
        df["period_num"] = df[timestamp_column].dt.day
    elif frequency == "M":
        df["Date"] = df[timestamp_column].dt.year
        df["period_num"] = df[timestamp_column].dt.month
    else:
        raise ValueError(
            f"Unsupported frequency: {frequency}. "
            f"Supported values: 'H' (hourly), 'D' (daily), 'M' (monthly)"
        )

    # Create period column name
    df["period_col"] = df["period_num"].apply(lambda x: f"{value_prefix}{x:02d}")

    # Pivot to wide format
    index_cols = id_columns + ["Date"] if id_columns else ["Date"]
    wide = df.pivot_table(
        index=index_cols, columns="period_col", values=value_column, aggfunc="first"
    ).reset_index()

    # Convert Date back to datetime if needed
    wide["Date"] = pd.to_datetime(wide["Date"])

    return wide


def add_timestamp_to_hourly_data(
    df: pd.DataFrame,
    date_column: str = "Date",
    hour_prefix: str = "Hour",
) -> pd.DataFrame:
    """
    Convenience function to transform hourly wide format to long format.

    This is a specialized version of wide_to_long_timeseries for hourly data
    with sensible defaults.

    Args:
        df: Input DataFrame with hourly columns (Hour01, Hour02, etc.)
        date_column: Name of the date column (default: "Date")
        hour_prefix: Prefix for hour columns (default: "Hour")

    Returns:
        DataFrame in long format with timestamp column

    Example:
        >>> df = pd.DataFrame({
        ...     "Date": ["2024-01-01"],
        ...     "Code": ["TBST"],
        ...     "Hour01": [100.0],
        ...     "Hour02": [110.0],
        ... })
        >>> result = add_timestamp_to_hourly_data(df)
    """
    # Detect ID columns (all except Date and Hour* columns)
    hour_columns = [col for col in df.columns if col.startswith(hour_prefix)]
    id_columns = [
        col for col in df.columns if col not in hour_columns and col != date_column
    ]

    return wide_to_long_timeseries(
        df=df,
        date_column=date_column,
        value_prefix=hour_prefix,
        id_columns=id_columns or None,
        frequency="H",
    )
