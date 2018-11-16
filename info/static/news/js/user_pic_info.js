function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
    // jquery.form.js插件，会自动帮我们把当前form标签里面的输入框内容组装成数据，发送到后端
    $(".pic_info").submit(function (e) {
        // 阻止表单默认提交行为
        e.preventDefault();

        //TODO 上传头像
        $(this).ajaxSubmit({
            url:"/user/user_pic_info",
            method:"post",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success:function(resp){
                if (resp.errno == "0") {
                    $(".now_user_pic").attr("src", resp.data.avatar_url)
                    $(".user_center_pic>img", parent.document).attr("src", resp.data.avatar_url)
                    $(".user_login>img", parent.document).attr("src", resp.data.avatar_url)
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
});