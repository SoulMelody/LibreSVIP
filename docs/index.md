# LibreSVIP
[![PyPi](https://img.shields.io/pypi/v/libresvip)](https://pypi.org/project/libresvip/)
[![Python Version](https://img.shields.io/pypi/pyversions/libresvip.svg)](https://pypi.org/project/libresvip/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/libresvip)](https://pypi.org/project/libresvip/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License](https://img.shields.io/pypi/l/libresvip?color=blue)](https://opensource.org/licenses/MIT)
[![GitHub Build](https://img.shields.io/github/actions/workflow/status/SoulMelody/LibreSVIP/package.yml?label=packaging)](https://github.com/SoulMelody/LibreSVIP/actions/workflows/package.yml?query=workflow%3APackaging)

LibreSVIP 是一个跨平台且通用的文件转换工具，它适用于多种不同歌声合成(有时也简称作 SVS)工程格式。

## 安装

从Github发布页下载: [发布页地址](https://github.com/SoulMelody/LibreSVIP/releases)

或者你也可以通过pip安装带有桌面支持的LibreSVIP (需要先安装 python 3.9 以上版本):

```bash
pip install libresvip[desktop]
```

## 翻译

![zh-CN translation](https://img.shields.io/badge/dynamic/json?color=blue&label=zh-CN&style=flat&logo=crowdin&query=%24.progress[?(@.data.languageId==%27zh-CN%27)].data.translationProgress&url=https%3A%2F%2Fbadges.awesome-crowdin.com%2Fstats-16219268-645830.json)
![ja translation](https://img.shields.io/badge/dynamic/json?color=blue&label=ja&style=flat&logo=crowdin&query=%24.progress[?(@.data.languageId==%27ja%27)].data.translationProgress&url=https%3A%2F%2Fbadges.awesome-crowdin.com%2Fstats-16219268-645830.json)

如果你想给一种新的语言或现有语言的翻译作出贡献, 请参阅 [LibreSVIP在Crowdin上的页面](https://crowdin.com/project/libresvip). 

## 参考资料

下文(原文为英文)将会就文本文件及二进制文件的解析这一方面，向你介绍一些相关的 python 第三方库：

- [Parsing In Python: Tools And Libraries](https://tomassetti.me/parsing-in-python/)