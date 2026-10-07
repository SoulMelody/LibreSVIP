sed -i "s|https://pypi.tuna.tsinghua.edu.cn/packages|https://files.pythonhosted.org/packages|g" ../uv.lock
sed -i "s|https://pypi.tuna.tsinghua.edu.cn/simple|https://pypi.org/simple|g" ../uv.lock
sed -i "s|https://mirrors.aliyun.com/qt/snapshots/ci/pyside/dev/latest|https://download.qt.io/snapshots/ci/pyside/dev/latest|g" ../uv.lock
