from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecret"

# In-memory storage for Q&A posts
qna = [{"id": 0, "author": "WUISP", "title": "환영합니다!", "body": "Q&A 게시판에 글을 남겨보세요."}]
_next_id = 1

# Login required decorator
def login_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return inner
    
# Home page
@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    if product_id == 1:
        return render_template("product1.html", user=session.get("user"), product_id=product_id)
    return redirect(url_for("index"))

VALID_USERNAME = "admin"
VALID_PASSWORD = "1234"

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session["user"] = username
            flash(f"{username}님, 환영합니다!", "success")
            return redirect(next_page or url_for("index"))
        else:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            
    return render_template("login.html", next=next_page)

# Logout
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for("index"))

# Q&A page
@app.route("/qna/<int:product_id>")
@login_required
def qna_page(product_id):
    return render_template("qna.html", qna=qna, user=session.get("user"), product_id=product_id)

# Add a new question
@app.route("/qna/add", methods=["POST"])
@login_required
def add_question():
    global _next_id
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    if not title:
        flash("제목을 입력하세요.", "error")
        return redirect(url_for("qna_page", product_id=1))
    qna.append({
        "id": _next_id,
        "author": session.get("user"),
        "title": title,
        "body": body
    })
    _next_id += 1
    flash("게시글이 등록되었습니다.", "success")
    return redirect(url_for("qna_page", product_id=1))

# Delete a question 
@app.route("/qna/delete/<int:post_id>", methods=["GET", "POST"]) # Allow GET requests
@login_required
def delete_question(post_id):
    global qna
    qna = [p for p in qna if p["id"] != post_id]
    flash(f"게시글 {post_id} 삭제됨.", "info")
    return redirect(url_for("qna_page", product_id=1))

if __name__ == "__main__":
    app.run(debug=True)

