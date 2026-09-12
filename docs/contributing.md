# 贡献代码

环境与常用命令见[环境搭建](setup.md)，类型检查与 pydantic 约定见[代码规范](coding_style.md)。

## 项目结构

多个前端共享同一转换核心——**格式转换逻辑永远写在 `libresvip` 核心与插件里，不要写进任何前端**：

| 入口 | 技术 | 位置 |
| --- | --- | --- |
| 桌面 GUI | PySide6 / QML | `libresvip/gui/`（界面在 `libresvip/res/` 的 QML，编译成 resources.rcc） |
| TUI | textual | `libresvip/tui/` |
| Web | 自研页面 | `libresvip/web/` |
| 移动端 | flet | `libresvip/mobile/` |
| CLI | typer | `libresvip/cli/`（含 `rpc/`，入口 `libresvip-cli`） |

核心层：

- `libresvip/model/` — 内部工程模型：`base.py`（全部模型的 pydantic 基类，`populate_by_name=True`），以及各类音高/曲线转换（`synthv_pitch`、`relative_pitch_curve`、`reset_time_axis`、`vocaloid/`…）
- `libresvip/core/` — tick 换算（`tick_counter`）、时间同步（`time_sync`）、注音（`lyric_phoneme/`）、异常与警告类型
- `libresvip/extension/` — 插件系统：`SVSConverter` 基类（`base.py`）、加载与元信息（`manager.py`）
- `libresvip/middlewares/` — 转换前后处理管道（音高平移、缩放、去歌词符号、替换歌词…）

格式插件 `libresvip/plugins/<format>/`（约 40 个格式，ace 至 y77）：

- 固定角色：`model.py`（目标格式 pydantic 模型）、`<format>_parser.py`（格式 → 内部 `Project`）、`<format>_generator.py`（`Project` → 格式）、`<format>_converter.py`（`SVSConverter` 子类，load/dump 入口）、`options.py`（输入/输出选项）
- 插件元信息在 `<format>.yapsy-plugin`，翻译在 `locales/<lang>/LC_MESSAGES/`（用户可见文案用 `gettext_lazy` 包 `_()`）；复杂插件可加常量/工具模块，但上述角色不变

周边：

- `scripts/` — 代码生成与编译（proto、snake_case pyi、Qt 资源、babel 编目）
- `tests/` — 扁平 `test_*.py` + `data/`、`files/` 测试素材
- `packaging/` — 各平台打包脚本；`deprecated/` 与 `experimental/` 存放旧实现与实验代码
