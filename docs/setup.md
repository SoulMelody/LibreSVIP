# 环境搭建

LibreSVIP 使用 [uv](https://docs.astral.sh/uv/) 管理依赖，要求 Python 3.11+。

## 安装开发依赖

```bash
uv sync --all-extras --group linting
```

## 常用命令

| 用途 | 命令 |
| --- | --- |
| 类型检查 | `uv run pyrefly check .` |
| Lint 并自动修复 | `uv run ruff check --fix .` |
| 格式化 | `uv run ruff format --config pyproject.toml --exclude tests/ .` |
| 测试 | `uv run pytest tests/ -v` |
| 全部钩子（与 CI 相同入口） | `uv run prek run --all-files` |

## Git 钩子

仓库使用 [prek](https://github.com/j178/prek) 管理 pre-commit 钩子，提交前会自动执行：

- 换行统一为 LF、清理行尾空白；
- JSON / YAML 语法检查；
- TOML 由 [tombi](https://tombi-toml.github.io/) 格式化，Markdown 由 [rumdl](https://github.com/rvben/rumdl) 格式化——不要手工对齐表格。

`.mo` 编译目录、Qt 资源（`resources.rcc`）与 `packaging/requirements-*.txt` 由 CI 的 compile-files 工作流在 push 到 main 时自动编译并回提交，正常情况下不需要手工产出这些文件（相关脚本在 `scripts/`）。
