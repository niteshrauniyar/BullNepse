"""
NEPSE API Fetcher
Primary data source: Official NEPSE API endpoints
"""

import requests
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)

NEPSE_BASE_URL = "https://nepalstock.com.np/api"
NEPSE_LIVE_URL = f"{NEPSE_BASE_URL}/nots/nepse-data/todaysprice"
NEPSE_SUMMARY_URL = f"{NEPSE_BASE_URL}/nots/nepse-data/summaryData"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://nepalstock.com.np/",
    "Origin": "https://nepalstock.com.np",
}

TIMEOUT = 15


def fetch_from_api() -> Optional[pd.DataFrame]:
    """
    Fetch today's market data from official NEPSE API.
    Returns normalized DataFrame or None on failure.
    """
    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # Attempt token refresh / auth handshake if needed
        try:
            token_url = f"{NEPSE_BASE_URL}/authenticate/prove"
            session.post(token_url, json={}, timeout=TIMEOUT)
        except Exception:
            pass  # Continue without token — some endpoints are public

        response = session.get(NEPSE_LIVE_URL, timeout=TIMEOUT)
        response.raise_for_status()

        data = response.json()

        # NEPSE API wraps data in different keys depending on endpoint version
        records = None
        for key in ("content", "data", "todayPrice", "businessDate", "items"):
            if isinstance(data, dict) and key in data:
                candidate = data[key]
                if isinstance(candidate, list) and len(candidate) > 0:
                    records = candidate
                    break

        if records is None and isinstance(data, list):
            records = data

        if not records:
            logger.warning("NEPSE API returned empty or unrecognized structure.")
            return None

        df = pd.DataFrame(records)
        logger.info(f"NEPSE API: fetched {len(df)} rows, columns: {list(df.columns)}")
        return df

    except requests.exceptions.ConnectionError:
        logger.error("NEPSE API: Connection failed.")
    except requests.exceptions.Timeout:
        logger.error("NEPSE API: Request timed out.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"NEPSE API: HTTP error {e}")
    except Exception as e:
        logger.error(f"NEPSE API: Unexpected error — {e}")

    return None
