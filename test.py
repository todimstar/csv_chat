import sys
print(sys.executable)
if sys.prefix != sys.base_prefix:
    print("正在虚拟环境中运行")
    print(f"虚拟环境路径: {sys.prefix}")
    print(f"主机Python路径: {sys.base_prefix}")
else:
    print("正在主机环境中运行")
    print(f"Python路径: {sys.prefix}")