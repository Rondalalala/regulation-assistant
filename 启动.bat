@echo off
chcp 65001 >nul 2>nul
title 西北投资制度管理平台

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo  [错误] 未检测到 Node.js
    echo.
    echo  请先安装 Node.js：
    echo  1. 浏览器打开 https://nodejs.org
    echo  2. 下载 LTS 版本并安装（一路下一步即可）
    echo  3. 安装完成后重新双击此文件
    echo.
    echo  正在打开 Node.js 官网...
    start https://nodejs.org
    pause
    exit /b
)

echo.
echo  ========================================
echo    西北投资制度管理平台 v2.0
echo  ========================================
echo.
echo  启动中...
echo.

node server.mjs

pause
