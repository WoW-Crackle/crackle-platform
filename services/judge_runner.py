from app import create_app
from extensions import db
from models.submission import Submission

from judge.workspace import make_workspace_from_base
from judge.patch_apply import apply_patch
from judge.pytest_exec import run_pytest

CSRF_BASE_DIR = "/mnt/c/Users/726ja/crackle-challenges/CSRF"

def run_submission(submission_id: int):
    app = create_app()

    with app.app_context():
        sub = Submission.query.get(submission_id)
        if not sub:
            return {"ok": False, "message": f"submission not found: {submission_id}"}

        sub.status = "running"
        db.session.commit()

        try:
            workdir = make_workspace_from_base(CSRF_BASE_DIR)

            ok, reason = apply_patch(workdir, sub.submitted_code or "")
            if not ok:
                sub.status = "failed"
                if hasattr(sub, "error_message"):
                    sub.error_message = f"패치 적용 실패: {reason}"
                db.session.commit()
                return {"ok": False, "stage": "patch", "reason": reason}

            r = run_pytest(workdir, timeout_sec=90)

            sub.status = "passed" if r.exit_code == 0 else "failed"
            if hasattr(sub, "result_json"):
                sub.result_json = {
                    "exit_code": r.exit_code,
                    "duration_sec": r.duration_sec,
                    "stdout": r.stdout,
                    "stderr": r.stderr,
                }
            db.session.commit()

            return {"ok": True, "exit_code": r.exit_code, "status": sub.status}

        except Exception as e:
            sub.status = "error"
            if hasattr(sub, "error_message"):
                sub.error_message = f"채점 중 오류: {e}"
            db.session.commit()
            return {"ok": False, "stage": "exception", "error": str(e)}
