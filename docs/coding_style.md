# 代码规范

## 类型检查

默认类型检查器是 **pyrefly**（`.pre-commit-config.yaml` 中的 `pyrefly-check` 钩子即门禁）：

```bash
uv run pyrefly check .
```

mypy（含 pydantic.mypy 插件）已降级为遗留工具——慢且明显更严，不要把它的输出当作通过/失败标准，也不要为满足它去改代码。

`pyproject.toml` 中 `[tool.pyrefly.errors]` / `[tool.ty.rules]` 忽略了一批调用形状错误，这是有意为之：

本仓库 pydantic 模型密集（`libresvip/model/base.py` 与各插件），其 `__init__` 由 dataclass_transform 合成。pyright / basedpyright / ty 等静态检查器解析不了它，会对普通的模型构造大量误报"参数不存在 / missing argument / unexpected keyword"（包括从未改动的文件）。遇到这类报错时：

- 不要加 `# type: ignore`、不要改写正常工作的 pydantic 代码来消音；
- IDE / 语言服务器里几十条此类错误属于工具噪音，不是代码问题；
- 判断标准只有一个：`uv run pyrefly check .` 零错误。

## Lint

Lint 与格式化统一用 [ruff](https://docs.astral.sh/ruff/)（pre-commit 的 `ruff-check` / `ruff-format` 钩子即门禁，规则配置在 `pyproject.toml` 的 `[tool.ruff]`）：

```bash
uv run ruff check --fix .              # lint，可自动修复的会直接改
uv run ruff format --config pyproject.toml --exclude tests/ .   # 格式化
```

要点：

- 行宽 100、`fix = true`——直接跑 `ruff check` 就会顺手修掉可修的，不要绕过；
- 选用了较严格的规则族（`ANN` 注解、`TC` 类型导入块、`PTH` 用 pathlib 不用 os.path、`T20` 禁 print、`INT` gettext 用法、`I` 导入排序等），import 排序按 `known-first-party = ["libresvip", "tests"]` 区分；
- 个别规则已全局忽略（如 `E501` 行长在格式化兜底、`PLC0415` 允许函数内 import），完整清单见 `pyproject.toml`，不要在代码里随手 `# noqa`——全仓目前只有约 20 处，均为刻意豁免（如 PySide6 的 `__feature__` 导入）。

## pydantic 模型约定

- 外部格式字段一律使用 camelCase 别名：`Field(alias="startOffset")`，序列化时 `by_alias=True`
- 旧字段一律转为可选并给默认值，不要让 `load` 对某个格式版本直接抛异常
- 兼容旧版本格式时：读侧用 `model_validator(mode="before")` 迁移旧键，写侧用 `model_serializer(mode="wrap")` 按版本输出

## 验证习惯

改插件前后，用目标格式的真实文件端到端跑一遍 converter 的 load/dump，而不是只做模型验证——序列化/反序列化路径才会暴露别名与字段可选性问题。
