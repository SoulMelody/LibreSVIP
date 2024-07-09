python -m nuitka --standalone --assume-yes-for-downloads --output-dir=nuitka --output-filename=libresvip_web \
 --nofollow-import-to=libresvip.cli --nofollow-import-to=libresvip.gui \
 --nofollow-import-to=arrow --nofollow-import-to=chardet --nofollow-import-to=doctest --nofollow-import-to=PIL \
 --nofollow-import-to=pydantic.mypy --nofollow-import-to=zstd \
 --nofollow-import-to=redis --nofollow-import-to=requests \
 --nofollow-import-to=matplotlib --nofollow-import-to=numpy --nofollow-import-to=pandas --nofollow-import-to=traitlets \
 --noinclude-pytest-mode=nofollow --noinclude-IPython-mode=nofollow \
 --disable-plugin=pyside6 --disable-plugins=tk-inter \
 --disable-plugins=matplotlib --disable-plugins=numpy \
 --disable-plugins=delvewheel --disable-plugins=upx \
 --windows-console-mode=disable --windows-icon-from-ico=../libresvip/res/libresvip.ico --user-package-configuration-file=./nuitka-libresvip.yml \
 --include-distribution-metadata=xsdata_pydantic \
 --include-package=xsdata_pydantic \
 --include-package=pygments.formatters.html \
 --include-package=libresvip \
 ../libresvip/web/__main__.py
# --force-stdout-spec=libresvip.out.log --force-stderr-spec=libresvip.err.log \