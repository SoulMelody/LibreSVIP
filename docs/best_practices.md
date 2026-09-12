# 最佳实践

为一个新的歌声合成工程格式编写插件时，按目标格式的类型选择解析与生成技术。下表是本仓库的选型速查，每一行都给出可直接参考的现有插件：

| 格式类型 | 解析 / 验证 | 生成 | 参考插件 |
| --- | --- | --- | --- |
| JSON / CBOR / YAML 等标准序列化 | 序列化库转 dict → pydantic 验证 | pydantic → 序列化库 | `ace`、`ds`、`vpr`、`tlpx`、`acep`、`ustx` |
| XML | xsdata（`xsdata-pydantic`） | xsdata XmlSerializer | `vsqx`、`ccs`、`musicxml`、`vspx`、`xvsq` |
| 自定义文本格式 | tatsu PEG 文法 | jinja2 模板 | `ust`、`nn` |
| Protobuf | `protobuf-py` 运行时 | 同左 | `svip3` |
| 自定义二进制 | construct | construct | `dv`、`mid`、`mtp`、`ppsf`、`svip`、`vshp`、`vsq`、`vxf` |

## 常见序列化格式：pydantic 验证

这类格式的分层很清晰：序列化库（`json` / `cbor2` / `yamlutils.load_yaml_1_2` 等）只负责字节 ↔ dict，结构验证全部交给 pydantic——`model.py` 是一棵 pydantic 模型树，parser 里 `FormatModel.model_validate(已反序列化的 dict)` 一步完成（YAML 格式参考 `ustx`，CBOR 参考 `tlpx`）。

初版模型不必手写：用 [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)（在 `code_gen` 依赖组，命令名叫 `datamodel-codegen`）从一份真实样例文件生成：

```bash
uv run --group code_gen datamodel-codegen \
  --input 样例文件.json \
  --output libresvip/plugins/<format>/model_gen.py \
  --output-model-type pydantic_v2.BaseModel \
  --base-class libresvip.model.base.BaseModel \
  --snake-case-field --disable-timestamp
```

`--snake-case-field` 会把 camelCase 键转成 snake_case 字段并**自动保留原始键名作为别名**（生成 `full_name: str = Field(..., alias='fullName')`），正好对齐本仓库“snake_case 字段 + camelCase 别名 + `by_alias=True` 序列化”的约定，省掉最机械的手写工作；`--base-class` 让模型直接继承仓库的 `BaseModel`；`--disable-timestamp` 保证重复生成不产生无谓 diff。生成结果仍是初版——之后照[代码规范](coding_style.md)清理：把必填改成可选并给默认值、删掉转换用不到的冗余字段。

## XML：xsdata

XML 格式统一用 [xsdata](https://xsdata.readthedocs.io/) 处理，仓库用的是它的 pydantic 集成 `xsdata-pydantic`（`XmlParser` / `XmlSerializer`）。生成的模型放进插件目录的 `models/` 子包（参考 `vsqx`：`models/vsqx3.py`、`models/vsqx4.py`）：

```bash
uv run --group code_gen xsdata generate --output xsdata_pydantic 样例文件或xsd -o libresvip/plugins/<format>/models/
```

`scripts/ts_model.py` 是同一个套路应用在 Qt Linguist `.ts` 文件上的例子——为"格式本身没有官方 schema"的情况提供了参照：拿一份样例文件生成模型，再手工修整。

## 自定义文本格式：tatsu 文法 + jinja2 模板

解析侧用 [tatsu](https://tatsu.readthedocs.io/)（仓库锁定 `tatsu-lts`），PEG 文法直接以字符串内嵌在 `model.py` 顶部，`tatsu.compile(...)` 编译后用 `NodeWalker` 遍历语法树（完整范例见 `nn` 与 `ust` 插件的 `model.py`）。不要用正则拼自定义文本解析器——文法写一次，后续遇到边角格式（引号、转义、可选段）时改一行文法即可。

生成侧不要手写字符串拼接。仓库封装了统一的 jinja2 环境 `libresvip.core.compat.jinja_env`：在插件的 `template.py` 里用 `add_template("格式名", "模板字符串")` 注册，再 `render_template("格式名", **上下文)` 渲染（参考 `ust`、`lrc`、`nn` 的 `template.py`）。

## Protobuf：buf 生成 + protobuf-py 运行时

`.proto` 文件统一放在 `libresvip/res/protos/`（现有 `libresvip.proto`、`svip3.proto`）。生成流程：

```bash
./scripts/gen_proto_files.sh   # 内部执行 cd libresvip/res/protos && uv run -- buf generate
```

`buf.gen.yaml` 使用本仓库的 `protoc-gen-py` 插件，生成的 `*_pb.py`（内嵌序列化的 file descriptor）**直接提交进仓库**，运行时用 [protobuf-py](https://github.com/soulmelodycn/protobuf-py) 而非 google 官方 protobuf 包（API 为 `from protobuf import Message` / `protobuf.wkt`）。

### 从闭源软件提取 proto 定义：pbtk

目标软件没有公开 schema 时（如 X Studio 的 svip3），用 [pbtk](https://github.com/vaitekoo/pbtk)（在 `code_gen` 依赖组）从其二进制可执行文件中提取内嵌的 protobuf descriptor，导出成 `.proto` 后放进 `libresvip/res/protos/` 再走上面的生成流程。`svip3.proto`（`package xstudio.proto`）就是这么来的。

## 自定义二进制格式：construct

自定义二进制结构用 [construct](https://construct.readthedocs.io/)（仓库用 `construct-typing` 提供类型标注）声明式描述，解析与生成共用同一个结构定义。参考 `dv/model.py`、`mid/midi_parser.py`、`ppsf/legacy_model.py`。

经验法则：

- 结构体写成模块级常量（`Struct(...)` / `Padded(...)` / `Array(...)` 嵌套），不要在函数里现拼；
- 整个文件的容错（加密区段、版本分支、头部魔数）放在 construct 结构之外，用普通 Python 处理（参考 `acep` 的加密区段处理）；
- 大端/小端、对齐与字符串编码在结构定义里显式声明。

## 逆向与辅助工具速查

| 工具 | 用途 | 所在依赖组 |
| --- | --- | --- |
| datamodel-code-generator | 从样例 JSON/YAML 生成 pydantic 模型初版 | `code_gen` |
| xsdata CLI | 从 XSD / 样例 XML 生成模型 | `code_gen` |
| pbtk | 从二进制可执行文件提取 protobuf 定义 | `code_gen` |
| buf + protoc-gen-py | 从 `.proto` 生成 Python 绑定 | `code_gen`（脚本 `scripts/gen_proto_files.sh`） |
| babel（`scripts/extract_messages.py`、`batch_compile_catalog.py`） | 抽取与编译翻译目录 | `i18n` / CI |

`scripts/` 下其余脚本与格式插件无关：`gen_snake_case_pyi.sh` 生成 PySide6 的 snake_case stub（GUI 开发用），`ts_model.py` 是 Qt `.ts` 翻译文件的 xsdata 模型（配合 `extract_messages.py` 把 Qt 翻译同步进 gettext 流程）。
