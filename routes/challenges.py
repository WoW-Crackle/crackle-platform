from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from extensions import db
from models.challenge import Challenge
from models.submission import Submission

from routes.auth import validate_access_token_or_401
from services.queue import judge_queue
from services.judge_runner import run_submission

challenges_bp = Blueprint("challenges", __name__)

def _now_utc():
    return datetime.now(timezone.utc)

@challenges_bp.route("/challenges/<int:challenge_id>/submissions", methods=["POST"])
def create_submission(challenge_id: int):
    # access token 검증
    user_id, err = validate_access_token_or_401()
    if err:
        return err

    # challenge 존재 확인
    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({"code": "not_found", "message": "해당 문제를 찾을 수 없습니다."}), 404

    # Request Body 검증
    data = request.get_json(silent=True) or {}
    submitted_code = (data.get("submitted_code") or "").strip()
    if not submitted_code:
        return jsonify({"code": "invalid_request", "message": "submitted_code가 필요합니다."}), 400

    # submission 생성
    submission = Submission(
        challenge_id=challenge_id,
        user_id=user_id,
        status="pending",
        submitted_code=submitted_code,
        created_at=_now_utc(),
    )
    db.session.add(submission)
    db.session.commit()

    # job enqueue
    try:
        job = judge_queue.enqueue(run_submission, submission.id)
        submission.job_id = job.id
        db.session.commit()
    except Exception:
        submission.status = "error"
        db.session.commit()
        return jsonify({"code": "internal_error", "message": "채점 작업 등록에 실패했습니다."}), 500

    return jsonify({
        "submission": {
            "id": submission.id,
            "challenge_id": submission.challenge_id,
            "user_id": submission.user_id,
            "status": submission.status,
            "created_at": submission.created_at.isoformat().replace("+00:00", "Z"),
        },
        "execution": {
            "job_id": submission.job_id,
            "status_url": f"/api/submissions/{submission.id}",
            "results_url": f"/api/submissions/{submission.id}/results",
        }
    }), 202