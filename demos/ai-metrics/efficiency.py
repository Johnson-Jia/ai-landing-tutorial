"""提效统计 —— 解析 Excel 上线记录，按年份同比，算需求/Bug 占比和人均效率。

对应 AI提效统计分析 的 01_parse_excel + 03_analyze_data 思路（简化）：
用户按 data/template.xlsx 录入自己的上线记录，这里解析并统计同比。
"""
import openpyxl


def parse_releases(xlsx_path):
    """解析上线记录 Excel。列：日期/定制或通用/应用/类型/jira_id/描述/开发人员。"""
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    records = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        date = str(row[0])
        if "说明" in date or "填写" in date or not date[:4].isdigit():
            continue
        typ = str(row[3] or "").strip()
        dev = str(row[6] or "").strip()
        records.append({"year": date[:4], "type": typ, "dev": dev})
    return records


def analyze(records, years=("2025", "2026")):
    """按年份统计上线条目 / 需求 / Bug / 人数 / 人均。"""
    stats = {}
    for y in years:
        rs = [r for r in records if r["year"] == y]
        devs = set()
        for r in rs:
            for d in r["dev"].split(","):
                d = d.strip()
                if d:
                    devs.add(d)
        req = sum(1 for r in rs if r["type"] == "需求")
        bug = sum(1 for r in rs if r["type"] == "Bug")
        stats[y] = {
            "total": len(rs),
            "req": req,
            "bug": bug,
            "devs": len(devs),
            "per_capita": (len(rs) / len(devs)) if devs else 0,
        }
    return stats
