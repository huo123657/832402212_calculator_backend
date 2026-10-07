"""calculator_service.py - 计算业务逻辑（Service 层）

职责：接收原始表达式 -> 规范化 -> 解析求值 -> 保存历史 -> 返回结果。
前端只负责收集输入和展示，所有计算都在这里完成。
"""

from service import expression_parser
from service import history_service

# 允许的最大表达式长度，防止超长恶意输入
MAX_EXPRESSION_LENGTH = 200


def _normalize(expression):
    """规范化表达式：统一全角/显示符号为标准运算符。

    前端界面上乘除显示为 × ÷，发送前可能未被转换，这里兜底处理。
    """
    return (
        str(expression)
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .strip()
    )


def calculate_and_store(raw_expression):
    """计算表达式并把成功结果写入历史。

    :param raw_expression: 前端发来的原始表达式字符串，如 "(1+2)*3"
    :return: dict，包含 expression / result(数值) / result_text(展示串) / time
    :raises expression_parser.ExpressionError: 表达式语法错误
    :raises expression_parser.DivisionByZeroError: 除数为零
    """
    expression = _normalize(raw_expression)

    if not expression:
        raise expression_parser.ExpressionError("Expression is empty")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise expression_parser.ExpressionError("Expression is too long")

    # 核心计算：词法分析 + 递归下降解析求值（不使用 eval）
    value = expression_parser.evaluate(expression)

    result_text = expression_parser.format_number(value)
    history_id, created_at = history_service.add_history(expression, result_text)

    return {
        "id": history_id,
        "expression": expression,
        "result": int(result_text) if result_text.lstrip("-").isdigit() else float(result_text),
        "result_text": result_text,
        "time": created_at,
    }
