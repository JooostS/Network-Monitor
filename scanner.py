# ---------- Imports ----------
import subprocess
import platform
import re
import threading
import socket
from typing import Dict, Any

# ---------- Regex Patterns ----------
MAC_WIN = re.compile(
    r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>([0-9a-f]{2}-){5}[0-9a-f]{2})",
    re.IGNORECASE,
)
MAC_UNIX = re.compile(
    r"\((?P<ip>\d+\.\d+\.\d+\.\d+)\)\s+at\s+(?P<mac>(([0-9a-f]{1,2}:){5}[0-9a-f]{1,2})|<incomplete>)",
    re.IGNORECASE,
)

# ---------- Common Ports ----------
COMMON_PORTS = [
    (53, "DNS"),
    (80, "HTTP"),
    (443, "HTTP"),
    (22, "TCP"),
    (445, "TCP"),
    (3389, "TCP"),
]

# ---------- ARP Parsing ----------
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

# ---------- Network Scanning ----------
def scan_network() -> Dict[str, Dict[str, Any]]:
    system = platform.system()
    devices: Dict[str, Dict[str, Any]] = {}
    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            devices = _parse_arp(system, result.stdout)
    except Exception:
        pass
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

# ---------- Ping Utilities ----------
def ping(host: str, timeout: int = 500):
    system = platform.system()
    count_flag = "-n" if system == "Windows" else "-c"
    try:
        if system == "Windows":
            cmd = ["ping", count_flag, "1", "-w", str(timeout), host]
        else:
            cmd = ["ping", count_flag, "1", "-W", str(max(1, int(timeout / 1000))), host]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return None
        m = re.search(r"time[=<]\s*(?P<val>\d+\.?\d*)\s*ms", result.stdout, re.IGNORECASE)
        if m:
            return float(m.group("val"))
        if "time<" in result.stdout:
            return 0.5
        return 0.0
    except Exception:
        return None

# ---------- Protocol Detection ----------
def detect_protocol(host: str, timeout_ms: int = 200) -> str:
    timeout = timeout_ms / 1000.0
    for port, label in COMMON_PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                return label
        except Exception:
            continue
    return "TCP"

# ---------- Concurrent Ping ----------
def threaded_ping(devices: Dict[str, Dict[str, Any]], callback=None):
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