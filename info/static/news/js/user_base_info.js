function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(function () {

    $(".base_info").submit(function (e) {
        e.preventDefault();

        var signature = $("#signature").val();
        var nick_name = $("#nick_name").val();
        var gender = $(".gender:checked").val();

        if (!nick_name) {
            alert('请输入昵称');
            return
        }
        if (!gender) {
            alert('请选择性别');
        }

        // 组织参数
        var params = {
            "signature": signature,
            "nick_name": nick_name,
            "gender": gender
        };
        
        // TODO 请求修改用户基本信息
        $.ajax({
            url:"/user/user_base_info",
            data: JSON.stringify(params),
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function(resp){
                if(resp.errno == 0){
                    // 修改成功
                    alert("保存成功")
                    // 前端中如果需要在ifram网页内部修改父级页面的html内容，要使用 parent.document来操作
                    // find　表示查找对应的标签内部的html代码
                    $(parent.document).find(".user_center_name").html(nick_name)
                    $(parent.document).find("#nick_name").html(nick_name)
                }else if(resp.errno == 4101){
                    $('.login_form_con').show();
                }else{
                    alert(resp.errmsg);
                }
            }
        })

    })
});