# 快速开始

## lmcp init

`lmcp init` 会生成一个最小的可用的 LMCP 服务器集群, 即其中只有 Velocity 本身. 

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
│
├── servers/                   # 存放由`lmcp build`命令生成的、可随时运行的服务端实例 (init时为空)
│   └── velocity/
│       └── ...
│
└── .lmcp/                     # 由lmcp工具自动管理的隐藏目录，用户通常无需关心
    ├── podman-compose.yml     # 由 `lmcp run` 动态生成的编排文件
    ├── cache/                 # 用于缓存下载的服务端核心、Mod等
    └── logs/                  # 用于存放持久化的日志文件
```