"""Engine analisis: gabungkan data market -> kirim ke Groq -> hasilkan setup."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from . import config
from .clients import APIError, GroqClient, SoSoValueClient, TwelveDataClient


@dataclass
class AnalysisResult:
    symbol: str = ""
    interval: str = ""
    current_price: float | None = None
    candles_count: int = 0
    twelvedata_ok: bool = False
    sosovalue_note: str = ""
    sosovalue_count: int = 0
    stats: dict = field(default_factory=dict)
    ai_raw: str = ""
    setup: dict | None = None
    error: str = ""


def _candles_to_text(candles: list[dict], limit: int = 80) -> str:
    """Format ringkas candle untuk prompt (hemat token)."""
    subset = candles[-limit:]
    lines = ["time,O,H,L,C"]
    for c in subset:
        lines.append(f"{c['time']},{c['open']},{c['high']},{c['low']},{c['close']}")
    return "\n".join(lines)


def _compute_stats(candles: list[dict]) -> dict:
    closes = [c["close"] for c in candles]
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    last = candles[-1]
    # Trend sederhana: bandingkan close vs MA(20) & struktur 3 swing terakhir
    ma20 = sum(closes[-20:]) / min(20, len(closes))
    swing_high = max(highs[-30:]) if len(highs) >= 5 else max(highs)
    swing_low = min(lows[-30:]) if len(lows) >= 5 else min(lows)
    # ATR kasar 14
    trs = []
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["high"], candles[i]["low"], candles[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    atr = sum(trs[-14:]) / max(1, len(trs[-14:])) if trs else 0
    return {
        "last_time": last["time"],
        "last_close": last["close"],
        "ma20": round(ma20, 6),
        "swing_high_30": round(swing_high, 6),
        "swing_low_30": round(swing_low, 6),
        "atr14": round(atr, 6),
        "bias_ma": "ABOVE MA20 (bullish)" if last["close"] > ma20 else "BELOW MA20 (bearish)",
    }


def _extract_json(text: str) -> dict | None:
    """Ambil JSON dari respons AI (bisa dibungkus markdown fence)."""
    t = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.DOTALL)
    if fence:
        t = fence.group(1)
    else:
        # Cari objek JSON terluar
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            t = t[start:end + 1]
    try:
        obj = json.loads(t)
        return obj if isinstance(obj, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


def _build_prompts(symbol: str, interval: str, candles: list[dict],
                   stats: dict, settings: dict) -> tuple[str, str]:
    method = config.method_by_code(settings["analysis_method"])
    method_name = method["name"] if method else settings["analysis_method"]
    method_desc = method["desc"] if method else ""

    system = (
        "Kamu adalah analis teknikal profesional spesialis forex & crypto. "
        "Baca data candle (OHLC) yang diberikan, identifikasi struktur pasar & chart pattern, "
        "lalu hasilkan satu setup trading yang jelas. Jawab HANYA dalam format JSON, tanpa teks lain. "
        "Field wajib: setup (BUY/SELL/WAIT), pattern (nama pola), confidence (0-100), "
        "entry (harga masuk), stop_loss, take_profit (array 1-3 level), risk_reward, "
        "invalidation (kondisi batal), key_levels (array level penting), "
        "bias (arah tren), reasoning (penjelasan singkat 3-5 poin, bahasa Indonesia)."
    )

    candle_text = _candles_to_text(candles)
    user = f"""INSTRUMEN: {symbol}
TIMEFRAME: {interval}
METODE ANALISIS: {method_name} — {method_desc}
PENGATURAN TRADE: Risk:Reward = {settings['risk_reward']}, Target = {settings['target_pips']} pips

STATISTIK SEDERHANA:
- Close terakhir: {stats['last_close']} @ {stats['last_time']}
- MA20: {stats['ma20']} → harga {stats['bias_ma']}
- Swing high (30 candle): {stats['swing_high_30']}
- Swing low (30 candle): {stats['swing_low_30']}
- ATR14 (volatilitas): {stats['atr14']}

DATA CANDLE (terlama → terbaru, format time,O,H,L,C):
{candle_text}

Berdasarkan metode {method_name}, tentukan setup terbaik saat ini.
Jika tidak ada setup valid, isi setup="WAIT" dan jelaskan alasannya.
Pastikan entry, stop_loss, take_profit masuk akal terhadap harga & ATR saat ini.
Jawab HANYA JSON."""
    return system, user


def run_analysis(symbol: str, interval: str, settings: dict) -> AnalysisResult:
    res = AnalysisResult(symbol=symbol.upper(), interval=interval)

    # 1. Ambil data TwelveData (utama)
    td = TwelveDataClient()
    try:
        candles = td.get_candles(symbol, interval, outputsize=140)
        res.twelvedata_ok = True
        res.candles_count = len(candles)
        res.current_price = candles[-1]["close"]
        res.stats = _compute_stats(candles)
    except APIError as e:
        res.error = str(e)
        return res

    # 2. Ambil data SoSoValue (tambahan, opsional) — untuk crypto perp / saham
    ssv = SoSoValueClient()
    if ssv.ready():
        ssv_candles, note = ssv.get_candles(symbol, interval, limit=140)
        res.sosovalue_note = note
        res.sosovalue_count = len(ssv_candles)
    else:
        res.sosovalue_note = "SOSOVALUE_API_KEY belum diisi — data ini dilewati."

    # 3. Analisis oleh Groq
    groq = GroqClient()
    if not groq.ready():
        res.error = "GROQ_API_KEY belum diisi. Buka menu [3] Env."
        return res

    system, user = _build_prompts(symbol, interval, candles, res.stats, settings)
    try:
        raw = groq.chat(system, user)
        res.ai_raw = raw
        res.setup = _extract_json(raw)
    except APIError as e:
        res.error = str(e)
    return res
