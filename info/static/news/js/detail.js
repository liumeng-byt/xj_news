function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        // 获取收藏的`新闻id`
        var news_id = $(this).attr("data-news-id");
        var action = "collect";

        // 组织参数
        var params = {
            "news_id": news_id,
            "action": action
        };

        // TODO 请求收藏新闻
        $.ajax({
            url:"/news/news_collect",
            data:JSON.stringify(params),
            method:"POST",
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token"),
            },
            success:function (resp) {
                if (resp.errno == 0) {
                    //成功
                    //隐藏收藏按钮
                    $(".collection").hide();
                    //显示已收藏按钮
                    $(".collected").show()

                }else if(resp.errno == 4101){
                    //如果没有登陆就显示登陆框
                    $(".login_form_con").show();
                }else {
                    //失败
                    alert(resp.errmsg)
                }
            }


        })
       
    });

    // 取消收藏
    $(".collected").click(function () {
        // 获取收藏的`新闻id`
        var news_id = $(this).attr("data-news-id");
        var action = "cancel_collect";

        // 组织参数
        var params = {
            "news_id": news_id,
            "action": action
        };

        // TODO 请求取消收藏新闻
        $.ajax({
            url:"/news/news_collect",
            data:JSON.stringify(params),
            method:"POST",
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken": getCookie("csrf_token"),
            },
            success:function (resp) {
                if (resp.errno == 0) {
                    //成功
                    //显示取消收藏按钮
                    $(".collected").hide();
                    //隐藏收藏按钮
                    $(".collection").show()

                }else if(resp.errno == 4101){
                    //如果没有登陆就显示登陆框
                    $(".login_form_con").show();
                }else {
                    //失败
                    alert(resp.errmsg)
                }
            }


        })

    });

    // 更新评论条数
    function updateCommentCount() {
        var length = $(".comment_list").length;
        $(".comment_count").html(length + "条评论");
    }

    // 评论提交
    $(".comment_form").submit(function (e) {
        // 阻止表单默认提交行为
        e.preventDefault();

        // 获取参数
        var news_id = $(this).attr("data-news-id");
        var comment = $(".comment_input").val();

        // 组织参数
        var params = {
            "news_id": news_id,
            "content": comment
        };

        // TODO 请求对新闻`进行评论`
        $.ajax({
            url:"/news/news_comment",
            data:JSON.stringify(params),
            method:"POST",
            contentType:"application/json",
            dataType:"json",
            headers:{
                "X-CSRFToken":getCookie("csrf_token")
            },
            success:function (resp) {
                if (resp.errno == 0){
                    //评论成功
                    //后端返回的新增内容
                    var comment = resp.data;
                    //把新增的评论添加到新闻列表前排
                    // 拼接内容
                    var comment_html = ''
                    comment_html += '<div class="comment_list">'
                    comment_html += '<div class="person_pic fl">'
                    if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                    }else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                    }
                    comment_html += '</div>'
                    comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>'
                    comment_html += '<div class="comment_text fl">'
                    comment_html += comment.content
                    comment_html += '</div>'
                    comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>'

                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>'
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                    comment_html += '<form class="reply_form fl" >'
                    comment_html += '<textarea class="reply_input"></textarea>'
                    comment_html += '<input type="button" value="回复" class="reply_sub fr" data-comment-id="' + comment.id + '" data-news-id="' + news_id + '">'
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                    comment_html += '</form>'

                    comment_html += '</div>'
                    // 拼接到内容的前面
                    $(".comment_list_con").prepend(comment_html)
                    // 让comment_sub 失去焦点
                    $('.comment_sub').blur();
                    // 清空输入框内容
                    $(".comment_input").val("")
                }else if (resp.errno == 4101){
                    $(".login_form_con").show();
                }else {
                    alert(resp.errmsg)
                }
            }

        })

    });

    $('.comment_list_con').delegate('a,input','click',function(){

        var sHandler = $(this).prop('class');

        if(sHandler.indexOf('comment_reply')>=0)
        {
            $(this).next().toggle();
        }

        if(sHandler.indexOf('reply_cancel')>=0)
        {
            $(this).parent().toggle();
        }

        if(sHandler.indexOf('comment_up')>=0)
        {
            var $this = $(this);
            // 默认点击时代表`点赞`
            var action = 'add';
            if(sHandler.indexOf('has_comment_up')>=0)
            {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                $this.removeClass('has_comment_up');
                // 如果已经点赞，设置为`取消点赞`
                action = 'remove';
            }else {
                $this.addClass('has_comment_up')
            }

            // 获取`评论id`
            var comment_id = $this.attr('data-comment-id');

            // 组织参数
            var params = {
                "comment_id": comment_id,
                "action": action
            };

            // TODO 请求`点赞`或`取消点赞`
            $.ajax({
                url:"/news/comment_like",
                data:JSON.stringify(params),
                type:"post",
                contentType:"application/json",
                headers:{
                    "X-CSRFToken":getCookie("csrf_token")
                },
                success:function (resp) {
                    if (resp.errno == 0){
                        //操作成功
                        if (resp.like_count == 0){
                            $this.html("赞1个")
                        }else {
                            $this.html(resp.like_count)
                        }
                    }else if (resp.errno == 4101){
                        $(".login_form_con").show();
                    }else {
                        alert(resp.errmsg)
                    }
                }
            })
        }

        if(sHandler.indexOf('reply_sub')>=0)
        {

            // 获取参数
            var $this = $(this);
            // var news_id = $this.parent().attr('data-newsid');
            var news_id = $this.attr('data-news-id');
            var parent_id = $this.attr('data-comment-id');
            var comment = $this.prev().val();

            // 如果没有评论内容
            if (!comment) {
                alert("请输入评论内容");
                return;
            }

            // 组织参数
            var params = {
                "news_id": news_id,
                "content": comment,
                "parent_id": parent_id
            };

            // TODO 请求`回复评论`
            $.ajax({
                url: "/news/news_comment",
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                data: JSON.stringify(params),
                success: function (resp) {
                    if (resp.errno == "0") {
                        var comment = resp.data
                // 拼接内容
                        var comment_html = ""
                        comment_html += '<div class="comment_list">'
                        comment_html += '<div class="person_pic fl">'
                        if (comment.user.avatar_url) {
                        comment_html += '<img src="' + comment.user.avatar_url + '" alt="用户图标">'
                        }else {
                        comment_html += '<img src="../../static/news/images/person01.png" alt="用户图标">'
                        }
                        comment_html += '</div>'
                        comment_html += '<div class="user_name fl">' + comment.user.nick_name + '</div>'
                        comment_html += '<div class="comment_text fl">'
                        comment_html += comment.content
                        comment_html += '</div>'
                        comment_html += '<div class="reply_text_con fl">'
                        comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>'
                        comment_html += '<div class="reply_text">'
                        comment_html += comment.parent.content
                        comment_html += '</div>'
                        comment_html += '</div>'
                        comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>'

                        comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">赞</a>'
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>'
                        comment_html += '<form class="reply_form fl" >'
                        comment_html += '<textarea class="reply_input"></textarea>'
                        comment_html += '<input type="button" value="回复" class="reply_sub fr" data-comment-id="' + comment.id + '" data-news-id="' + news_id + '">'
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">'
                        comment_html += '</form>'

                        comment_html += '</div>'
                        $(".comment_list_con").prepend(comment_html)
                        // 请空输入框
                        $this.prev().val('')
                        // 关闭
                        $this.parent().hide()
                    }else {
                        alert(resp.errmsg)
                    }
                }
            })
        }
    });

    // 关注当前新闻作者
    // 关注当前新闻作者
    $(".focus").click(function () {
            // 获取参数
            $this = $(this);
            author_id = $this.attr("data-author-id");
            // 组织参数
            var params = {
                "author_id": author_id,
                "action": "follow",
            };

            $.ajax({
                url:"/news/author_fans",
                data: JSON.stringify(params),
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                success: function(resp){
                    if(resp.errno == 0){
                        // 关注成功
                        // 更新作者粉丝数量
                        $(".follows b").html(resp.followers_count);
                        $(".focus").hide();
                        $(".focused").show();

                    }else if(resp.errno == 4101){
                        $('.login_form_con').show();
                    }else{
                        alert(resp.errmsg);
                    }
                }
            });
    });

    // 取消关注当前新闻作者
    $(".focused").click(function () {
            // 获取参数
            author_id = $(this).attr("data-author-id");
            // 组织参数
            var params = {
                "author_id": author_id,
                "action": "cancel_follow",
            };

            $.ajax({
                url:"/news/author_fans",
                data: JSON.stringify(params),
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                success: function(resp){
                    if(resp.errno == 0){
                        // 关注成功
                        // 更新作者粉丝数量
                        $(".follows b").html(resp.followers_count);
                        $(".focused").hide();
                        $(".focus").show();

                    }else if(resp.errno == 4101){
                        $('.login_form_con').show();
                    }else{
                        alert(resp.errmsg);
                    }
                }
            })
    });
});