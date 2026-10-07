"""database.py - SQLite 数据库访问层（Model 层）

负责 calculation_history 表的建表、增、查、删等底层操作。
业务层（service）不直接接触 SQL，统一通过本模块访问数据库。
"""

import os
import sqlite3

from datetime import datetime

# 数据库文件默认放在后端项目根目录下（src/model 的上两级），
# 可通过环境变量 CALCULATOR_DB_PATH 覆盖（用于测试或部署时自定义位置）。
_DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "calculator.db",
)
DB_PATH = os.environ.get("CALCULATOR_DB_PATH", _DEFAULT_DB_PATH)


def get_connection():
    """获取数据库连接，行结果以 dict 形式返回。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库：建表（若不存在）。应用启动时调用一次。"""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                expression  TEXT    NOT NULL,
                result      TEXT    NOT NULL,
                created_at  TEXT    NOT NULL
            )
            """
        )


def insert_history(expression, result):
    """插入一条计算历史，返回 (id, created_at)。"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO calculation_history (expression, result, created_at) "
            "VALUES (?, ?, ?)",
            (expression, result, created_at),
        )
        return cursor.lastrowid, created_at


def get_all_history():
    """查询全部历史记录，按 id 倒序（新的在前）。"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, expression, result, created_at "
            "FROM calculation_history ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_history(history_id):
    """删除指定 id 的历史记录。删除成功返回 True，记录不存在返回 False。"""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM calculation_history WHERE id = ?", (history_id,)
        )
        return cursor.rowcount > 0


def delete_all_history():
    """清空全部历史记录，返回被删除的条数。"""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM calculation_history")
        return cursor.rowcount
