function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function(){
    $(".news_edit").submit(function (e) {
        // 阻止表单默认提交行为
        e.preventDefault();

        // TODO 新闻编辑提交
    })
});

// 点击取消，返回上一页
function cancel() {
    history.go(-1);
}