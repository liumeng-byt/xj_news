# 函数中公用的代码，或者辅助代码


# 注册自定义的过滤器使用的函数（用于点击排行的前三个序号颜色）
def do_index_class(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""