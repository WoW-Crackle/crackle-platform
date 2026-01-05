
function showTab(tabName) {
    const image = document.getElementById("tab-image");
    if (tabName === "info") {
    image.src = "/static/img/information.png";
    } else if (tabName === "size") {
    image.src = "/static/img/size.png";
    } else if (tabName === "review") {
    image.src = "/static/img/review.png";
    }
}
function showTab(tabName, element) {
const image = document.getElementById("tab-image");

// 이미지 변경
if (tabName === "info") {
    image.src = "/static/img/information.png";
} else if (tabName === "size") {
    image.src = "/static/img/size.png";
} else if (tabName === "review") {
    image.src = "/static/img/review.png";
}

// 탭 강조 처리
const tabs = document.querySelectorAll(".tab-link");
tabs.forEach(tab => tab.classList.remove("active"));
element.classList.add("active");
}

function confirmLogin(loginUrl) {
if (confirm("로그인이 필요합니다. 이동하시겠습니까?")) {
    window.location.href = loginUrl;
}
return false; // 링크 기본 동작 막기
}
