export PYTHON_PLATFORM=$1
export WHEELS_DIR=./build/site-packages/$2
export UV_COMPILE_BYTECODE=0
mkdir -p $WHEELS_DIR
uv pip install --no-deps --target $WHEELS_DIR -U --platform $PYTHON_PLATFORM --python-version 3.12 --extra-index-url https://pypi.flet.dev/ -r requirements-android.txt
uv pip install --no-deps --target $WHEELS_DIR -U ../dist/*.whl
