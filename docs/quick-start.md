# 快速开始

## lmcp init

假设你需要在 `my-lmcp-cluster/` 文件夹初始化lmcp:

```bash
lmcp init
```

它会生成这样的目录结构:
```
my-minecraft-cluster/         # 用户自己创建的项目根目录
├── lmcp.yml                   # 【核心】群组服的主配置文件，定义了包含哪些服务器
│
├── templates/                 # 存放用户编写或由lmcp extract生成的“服务端定义文件” (init时为空)
│   ├── survival_1.12.2.yml
│   └── creative_1.20.4.yml
│
├── servers/                   # 存放由`lmcp build`命令生成的、可随时运行的服务端实例 (init时为空)
│   ├── survival/              # 这是生存服的完整文件夹，包含世界、mods、配置等, survival是你定义的服务端名称
│   │   ├── world/             # <--- 这是“状态”，由游戏生成
│   │   ├── mods/              # <--- 这是“配置”，由模板构建
│   │   ├── server.properties  # <--- 这是“配置”，由模板构建
│   │   └── ...
│   └── creative/
│       └── ...
│
├── backups/                   # 默认备份输出目录
│
└── .lmcp/                     # 由lmcp工具自动管理的隐藏目录，用户通常无需关心
    ├── podman-compose.yml     # 由 `lmcp run` 动态生成的编排文件
    ├── cache/                 # (可选) 用于缓存下载的服务端核心、Mod等
    └── logs/                  # (可选) 用于存放持久化的日志文件
```