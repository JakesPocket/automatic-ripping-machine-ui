"""Read MakeMKV rip progress from ARM progress files.

MakeMKV writes real-time PRGV/PRGC messages to a dedicated progress file
at {LOGPATH}/progress/{job_id}.log via the ``--progress=`` flag.  This is
separate from the main job log which only receives this data after the
subprocess completes (stdout is buffered by subprocess.run).
"""
import logging
import os
import re

from backend.config import settings

log = logging.getLogger(__name__)


def _parse_progress_lines(lines: list[str]) -> tuple:
    """Scan MakeMKV progress lines and return (last_prgv, last_prgc, last_prgt)."""
    last_prgv = None
    last_prgc = None
    last_prgt = None
    for line in lines:
        if line.startswith("PRGT:"):
            m = re.match(r'PRGT:\d+,\d+,"([^"]+)"', line)
            if m:
                last_prgt = m.group(1)
        elif line.startswith("PRGV:"):
            m = re.match(r"PRGV:(\d+),(\d+),(\d+)", line)
            if m:
                last_prgv = m
        elif line.startswith("PRGC:"):
            m = re.match(r'PRGC:\d+,(\d+),"([^"]+)"', line)
            if m:
                last_prgc = m
    return last_prgv, last_prgc, last_prgt


def get_rip_progress(job_id: int) -> dict:
    """Parse MakeMKV progress from a job's progress file.

    Returns {"progress": float | None, "stage": str | None}
    """
    result: dict = {"progress": None, "stage": None}

    path = os.path.join(settings.arm_log_path, "progress", f"{job_id}.log")
    if not os.path.isfile(path):
        return result

    try:
        with open(path, "rb") as f:
            data = f.read().decode("utf-8", errors="replace")
    except OSError:
        return result

    last_prgv, last_prgc, last_prgt = _parse_progress_lines(data.splitlines())

    if last_prgv:
        total = int(last_prgv.group(2))
        maximum = int(last_prgv.group(3))
        if maximum > 0:
            is_rip_phase = last_prgt and "Saving" in last_prgt
            if is_rip_phase:
                result["progress"] = round(total / maximum * 100, 1)
            else:
                result["stage"] = last_prgt

    if last_prgc:
        index = int(last_prgc.group(1)) + 1
        name = last_prgc.group(2)
        result["stage"] = f"Title {index}: {name}"

    return result
