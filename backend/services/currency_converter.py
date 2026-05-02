from __future__ import annotations

import logging
import time
from threading import Lock

import httpx

import core.config as cfg

# ---------------------------------------------------------------------------
# Currency Converter – Phase 6 (upgraded with live rates)
# ---------------------------------------------------------------------------
# Fetches live exchange rates from ExchangeRate-API when a key is configured.
# Falls back to static rates if the API is unavailable or key is missing.
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# Static fallback rates (INR as base currency).
# Used when EXCHANGE_RATE_API_KEY is absent or API call fails.
_STATIC_RATES_FROM_INR: dict[str, float] = {
    "INR": 1.0,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095,
    "AED": 0.044,
    "SGD": 0.016,
    "JPY": 1.80,
    "CAD": 0.016,
    "AUD": 0.018,
    "CNY": 0.086,
    "SAR": 0.045,
    "MYR": 0.056,
    "THB": 0.42,
    "KWD": 0.0037,
    "CHF": 0.011,
    "HKD": 0.094,
    "NZD": 0.020,
    "ZAR": 0.22,
}

# ---------------------------------------------------------------------------
# Live rate cache
# ---------------------------------------------------------------------------
_CACHE_TTL_SECONDS = 6 * 3600  # 6 hours
_cache_lock = Lock()
_cached_rates: dict[str, float] | None = None
_cached_at: float = 0.0
_using_live_rates: bool = False


def _fetch_live_rates() -> dict[str, float] | None:
    """Fetch live rates from ExchangeRate-API. Returns None on failure."""
    api_key = cfg.EXCHANGE_RATE_API_KEY
    if not api_key:
        return None

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/INR"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
        if response.status_code != 200:
            logger.warning("ExchangeRate-API returned HTTP %s", response.status_code)
            return None
        data = response.json()
        if data.get("result") != "success":
            logger.warning("ExchangeRate-API error: %s", data.get("error-type", "unknown"))
            return None
        rates = data.get("conversion_rates", {})
        if not rates:
            return None
        # API returns rates FROM INR (e.g. 1 INR = 0.012 USD), which is what we need.
        logger.info("Fetched live exchange rates for %d currencies.", len(rates))
        return {k.upper(): float(v) for k, v in rates.items()}
    except Exception as exc:
        logger.warning("Failed to fetch live exchange rates: %s", exc)
        return None


def _get_rates() -> tuple[dict[str, float], bool]:
    """Return (rates_dict, is_live). Uses cached live rates when available."""
    global _cached_rates, _cached_at, _using_live_rates  # noqa: PLW0603

    now = time.time()
    with _cache_lock:
        # Return cached live rates if still fresh
        if _cached_rates is not None and (now - _cached_at) < _CACHE_TTL_SECONDS:
            return _cached_rates, _using_live_rates

    # Try to fetch fresh live rates
    live = _fetch_live_rates()
    with _cache_lock:
        if live is not None:
            _cached_rates = live
            _cached_at = time.time()
            _using_live_rates = True
            return _cached_rates, True
        # If we had cached rates that are now stale, keep using them
        if _cached_rates is not None:
            logger.info("Using stale cached rates (API refresh failed).")
            return _cached_rates, True

    # Ultimate fallback: static rates
    return _STATIC_RATES_FROM_INR, False


SUPPORTED_CURRENCIES: list[str] = sorted(_STATIC_RATES_FROM_INR.keys())


def get_rate(target_currency: str) -> float:
    """
    Return the exchange rate from INR to ``target_currency``.

    Uses live rates when available, falls back to static rates.

    Raises
    ------
    ValueError
        If the currency code is not supported.
    """
    code = target_currency.upper()
    rates, is_live = _get_rates()
    rate = rates.get(code)
    if rate is None:
        # Live rates cover many currencies not in the static list
        if is_live:
            raise ValueError(
                f"Currency '{code}' is not available in live rate data."
            )
        raise ValueError(
            f"Currency '{code}' is not supported. "
            f"Supported currencies: {SUPPORTED_CURRENCIES}"
        )
    return rate


def convert_from_inr(amount_inr: float, target_currency: str) -> tuple[float, float]:
    """
    Convert an INR amount to the target display currency.

    Parameters
    ----------
    amount_inr:
        Amount in Indian Rupees.
    target_currency:
        ISO 4217 currency code (3 letters).

    Returns
    -------
    tuple[float, float]
        (display_amount, exchange_rate) where display_amount is rounded to
        2 decimal places.
    """
    rate = get_rate(target_currency)
    display_amount = round(amount_inr * rate, 2)
    return display_amount, rate
