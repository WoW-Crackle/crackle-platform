import subprocess
import time
from dataclasses import dataclass

@dataclass(frozen=True)
class PytestResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_sec: float

def run_pytest(workdir: str, timeout_sec: int = 60) -> PytestResult:
    start = time.time()
    p = subprocess.run(
        ["pytest", "-q"],
        cwd=workdir,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
    )
    end = time.time()
    return PytestResult(
        exit_code=p.returncode,
        stdout=p.stdout[-20000:],  
        stderr=p.stderr[-20000:],
        duration_sec=round(end - start, 3),
    )