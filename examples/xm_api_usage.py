"""
XM API Usage Examples

This file demonstrates how to use the XM API client to fetch Colombian
electricity market data.
"""

import asyncio
from datetime import date
from colombian_grid.core.xm import AsyncXMClient, SyncXMClient


async def example_async_usage():
    """Example of using the async XM client."""
    print("=== Async XM Client Example ===\n")

    async with AsyncXMClient() as client:
        # 1. Get all available metrics
        print("1. Fetching available metrics...")
        metrics = await client.get_available_metrics()
        print(f"Total metrics available: {len(metrics)}")
        print(f"\nFirst 5 metrics:\n{metrics.head()}\n")

        # 2. Find metrics related to generation
        print("2. Finding generation-related metrics...")
        gen_metrics = metrics[metrics["MetricName"].str.contains("Gener", na=False)]
        print(
            f"Generation metrics:\n{gen_metrics[['MetricId', 'MetricName', 'Entity']].head()}\n"
        )

        # 3. Fetch system-wide generation data for a short period
        print("3. Fetching system generation data (Jan 1-5, 2024)...")
        gen_data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )
        print(f"Data shape: {gen_data.shape}")
        print(f"Data preview:\n{gen_data.head()}\n")

        # 4. Fetch generation by resource with filters
        print("4. Fetching filtered resource generation data...")
        filtered_data = await client.get_data(
            metric="Gene",
            entity="Recurso",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 3),
            filter_by=["TBST", "GVIO"],  # Specific power plants
        )
        print(f"Filtered data shape: {filtered_data.shape}")
        print(
            f"Unique resources: {filtered_data['Code'].unique() if 'Code' in filtered_data.columns else 'N/A'}\n"
        )

        # 5. Fetch demand data
        print("5. Fetching real demand data...")
        demand_data = await client.get_data(
            metric="DemaReal",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
        )
        print(f"Demand data shape: {demand_data.shape}")
        print(f"Demand data preview:\n{demand_data.head()}\n")


def example_sync_usage():
    """Example of using the sync XM client."""
    print("\n=== Sync XM Client Example ===\n")

    with SyncXMClient() as client:
        # 1. Get available metrics
        print("1. Fetching available metrics...")
        metrics = client.get_available_metrics()
        print(f"Total metrics available: {len(metrics)}")

        # 2. Find price-related metrics
        print("\n2. Finding price-related metrics...")
        price_metrics = metrics[metrics["MetricName"].str.contains("Prec", na=False)]
        print(
            f"Price metrics:\n{price_metrics[['MetricId', 'MetricName', 'Entity']].head()}\n"
        )

        # 3. Fetch national price data
        print("3. Fetching national price data...")
        price_data = client.get_data(
            metric="PrecBolsNaci",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 15),
        )
        print(f"Price data shape: {price_data.shape}")
        print(f"Price data preview:\n{price_data.head()}\n")


def example_long_time_span():
    """Example of fetching data for a very long time span (automatic chunking)."""
    print("\n=== Long Time Span Example (with automatic chunking) ===\n")

    with SyncXMClient() as client:
        print("Fetching 2 years of monthly data...")
        # This will automatically chunk the requests to avoid API overload
        monthly_data = client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2022, 1, 1),
            end_date=date(2023, 12, 31),
        )
        print(f"Data shape: {monthly_data.shape}")
        print(
            f"Date range: {monthly_data['Date'].min()} to {monthly_data['Date'].max()}"
        )
        print(f"Data preview:\n{monthly_data.head()}\n")


def example_data_analysis():
    """Example of basic data analysis with XM data."""
    print("\n=== Data Analysis Example ===\n")

    with SyncXMClient() as client:
        # Fetch generation data
        print("Fetching generation data for analysis...")
        gen_data = client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        if "Date" in gen_data.columns:
            print(f"Date range: {gen_data['Date'].min()} to {gen_data['Date'].max()}")

        # Calculate basic statistics for hourly columns
        hour_cols = [col for col in gen_data.columns if "Hour" in col]
        if hour_cols:
            print("\nHourly generation statistics:")
            print(gen_data[hour_cols].describe())

        print(f"\nTotal records: {len(gen_data)}")


if __name__ == "__main__":
    # Run async example
    asyncio.run(example_async_usage())

    # Run sync examples
    example_sync_usage()
    # example_long_time_span()  # Uncomment to test long time spans
    # example_data_analysis()  # Uncomment for data analysis example
