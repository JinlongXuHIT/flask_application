# 自定义过滤器
# 过滤器的本质为函数
def func_index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}

    return index_dict.get(index, "")