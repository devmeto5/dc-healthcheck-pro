"""Portable evaluation and reporting; collectors are kept separate."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
import json
import math


@dataclass(frozen=True)
class Result:
    check: str
    status: str
    summary: str
    recommendation: str = "No action required."
    value: float | None = None
    unit: str | None = None


def threshold(check, value, warning, critical, unit, recommendation):
    if not all(math.isfinite(v) for v in (value, warning, critical)):
        raise ValueError("Measurements and thresholds must be finite")
    if not 0 <= warning < critical or value < 0:
        raise ValueError("Expected a nonnegative value and 0 <= warning < critical")
    status = "CRITICAL" if value >= critical else "WARNING" if value >= warning else "OK"
    return Result(check, status, f"{value:.2f} {unit}; warning >= {warning}, critical >= {critical}",
                  recommendation if status != "OK" else "No action required.", round(value, 3), unit)


def overall(results):
    statuses = {r.status for r in results}
    for status in ("CRITICAL", "UNKNOWN", "WARNING"):
        if status in statuses:
            return status
    return "OK" if results else "UNKNOWN"


def report(results, mode):
    return {"schema_version": "1.0", "tool_version": "0.1.0", "mode": mode,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": overall(results), "checks": [asdict(r) for r in results]}


def render_json(data):
    return json.dumps(data, indent=2, allow_nan=False) + "\n"


def render_html(data):
    def e(value):
        return escape(str(value), quote=True)
    rows = "".join(f"<tr><td>{e(r['check'])}</td><td>{e(r['status'])}</td>"
                   f"<td>{e(r['summary'])}</td><td>{e(r['recommendation'])}</td></tr>"
                   for r in data["checks"])
    return ("<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>DC HealthCheck Pro report</title><style>"
            "body{font:16px system-ui;margin:3rem auto;padding:0 1rem;max-width:1100px;color:#172438}"
            "table{border-collapse:collapse;width:100%}td,th{padding:12px;text-align:left;"
            "border-bottom:1px solid #ccd5df;vertical-align:top}th{background:#edf3fa}"
            "h1{color:#125b82}.table{overflow-x:auto}footer{margin-top:2rem;color:#526171}"
            "</style><h1>DC HealthCheck Pro</h1>"
            f"<p><strong>{e(data['status'])}</strong> · Mode: {e(data['mode'])} · "
            f"{e(data['generated_at'])}</p><div class='table'><table>"
            "<thead><tr><th>Check</th><th>Status</th><th>Evidence</th><th>Next step</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div><footer>"
            "Point-in-time assessment. UNKNOWN means evidence was unavailable. "
            "DEMO reports contain synthetic data. No remediation was performed.</footer></html>")
