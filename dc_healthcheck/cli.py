"""Command-line entry point and strict configuration loading."""

import argparse
import math
from pathlib import Path
import sys
import tomllib

from .collectors import collect
from .core import Result, render_html, render_json, report, threshold

DEFAULTS = {"load": [1.0, 2.0], "memory": [80, 95], "disk": [80, 90],
            "paths": ["/"], "interfaces": [], "services": [], "timeout": 5}
EXIT_CODES = {"OK": 0, "WARNING": 1, "CRITICAL": 2, "UNKNOWN": 3}


def configuration(path=None):
    config = dict(DEFAULTS)
    if path:
        raw = Path(path).read_bytes()
        if len(raw) > 65536:
            raise ValueError("Configuration must be at most 64 KiB")
        data = tomllib.loads(raw.decode("utf-8"))
        if set(data) - set(DEFAULTS):
            raise ValueError("Unrecognized configuration keys")
        config.update(data)
    for key in ("load", "memory", "disk"):
        pair = config[key]
        if (not isinstance(pair, list) or len(pair) != 2
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in pair)
                or not 0 <= pair[0] < pair[1]
                or (key != "load" and pair[1] > 100)):
            raise ValueError(f"Invalid thresholds for {key}")
    for key in ("paths", "interfaces", "services"):
        values = config[key]
        if (not isinstance(values, list) or len(values) > 64
                or any(not isinstance(v, str) or not v or len(v) > 4096 for v in values)
                or len(set(values)) != len(values)):
            raise ValueError(f"Invalid list for {key}")
    if type(config["timeout"]) not in (int, float) or not 0 < config["timeout"] <= 30:
        raise ValueError("Timeout must be > 0 and <= 30 seconds")
    return config


def demo(config):
    return [threshold("load", 0.35, *config["load"], "load/CPU", "Inspect running tasks."),
            threshold("memory", 54.0, *config["memory"], "% used", "Inspect memory consumers."),
            threshold("disk:/demo-data", 93.0, *config["disk"], "% used", "Review capacity."),
            Result("interface:demo0", "WARNING", "Synthetic link is down", "Inspect cabling."),
            Result("service:demo.service", "OK", "Synthetic service is active")]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only Linux diagnostics. Demo runs on any OS.")
    parser.add_argument("--version", action="version", version="DC HealthCheck Pro 0.1.0")
    parser.add_argument("--demo", action="store_true", help="Use synthetic data, no host inspection")
    parser.add_argument("--config", type=Path, help="TOML configuration")
    parser.add_argument("--format", choices=("text", "json", "html"), default="text")
    parser.add_argument("--output", type=Path, help="Create a new report file; refuses overwrite")
    args = parser.parse_args(argv)
    try:
        config = configuration(args.config)
        if not args.demo and sys.platform != "linux":
            raise ValueError("Live checks require Linux; use --demo on this platform")
        results = demo(config) if args.demo else collect(config)
        data = report(results, "DEMO" if args.demo else "LIVE")
        if args.format == "json":
            output = render_json(data)
        elif args.format == "html":
            output = render_html(data)
        else:
            output = f"DC HealthCheck Pro | {data['mode']} | {data['status']}\n" + "\n".join(
                f"[{r.status}] {r.check}: {r.summary}\n  Next step: {r.recommendation}" for r in results) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(output)
        else:
            print(output, end="")
        return EXIT_CODES[data["status"]]
    except (OSError, ValueError, UnicodeError) as error:
        print(f"dc-healthcheck: {error}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
