# Namishu Arithmetic

生成可打印的整数、分数和小数四则运算练习。

[English](README.md)

提供 **3 个系列、68 个级别**，涵盖加减乘除、负数、括号、混合运算和填空。
生成 A4 PDF，可用于家庭或课堂练习。程序在本地运行，不需要账户或 API 密钥。

![加法练习预览](examples/addition.png)

## 快速上手

环境要求：**Python 3.10+**。运行依赖为 NumPy、PyYAML、ReportLab。
默认使用 PDF 标准字体 Helvetica，由阅读器提供显示，不需要安装或附带字体文件。
配置已包含在安装包中。代码面向 macOS、Linux、Windows，验证矩阵见 CI 配置。

下载或克隆本仓库，在项目目录打开终端：

```bash
python -m venv .venv
```

macOS/Linux 激活环境：

```bash
source .venv/bin/activate
```

Windows PowerShell 激活环境：

```powershell
.venv\Scripts\Activate.ps1
```

安装并生成第一份练习：

```bash
python -m pip install .
arithmetic generate --series addsub --level 1 --pages 5 --output worksheets/addition.pdf
```

命令完成后会显示文件位置。用 PDF 阅读器打开，选择 A4、实际大小打印。
此级别的两个操作数均在 0–10，**结果可能达到 20**。

如果使用 `uv`，先执行 `uv sync`，再以 `uv run arithmetic generate` 加同样参数生成。
以上方法直接安装仓库内容，不依赖本项目已发布到 PyPI。

## 不会写代码，也可以让 Agent 帮忙

Agent 需要能下载仓库、执行命令、安装依赖，并把生成文件交给你。
只有聊天能力、没有执行环境的助手不能独立完成这些步骤。

把仓库地址或本地目录交给 Agent，再复制这段话：

> 请阅读这个项目的 README.zh-CN.md 和 AGENTS.md，准备运行环境。
> 帮我生成 5 页不含负操作数的基础乘法练习，保存到 worksheets 文件夹。
> 根据文档选择已有题型，检查 PDF 是否成功生成，告诉我文件位置和实际采用的参数。

你只需要描述运算种类、数字类型、是否允许负操作数，以及需要几页。
Agent 可以按照[题型目录](docs/levels.zh-CN.md)和[操作指南](docs/agent-guide.md)完成工作。

也可以直接下载示例：[加法](examples/addition.pdf)、[乘法](examples/multiplication.pdf)、
[分数](examples/fractions.pdf)、[小数](examples/decimals.pdf)。

## 选择练习

| Series | Level | 内容 |
|---|---:|---|
| `addsub` | 1–24 | 整数加减、负数、填空 |
| `muldiv` | 1–26 | 整数乘除、括号、四则混合、填空 |
| `fraction` | 1–18 | 分数、小数、三种数字混合运算 |

编号表示预设题型，不代表学校年级，也不保证难度严格递增。
`fraction` 是稳定的调用标识，其中包含小数题型。

```bash
arithmetic list --lang zh-CN
arithmetic describe --series fraction --level 10 --lang zh-CN
arithmetic generate --series fraction --level 10 --pages 2 --seed 42 --output worksheets/decimals.pdf
```

[完整目录](docs/levels.zh-CN.md)介绍每个级别的练习目标、源范围、实际例题、每页题数和生成命令。
Agent 可以通过 `list --json`、`describe --json` 获取同源结构化信息。

## 行为与配置

- 默认生成 `addsub` Level 1，共 10 页。整数系列默认每页 10 题，分数系列 14 题；
  分数系列 Level 8、9、17、18 固定为每页 12 题。
- 同一程序和依赖版本下，`--seed` 可复现题目内容；日期和元数据使 PDF 字节不一定相同。
- 普通模式排除无定义的算式，以及没有唯一有理数解的填空。源数范围不一定限制答案范围。
- `--allow-undefined` 启用除零识别教学模式，并在页脚标注。它允许出现此类题，不保证每页都有。
- 分数采用 `3/4` 行内形式；支持与整数、小数混排。
- 首版没有答案页、任意操作数范围参数或图形界面。
- 多样性选择会减少重复；题池较小时仍可能重复。

通过 `--config examples/override.yaml` 合并版式与每页题数配置。
完整参数、路径规则、批量生成、Python 调用和故障排查见[使用说明](docs/usage.zh-CN.md)。

## 开发

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/build_catalog_docs.py --check
uv build
```

参阅[贡献指南](CONTRIBUTING.md)。

## 许可证与 PDF 使用

代码和项目自有文档采用 [MIT](LICENSE)，按其条款允许使用、修改、分发和商业使用。

Namishu 允许你打印、分享、修改及销售生成的练习纸。仅因使用本程序生成 PDF，
不要求附带软件许可证；第三方素材仍遵守其各自适用条款。
本项目不分发字体文件；安装的依赖包保留各自的许可证。
使用本软件不表示 Namishu 对你的材料作出背书。
