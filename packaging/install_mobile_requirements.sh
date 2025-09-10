export PYTHON_PLATFORM=$1
export WHEELS_DIR=./build/site-packages/$2
mkdir -p $WHEELS_DIR
uv run python -m pip install --no-deps --target $WHEELS_DIR -U --no-compile --platform $PYTHON_PLATFORM --python-version 3.12 --extra-index-url https://pypi.flet.dev/ -r requirements-android.txt
uv run python -m pip install --no-deps --target $WHEELS_DIR -U --no-compile ../dist/*.whl
