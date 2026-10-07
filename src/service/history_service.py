"""history_service.py - 计算历史业务逻辑（Service 层）

封装历史记录的查询、单条删除、清空，供控制器调用。
数据实际读写全部落在 SQLite 数据库（model/database.py）。
"""

from model import database


def add_history(expression, result_text):
    """新增一条历史记录，返回 (id, created_at)。"""
    return database.insert_history(expression, result_text)


def list_history():
    """返回全部历史记录列表（新记录在前）。"""
    return database.get_all_history()


def remove_history(history_id):
    """按 id 删除一条历史。

    :return: True 删除成功 / False 记录不存在
    """
    return database.delete_history(history_id)


def clear_history():
    """清空全部历史，返回删除条数。"""
    return database.delete_all_history()
