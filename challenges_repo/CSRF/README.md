## CSRF (Cross-Site Request Forgery) Challenge

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey?logo=flask)
![Purpose](https://img.shields.io/badge/Purpose-Learning--&--Demo-yellow)

간단한 Flask 기반 CSRF 예제입니다.  
로그인(세션) 기반으로 동작하며, 상품 상세 페이지와 Q&A 게시판(글쓰기/삭제) 기능을 포함합니다.  
이 저장소는 교육/실습용이며, CSRF을 확인·실습하도록 의도적으로 일부 취약한 구현을 포함할 수 있습니다.

### 📁파일 구조

```text
CSRF/
├── app.py
├── static/
│ ├── css/
│ │ └── style.css
│ ├── img/
│ │ ├── information.png
│ │ ├── review.png
│ │ ├── size.png
│ │ ├── tee1.png
│ │ ├── tee2.png
│ │ ├── tee3.png
│ │ ├── tee4.png
│ │ ├── tee5.png
│ │ └── tee6.png
│ └── js/
│ └── script.js
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── product1.html
│ └── qna.html
└── README.md
```
### 🎯기능 요약

- 세션 기반 로그인 / 로그아웃(`admin` / `1234`)
- 상품 목록 및 1번 상품 상세 페이지
- 상품 상세에서 Q&A(로그인 필요) 접근
- Q&A: 글 목록, 글쓰기(post), 글 삭제(GET/POST 허용(현 코드)) — **취약점을 위해 허용된 부분 존재**
- Flash 메시지로 사용자 피드백 제공

### 🚀필요 사항
```
Python 3.7+
Flask
```
### 🛠️ flask 설치
```python
pip install flask 
```
### ▶️실행
```python
python app.py
```
### 해설
```
# Delete a question 
@app.route("/qna/delete/<int:post_id>", methods=["GET", "POST"]) # Allow GET requests
@login_required
def delete_question(post_id):
    global qna
    qna = [p for p in qna if p["id"] != post_id] # <-- 2. 인가(Authorization) 없음
    flash(f"게시글 {post_id} 삭제됨.", "info")
    return redirect(url_for("qna_page", product_id=1))
```
**delete_question 함수에 취약점이 존재 합니다.**
1. `GET` 요청을 허용합니다. 즉, 주소창 입력으로도 '삭제'가 가능합니다.
2. 로그인한 사용자가 이 게시글의 작성자인지 여부를 확인하지 않습니다.

**워게임의 목표는 기본 작성자 WUISP의 게시글을 삭제하는 것입니다.**
1. 사이트에 로그인 후 Q&A 게시판이 들어갑니다.
2. 현재 주소의 마지막 부분을`/qna/delete/0`으로 바꿔서 입력합니다.
3. "게시글 0 삭제됨" 이라는 메시지와 함께"WUISP"의 게시글이 삭제된 것을 볼 수 있습니다.

