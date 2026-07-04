#!/usr/bin/env python3
"""PostgreSQL 只读查询脚本（教学骨架）。

完整实现含 SSH 隧道建连、租户库发现、schema 拉取等；
本文件是教学骨架，演示「安全护栏」的关键结构，不能直接跑（需补 SSH/DB 配置）。

安全护栏（命门，必须实现）：
1. 仅 SELECT —— 写操作直接拒绝
2. SSH 隧道 —— 自动建/关，不留长连接
3. 租户隔离 —— SQL 自动加 corp_code 条件
4. 自动 LIMIT —— 无 LIMIT 加 LIMIT 2000
"""
import sys
import re

# ===== 护栏 1：仅 SELECT =====
WRITE_PATTERN = re.compile(r"\b(insert|update|delete|drop|alter|truncate|create|grant)\b", re.IGNORECASE)

def reject_write(sql: str) -> None:
    if WRITE_PATTERN.search(sql):
        sys.exit("拒绝：仅支持 SELECT 查询，写操作被护栏拦截。")

# ===== 护栏 4：自动 LIMIT =====
def ensure_limit(sql: str) -> str:
    if "limit" not in sql.lower():
        sql = sql.rstrip("; ") + " LIMIT 2000"
    return sql

# ===== 护栏 3：租户隔离（自动加 corp_code） =====
def add_tenant_filter(sql: str, corp_code: str) -> str:
    # 简化示意：完整实现要解析 SQL AST，精确注入到 WHERE
    # 这里只演示「必须带 corp_code」的红线思想
    if "corp_code" not in sql.lower():
        print(f"警告：SQL 未带 corp_code，租户隔离护栏要求每条查询必带租户条件。")
    return sql

def run_query(corp_code: str, sql: str) -> None:
    """主流程：护栏检查 → SSH 隧道 → 查询 → 关隧道。"""
    reject_write(sql)                      # 护栏 1
    sql = ensure_limit(sql)                # 护栏 4
    sql = add_tenant_filter(sql, corp_code)  # 护栏 3

    # 护栏 2：SSH 隧道（骨架，完整实现用 paramiko/sshtunnel）
    # with SSHTunnel(...) as tunnel:
    #     conn = psycopg2.connect(host=tunnel.local_bind_host, ...)
    #     cur.execute(sql)
    print(f"[教学骨架] 将通过 SSH 隧道对租户 {corp_code} 执行：{sql}")
    print("（完整实现需补 SSH/DB 连接，本骨架演示护栏结构）")

if __name__ == "__main__":
    # 用法：python3 pg_tunnel_query.py <corp_code> "<sql>"
    #       python3 pg_tunnel_query.py --info <corp_code>
    #       python3 pg_tunnel_query.py --schema <corp_code>
    args = sys.argv[1:]
    if len(args) < 2:
        print("用法: pg_tunnel_query.py <corp_code> '<sql>' | --info <corp_code> | --schema <corp_code>")
        sys.exit(1)
    if args[0] == "--info":
        print(f"[骨架] 查租户 {args[1]} 的连接信息（需补 DB 配置发现逻辑）")
    elif args[0] == "--schema":
        print(f"[骨架] 同步租户 {args[1]} 的表结构到 schemas/（需补 schema 拉取逻辑）")
    else:
        run_query(args[0], args[1])
