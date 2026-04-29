export PYTHON_PLATFORM=$1
export WHEELS_DIR=./build/site-packages/$2
mkdir -p $WHEELS_DIR
uv run python -m ensurepip
uv run python -m pip install --no-deps --target $WHEELS_DIR --no-compile -U --platform $PYTHON_PLATFORM --python-version 3.12 --extra-index-url https://pypi.flet.dev/ -r requirements-android.txt
uv run python -m pip install --no-deps --target $WHEELS_DIR --no-compile -U ../dist/*.whl
