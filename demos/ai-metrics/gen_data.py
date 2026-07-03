"""生成 demo 所需的示例数据（开箱即跑）：
  1. sample_repo/ —— 示例 git 仓库，含 3 类提交演示三层 AI 识别算法：
       - 作者 Alice 的多条「干净提交」（风格 A，用来建风格画像）
       - Alice 的「AI 提交」（风格 B + Co-authored-by Claude，与画像差异大 → 高置信度）
       - Alice 的「误标提交」（风格 A + Co-authored-by Claude，与画像很像 → 风格学降置信度，演示反伪造）
  2. data/template.xlsx —— Excel 模板（用户按此录入自己的上线记录）
  3. data/sample_releases.xlsx —— 示例上线记录（2025 vs 2026 同比）
"""
import os
import subprocess
from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "workspace")   # 运行时产物单独放这里，不污染源码目录
REPO = os.path.join(WORK, "sample_repo")
DATA = os.path.join(WORK, "data")

# ===== 风格 A：Alice 本人手写风格（多行中文注释 + print 调试 + data_x 命名 + for-append）=====
STYLE_A = {
    "utils.py": (
        "# 工具函数模块\n"
        "# 这个文件提供基础的数据获取功能\n"
        "# 主要用来演示作者本人的代码风格\n"
        "# 习惯用 print 调试，变量用 data_ 前缀命名\n"
        "# 手写循环，不追求简洁，重视可读\n"
        "def get_list():\n"
        "    print('start get_list')\n"
        "    data_list = []\n"
        "    for i in range(10):\n"
        "        data_list.append(i * 2)\n"
        "    print('got', data_list)\n"
        "    return data_list\n"
    ),
    "helpers.py": (
        "# 帮助函数\n"
        "# 提供数据计算相关的辅助方法\n"
        "# 沿用 print 调试和 data_ 命名风格\n"
        "# 手写循环累加，不用内置函数\n"
        "# 注释都用中文，方便团队阅读\n"
        "def calc_data():\n"
        "    print('calc start')\n"
        "    data_sum = 0\n"
        "    for j in range(5):\n"
        "        data_sum = data_sum + j\n"
        "    print('sum is', data_sum)\n"
        "    return data_sum\n"
    ),
    "common.py": (
        "# 通用方法集合\n"
        "# 包含数据加载等公共功能\n"
        "# 保持 print 调试习惯\n"
        "# 变量命名用 data_items 这类风格\n"
        "# 注释中文，代码英文，符合团队规范\n"
        "def load_data():\n"
        "    print('loading data')\n"
        "    data_items = []\n"
        "    for k in range(8):\n"
        "        data_items.append(k)\n"
        "    print('loaded', len(data_items))\n"
        "    return data_items\n"
    ),
}

# ===== 风格 B：AI 生成风格（type hints + dataclass + 长 docstring + 列表/集合推导）=====
STYLE_B = {
    "feature.py": (
        "from typing import List, Optional, Dict, Any, Set\n"
        "from dataclasses import dataclass, field\n"
        "\n"
        "@dataclass\n"
        "class Item:\n"
        "    \"\"\"Represents a single processable item with metadata.\"\"\"\n"
        "    id: int\n"
        "    name: str\n"
        "    tags: List[str] = field(default_factory=list)\n"
        "\n"
        "    def is_valid(self) -> bool:\n"
        "        \"\"\"Check whether this item satisfies validation rules.\"\"\"\n"
        "        return self.id > 0 and bool(self.name)\n"
        "\n"
        "\n"
        "def process_items(items: List[Item]) -> Dict[str, Any]:\n"
        "    \"\"\"Process the given items and return aggregated results.\n"
        "\n"
        "    Args:\n"
        "        items: List of Item objects to process.\n"
        "\n"
        "    Returns:\n"
        "        Dictionary containing processed entries and summary statistics.\n"
        "    \"\"\"\n"
        "    valid: List[Item] = [item for item in items if item.is_valid()]\n"
        "    return {\n"
        "        'count': len(valid),\n"
        "        'names': [item.name.upper() for item in valid],\n"
        "        'tags': {tag for item in valid for tag in item.tags},\n"
        "    }\n"
        "\n"
        "\n"
        "def validate_config(config: Dict[str, Any]) -> Optional[List[str]]:\n"
        "    \"\"\"Validate configuration and return sorted keys if valid.\"\"\"\n"
        "    if not config or not config.get('enabled'):\n"
        "        return None\n"
        "    return sorted(config.keys())\n"
    ),
}

# ===== 误标提交：风格 A 的代码，但带了 Co-authored-by（演示风格学反伪造）=====
STYLE_A_MISFLAG = {
    "manual_fix.py": (
        "# 手动修复\n"
        "# 这个修改是开发人员手工写的\n"
        "# 风格和本人完全一致，多行中文注释\n"
        "# 但提交时被工具自动加了 AI 标记\n"
        "# 风格学应该识别出它像本人，降低置信度\n"
        "def fix_data():\n"
        "    print('fix start')\n"
        "    data_fixed = []\n"
        "    for n in range(6):\n"
        "        data_fixed.append(n + 1)\n"
        "    print('fixed', data_fixed)\n"
        "    return data_fixed\n"
    ),
}


def run(cmd, cwd):
    """执行命令（list 形式，不用 shell，避免引号/中文问题）。"""
    subprocess.run(cmd, cwd=cwd, check=True)


def write_file(name, content):
    with open(os.path.join(REPO, name), "w", encoding="utf-8") as f:
        f.write(content)


def git_commit(repo, msg, ai=False):
    run(["git", "add", "-A"], repo)
    cmd = ["git", "commit", "-m", msg]
    if ai:
        cmd += ["-m", "Co-authored-by: Claude <noreply@anthropic.com>"]
    run(cmd, repo)


def init_sample_repo():
    if os.path.exists(os.path.join(REPO, ".git")):
        return False  # 已初始化
    os.makedirs(REPO, exist_ok=True)
    run(["git", "init"], REPO)
    run(["git", "config", "user.email", "alice@demo.com"], REPO)
    run(["git", "config", "user.name", "Alice"], REPO)
    # ① 干净提交（风格 A，建画像）
    for name, content in STYLE_A.items():
        write_file(name, content)
        git_commit(REPO, f"add {name}", ai=False)
    # ② AI 提交（风格 B + Co-authored-by）
    for name, content in STYLE_B.items():
        write_file(name, content)
        git_commit(REPO, f"add {name} (AI generated)", ai=True)
    # ③ 误标提交（风格 A + Co-authored-by，测反伪造）
    for name, content in STYLE_A_MISFLAG.items():
        write_file(name, content)
        git_commit(REPO, f"{name} by hand", ai=True)
    return True


# ===== Excel：上线记录模板与示例数据 =====
EXCEL_HEADER = ["日期", "定制或通用", "应用", "类型", "jira_id", "描述", "开发人员"]


def gen_template():
    """生成空模板 + 填写说明 + 一行示例。"""
    wb = Workbook()
    ws = wb.active
    ws.title = "上线记录"
    ws.append(EXCEL_HEADER)
    ws.append(["填写说明：每行一条上线记录；类型填『需求』或『Bug』；日期格式 2025-03-15；开发人员多人用逗号分隔"])
    ws.append(["2025-03-10", "通用", "课程管理", "需求", "JIRA-001", "新增课程导入功能", "张三"])
    wb.save(os.path.join(DATA, "template.xlsx"))


# 示例上线记录（2025 基线 vs 2026 AI 推行后；体现需求升、Bug 降、人数略降）
SAMPLE_ROWS = [
    # 2025 基线（需求 / Bug 各半，5 人）
    ["2025-03-05", "通用", "课程管理", "需求", "JIRA-101", "课程列表分页", "张三"],
    ["2025-03-08", "定制", "考试模块", "Bug", "JIRA-102", "交卷卡顿", "李四"],
    ["2025-03-12", "通用", "用户中心", "需求", "JIRA-103", "批量导入用户", "王五"],
    ["2025-03-15", "定制", "课程管理", "Bug", "JIRA-104", "导出乱码", "张三"],
    ["2025-03-20", "通用", "考试模块", "需求", "JIRA-105", "随机组卷", "赵六"],
    ["2025-03-25", "定制", "用户中心", "Bug", "JIRA-106", "登录失败", "李四"],
    ["2025-04-02", "通用", "课程管理", "需求", "JIRA-107", "课程分类", "张三"],
    ["2025-04-08", "定制", "考试模块", "Bug", "JIRA-108", "成绩统计错", "赵六"],
    ["2025-04-12", "通用", "用户中心", "需求", "JIRA-109", "权限调整", "王五"],
    ["2025-04-18", "定制", "课程管理", "Bug", "JIRA-110", "封面上传失败", "张三"],
    # 2026 AI 推行后（需求升、Bug 明显降，仍是 5 人但其中含 AI 协作）
    ["2026-03-03", "通用", "课程管理", "需求", "JIRA-201", "课程标签体系", "张三"],
    ["2026-03-06", "定制", "考试模块", "需求", "JIRA-202", "智能组卷规则", "赵六"],
    ["2026-03-10", "通用", "用户中心", "需求", "JIRA-203", "组织架构树", "王五"],
    ["2026-03-13", "定制", "课程管理", "Bug", "JIRA-204", "标签筛选异常", "张三"],
    ["2026-03-17", "通用", "考试模块", "需求", "JIRA-205", "阅卷批注", "赵六"],
    ["2026-03-21", "定制", "用户中心", "需求", "JIRA-206", "消息中心", "李四"],
    ["2026-04-02", "通用", "课程管理", "需求", "JIRA-207", "课程市场对接", "张三"],
    ["2026-04-05", "定制", "考试模块", "Bug", "JIRA-208", "倒计时偏差", "赵六"],
    ["2026-04-09", "通用", "用户中心", "需求", "JIRA-209", "个人发展计划", "王五"],
    ["2026-04-13", "定制", "课程管理", "需求", "JIRA-210", "学习地图", "张三"],
]


def gen_sample_releases():
    wb = Workbook()
    ws = wb.active
    ws.title = "上线记录"
    ws.append(EXCEL_HEADER)
    for row in SAMPLE_ROWS:
        ws.append(row)
    wb.save(os.path.join(DATA, "sample_releases.xlsx"))


def main():
    os.makedirs(DATA, exist_ok=True)
    created = init_sample_repo()
    print(f"sample_repo: {'已初始化' if created else '已存在，跳过'}")
    gen_template()
    print("data/template.xlsx 已生成（用户按此模板录入）")
    gen_sample_releases()
    print("data/sample_releases.xlsx 已生成（示例 2025/2026 数据）")


if __name__ == "__main__":
    main()
