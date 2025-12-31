from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User
from models.refresh_token import RefreshToken
import re
import jwt
import uuid

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# 이메일 형식 검증 정규식
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# 토큰 만료 정책 설정 
ACCESS_EXPIRES_MIN = 30
REFRESH_EXPIRES_DAYS = 14

# 모든 토큰 시간 계산은 UTC 기준 
def _now_utc():
    return datetime.now(timezone.utc)

# Authorization 헤더에서 Bearer 토큰 추출
def _get_bearer_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth.split(" ", 1)[1].strip()

# 앱 설정의 SECRET_KEY로 JWT 서명 
def _encode_jwt(payload: dict) -> str:
    secret = current_app.config.get("SECRET_KEY")
    return jwt.encode(payload, secret, algorithm="HS256")

# JWT 검증/디코딩 
def _decode_jwt(token: str) -> dict:
    secret = current_app.config.get("SECRET_KEY")
    return jwt.decode(token, secret, algorithms=["HS256"])

# 로그인 성공 시 access/refresh JWT 발급 + refresh 토큰 DB 저장
def _issue_tokens(user: User):
    now = _now_utc()

    access_payload = {
        "sub": str(user.id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_EXPIRES_MIN)).timestamp()),
    }

    refresh_jti = uuid.uuid4().hex
    refresh_exp = now + timedelta(days=REFRESH_EXPIRES_DAYS)
    refresh_payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": refresh_jti,
        "iat": int(now.timestamp()),
        "exp": int(refresh_exp.timestamp()),
    }

    access_token = _encode_jwt(access_payload)
    refresh_token = _encode_jwt(refresh_payload)

    # refresh token을 서버(DB)에 저장
    db.session.add(
        RefreshToken(
            jti=refresh_jti,
            user_id=user.id,
            revoked=False,
            expires_at=refresh_exp,
        )
    )
    db.session.commit()

    return access_token, refresh_token

# 보호된 API에서 access token 검증 
def validate_access_token_or_401():
    token = _get_bearer_token()
    if not token:
        return None, (
            jsonify({"code": "invalid_token", "message": "유효하지 않거나 만료된 토큰입니다."}),
            401,
        )
    try:
        payload = _decode_jwt(token)
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("wrong token type")
        user_id = int(payload.get("sub"))
        return user_id, None
    except Exception:
        return None, (
            jsonify({"code": "invalid_token", "message": "유효하지 않거나 만료된 토큰입니다."}),
            401,
        )

# 필수 필드 존재 여부 검증 및 형식/제약조건 검증
def validate_register_payload(data: dict):
    errors = {}

    # username 
    username = data.get("username")
    if not username or not isinstance(username, str):
        errors.setdefault("username", []).append("사용자 이름은 필수입니다.")

    # email 
    email = data.get("email")
    if not email or not isinstance(email, str):
        errors.setdefault("email", []).append("이메일은 필수입니다.")
    elif not EMAIL_REGEX.match(email):
        errors.setdefault("email", []).append("이메일 형식이 올바르지 않습니다.")
    
    # password
    password = data.get("password")
    if not password or not isinstance(password, str):
        errors.setdefault("password", []).append("비밀번호는 필수입니다.")
    else:
        # 최소 10자
        if len(password) < 10:
            errors.setdefault("password", []).append("비밀번호는 최소 10자 이상이어야 합니다.")
        # 대문자 / 소문자 / 숫자 / 특수문자 각각 최소 1개
        if not re.search(r"[A-Z]", password):
            errors.setdefault("password", []).append("대문자를 최소 1자 이상 포함해야 합니다.")
        if not re.search(r"[a-z]", password):
            errors.setdefault("password", []).append("소문자를 최소 1자 이상 포함해야 합니다.")
        if not re.search(r"[0-9]", password):
            errors.setdefault("password", []).append("숫자를 최소 1자 이상 포함해야 합니다.")
        if not re.search(r"[^A-Za-z0-9]", password):
            errors.setdefault("password", []).append("특수문자를 최소 1자 이상 포함해야 합니다.")
    
    # password_confirm 
    password_confirm = data.get("password_confirm")
    if not password_confirm or not isinstance(password_confirm, str):
        errors.setdefault("password_confirm", []).append("비밀번호 확인은 필수입니다.")
    elif password and password_confirm != password:
        errors.setdefault("password_confirm", []).append("비밀번호가 일치하지 않습니다.")

    if errors:
        return None, errors

    cleaned = {
        "username": username.strip() if isinstance(username, str) else username,
        "email": email.strip().lower() if isinstance(email, str) else email,
        "password": password,
    }
    return cleaned, None


@auth_bp.route("/register", methods=["POST"])
def register():
    # Content-Type 및 JSON 파싱
    if not request.is_json:
        return (
            jsonify(
                {
                    "code": "validation_error",
                    "errors": {
                        "body": ["Content-Type은 application/json 이어야 합니다."]
                    },
                }
            ),
            422,
        )

    data = request.get_json(silent=True) or {}
    cleaned, validation_errors = validate_register_payload(data)

    # 422 – 유효성 검증 실패
    if validation_errors:
        return jsonify({"code": "validation_error", "errors": validation_errors}), 422

    username = cleaned["username"]
    email = cleaned["email"]
    password = cleaned["password"]

    # 409 – 중복 체크 (username / email)
    duplicate_errors = {}

    if User.query.filter_by(name=username).first():
        duplicate_errors.setdefault("username", []).append("이미 사용 중인 사용자 이름입니다.")

    if User.query.filter_by(email=email).first():
        duplicate_errors.setdefault("email", []).append("이미 사용 중인 이메일입니다.")

    if duplicate_errors:
        return jsonify({"code": "duplicate", "errors": duplicate_errors}), 409

    # 사용자 생성 (role은 기본값 'user')
    hashed_password = generate_password_hash(password)

    user = User(
        name=username,
        email=email,
        password=hashed_password,
        # role 컬럼은 모델의 default='user' 사용
    )
    db.session.add(user)
    db.session.commit()

    # created_at을 ISO 8601 + Z(UTC) 포맷으로 변환
    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    created_at_str = created_at.isoformat().replace("+00:00", "Z")

    response_body = {
        "user_id": user.id,
        "username": user.name,
        "email": user.email,
        "created_at": created_at_str,
    }

    return jsonify(response_body), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return (
            jsonify(
                {
                    "code": "validation_error",
                    "errors": {
                        "body": ["Content-Type은 application/json 이어야 합니다."]
                    },
                }
            ),
            422,
        )

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    errors = {}

    if not email:
        errors.setdefault("email", []).append("필수 입력 항목입니다.")
    if not password:
        errors.setdefault("password", []).append("필수 입력 항목입니다.")

    if errors:
        return jsonify({"code": "validation_error", "errors": errors}), 422

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return (
            jsonify(
                {
                    "code": "invalid_credentials",
                    "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
                }
            ),
            401,
        )
    
    # JWT access/refresh 발급 + refresh DB 저장
    access_token, refresh_token = _issue_tokens(user)

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.name,
                },
            }
        ),
        200,
    )

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # Content-Type / JSON 검증 (422)
    if not request.is_json:
        return (
            jsonify(
                {"code": "validation_error", "errors": {"body": ["Content-Type은 application/json 이어야 합니다."]}}
            ),
            422,
        )
    
    # access token 검증 (401)
    user_id, err = _validate_access_token_or_401()
    if err:
        return err
    
    data = request.get_json(silent=True) or {}
    refresh_token = data.get("refresh_token")
    all_devices = bool(data.get("all_devices", False))

    # refresh_token 필수 (422)
    if not refresh_token or not isinstance(refresh_token, str):
        return jsonify({"code": "validation_error", "errors": {"refresh_token": ["필수 입력 항목입니다."]}}), 422

    # refresh token decode -> jti/user_id 확인
    try:
        payload = _decode_jwt(refresh_token)
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError("wrong token type")
        refresh_user_id = int(payload.get("sub"))
        jti = payload.get("jti")
        if not jti:
            raise jwt.InvalidTokenError("missing jti")
    except Exception:
        # 유효하지 않은 refresh 토큰은 "찾을 수 없음"으로 처리 (명세 404)
        return (
            jsonify({"code": "refresh_token_not_found", "message": "Refresh token을 찾을 수 없습니다."}),
            404,
        )

    # access token의 사용자와 refresh token의 사용자가 다르면 거부
    if refresh_user_id != user_id:
        return (
            jsonify({"code": "refresh_token_not_found", "message": "Refresh token을 찾을 수 없습니다."}),
            404,
        )

    if all_devices:
        # 해당 유저의 모든 refresh 토큰 무효화
        updated = (
            RefreshToken.query.filter_by(user_id=user_id, revoked=False)
            .update({"revoked": True})
        )
        db.session.commit()

        if updated == 0:
            return (
                jsonify({"code": "refresh_token_not_found", "message": "Refresh token을 찾을 수 없습니다."}),
                404,
            )

        return jsonify({"message": "Logged out successfully."}), 200

    # 단일 토큰 무효화
    rt = RefreshToken.query.filter_by(jti=jti, user_id=user_id).first()
    if not rt or rt.revoked:
        return (
            jsonify({"code": "refresh_token_not_found", "message": "Refresh token을 찾을 수 없습니다."}),
            404,
        )

    rt.revoked = True
    db.session.commit()

    return jsonify({"message": "Logged out successfully."}), 200