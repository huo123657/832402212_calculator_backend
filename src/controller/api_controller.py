"""api_controller.py - REST API 控制器（Controller 层）

定义前后端通信的全部 HTTP 接口，负责：
    - 接收并校验请求参数（不信任任何前端数据）
    - 调用 Service 层完成业务
    - 返回统一格式的 JSON 响应 + 合适的 HTTP 状态码

统一响应格式：
    成功: {"success": true,  ...业务字段...}
    失败: {"success": false, "message": "错误原因"}
"""

from flask import Blueprint, jsonify, request

from service import calculator_service
from service import history_service

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _error(message, status):
    """构造统一的失败响应。"""
    return jsonify({"success": False, "message": message}), status


@api_bp.route("/calculate", methods=["POST"])
def calculate():
    """计算接口：前端发送表达式，后端计算并返回结果。

    请求: {"expression": "(1+2)*3"}
    成功: 200 {"success": true, "expression": "(1+2)*3", "result": 9, ...}
    失败: 400 {"success": false, "message": "Invalid character: a"}
    """
    body = request.get_json(silent=True)
    if body is None:
        return _error("Request body must be valid JSON", 400)

    raw_expression = body.get("expression")
    if not isinstance(raw_expression, str):
        return _error("Field 'expression' is required and must be a string", 400)

    try:
        outcome = calculator_service.calculate_and_store(raw_expression)
    except calculator_service.expression_parser.DivisionByZeroError:
        return _error("Division by zero", 400)
    except calculator_service.expression_parser.ExpressionError as exc:
        return _error(str(exc), 400)

    return jsonify(
        {
            "success": True,
            "expression": outcome["expression"],
            "result": outcome["result"],
            "id": outcome["id"],
            "time": outcome["time"],
        }
    ), 200


@api_bp.route("/history", methods=["GET"])
def get_history():
    """查询全部计算历史（读自数据库）。

    成功: 200 {"success": true, "data": [{id, expression, result, created_at}, ...]}
    """
    return jsonify({"success": True, "data": history_service.list_history()}), 200


@api_bp.route("/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    """删除指定 id 的历史记录。

    成功: 200 {"success": true, "message": "History #3 deleted"}
    失败: 404 {"success": false, "message": "History #3 not found"}
    """
    if history_service.remove_history(history_id):
        return jsonify(
            {"success": True, "message": "History #%d deleted" % history_id}
        ), 200
    return _error("History #%d not found" % history_id, 404)


@api_bp.route("/history", methods=["DELETE"])
def clear_history():
    """清空全部历史记录（扩展功能）。"""
    deleted = history_service.clear_history()
    return jsonify(
        {
            "success": True,
            "message": "All history cleared",
            "deleted": deleted,
        }
    ), 200
