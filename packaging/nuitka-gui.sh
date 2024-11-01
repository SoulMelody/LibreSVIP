python -m nuitka --standalone --assume-yes-for-downloads --output-dir=nuitka --output-filename=libresvip_gui \
 --nofollow-import-to=libresvip.cli --nofollow-import-to=libresvip.web --nofollow-import-to=libresvip.tui \
 --nofollow-import-to=arrow --nofollow-import-to=chardet --nofollow-import-to=markdown2 \
 --nofollow-import-to=pydantic.mypy --nofollow-import-to=zstd \
 --nofollow-import-to=redis --nofollow-import-to=requests \
 --nofollow-import-to=matplotlib --nofollow-import-to=numpy --nofollow-import-to=pandas --nofollow-import-to=traitlets \
 --noinclude-pytest-mode=nofollow --noinclude-IPython-mode=nofollow \
 --enable-plugin=pyside6 --include-qt-plugins=qml --disable-plugins=tk-inter \
 --disable-plugins=matplotlib --disable-plugins=numpy \
 --disable-plugins=delvewheel --disable-plugins=upx \
 --windows-console-mode=disable --force-stdout-spec=libresvip.out.log --force-stderr-spec=libresvip.err.log \
 --windows-icon-from-ico=../libresvip/res/libresvip.ico --user-package-configuration-file=./nuitka-libresvip.yml \
 --include-distribution-metadata=xsdata_pydantic \
 --include-package=xsdata_pydantic \
 --include-package=libresvip \
 ../libresvip/gui/__main__.py