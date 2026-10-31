@echo off
start "CatchBlock backend" cmd /k "cd /d %~dp0cb && python -m catchblock.cli serve"
start "CatchBlock frontend" cmd /k "cd /d %~dp0web && npm install && npm run dev"
echo Opening http://localhost:5173 in a few seconds...
timeout /t 8 >nul
start http://localhost:5173
