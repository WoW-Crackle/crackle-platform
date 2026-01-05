import os
import re
from dataclasses import dataclass
from urllib.parse import urljoin
import pytest
import requests


@dataclass(frozen=True)
class AppConfig:
    base_url: str        # 서버 주소 
    username: str        # 테스트 계정 아이디
    password: str        # 테스트 계정 비밀번호
    csrf_field_name: str # CSRF 토큰 필드 이름


# 환경변수에서 값을 읽어오고, 없으면 기본값 사용
def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


# base_url과 path를 안전하게 결합하여 URL 생성
def url(base: str, path: str) -> str:
    return urljoin(base.rstrip("/") + "/", path.lstrip("/"))


# HTML에서 hidden input의 value 값 추출
def extract_hidden_value(html: str, name: str) -> str:
    patterns = [
        rf'name="{re.escape(name)}"\s+value="([^"]+)"',
        rf'value="([^"]+)"\s+name="{re.escape(name)}"',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1)
    raise AssertionError(f"HTML에서 hidden 필드 '{name}'를 찾을 수 없습니다.")


# Q&A 페이지에서 게시글 개수(N) 파싱
def parse_qna_count(html: str) -> int:
    m = re.search(r"Q&A\s*게시판\s*\((\d+)\)", html)
    if not m:
        raise AssertionError("Q&A 페이지에서 게시글 개수를 찾을 수 없습니다.")
    return int(m.group(1))


# Q&A 페이지 HTML에서 삭제 요청 URL을 찾아 post_id 추출
def extract_any_delete_post_id(html: str) -> int:
    m = re.search(r"/qna/delete/(\d+)", html)
    if not m:
        raise AssertionError("Q&A 페이지에서 삭제 가능한 게시글 ID를 찾을 수 없습니다.")
    return int(m.group(1))


# /qna/1 페이지 HTML 가져오기
def fetch_qna_html(s: requests.Session, cfg: AppConfig) -> str:
    r = s.get(url(cfg.base_url, "/qna/1"), allow_redirects=True)
    assert r.status_code == 200, (
        f"/qna/1 페이지 로드에 실패했습니다. (HTTP {r.status_code})"
    )
    return r.text


# 현재 Q&A 게시글 개수 반환
def get_qna_count(s: requests.Session, cfg: AppConfig) -> int:
    return parse_qna_count(fetch_qna_html(s, cfg))


# CSRF 토큰이 존재하면 반환, 없으면 None
def get_csrf_token_if_present(s: requests.Session, cfg: AppConfig) -> str | None:
    html = fetch_qna_html(s, cfg)
    try:
        return extract_hidden_value(html, cfg.csrf_field_name)
    except AssertionError:
        return None


# 삭제 가능한 게시글 ID가 있으면 반환, 없으면 None
def get_delete_id_if_present(s: requests.Session, cfg: AppConfig) -> int | None:
    html = fetch_qna_html(s, cfg)
    try:
        return extract_any_delete_post_id(html)
    except AssertionError:
        return None


# 테스트 환경 설정 fixture
@pytest.fixture(scope="session")
def cfg() -> AppConfig:
    return AppConfig(
        base_url=_env("APP_BASE_URL", "http://127.0.0.1:5000"),
        username=_env("TEST_USERNAME", "admin"),
        password=_env("TEST_PASSWORD", "1234"),
        csrf_field_name=_env("CSRF_FIELD_NAME", "csrf_token"),
    )


# requests 세션 생성
@pytest.fixture()
def client() -> requests.Session:
    return requests.Session()


# 로그인된 상태의 세션 fixture
@pytest.fixture()
def logged_in(client: requests.Session, cfg: AppConfig) -> requests.Session:
    # 로그인 페이지 접근
    r_get = client.get(url(cfg.base_url, "/login"), allow_redirects=True)
    r_get.raise_for_status()

    # 로그인 요청
    r_post = client.post(
        url(cfg.base_url, "/login"),
        data={
            "username": cfg.username,
            "password": cfg.password
        },
        allow_redirects=True,
    )
    assert r_post.status_code in (200, 302), (
        f"로그인에 실패했습니다. (HTTP {r_post.status_code})"
    )
    return client