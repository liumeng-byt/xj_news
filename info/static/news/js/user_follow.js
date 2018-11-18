function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    $(".focused").click(function () {

        // TODO 取消关注当前新闻作者
        var $this = $(this)
        var user_id = $this.attr("data-user-id")
        // var user_id = $(this).prop("data-user-id")
        // alert(user_id);
        var params = {
            "action":"cancel_follow",
            "author_id":user_id
        };
        $.ajax({
            url:"/news/author_fans",
            type:"POST",
            contentType:"application/json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            data:JSON.stringify(params),
            success:function (resp) {
                if (resp.errno == 0){
                    //取消关注成功
                    alert(resp.errmsg)
                    window.location.reload()
                }else if (resp.errno == 4101){
                    //未登陆，弹出登陆框
                    $('.login_form_con').show();
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});