"""
enigma_config.py — Central numeric constants for ENIGMA APEX

Edit these values to tune system behaviour without touching algorithm code.
Values are grouped by subsystem; all constants are module-level so any file
can do:

    from enigma_config import KELLY_FRACTION_CAP, ATR_STOP_LOSS_MULTIPLE

"""

# ---------------------------------------------------------------------------
# Kelly Criterion / Position Sizing
# ---------------------------------------------------------------------------

KELLY_FRACTION_CAP: float = 0.25
"""Maximum Kelly fraction applied. No single trade risks more than this
fraction of capital regardless of what the formula produces."""

# ---------------------------------------------------------------------------
# ATR-Based Stop / Target Distances
# ---------------------------------------------------------------------------

ATR_STOP_LOSS_MULTIPLE: float = 1.5
"""Stop-loss distance = ATR × this value."""

ATR_PROFIT_TARGET_MULTIPLE: float = 2.0
"""Profit-target distance = ATR × this value (1.33 R:R at default stop)."""

# ---------------------------------------------------------------------------
# Edge / Signal Validation
# ---------------------------------------------------------------------------

MIN_POWER_SCORE: int = 15
"""Minimum Enigma power-score to consider a setup tradeable."""

CADENCE_THRESHOLD_AM: int = 2
"""Max consecutive cadence failures before flagging a high-probability AM setup."""

CADENCE_THRESHOLD_PM: int = 3
"""Max consecutive cadence failures before flagging a high-probability PM setup."""

MIN_VOLUME_SURGE: float = 1.5
"""Volume must be at least this multiple of the rolling average to qualify as a surge."""

# ---------------------------------------------------------------------------
# OCR / Computer-Vision Thresholds
# ---------------------------------------------------------------------------

OCR_ACTIVATION_PIXEL_THRESHOLD: int = 100
"""Minimum HSV-masked pixel count to treat a confluence level or MACVU state
as active. Raise this if false positives appear; lower it if valid signals are
missed on darker screens."""

OCR_COLOR_SIGNAL_MIN_PIXELS: int = 50
"""Minimum dominant-colour pixel count for the final 'is any signal present'
check in the single-chart OCR reader. Below this the reader returns 'NONE'."""

OCR_CONFIDENCE_THRESHOLD: int = 60
"""Minimum Tesseract confidence score (0–100) for accepting a text reading."""
