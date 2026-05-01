from __future__ import annotations

# ---------------------------------------------------------------------------
# Currency Converter – Phase 6
# ---------------------------------------------------------------------------
# Static exchange-rate table (INR as base currency).
# Rates are approximate and intended for display purposes only.
# Swap out _RATES_FROM_INR entries or add a live-rate fetcher in Phase 9+.
# ---------------------------------------------------------------------------

_RATES_FROM_INR: dict[str, float] = {
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

SUPPORTED_CURRENCIES: list[str] = sorted(_RATES_FROM_INR.keys())


def get_rate(target_currency: str) -> float:
    """
    Return the exchange rate from INR to ``target_currency``.

    Raises
    ------
    ValueError
        If the currency code is not in the static rate table.
    """
    code = target_currency.upper()
    rate = _RATES_FROM_INR.get(code)
    if rate is None:
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
