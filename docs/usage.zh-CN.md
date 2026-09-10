# 使用与配置

[English](usage.md)

安装和首次生成请从 [README](../README.zh-CN.md) 开始。
通过[题型目录](levels.zh-CN.md)选择练习，或让 Agent 按照[英文操作指南](agent-guide.md)代为生成。

## 命令

`arithmetic --help` 及各子命令的 `--help` 会列出可用参数。
也可以使用等价入口 `python -m namishu_arithmetic`。

| 命令 | 参数 |
|---|---|
| `list` | `--series`、`--lang en/zh-CN`、`--json` |
| `describe` | 必填 `--series`、必填 `--level`、`--lang`、`--json` |
| `generate` | `--series`、`--level`、`--pages`、`--seed`、`--output`、`--config`、`--allow-undefined`、`--force`、`--json` |
| `generate --all` | `--output-dir`、`--pages`、`--seed`、`--config`、`--allow-undefined`、`--force`、`--json` |

单文件默认生成 `addsub` Level 1，共 10 页，输出到
`worksheets/{series}/level-{level}.pdf`。批量模式生成全部 68 个级别，
不能同时指定 `--series`、`--level` 或 `--output`。

```bash
arithmetic generate --all --pages 1 --seed 42 --output-dir worksheets/collection
```

不指定 `--seed` 时，程序自动选择种子并在结果中报告。同一程序和依赖版本下，
相同种子与设置可复现题目内容；PDF 日期和元数据可能不同。

普通模式排除无定义算式以及没有唯一有理数解的填空。
`--allow-undefined` 允许完整的无定义算式用于识别练习，并标注页脚，但不保证出现比例。
填空题仍必须有唯一的有效有理数解。

## 路径与输出

命令行的输出路径和配置路径相对当前工作目录。
YAML 内的自定义字体路径相对该 YAML 文件所在目录。
标准 Helvetica 不需要字体文件，默认设置随程序提供，安装后可以从任意目录运行。

覆盖已有文件需要显式指定 `--force`。错误信息输出到 stderr，退出码为 2；
成功时的 `--json` 输出是 stdout 上的单个 JSON 对象。
生成结果包含文件绝对路径、页数、每页题数、seed、series、level，以及是否允许无定义算式。

## 配置

将以下内容保存为 `worksheet.yaml`。只覆盖写出的设置，其他设置保持默认值。

```yaml
problems_per_page:
  default: 12
  fraction: 14
layout:
  page:
    width_mm: 210
    height_mm: 297
  margin:
    left_mm: 20
    right_mm: 20
    top_mm: 25
    bottom_mm: 25
  typography:
    line_spacing_ratio: 1.0
```

```bash
arithmetic generate --series addsub --level 1 --pages 2 --config worksheet.yaml --output worksheets/addition.pdf
```

`default` 控制整数系列的每页题数，`fraction` 单独设置，默认每页 14 题。
分数系列 Level 8、9、17、18 固定为每页 12 题。
尺寸单位为毫米，以 `*_pt` 命名的字段使用点。较长算式会缩小以适应页宽。
版式配置不改变操作数范围。

多样性设置 `candidate_multiplier`、`max_same_leading_operand_per_page`、
`max_special_operand_per_page` 影响题目选择，不改变数学难度。
这些是选择偏好，不能保证所有题目互不重复。

## 字体

默认 Helvetica 覆盖当前英文标题、数字和四则运算符，不包含中文字形。
不同 PDF 阅读器可能使用略有差异的替代字体。无需安装字体或查找系统字体目录。
可参阅 [ReportLab 字体说明](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/)。

如需使用其他 PDF 标准字体，可在 YAML 覆盖配置中加入：

```yaml
layout:
  typography:
    font_name: Times-Roman
    font_path: null
```

也可以选择 `Courier`。如需自行提供本地 TrueType 字体，使用一个与 PDF 标准字体名称
不同的自定义 `font_name`，并将 `font_path` 设置为相对 YAML 文件的路径。
自备字体仍需遵守其适用的许可证。

## Python 调用

```python
from namishu_arithmetic import ArithmeticApp

app = ArithmeticApp()
path = app.generate("fraction", 10, "worksheets/decimals.pdf", pages=2, seed=42)
problems = app.generate_pages("fraction", 10, pages=2, seed=42)
```

Python API 会写入指定路径，并覆盖已有文件；命令行的覆盖保护仅适用于 CLI。
`generate_pages` 返回 `list[list[str]]`，每个内层列表是一页的题目字符串，不写 PDF。
可用 `ArithmeticApp(config_path="worksheet.yaml")` 加载覆盖配置。
两个生成方法都可以通过 `allow_undefined=True` 启用教学模式。
不支持在多个线程中并发生成。

## 从旧命令切换

如果此前使用 printables-python 中的生成器，请安装本独立项目，并将
`uv run pt arithmetic ...` 改为 `uv run arithmetic generate ...`。
生成完整题集使用 `uv run arithmetic generate --all`。

原有 3 个 series 和 68 个 level 编号保持不变。
默认输出改为 `worksheets/{series}/level-{level}.pdf`，可以通过 `--output` 指定其他位置。
普通模式现在会排除无定义算式和无效填空，因此旧 seed 可能生成不同题目。

## 限制与排错

- 不提供任意数值范围选择、答案页、年级或课程映射、图形界面。
- 分数采用行内形式，可能尚未约分，每个分数作为一个操作数。
- 即使源数都是整数，填空答案也可能是负数或分数。
- 候选题池较小时，仍可能出现重复或相似题目。
- 找不到 `arithmetic` 时，先激活环境，或使用 `python -m namishu_arithmetic`。
- 自定义字体加载失败时，修正路径或移除字体覆盖配置。
- Windows PowerShell 无法激活环境时，可直接执行 `.venv\Scripts\python.exe -m pip install .`
  和 `.venv\Scripts\python.exe -m namishu_arithmetic generate`。
- CLI 会检查文件是否生成；页数和版面请使用 PDF 阅读器打开确认。
