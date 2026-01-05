import subprocess

def apply_patch(workdir: str, patch_text: str) -> tuple[bool, str]:
    subprocess.run(["git", "init"], cwd=workdir, capture_output=True, text=True)
    p = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "-"],
        cwd=workdir,
        input=patch_text,
        text=True,
        capture_output=True,
    )
    if p.returncode != 0:
        return False, (p.stderr or p.stdout or "patch 적용 실패")
    return True, ""