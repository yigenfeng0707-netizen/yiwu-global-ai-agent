@echo off
REM 现场 live 自主演示启动器（需 remio 桌面端在线 + aApp 知识库就绪）
cd /d %~dp0
python scripts\autonomous_agent.py
echo.
echo 已生成 demo_autonomous_live_transcript.md（实时自主决策轨迹）
pause
