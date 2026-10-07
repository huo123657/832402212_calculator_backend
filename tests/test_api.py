"""test_api.py - API 自动化测试（基于 Flask test client，无需先启动服务）

运行方式（在后端项目根目录）：
    python tests/test_api.py

覆盖内容：
    功能1 基础四则运算        功能2 复合表达式与优先级
    异常处理（非法/除零等）    功能3 历史查询    功能4 历史删除
"""

import os
import sys
import tempfile

# 使用临时数据库，避免测试污染真实数据
os.environ["CALCULATOR_DB_PATH"] = os.path.join(tempfile.gettempdir(), "calc_test.db")

# 把 src 目录加入模块搜索路径
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"),
)

from app import create_app  # noqa: E402

app = create_app()
client = app.test_client()

_passed = 0
_failed = 0


def check(name, method, url, expected_status, payload=None, expect=None):
    """发送请求并断言状态码与响应字段。"""
    global _passed, _failed
    if method == "POST":
        response = client.post(url, json=payload)
    elif method == "DELETE":
        response = client.delete(url)
    else:
        response = client.get(url)
    data = response.get_json(silent=True)

    ok = response.status_code == expected_status
    detail = ""
    if ok and expect:
        for key, value in expect.items():
            if data.get(key) != value:
                ok = False
                detail = f"  (expect {key}={value!r}, got {data.get(key)!r})"
                break

    if ok:
        _passed += 1
        print(f"[PASS] {name}")
    else:
        _failed += 1
        print(f"[FAIL] {name}  status={response.status_code} body={data}{detail}")
    return data


print("=" * 60)
print("功能1：基础四则运算")
print("=" * 60)
check("加法 12+8=20", "POST", "/api/calculate", 200,
      {"expression": "12+8"}, {"success": True, "expression": "12+8", "result": 20})
check("减法 10-4=6", "POST", "/api/calculate", 200,
      {"expression": "10-4"}, {"success": True, "result": 6})
check("乘法 5*8=40", "POST", "/api/calculate", 200,
      {"expression": "5*8"}, {"success": True, "result": 40})
check("除法 10/4=2.5", "POST", "/api/calculate", 200,
      {"expression": "10/4"}, {"success": True, "result": 2.5})

print("=" * 60)
print("功能2：复合表达式（优先级/括号/一元符号/小数）")
print("=" * 60)
check("优先级 1+2*3=7", "POST", "/api/calculate", 200,
      {"expression": "1+2*3"}, {"result": 7})
check("括号 (1+2)*3=9", "POST", "/api/calculate", 200,
      {"expression": "(1+2)*3"}, {"result": 9})
check("混合 10/2+7=12", "POST", "/api/calculate", 200,
      {"expression": "10/2+7"}, {"result": 12})
check("混合 8-3*2=2", "POST", "/api/calculate", 200,
      {"expression": "8-3*2"}, {"result": 2})
check("一元负号 -5+8=3", "POST", "/api/calculate", 200,
      {"expression": "-5+8"}, {"result": 3})
check("负数乘法 3*-2=-6", "POST", "/api/calculate", 200,
      {"expression": "3*-2"}, {"result": -6})
check("小数 0.1+0.2=0.3", "POST", "/api/calculate", 200,
      {"expression": "0.1+0.2"}, {"result": 0.3})
check("嵌套括号 ((2+3))*4=20", "POST", "/api/calculate", 200,
      {"expression": "((2+3))*4"}, {"result": 20})
check("全角符号 5×8=40", "POST", "/api/calculate", 200,
      {"expression": "5×8"}, {"result": 40})

print("=" * 60)
print("异常处理")
print("=" * 60)
check("除零 5/0 -> 400", "POST", "/api/calculate", 400,
      {"expression": "5/0"}, {"success": False, "message": "Division by zero"})
check("非法字符 abc -> 400", "POST", "/api/calculate", 400,
      {"expression": "abc"}, {"success": False})
check("语法错误 1++ -> 400", "POST", "/api/calculate", 400,
      {"expression": "1++"}, {"success": False})
check("缺右括号 (1+2 -> 400", "POST", "/api/calculate", 400,
      {"expression": "(1+2"}, {"success": False})
check("多余右括号 1+2) -> 400", "POST", "/api/calculate", 400,
      {"expression": "1+2)"}, {"success": False})
check("空表达式 -> 400", "POST", "/api/calculate", 400,
      {"expression": ""}, {"success": False})
check("多小数点 1.2.3 -> 400", "POST", "/api/calculate", 400,
      {"expression": "1.2.3"}, {"success": False})
check("超长表达式 -> 400", "POST", "/api/calculate", 400,
      {"expression": "1" * 300}, {"success": False})
check("缺少 expression 字段 -> 400", "POST", "/api/calculate", 400,
      {"value": "1+1"}, {"success": False})
response = client.post("/api/calculate", data="hello", content_type="text/plain")
if response.status_code == 400:
    _passed += 1
    print("[PASS] 非 JSON 请求体 -> 400")
else:
    _failed += 1
    print(f"[FAIL] 非 JSON 请求体  status={response.status_code}")

print("=" * 60)
print("功能3：计算历史查询")
print("=" * 60)
history = check("查询历史列表", "GET", "/api/history", 200, expect={"success": True})
records = history["data"]
if len(records) >= 10:
    _passed += 1
    print(f"[PASS] 历史记录条数 >= 10（当前 {len(records)} 条）")
else:
    _failed += 1
    print(f"[FAIL] 历史记录条数不足（当前 {len(records)} 条）")
fields_ok = all(
    set(record) == {"id", "expression", "result", "created_at"} for record in records
)
if fields_ok:
    _passed += 1
    print("[PASS] 历史记录字段完整（id/expression/result/created_at）")
else:
    _failed += 1
    print("[FAIL] 历史记录字段缺失")

print("=" * 60)
print("功能4：删除历史记录")
print("=" * 60)
target_id = records[0]["id"]
check(f"删除存在的记录 #{target_id}", "DELETE", f"/api/history/{target_id}", 200,
      expect={"success": True})
check(f"再次删除 #{target_id} -> 404", "DELETE", f"/api/history/{target_id}", 404,
      expect={"success": False})
check("删除不存在的 #99999 -> 404", "DELETE", "/api/history/99999", 404,
      expect={"success": False})
after_delete = client.get("/api/history").get_json()["data"]
if all(record["id"] != target_id for record in after_delete):
    _passed += 1
    print(f"[PASS] 数据库中已无记录 #{target_id}")
else:
    _failed += 1
    print(f"[FAIL] 记录 #{target_id} 仍存在于数据库")

print("=" * 60)
print(f"测试完成：通过 {_passed} 项，失败 {_failed} 项")
print("=" * 60)
sys.exit(1 if _failed else 0)
