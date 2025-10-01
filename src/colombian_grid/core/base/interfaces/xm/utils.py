# XM API endpoints
XM_BASE_URL = "https://servapibi.xm.com.co"

XM_HOURLY_URL = f"{XM_BASE_URL}/hourly"
XM_DAILY_URL = f"{XM_BASE_URL}/daily"
XM_MONTHLY_URL = f"{XM_BASE_URL}/monthly"
XM_LISTS_URL = f"{XM_BASE_URL}/lists"

# API restrictions by data type (max days per request)
MAX_DAYS_RESTRICTIONS = {
    "hourly": 30,
    "daily": 30,
    "monthly": 731,
    "annual": 366,
}

# Chunking limits to avoid API overhead
CHUNK_DAYS_BY_TYPE = {
    "hourly": 30,  # 30 days for hourly data
    "daily": 30,  # 30 days for daily data
    "monthly": 731,  # ~2 years for monthly data
    "annual": 366,  # 1 year for annual data
}

MAX_CHUNK_YEARS = 2  # Maximum 2 years per chunk for long time spans
