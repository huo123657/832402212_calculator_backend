"""expression_parser.py - 安全的数学表达式解析与求值模块

采用「词法分析 + 递归下降语法分析 + 边解析边求值」的方式处理四则运算表达式。
全程只把输入当作「数字和运算符组成的字符串」来处理，
不使用 eval / exec 等会把用户输入当代码执行的函数，保证安全性。

支持的语法（EBNF 文法）：
    expression := term  (('+' | '-') term)*        # 加减，优先级低
    term       := factor (('*' | '/') factor)*     # 乘除，优先级高
    factor     := ('+' | '-') factor               # 一元正负号
                | '(' expression ')'               # 括号
                | NUMBER                           # 整数 / 小数

优先级通过文法层次天然体现：expression 处理加减，term 处理乘除，
factor 处理一元符号和括号 —— 乘除在更深的层次先结合，因此优先级更高。
"""

import numbers


class ExpressionError(ValueError):
    """表达式语法错误（非法字符、括号不匹配、格式不完整等）。"""


class DivisionByZeroError(ArithmeticError):
    """除数为零错误。"""


_OPERATORS = {"+", "-", "*", "/", "(", ")"}


def tokenize(expression):
    """词法分析：把表达式字符串切分成 token 列表。

    数字 token 存为 float，运算符 / 括号 token 存为单字符字符串。
    例："-5+8" -> ['-', 5.0, '+', 8.0]
    """
    tokens = []
    i = 0
    length = len(expression)
    while i < length:
        char = expression[i]
        if char in _OPERATORS:
            tokens.append(char)
            i += 1
        elif char.isdigit() or char == ".":
            dot_count = 0
            j = i
            while j < length and (expression[j].isdigit() or expression[j] == "."):
                if expression[j] == ".":
                    dot_count += 1
                j += 1
            number_text = expression[i:j]
            if dot_count > 1 or number_text == ".":
                raise ExpressionError("Invalid number: " + number_text)
            tokens.append(float(number_text))
            i = j
        else:
            raise ExpressionError("Invalid character: " + char)
    return tokens


class _Parser:
    """递归下降语法分析器，解析的同时直接求值。"""

    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0

    def _peek(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _advance(self):
        token = self._peek()
        self._pos += 1
        return token

    def parse(self):
        if not self._tokens:
            raise ExpressionError("Expression is empty")
        value = self._expression()
        if self._pos < len(self._tokens):
            raise ExpressionError(
                "Unexpected token: " + str(self._tokens[self._pos])
            )
        return value

    def _expression(self):
        """加减层：term (('+'|'-') term)*"""
        value = self._term()
        while self._peek() in ("+", "-"):
            operator = self._advance()
            right = self._term()
            value = value + right if operator == "+" else value - right
        return value

    def _term(self):
        """乘除层：factor (('*'|'/') factor)*，除零在这里拦截。"""
        value = self._factor()
        while self._peek() in ("*", "/"):
            operator = self._advance()
            right = self._factor()
            if operator == "*":
                value = value * right
            else:
                if right == 0:
                    raise DivisionByZeroError("Division by zero")
                value = value / right
        return value

    def _factor(self):
        """一元符号 / 括号 / 数字层。"""
        token = self._peek()
        if token == "+":
            self._advance()
            return self._factor()
        if token == "-":
            self._advance()
            return -self._factor()
        if token == "(":
            self._advance()
            value = self._expression()
            if self._peek() != ")":
                raise ExpressionError("Missing closing parenthesis")
            self._advance()
            return value
        if isinstance(token, float):
            return self._advance()
        if token is None:
            raise ExpressionError("Incomplete expression")
        raise ExpressionError("Unexpected token: " + str(token))


def evaluate(expression):
    """解析并计算表达式，返回 float 结果。

    :raises ExpressionError: 表达式语法错误
    :raises DivisionByZeroError: 除数为零
    """
    tokens = tokenize(expression)
    return _Parser(tokens).parse()


def format_number(value):
    """把计算结果格式化为适合展示/存储的字符串。

    - 浮点误差处理：四舍五入到 10 位小数，去掉多余的 0，
      例如 0.1+0.2 得到 0.3 而不是 0.30000000000000004
    - 整数值结果去掉小数点，例如 20.0 显示为 20
    """
    if not isinstance(value, numbers.Real):
        raise TypeError("value must be a real number")
    value = round(float(value), 10)
    if value == int(value):
        return str(int(value))
    return repr(value)
