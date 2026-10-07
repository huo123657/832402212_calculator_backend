"""app.py - 后端应用入口

启动方式（在后端项目根目录）：
    python src/app.py
默认监听 http://127.0.0.1:5000
"""

import os
import sys

# 保证以任意工作目录启动时都能找到 src 下的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify

from controller.api_controller import api_bp
from model.database import init_db


def create_app():
    """应用工厂：创建 Flask 应用、初始化数据库、注册路由与全局处理。"""
    app = Flask(__name__)
    init_db()
    app.register_blueprint(api_bp)

    # ---------- 跨域支持 ----------
    # 前后端分离部署（不同端口 / 不同域名）时浏览器会发起跨域请求，
    # 这里统一在响应头中放行；预检 OPTIONS 请求由 Flask 自动响应。
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    # ---------- 全局异常兜底 ----------
    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"success": False, "message": "API not found"}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def handle_server_error(_error):
        return jsonify({"success": False, "message": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    # debug=False：生产/演示环境不要开调试模式
    app.run(host="0.0.0.0", port=5000, debug=False)
