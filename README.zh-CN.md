<h1 align="center">Namishu Arithmetic</h1>

<p align="center">生成可打印的整数、分数和小数四则运算练习。</p>

<p align="center">
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&amp;logo=python&amp;logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-22A06B?style=flat" alt="License: MIT"></a>
  <a href="examples/addition.pdf"><img src="https://img.shields.io/badge/PDF-A4-E05D44?style=flat" alt="PDF: A4"></a>
</p>

<p align="center"><a href="README.md">English</a> · <strong>简体中文</strong></p>

<p align="center">
  <a href="#快速上手">快速上手</a> · <a href="docs/levels.zh-CN.md">题型目录</a> ·
  <a href="#其他命令">其他命令</a> · <a href="docs/agent-guide.md">Agent 指南</a>
</p>

---

Namishu Arithmetic 是一个数学口算练习纸生成工具，适合家长准备日常练习、教师布置课堂作业，
也适合需要反复练习某类运算的学习者。选择题型和页数，就能生成可直接打印的 A4 PDF，
省去手工出题和排版的时间；需要更多练习时，再运行一次即可得到一组新题。

项目提供 **3 个系列、68 个级别**，覆盖整数、分数和小数的加减乘除，
包含负数、括号、混合运算和填空题。你可以按练习目标选择预设题型，
调整每页题数和版式，也可以固定随机种子，重复生成同一组题目。

<p align="center">
  示例 PDF 文件：<a href="examples/addition.pdf">加法</a> · <a href="examples/multiplication.pdf">乘法</a> ·
  <a href="examples/fractions.pdf">分数</a> · <a href="examples/decimals.pdf">小数</a>
</p>

## 安装

环境：**Python 3.10+ 和 uv**。

```bash
git clone https://github.com/namishu/arithmetic.git
cd arithmetic
uv sync
```

以下命令均在项目目录执行。

## 快速上手

选择一个系列和级别，即可生成练习：

| 系列（`--series`） | 级别（`--level`） | 内容 |
|---|---|---|
| `addsub` | 1–24 | 整数加减、负数、填空 |
| `muldiv` | 1–26 | 整数乘除、括号、四则混合、填空 |
| `fraction` | 1–18 | 分数、小数及混合数字运算 |

每个级别对应一种预设题型，具体内容见[题型目录](docs/levels.zh-CN.md)。
例如，`addsub` 的第 1 级是两个 0–10 的整数相加，结果可能达到 20。

### 生成 PDF

生成 **5 页加法练习**，保存到 `worksheets/addition.pdf`：

```bash
uv run arithmetic generate --series addsub --level 1 --pages 5 --output worksheets/addition.pdf
```

`generate` 用于生成 PDF。上面命令的四个参数分别是：

| 参数 | 含义 | 是否必填 |
|---|---|---|
| `--series addsub` | 选择加减法系列 | 必填 |
| `--level 1` | 选择该系列的第 1 级题型 | 必填 |
| `--pages 5` | 生成 5 页 | 可选，默认 10 页 |
| `--output worksheets/addition.pdf` | 指定 PDF 文件位置 | 可选，默认 `worksheets/{series}/level-{level}.pdf` |

完成后会显示文件位置。打开 PDF，按 A4、实际大小打印。

生成时还可以添加以下参数：

| 参数 | 用途 |
|---|---|
| `--seed 42` | 固定随机种子，在相同程序和依赖版本下复现题目；省略时随机选择并显示种子 |
| `--disallow-zero-denominator` | 排除分母或除数为 0 的算式；默认允许 |
| `--config examples/override.yaml` | 从 YAML 文件读取版式和每页题数配置 |
| `--force` | 覆盖同名文件；默认遇到已有文件会报错 |
| `--json` | 以 JSON 返回生成文件的位置、页数、题型、种子等信息，供程序或 Agent 读取 |

例如，生成 **2 页除法练习，排除除零，并固定种子**：

```bash
uv run arithmetic generate --series muldiv --level 5 --pages 2 --seed 42 --disallow-zero-denominator --output worksheets/division.pdf
```

也可以将仓库地址或本地目录交给能执行命令的 Agent，直接描述需求：

> 请用这个项目生成 5 页不含负操作数的基础乘法练习，保存到 worksheets 文件夹。
> 检查 PDF，并给出文件链接和生成参数。

## 其他命令

### 查看题型：`list`

列出所有系列、级别和题型名称；`--series` 可限定系列，`--json` 可返回 JSON。

```bash
uv run arithmetic list
uv run arithmetic list --series muldiv
```

### 查看级别详情：`describe`

显示指定级别的数值范围、运算规则、例题和每页题数。
`--series` 和 `--level` 必填，`--json` 可返回 JSON。

```bash
uv run arithmetic describe --series muldiv --level 5
```

### 生成完整题集：`generate --all`

为全部 68 个级别分别生成 PDF。下面的命令每个级别生成 1 页：

```bash
uv run arithmetic generate --all --pages 1 --output-dir worksheets/collection
```

`--all` 选择全部题型，`--output-dir` 指定根目录，默认是 `worksheets`。
文件按 `{series}/level-{level}.pdf` 存放。
批量生成可搭配 `--pages`、`--seed`、`--disallow-zero-denominator`、`--config`、`--force` 和 `--json`；
不能搭配 `--series`、`--level` 或 `--output`。`--output-dir` 仅用于批量生成。

### 帮助与版本

```bash
uv run arithmetic --help
uv run arithmetic generate --help
uv run arithmetic --version
```

`list` 和 `describe` 也支持 `--help`。

## 默认配置

| 项目 | 默认值 |
|---|---|
| 页数 | 每个 PDF 10 页 |
| 每页题数 | 整数系列 10 题；分数系列 14 题，其中第 8、9、17、18 级固定为 12 题 |
| 纸张 | A4 |
| 输出路径 | `worksheets/{series}/level-{level}.pdf` |
| 分母或除数为 0 | 允许 |
| 输出语言 | 英文 |

系列和级别须显式选择。填空题始终要求唯一有效的有理数解。
将以下配置保存为 `worksheet.yaml`，即可调整每页题数、页边距（毫米）和行距。
只修改写出的设置，其余保持默认值。

```yaml
problems_per_page:
  default: 12
layout:
  margin:
    left_mm: 20
    right_mm: 20
  typography:
    line_spacing_ratio: 1.0
```

```bash
uv run arithmetic generate --series addsub --level 1 --config worksheet.yaml
```

`default` 设置整数系列的每页题数；在同一层添加 `fraction` 可设置分数系列的每页题数。
上述四个固定为 12 题的级别保持原值。
也可直接使用 [examples/override.yaml](examples/override.yaml)。

## 许可证

代码和项目自有文档采用 [MIT 许可证](LICENSE)。
生成的练习纸可打印、分享、修改及销售。第三方素材遵循各自的许可条款。
