<!-- 图片让人直接看到 产品样子 -->
![Mainpage](assets/images/image.png)

#   xxxx project

<!-- badge 酷 -->

<p align="center">
   <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
   <a href="https://hub.docker.com/r/YOUR_DOCKER_IMAGE"><img src="https://img.shields.io/badge/Docker-Supported-blue" alt="Docker"></a>
</p>

## 目录 / Table of Contents
- xxx
- xxx

<!-- 可以加工后，放到简历，linkedin，这里是 og 版本内容 -->
## 项目概述 / Project Overview
LeanyAI 是一个基于 Next.js 和 FastAPI 的多语言 AI 平台，支持前后端分离部署，提供可扩展的工作流管理和 i18n 国际化功能。
- Solely responsible for developing complete SaaS platform: AI-powered email assistant
- Frontend architecture: React/Next.js with responsive design and cloud deployment on Vercel
- Backend implementation: RESTful API as microservice solution with LLM integration for text analysis


## 项目结构 / Directory Structure
```text
/
├── web/                      # 前端 Next.js 应用，详见 web/README.md
...
│   └── readme.md             # 前端使用说明
├── api/                      # 后端服务 (FastAPI, 包含 fastapi 和 minio 相关代码)
│   ├── main.py               # FastAPI 相关代码
...
│   └── Dockerfile.minio      # MinIO 集成与相关代码
├── docker/
│   ├── docker-compose.yml    # Docker Compose 配置
│   └── readme.md             # Docker 使用说明
└── docs/                     # 文档与设计资源
```

## 先决条件 / Prerequisites
- Node.js >= 18
- pnpm >= 7
- Docker & Docker Compose
- uv


## 安装与启动 / Getting Started
