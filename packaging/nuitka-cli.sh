python -m nuitka --standalone --assume-yes-for-downloads --output-dir=nuitka --output-filename=libresvip_cli \
 --nofollow-import-to=libresvip.gui --nofollow-import-to=libresvip.web \
 --nofollow-import-to=anyio --nofollow-import-to=arrow --nofollow-import-to=chardet --nofollow-import-to=markdown2 \
 --nofollow-import-to=ruamel.yaml --nofollow-import-to=pydantic.mypy --nofollow-import-to=zstd \
 --nofollow-import-to=httpcore --nofollow-import-to=httpx --nofollow-import-to=redis --nofollow-import-to=requests \
 --nofollow-import-to=matplotlib --nofollow-import-to=numpy --nofollow-import-to=pandas --nofollow-import-to=traitlets \
 --noinclude-pytest-mode=nofollow --noinclude-IPython-mode=nofollow \
 --disable-plugin=pyside6 --disable-plugins=tk-inter \
 --disable-plugins=matplotlib --disable-plugins=numpy \
 --disable-plugins=delvewheel --disable-plugins=upx \
 --enable-console --windows-icon-from-ico=../libresvip/res/libresvip.ico --user-package-configuration-file=./nuitka-libresvip.yml \
 --include-package=libresvip \
 ../libresvip/cli/__main__.py
# --force-stdout-spec=libresvip.out.txt \