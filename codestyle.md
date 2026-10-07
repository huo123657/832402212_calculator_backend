# codestyle.md - 后端代码规范

> 本代码规范依据 **PEP 8 —— Python 官方代码风格指南** 制定，
> 来源：https://peps.python.org/pep-0008/
> 并参考 Google Python Style Guide 的部分实践：
> https://google.github.io/styleguide/pyguide.html
> 本项目（Flask 后端）在遵循 PEP 8 的基础上，补充了以下项目约定。

## 1. 代码布局

- 使用 **4 个空格** 缩进，禁止使用 Tab。
- 每行不超过 **88 个字符**（与 Black 等主流格式化工具一致）。
- 顶层函数与类定义之间空 **2 行**，类内方法之间空 **1 行**。
- 运算符两侧、逗号后保留 **1 个空格**；括号内侧不加空格。

```python
# 正确
result = value_a + value_b
func(a, b)

# 错误
result=value_a+value_b
func( a,b )
```

## 2. 命名规范

| 对象 | 风格 | 示例 |
| ---- | ---- | ---- |
| 模块/文件名 | 小写下划线 | `expression_parser.py` |
| 函数/方法 | 小写下划线（snake_case） | `calculate_and_store()` |
| 变量 | 小写下划线 | `history_id` |
| 常量 | 全大写下划线 | `MAX_EXPRESSION_LENGTH` |
| 类名 | 大驼峰（PascalCase） | `ExpressionError` |
| 受保护的内部成员 | 前置单下划线 | `_normalize()`、`_Parser` |

## 3. 导入规范

- 导入置于文件顶部（`app.py` 中的 `sys.path` 处理除外，需在导入前执行）。
- 顺序：标准库 → 第三方库 → 本项目模块，组间空 1 行。
- 使用 `from package import module` 形式导入本项目模块，禁止 `import *`。

```python
import os
import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request

from service import calculator_service
```

## 4. 文档字符串与注释

- 每个模块、每个公开函数必须编写 docstring，说明职责、参数与异常。
- 注释解释「为什么这样实现」，不复述代码本身。
- 关键算法（如表达式解析）在模块 docstring 中给出文法定义。

## 5. 异常处理

- 为业务定义专用异常类：`ExpressionError`（语法错误）、`DivisionByZeroError`（除零）。
- 只捕获能处理的异常；控制器层统一把业务异常转换为带 HTTP 状态码的 JSON 响应。
- 禁止裸 `except:`，禁止吞掉异常不报错。

## 6. 安全约定

- **严禁**使用 `eval` / `exec` 处理用户输入。
- 所有 SQL 一律使用参数化查询（`?` 占位符），防止 SQL 注入。
- 对外部输入先校验（类型、长度、合法字符），再进入业务逻辑。

## 7. 其他

- 字符串优先使用双引号（与项目现有代码保持一致）。
- 布尔比较使用 `is`（如 `if token is None`）。
- 提交前确保 `python tests/test_api.py` 全部通过。
