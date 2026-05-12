from __future__ import annotations

# Default time stretch per fermata shape, modeled on MuseScore 4's playback
# defaults so audio rendered from converted projects matches MuseScore output
# for typical scores.
FERMATA_STRETCH: dict[str, float] = {
    "": 1.5,
    "normal": 1.5,
    "angled": 1.25,
    "short": 1.25,
    "square": 2.0,
    "long": 2.0,
    "double-square": 3.0,
    "double-dot": 3.0,
    "very-long": 3.0,
    "half-curve": 1.75,
    "curlew": 1.75,
    "double-angled": 1.75,
}
