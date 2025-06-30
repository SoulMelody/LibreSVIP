echo "libresvip[crypto,lxml,zstd,ujson,mobile]" > requirements-pypy.txt
pyfuze ./libresvip/mobile --entry __main__.py \
  --unzip-path ./app_data --output-name libresvip-mobile.exe \
  --python pypy-3.10.16-windows-x86_64-none \
  --reqs requirements-pypy.txt --win-gui