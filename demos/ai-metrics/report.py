"""报告生成 —— Markdown + HTML（ECharts 可视化）两种。

HTML 报告对齐 AI提效统计分析 的风格（卡片 + ECharts 图表 + 表格），用 CDN 加载
ECharts 5.5.0，数据从 git_stats / eff_stats 注入图表 option。
"""
import json


def render(git_stats, eff_stats):
    """生成 Markdown 报告：AI 占比 + 风格学反伪造样例 + 提效同比。"""
    md = ["# AI 度量与提效分析报告", ""]
    md.append("## 一、AI 代码占比（三层识别算法）")
    md.append("")
    md.append(f"- 总提交：**{git_stats['total_commits']}**，AI 提交：**{git_stats['ai_commits']}**（{git_stats['commit_ratio']:.1f}%）")
    md.append(f"- 新增行：**{git_stats['total_added']}**，AI 新增：**{git_stats['ai_added']}**（{git_stats['line_ratio']:.1f}%）")
    md.append("")
    md.append("### 作者明细")
    md.append("| 作者 | 总提交 | AI 提交 | AI 占比 |")
    md.append("|---|---|---|---|")
    for email, a in git_stats["by_author"].items():
        ratio = (a["ai"] / a["total"] * 100) if a["total"] else 0
        md.append(f"| {a['name']} | {a['total']} | {a['ai']} | {ratio:.0f}% |")
    md.append("")
    md.append("### 风格学反伪造样例（每个 AI 提交的相似度与置信度）")
    md.append("")
    md.append("> 相似度高 = 像本人手写 = 可能误标 → 置信度低；相似度低 = 不像本人 = 确认 AI → 置信度高")
    md.append("")
    md.append("| 提交 | 来源 | 相似度 | 置信度 |")
    md.append("|---|---|---|---|")
    for c in git_stats["commits"]:
        d = c["detect"]
        if d["is_ai"]:
            sim = f"{d['similarity']:.2f}" if d["similarity"] is not None else "-"
            md.append(f"| {c['hash'][:8]} | {d['source']} | {sim} | {d['confidence']:.2f} |")
    md.append("")
    md.append("## 二、提效同比（上线记录）")
    md.append("")
    md.append("| 指标 | 2025 | 2026 | 同比 |")
    md.append("|---|---|---|---|")
    s25, s26 = eff_stats["2025"], eff_stats["2026"]
    for key, label, is_float in [
        ("total", "上线条目", False), ("req", "需求", False),
        ("bug", "Bug", False), ("devs", "参与人数", False),
        ("per_capita", "人均条目", True),
    ]:
        v25, v26 = s25[key], s26[key]
        chg = f"{(v26 - v25) / v25 * 100:+.1f}%" if v25 else "-"
        if is_float:
            md.append(f"| {label} | {v25:.1f} | {v26:.1f} | {chg} |")
        else:
            md.append(f"| {label} | {v25} | {v26} | {chg} |")
    return "\n".join(md)


def render_html(git_stats, eff_stats):
    """生成 HTML 报告（ECharts 可视化）。对齐 AI提效统计分析 风格。"""
    s25, s26 = eff_stats["2025"], eff_stats["2026"]

    def chg(a, b):
        return f"{(b - a) / a * 100:+.1f}%" if a else "-"

    # 风格学 sim 分桶（看 AI 提交的相似度分布 → 反伪造效果）
    sims = [c["detect"]["similarity"] for c in git_stats["commits"]
            if c["detect"]["is_ai"] and c["detect"]["similarity"] is not None]
    bin_labels = ["0-0.2\n(确认AI)", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0\n(可能误标)"]
    bin_counts = [0, 0, 0, 0, 0]
    for s in sims:
        bin_counts[min(int(s / 0.2), 4)] += 1

    # 表格行
    ai_rows = "".join(
        f'<tr><td>{c["hash"][:8]}</td><td>{c["detect"]["source"]}</td>'
        f'<td>{c["detect"]["similarity"]:.2f}</td><td>{c["detect"]["confidence"]:.2f}</td></tr>'
        for c in git_stats["commits"] if c["detect"]["is_ai"])
    author_rows = "".join(
        f'<tr><td>{a["name"]}</td><td>{a["total"]}</td><td>{a["ai"]}</td>'
        f'<td>{a["ai"]/a["total"]*100:.0f}%</td></tr>'
        for a in git_stats["by_author"].values())

    ai_commits = git_stats["ai_commits"]
    non_ai = git_stats["total_commits"] - ai_commits

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 度量与提效分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
:root{{--pri:#4f46e5;--ok:#10b981;--err:#ef4444;--bg:#f8fafc;--card:#fff;--txt:#1e293b;--txt2:#64748b;--bdr:#e2e8f0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--txt);line-height:1.6}}
.hd{{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:40px;text-align:center}}
.hd h1{{font-size:28px;margin-bottom:8px}}.hd .sub{{font-size:14px;opacity:.9}}
.ct{{max-width:1100px;margin:0 auto;padding:28px 20px}}
.stl{{font-size:20px;font-weight:700;color:var(--pri);margin:30px 0 16px;padding-bottom:8px;border-bottom:2px solid var(--pri)}}
.kg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin-bottom:8px}}
.kc{{background:var(--card);border-radius:10px;padding:18px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08);border:1px solid var(--bdr)}}
.kl{{font-size:12px;color:var(--txt2);margin-bottom:4px}}.kv{{font-size:24px;font-weight:700;color:var(--pri)}}
.cb{{background:var(--card);border-radius:10px;padding:18px;margin-bottom:18px;box-shadow:0 1px 3px rgba(0,0,0,.08);border:1px solid var(--bdr)}}
.cb h3{{font-size:15px;font-weight:600;margin-bottom:12px}}
.cr{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:18px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#f1f5f9;padding:8px 12px;text-align:left;border-bottom:2px solid var(--bdr)}}
td{{padding:8px 12px;border-bottom:1px solid var(--bdr)}}
.ft{{text-align:center;padding:20px;color:var(--txt2);font-size:12px}}
@media(max-width:768px){{.cr{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="hd">
<h1>AI 度量与提效分析报告</h1>
<div class="sub">三层 AI 识别（Co-authored-by + 风格学）+ 提效同比 · 由 demos/ai-metrics 生成</div>
</div>
<div class="ct">

<div class="stl">一、核心指标</div>
<div class="kg">
<div class="kc"><div class="kl">AI 提交占比</div><div class="kv">{git_stats['commit_ratio']:.1f}%</div><div class="kl">{ai_commits}/{git_stats['total_commits']} 提交</div></div>
<div class="kc"><div class="kl">AI 代码行占比</div><div class="kv">{git_stats['line_ratio']:.1f}%</div><div class="kl">{git_stats['ai_added']}/{git_stats['total_added']} 行</div></div>
<div class="kc"><div class="kl">上线条目同比</div><div class="kv">{chg(s25['total'], s26['total'])}</div><div class="kl">{s25['total']}→{s26['total']}</div></div>
<div class="kc"><div class="kl">需求同比</div><div class="kv" style="color:var(--ok)">{chg(s25['req'], s26['req'])}</div><div class="kl">{s25['req']}→{s26['req']}</div></div>
<div class="kc"><div class="kl">Bug 同比</div><div class="kv" style="color:var(--err)">{chg(s25['bug'], s26['bug'])}</div><div class="kl">{s25['bug']}→{s26['bug']}</div></div>
</div>

<div class="stl">二、提效同比（上线记录）</div>
<div class="cb"><h3>上线 / 需求 / Bug 同比（2025 vs 2026）</h3><div id="c1" style="height:320px"></div></div>
<div class="cr">
<div class="cb"><h3>需求 vs Bug 占比（2025）</h3><div id="c2" style="height:300px"></div></div>
<div class="cb"><h3>需求 vs Bug 占比（2026）</h3><div id="c3" style="height:300px"></div></div>
</div>

<div class="stl">三、AI 代码识别（三层算法）</div>
<div class="cr">
<div class="cb"><h3>AI vs 非 AI（提交数）</h3><div id="c4" style="height:300px"></div></div>
<div class="cb"><h3>风格学反伪造：AI 提交相似度分布</h3><div id="c5" style="height:300px"></div></div>
</div>
<div class="cb"><h3>风格学反伪造样例</h3>
<table><thead><tr><th>提交</th><th>来源</th><th>相似度</th><th>置信度</th></tr></thead><tbody>{ai_rows}</tbody></table></div>
<div class="cb"><h3>作者 AI 统计</h3>
<table><thead><tr><th>作者</th><th>总提交</th><th>AI 提交</th><th>AI 占比</th></tr></thead><tbody>{author_rows}</tbody></table></div>

</div>
<div class="ft">由 demos/ai-metrics 自动生成 · 三层 AI 识别 + 提效同比 · ECharts 可视化</div>

<script>
var ch1=echarts.init(document.getElementById('c1'));
ch1.setOption({{tooltip:{{trigger:'axis'}},legend:{{data:['2025年','2026年'],top:0}},grid:{{left:40,right:20,bottom:30,top:40}},xAxis:{{type:'category',data:['上线条目','需求','Bug']}},yAxis:{{type:'value'}},series:[{{name:'2025年',type:'bar',data:[{s25['total']},{s25['req']},{s25['bug']}],itemStyle:{{color:'#94a3b8'}}}},{{name:'2026年',type:'bar',data:[{s26['total']},{s26['req']},{s26['bug']}],itemStyle:{{color:'#4f46e5'}}}}]}});
var ch2=echarts.init(document.getElementById('c2'));
ch2.setOption({{tooltip:{{trigger:'item',formatter:'{{b}}: {{c}} ({{d}}%)'}},color:['#10b981','#ef4444'],series:[{{type:'pie',radius:['40%','70%'],data:[{{name:'需求',value:{s25['req']}}},{{name:'Bug',value:{s25['bug']}}}]}}]}});
var ch3=echarts.init(document.getElementById('c3'));
ch3.setOption({{tooltip:{{trigger:'item',formatter:'{{b}}: {{c}} ({{d}}%)'}},color:['#10b981','#ef4444'],series:[{{type:'pie',radius:['40%','70%'],data:[{{name:'需求',value:{s26['req']}}},{{name:'Bug',value:{s26['bug']}}}]}}]}});
var ch4=echarts.init(document.getElementById('c4'));
ch4.setOption({{tooltip:{{trigger:'item',formatter:'{{b}}: {{c}} ({{d}}%)'}},color:['#4f46e5','#94a3b8'],series:[{{type:'pie',radius:['40%','70%'],data:[{{name:'AI 提交',value:{ai_commits}}},{{name:'非 AI',value:{non_ai}}}]}}]}});
var ch5=echarts.init(document.getElementById('c5'));
ch5.setOption({{tooltip:{{trigger:'axis'}},grid:{{left:40,right:20,bottom:60,top:30}},xAxis:{{type:'category',data:{json.dumps(bin_labels, ensure_ascii=False)},axisLabel:{{interval:0}}}},yAxis:{{type:'value',name:'提交数'}},series:[{{type:'bar',data:{json.dumps(bin_counts)},itemStyle:{{color:'#7c3aed'}},label:{{show:true,position:'top'}}}}]}});
window.addEventListener('resize',function(){{[ch1,ch2,ch3,ch4,ch5].forEach(function(c){{c.resize();}})}});
</script>
</body>
</html>'''
