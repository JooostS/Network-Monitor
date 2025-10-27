import subprocess
import platform
import re
import threading
import socket
from typing import Dict, Any

# Regexes for ARP output (Windows / Unix)
MAC_WIN = re.compile(
    r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>([0-9a-f]{2}-){5}[0-9a-f]{2})",
    re.IGNORECASE,
)
MAC_UNIX = re.compile(
    r"\((?P<ip>\d+\.\d+\.\d+\.\d+)\)\s+at\s+(?P<mac>(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})|<incomplete>)",
    re.IGNORECASE,
)

# Lightweight set of common ports → protocol label
COMMON_PORTS = [
    (53, "DNS"),
    (80, "HTTP"),
    (443, "HTTP"),   # show HTTPS as HTTP for simplified UI
    (22, "TCP"),     # SSH → TCP label (per requested set)
    (445, "TCP"),    # SMB
    (3389, "TCP"),   # RDP
]


def _parse_arp(system: str, text: str):
    devices = {}
    if system == "Windows":
        for m in MAC_WIN.finditer(text):
            ip = m.group("ip")
            mac = m.group("mac").lower().replace("-", ":")
            devices[ip] = {
                "mac": mac, "status": "Offline", "ping": None,
                "history": [], "protocol": ""
            }
    else:
        for m in MAC_UNIX.finditer(text):
            ip = m.group("ip")
            mac = m.group("mac").lower()
            if mac == "<incomplete>":
                mac = ""
            devices[ip] = {
                "mac": mac, "status": "Offline", "ping": None,
                "history": [], "protocol": ""
            }
    return devices


def scan_network() -> Dict[str, Dict[str, Any]]:
    """Return devices from the ARP cache. On Linux, fall back to `ip neigh`."""
    system = platform.system()
    devices: Dict[str, Dict[str, Any]] = {}

    # Try `arp -a`
    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            devices = _parse_arp(system, result.stdout)
    except Exception:
        pass

    # Linux fallback: `ip neigh`
    if not devices and system in ("Linux",):
        try:
            res = subprocess.run(["ip", "neigh"], capture_output=True, text=True)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    m = re.search(
                        r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+.*lladdr\s+(?P<mac>([0-9a-f]{2}:){5}[0-9a-f]{2})",
                        line,
                        re.I,
                    )
                    if m:
                        ip = m.group("ip")
                        mac = m.group("mac").lower()
                        devices[ip] = {
                            "mac": mac, "status": "Offline", "ping": None,
                            "history": [], "protocol": ""
                        }
        except Exception:
            pass

    return devices


def ping(host: str, timeout: int = 500):
    """Ping once and return latency in ms (float), or None if unreachable."""
    system = platform.system()
    count_flag = "-n" if system == "Windows" else "-c"

    try:
        if system == "Windows":
            # -w timeout is ms on Windows
            cmd = ["ping", count_flag, "1", "-w", str(timeout), host]
        else:
            # -W timeout is seconds on Unix
            cmd = ["ping", count_flag, "1", "-W", str(max(1, int(timeout / 1000))), host]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return None

        # Supports "time=12ms", "time=12.3 ms", "time<1ms"
        m = re.search(r"time[=<]\s*(?P<val>\d+\.?\d*)\s*ms", result.stdout, re.IGNORECASE)
        if m:
            return float(m.group("val"))
        if "time<" in result.stdout:
            return 0.5
        return 0.0
    except Exception:
        return None


def detect_protocol(host: str, timeout_ms: int = 200) -> str:
    """Very small TCP probe on a few ports to infer a protocol label."""
    timeout = timeout_ms / 1000.0
    for port, label in COMMON_PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                return label
        except Exception:
            continue
    return "TCP"  # generic fallback if nothing responds


def threaded_ping(devices: Dict[str, Dict[str, Any]], callback=None):
    """Ping all IPs concurrently; call callback(ip, info) for each result."""
    threads = []

    def worker(ip: str, info: Dict[str, Any]):
        latency = ping(ip)
        info["ping"] = latency
        info["status"] = "Online" if latency is not None else "Offline"
        info["history"].append(info["status"])
        if info["status"] == "Online":
            try:
                info["protocol"] = detect_protocol(ip)
            except Exception:
                info["protocol"] = "TCP"
        if callback:
            try:
                callback(ip, info)
            except Exception:
                pass

    for ip, info in devices.items():
        t = threading.Thread(target=worker, args=(ip, info), daemon=True)
        t.start()
        threads.append(t)

    return threads