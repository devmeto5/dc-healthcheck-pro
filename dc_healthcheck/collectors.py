"""Linux collectors. No shell, privilege escalation, or configuration changes."""

import os
from pathlib import Path
import re
import shutil
import subprocess

from .core import Result, threshold


def memory_percent(text):
    fields = {}
    for line in text.splitlines():
        key, _, rest = line.partition(":")
        if key in ("MemTotal", "MemAvailable"):
            parts = rest.split()
            if len(parts) != 2 or parts[1] != "kB":
                raise ValueError("Invalid memory units")
            fields[key] = int(parts[0])
    total, available = fields["MemTotal"], fields["MemAvailable"]
    if total <= 0 or not 0 <= available <= total:
        raise ValueError("Invalid memory measurements")
    return (total - available) / total * 100


def memory(config):
    value = memory_percent(Path("/proc/meminfo").read_text())
    return threshold("memory", value, *config["memory"], "% used",
                     "Inspect memory consumers and available RAM; investigate sustained pressure.")


def load(config):
    cpus = os.cpu_count()
    if not cpus:
        raise ValueError("CPU count unavailable")
    return threshold("load", os.getloadavg()[0] / cpus, *config["load"], "load/CPU",
                     "Inspect runnable tasks and I/O waits. Load is not CPU utilization.")


def disk(path, config):
    usage = shutil.disk_usage(path)
    if usage.total <= 0:
        raise ValueError("Filesystem capacity unavailable")
    return threshold(f"disk:{path}", usage.used / usage.total * 100, *config["disk"], "% used",
                     "Review capacity and retention policy; do not delete files without approval.")


def interface(name):
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", name) or name in (".", ".."):
        raise ValueError("Invalid interface name")
    state = (Path("/sys/class/net") / name / "operstate").read_text().strip()
    if state == "up":
        return Result(f"interface:{name}", "OK", "Operational state: up")
    if state in ("down", "lowerlayerdown", "notpresent", "dormant", "testing"):
        return Result(f"interface:{name}", "WARNING", f"Operational state: {state}",
                      "Check intended link state, cabling, optics, and switch port.")
    return Result(f"interface:{name}", "UNKNOWN", f"Operational state: {state}",
                  "Verify link state manually; this does not prove network reachability.")


def service(name, timeout):
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.@:-]{0,127}\.service", name):
        raise ValueError("Use an explicit valid .service unit name")
    executable = shutil.which("systemctl")
    if not executable:
        raise FileNotFoundError("systemctl unavailable")
    proc = subprocess.run([executable, "is-active", "--", name], capture_output=True,
                          text=True, timeout=timeout, check=False,
                          env={**os.environ, "LC_ALL": "C"})
    state = proc.stdout.strip()
    if proc.returncode == 0 and state == "active":
        return Result(f"service:{name}", "OK", "Service is active")
    if state in ("inactive", "failed"):
        return Result(f"service:{name}", "CRITICAL", f"Service is {state}",
                      "Inspect service logs and dependencies before attempting a restart.")
    return Result(f"service:{name}", "UNKNOWN", "Service state could not be confirmed",
                  "Verify that the unit exists and systemd is running; check permissions.")


def guarded(name, action):
    try:
        return action()
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        return Result(name, "UNKNOWN", f"Evidence unavailable ({type(error).__name__})",
                      "Check platform support, permissions, configuration, and command timeout.")


def collect(config):
    jobs = [("load", lambda: load(config)), ("memory", lambda: memory(config))]
    jobs += [(f"disk:{p}", lambda p=p: disk(p, config)) for p in config["paths"]]
    jobs += [(f"interface:{n}", lambda n=n: interface(n)) for n in config["interfaces"]]
    jobs += [(f"service:{n}", lambda n=n: service(n, config["timeout"])) for n in config["services"]]
    return [guarded(name, action) for name, action in jobs]
