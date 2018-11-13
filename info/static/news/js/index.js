var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 获取首页新闻信息
    updateNewsData();

    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active');
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid;

            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            updateNewsData();
        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            // 判断`是否正在向服务器请求获取数据`
            if (!data_querying) {
                // 设置`是否正在向服务器请求获取数据`data_querying为true
                // 防止页面滚动时多次向服务器请求数据
                data_querying = true;

                // 判断是否还有`下一页`，如果有则获取`下一页`内容
                if (cur_page < total_page) {
                    updateNewsData();
                }
                else {
                    data_querying = false;
                }
            }
        }
    })
});

// 获取指定页码的`分类新闻信息`
function updateNewsData() {
    // 组织参数
    var params = {
        "cid": currentCid,
        "page": cur_page,
        "per_page": 50
    };
    data_querying = false;
    // TODO 更新新闻数据
    $.ajax({
        url:"/news_list",
        method:"GET",
        data:params,
        dataType:"json",
        success: function(resp){
            if(resp.errno==0){
                // 请求成功以后，把通过js把新闻内容进行替换
                // 先清空原有数据
                if (cur_page == 1) {
                    $(".list_con").html('');
                }
                htmlContent = "";
                for (var i=0;i<resp.newsList.length;i++) {
                    var news = resp.newsList[i];
                    htmlContent += '<li>';
                    htmlContent += '<a href="/news/'+news.id+'" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>';
                    htmlContent += '<a href="/news/'+news.id+'" class="news_title fl">' + news.title + '</a>';
                    htmlContent += '<a href="/news/'+news.id+'" class="news_detail fl">' + news.digest + '</a>';
                    htmlContent += '<div class="author_info fl">';
                    htmlContent += '<div class="source fl">来源：' + news.source + '</div>';
                    htmlContent += '<div class="time fl">' + news.create_time + '</div>';
                    htmlContent += '</div>';
                    htmlContent += '</li>';
                }
                $(".list_con").append(htmlContent);
                // 修改当前js的获取数据的状态为flase，表示已经获取完数据了
                data_querying = false
                // 根据后端返回的总页码和当前页码，重新设置
                total_page = resp.totalPage
                cur_page = resp.currentPage
            }
        }
    })

}