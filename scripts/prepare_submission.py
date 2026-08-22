"""
Prepare the competition submission package.

Copies all required artifacts (videos, docs, transcripts, aApp info) into a
single `submission/` folder and writes `submission/提交清单.md` mapping each
file to the official requirement. Zip `submission/` and upload to 51tokenlink.com.

Usage:
    python scripts/prepare_submission.py
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'submission')

# (src_rel, dest_rel, requirement mapped to)
ITEMS = [
    ('README.md', 'README.md', '项目总览 + aApp/知识库说明'),
    ('demo_video_autonomous.mp4', 'demo/demo_video_autonomous.mp4', '主 Demo：端到端自主闭环（最强差异点）'),
    ('demo_video_narrated.mp4', 'demo/demo_video_narrated.mp4', '演示视频：精修配音版（价格卡+钢琴BGM）'),
    ('demo_video_short.mp4', 'demo/demo_video_short.mp4', '演示视频：54 秒社媒版'),
    ('demo_video_hook.mp4', 'demo/demo_video_hook.mp4', '演示视频：路演开场钩子'),
    ('docs/商业计划书.md', 'docs/商业计划书.md', '说明文档：商业闭环/TAM/反幻觉信任状'),
    ('docs/路演一页纸.md', 'docs/路演一页纸.md', '说明文档：评委对齐一页纸'),
    ('docs/出海诊断报告样例_无线耳机.md', 'docs/出海诊断报告样例_无线耳机.md', '真实数据信任状示例（无线耳机）'),
    ('docs/出海诊断报告_宠物用品.md', 'docs/出海诊断报告_宠物用品.md', '自动报告示例（宠物用品，证明可复制）'),
    ('docs/自评与改进.md', 'docs/自评与改进.md', '说明文档：自评 8.8/10'),
    ('docs/金义新区落地方案.md', 'docs/金义新区落地方案.md', '落地承诺：金义新区落地方案（冲产业落地奖核心）'),
    ('docs/致金义新区投促局的对接函.md', 'docs/致金义新区投促局的对接函.md', '提交材料：落地对接函'),
    ('docs/商户合作意向书_LOI模板.md', 'docs/商户合作意向书_LOI模板.md', '提交材料：商户 LOI 模板（冲产业落地奖）'),
    ('docs/商户内测邀请（一页纸）.md', 'docs/商户内测邀请（一页纸）.md', '落地转化：商户内测邀请'),
    ('docs/金漪湖OPC赛道合规说明.md', 'docs/金漪湖OPC赛道合规说明.md', '官方工具 remio 合规说明（硬性要求佐证）'),
    ('docs/架构设计.md', 'docs/架构设计.md', '技术架构设计（技术性佐证）'),
    ('docs/30秒路演hook.md', 'docs/30秒路演hook.md', '答辩：30 秒开场钩子口播稿'),
    ('docs/比赛提交清单与流程.md', 'docs/比赛提交清单与流程.md', '提交材料：赛道/流程/清单'),
    ('docs/答辩落地证据包.md', 'docs/答辩落地证据包.md', '答辩：证据顺序+话术'),
    ('docs/路演PPT备注稿.md', 'docs/路演PPT备注稿.md', '答辩：PPT 备注稿'),
    ('docs/致决赛评委的邀约与致谢函.md', 'docs/致决赛评委的邀约与致谢函.md', '答辩：致评委函'),
    ('demo_api_transcript.md', 'demo/demo_api_transcript.md', '真实抓取实录（非合成数据佐证）'),
    ('demo_autonomous_live_transcript.md', 'demo/demo_autonomous_live_transcript.md', '实时自主编排实录（5 步决策卡）'),
]

APP_INFO = """义乌小商品出海智能体-OPC · 参赛提交说明
================================================
赛道：金漪湖·论剑 2026 智能体 OPC 创新创业大赛 —— 「OPC 智能体」赛道
官方工具：remio 睿妙（知识库 + aApp 智能体应用）

aApp 名称：yiwu-opc-assistant（v3，已发布）
aApp 端点：/ask、/competitor-research、/select-product、/compliance-check、/policy-replicate、/welcome
知识库：remio 知识库（小商品出海 / 1039 / RCEP / 金义落地 等笔记 + 3 个 Agent）
真实自主编排器：scripts/autonomous_agent.py（LLM 规划 + 规则兜底，实时跑通）

提交方式：将本 submission/ 文件夹整体压缩后，于
https://51tokenlink.com/ 「注册参赛」→ 个人中心「参赛项目」上传。
主 Demo 建议选 demo/demo_video_autonomous.mp4。
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    total = 0
    for src, dest, desc in ITEMS:
        sp = os.path.join(ROOT, src)
        dp = os.path.join(OUT, dest)
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        if os.path.exists(sp):
            shutil.copy2(sp, dp)
            size = os.path.getsize(dp)
            total += size
            rows.append((src, desc, '%.1f MB' % (size / 1e6)))
            print('OK  ', src)
        else:
            rows.append((src, desc, '缺失'))
            print('MISS', src)

    with open(os.path.join(OUT, 'APP_INFO.txt'), 'w', encoding='utf-8') as f:
        f.write(APP_INFO)

    with open(os.path.join(OUT, '提交清单.md'), 'w', encoding='utf-8') as f:
        f.write('# 参赛提交清单（自动生成）\n\n')
        f.write('赛道：**OPC 智能体**（官方工具 remio 睿妙）\n\n')
        f.write('| 文件 | 对应要求 | 大小 |\n|---|---|---|\n')
        for src, desc, size in rows:
            f.write('| `%s` | %s | %s |\n' % (src, desc, size))
        f.write('\n总计约 %.1f MB。将本文件夹压缩为 submission.zip 后上传至 51tokenlink.com。\n' % (total / 1e6))

    print('\nWROTE', OUT, '(%.1f MB)' % (total / 1e6))
    print('Manifest: submission/提交清单.md')


if __name__ == '__main__':
    main()
