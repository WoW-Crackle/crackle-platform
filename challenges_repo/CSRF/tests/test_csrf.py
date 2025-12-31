import pytest
import requests
from conftest import (
    AppConfig,
    url,
    get_qna_count,
    get_csrf_token_if_present,
    get_delete_id_if_present,
)


# [공통 유틸] 정답 코드에는 토큰이 존재해야 한다. 취약 버전에서는 토큰이 없으니 이 함수가 실패한다.  
def _require_token(token: str | None):
    assert token is not None, (
        "CSRF 토큰이 존재하지 않습니다. "
    )


# [공격 시나리오 1] CSRF 토큰 없이 게시글을 추가(add)하면, 게시글 개수에 변화가 없어야 한다. 
@pytest.mark.csrf
def test_no_token_add_does_not_change_state(logged_in: requests.Session, cfg: AppConfig):
    # 현재 게시글 개수 
    before = get_qna_count(logged_in, cfg)
    # CSRF 토큰 없이 게시글 추가 시도 
    logged_in.post(
        url(cfg.base_url, "/qna/add"),
        data={"title": "csrf_oracle_title", "body": "csrf_oracle_body"},
        allow_redirects=True,
    )
    # 개시글 개수 확인 
    after = get_qna_count(logged_in, cfg)
    # 토큰 없는 요청으로 상태가 변하면 취약 
    assert after == before, (
        f"CSRF 토큰 없이 게시글이 추가되었습니다. "
        f"(이전: {before}, 이후: {after})"
    )


# [정상 시나리오 1] CSRF 토큰을 포함한 게시글 추가(add) 요청은, 정상 흐름이므로 게시글 개수가 +1 증가한다. 
@pytest.mark.csrf
def test_valid_token_add_changes_state(logged_in: requests.Session, cfg: AppConfig):
    before = get_qna_count(logged_in, cfg)
    # CSRF 토큰 획득 
    token = get_csrf_token_if_present(logged_in, cfg)
    _require_token(token)
    # 정상적인 토큰 포함 요청 
    logged_in.post(
        url(cfg.base_url, "/qna/add"),
        data={
            "title": "valid_token_title",
            "body": "valid_token_body",
            cfg.csrf_field_name: token,
        },
        allow_redirects=True,
    )
    after = get_qna_count(logged_in, cfg)
    assert after == before + 1, (
        f"CSRF 토큰을 포함한 정상 요청임에도 게시글이 추가되지 않았습니다. "
        f"(이전: {before}, 이후: {after})"
    )


# [공격 시나리오 2] CSRF 토큰 없이 게시글을 삭제(delete)하면, 서버 상태에 변화가 없어야 한다. 
@pytest.mark.csrf
def test_no_token_delete_does_not_change_state(logged_in: requests.Session, cfg: AppConfig):
    before = get_qna_count(logged_in, cfg)
    # 삭제 가능한 게시글 ID 확보 
    delete_id = get_delete_id_if_present(logged_in, cfg)
    assert delete_id is not None, "No delete target found. Ensure there is at least one deletable post."
    # CSRF 토큰 없이 삭제 시도 
    logged_in.post(
        url(cfg.base_url, f"/qna/delete/{delete_id}"),
        data={},  # no token
        allow_redirects=True,
    )
    after = get_qna_count(logged_in, cfg)
    assert after == before, (
        f"CSRF 토큰 없이 게시글이 삭제되었습니다. "
        f"(이전: {before}, 이후: {after})"
    )


# [정상 시나리오 2] CSRF 토큰을 포함한 게시글 삭제(delete) 요청은 게시글 개수가 -1 감소해야 한다. 
@pytest.mark.csrf
def test_valid_token_delete_changes_state(logged_in: requests.Session, cfg: AppConfig):
    # 토큰 
    token = get_csrf_token_if_present(logged_in, cfg)
    _require_token(token)
    # 삭제 대상이 될 게시글 추가
    before_add = get_qna_count(logged_in, cfg)
    logged_in.post(
        url(cfg.base_url, "/qna/add"),
        data={"title": "to_delete", "body": "to_delete", cfg.csrf_field_name: token},
        allow_redirects=True,
    )
    after_add = get_qna_count(logged_in, cfg)
    assert after_add == before_add + 1, (
        "삭제 테스트를 위한 게시글 생성에 실패했습니다."
    )
    # 생성된 게시글의 delete id 확보
    delete_id = get_delete_id_if_present(logged_in, cfg)
    assert delete_id is not None, (
        "게시글은 생성되었으나 삭제 대상 ID를 찾을 수 없습니다."
    )
    # CSRF 토큰을 포함하여 삭제 요청 
    before_del = get_qna_count(logged_in, cfg)
    logged_in.post(
        url(cfg.base_url, f"/qna/delete/{delete_id}"),
        data={cfg.csrf_field_name: token},
        allow_redirects=True,
    )
    after_del = get_qna_count(logged_in, cfg)
    assert after_del == before_del - 1, (
        f"CSRF 토큰을 포함한 정상 삭제 요청이 반영되지 않았습니다. "
        f"(이전: {before_del}, 이후: {after_del})"
    )