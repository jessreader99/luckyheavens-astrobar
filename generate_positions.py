#!/usr/bin/env python3
import json
import datetime as dt
import swisseph as swe
from pathlib import Path

PLANETS = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS),
    ("Mars", swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN),
]

SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
              "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
PLANET_GLYPHS = {"Sun":"☉","Moon":"☽","Mercury":"☿","Venus":"♀","Mars":"♂","Jupiter":"♃","Saturn":"♄"}

def jd_from_utc(u: dt.datetime) -> float:
    hour = u.hour + u.minute/60 + u.second/3600
    return swe.julday(u.year, u.month, u.day, hour, swe.GREG_CAL)

def norm(x: float) -> float:
    return (x + 360.0) % 360.0

def sign_index(lon: float) -> int:
    return int(norm(lon) // 30) % 12

def deg_in_sign(lon: float) -> float:
    return norm(lon) % 30.0

def main():
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    now = dt.datetime.now(dt.timezone.utc)
    jd = jd_from_utc(now)

    planets = []
    for name, pid in PLANETS:
        vals = swe.calc_ut(jd, pid, flags)[0]
        lon = float(vals[0])
        spd = float(vals[3]) if len(vals) > 3 else 0.0
        si = sign_index(lon)
        planets.append({
            "planet": name,
            "planetGlyph": PLANET_GLYPHS.get(name, ""),
            "sign": SIGN_NAMES[si],
            "signGlyph": SIGN_GLYPHS[si],
            "deg": round(deg_in_sign(lon), 2),
            "retrograde": bool(spd < 0),
        })

    payload = {
        "generatedAtUTC": now.isoformat().replace("+00:00", "Z"),
        "planets": planets
    }

    out_dir = Path("site")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "positions.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    main()
