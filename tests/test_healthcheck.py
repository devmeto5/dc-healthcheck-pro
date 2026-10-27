import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from dc_healthcheck import collectors
from dc_healthcheck.cli import configuration, main
from dc_healthcheck.core import Result, overall, render_html, report, threshold


class EvaluationTests(unittest.TestCase):
    def test_inclusive_threshold_boundaries(self):
        for value, expected in [(0, "OK"), (79.99, "OK"), (80, "WARNING"), (90, "CRITICAL")]:
            with self.subTest(value=value):
                self.assertEqual(threshold("disk", value, 80, 90, "%", "Review").status, expected)

    def test_invalid_measurements(self):
        for value in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                threshold("disk", value, 80, 90, "%", "Review")

    def test_unknown_does_not_mask_known_critical(self):
        results = [Result("a", "UNKNOWN", "missing"), Result("b", "CRITICAL", "bad")]
        self.assertEqual(overall(results), "CRITICAL")
        self.assertEqual(overall(results[:1] + [Result("c", "WARNING", "warn")]), "UNKNOWN")
        self.assertEqual(overall([]), "UNKNOWN")

    def test_report_escapes_untrusted_html(self):
        html = render_html(report([Result("<script>alert(1)</script>", "UNKNOWN", '<img src=x>')], "DEMO"))
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img", html)
        self.assertIn("&lt;script&gt;", html)


class CollectorTests(unittest.TestCase):
    def test_memory_uses_available_not_free(self):
        self.assertEqual(collectors.memory_percent("MemTotal: 1000 kB\nMemFree: 100 kB\nMemAvailable: 600 kB"), 40)

    def test_bad_memory_evidence(self):
        for text in ("", "MemTotal: 0 kB\nMemAvailable: 0 kB", "MemTotal: 1 kB\nMemAvailable: 2 kB",
                     "MemTotal: 100 MB\nMemAvailable: 20 kB"):
            with self.subTest(text=text), self.assertRaises((ValueError, KeyError)):
                collectors.memory_percent(text)

    def test_permission_failure_is_unknown(self):
        def denied():
            raise PermissionError("private detail")
        result = collectors.guarded("memory", denied)
        self.assertEqual(result.status, "UNKNOWN")
        self.assertNotIn("private detail", result.summary)

    def test_command_timeout_is_unknown(self):
        with patch("dc_healthcheck.collectors.shutil.which", return_value="/bin/systemctl"), \
             patch("dc_healthcheck.collectors.subprocess.run", side_effect=subprocess.TimeoutExpired("systemctl", 1)):
            result = collectors.guarded("service:x.service", lambda: collectors.service("x.service", 1))
        self.assertEqual(result.status, "UNKNOWN")

    def test_service_states_and_safe_arguments(self):
        for code, state, expected in [(0, "active", "OK"), (3, "inactive", "CRITICAL"),
                                      (3, "failed", "CRITICAL"), (4, "unknown", "UNKNOWN"),
                                      (1, "", "UNKNOWN"), (3, "activating", "UNKNOWN")]:
            with self.subTest(state=state), \
                 patch("dc_healthcheck.collectors.shutil.which", return_value="/bin/systemctl"), \
                 patch("dc_healthcheck.collectors.subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess([], code, state, "")
                self.assertEqual(collectors.service("sshd.service", 5).status, expected)
                self.assertEqual(run.call_args.args[0], ["/bin/systemctl", "is-active", "--", "sshd.service"])
                self.assertNotIn("shell", run.call_args.kwargs)
                self.assertEqual(run.call_args.kwargs["timeout"], 5)

    def test_reject_command_and_path_injection(self):
        for name in ("--help", "a;touch x.service", "../x.service"):
            with self.assertRaises(ValueError):
                collectors.service(name, 5)
        for name in ("../etc", "..", ".", "eth0/../../etc"):
            with self.assertRaises(ValueError):
                collectors.interface(name)

    def test_interface_states(self):
        for state, expected in [("up", "OK"), ("down", "WARNING"), ("unknown", "UNKNOWN")]:
            with patch.object(Path, "read_text", return_value=state):
                self.assertEqual(collectors.interface("eth0").status, expected)

    def test_load_normalization(self):
        with patch("dc_healthcheck.collectors.os.cpu_count", return_value=4), \
             patch("dc_healthcheck.collectors.os.getloadavg", return_value=(4, 2, 1), create=True):
            result = collectors.load(configuration())
        self.assertEqual(result.status, "WARNING")
        self.assertEqual(result.value, 1)

    def test_disk_threshold(self):
        with patch("dc_healthcheck.collectors.shutil.disk_usage") as usage:
            usage.return_value.total = 100
            usage.return_value.used = 90
            self.assertEqual(collectors.disk("/", configuration()).status, "CRITICAL")


class ConfigAndCliTests(unittest.TestCase):
    def test_invalid_configurations(self):
        cases = ['disk = [90, 80]', 'disk = [80, 101]', 'memory = [true, 95]',
                 'load = [1, inf]', 'timeout = nan', 'timeout = 0', 'timeout = true',
                 'paths = "/"', 'paths = ["/", "/"]', 'typo = 1', 'broken = [']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            for text in cases:
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        configuration(path)

    def test_valid_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text('disk = [70, 85]\nservices = ["sshd.service"]', encoding="utf-8")
            self.assertEqual(configuration(path)["disk"], [70, 85])

    def test_demo_never_collects_live_data(self):
        with patch("dc_healthcheck.cli.collect", side_effect=AssertionError("Live collection forbidden")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            code = main(["--demo", "--format", "json"])
        data = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(data["mode"], "DEMO")
        self.assertEqual(data["schema_version"], "1.0")
        self.assertEqual(len(data["checks"]), 5)

    def test_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.html"
            self.assertEqual(main(["--demo", "--format", "html", "--output", str(path)]), 2)
            original = path.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["--demo", "--output", str(path)]), 3)
            self.assertEqual(path.read_bytes(), original)

    def test_unsupported_live_platform(self):
        with patch("dc_healthcheck.cli.sys.platform", "win32"), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main([]), 3)

    def test_module_entry_point(self):
        proc = subprocess.run([sys.executable, "-m", "dc_healthcheck", "--demo", "--format", "json"],
                              capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stdout)["status"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
