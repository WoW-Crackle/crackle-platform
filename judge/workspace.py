import os
import shutil
import tempfile

class WorkspaceError(RuntimeError):
    pass

def get_base_dir(challenges_root: str, challenge_slug: str) -> str:
    base_dir = os.path.join(challenges_root, challenge_slug)
    if not os.path.isdir(base_dir):
        raise WorkspaceError(f"문제 베이스 디렉토리를 찾을 수 없습니다: {base_dir}")
    return base_dir

def make_workspace_from_base(base_dir: str) -> str:
    ws = tempfile.mkdtemp(prefix="crackle_ws_")
    repo_dir = os.path.join(ws, "repo")
    shutil.copytree(base_dir, repo_dir, dirs_exist_ok=True)
    return repo_dir