python -m nuitka --standalone --assume-yes-for-downloads --output-dir=libresvip_gui \
 --nofollow-import-to=libresvip.cli --nofollow-import-to=libresvip.web \
 --nofollow-import-to=arrow --nofollow-import-to=chardet --nofollow-import-to=markdown2 \
 --nofollow-import-to=ruamel.yaml --nofollow-import-to=pydantic.mypy --nofollow-import-to=zstd \
 --nofollow-import-to=redis --nofollow-import-to=requests \
 --nofollow-import-to=matplotlib --nofollow-import-to=numpy --nofollow-import-to=pandas --nofollow-import-to=traitlets \
 --noinclude-pytest-mode=nofollow --noinclude-IPython-mode=nofollow \
 --enable-plugin=pyside6 --include-qt-plugins=qml --disable-plugins=tk-inter \
 --disable-plugins=matplotlib --disable-plugins=numpy \
 --disable-plugins=delvewheel --disable-plugins=upx \
 --disable-console --windows-icon-from-ico=../libresvip/res/libresvip.ico --user-package-configuration-file=./nuitka-libresvip.yml \
 --include-package=libresvip --include-distribution-metadata=libresvip \
 ../libresvip/gui/__main__.py