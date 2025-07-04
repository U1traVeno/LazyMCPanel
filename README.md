# LazyMCPanel (`lmcp`)

**此项目处于假想阶段, 以下内容目前完全是一个对于项目预期效果的设想. 欢迎参与讨论和贡献!**

------

**一个声明式的、用于快速部署和管理 Minecraft 群组服的命令行工具。**

`lmcp` 旨在将手动、易错的服务端配置过程，转变为一种优雅的、可复现的、代码化的管理模式。只需要编写简单的模板文件来“定义”使用 MCDReforged 的 Minecraft 服务器，剩下的下载、配置、网络、启动和监控工作，都交给 `lmcp`。

告别手动复制、修改配置和管理复杂Java/Python环境的繁琐流程，让你的服务器管理变得“懒惰”而高效。

本项目使用**Typer**和**Textual**构建，并与 **MCDReforged** 和 **Velocity** 深度集成。

---

## ✨ 项目特性

* **声明式管理**
    * 使用简洁的YAML模板文件 (`server.yml`) 来定义一个服务器的一切：服务端核心、版本、Mod列表、MCDR插件、核心配置等。模板即文档。

* **可复现性与可移植性**
    * 任何人都可以在任何支持Docker或Podman的机器上，通过同一份模板文件，构建出完全相同的服务器环境。
    * 将你的模板文件纳入Git版本控制，轻松追踪、回滚或试验你的服务器配置。

* **环境隔离**
    * 每个Minecraft服务器都运行在独立的容器中，拥有自己专属的、互不干扰的Java环境（无论是Java 8还是Java 21）。这在处理不同版本的服务端时尤为方便.

* **自动化编排**
    * 自动处理Velocity代理和后端服务器之间的网络配置、端口映射和密钥转发。你无需再手动修改任何 `velocity.toml` 或 `server.properties` 中的网络设置(当然也可以手动修改, 如果你需要)。

* **集成化监控**
    * 图形化的监控面板，实时显示所有服务器的运行状态、日志和性能指标, 管理所有服务器而无需额外配置或安装任何东西。

---

## 🚀 功能列表 (Commands)

`lmcp` 提供了一套符合直觉的命令行工具来管理你的整个群组服生命周期

* **`lmcp`**
    * **[运行]** 启动 `lmcp.yml` 中定义的所有服务器，并自动创建监控面板。 -f 选项可以指定一个不同的配置文件路径。
    * 如果没有 `lmcp.yml` 文件，则会提示使用 `lmcp init` 命令来初始化一个新的项目。
  
* **`lmcp init`**
    * 在当前目录初始化一个新的 `lmcp` 群组服项目，创建所需的基本目录结构（`servers/`, `templates/`）和主配置文件 `lmcp.yml`.

* **`lmcp add <path_to_server> --name <server_name>`**
    * 将一个已存在的、位于任意路径的服务端文件夹“注册”到 `lmcp` 项目中进行管理，而无需移动或复制原始文件。

* **`lmcp extract <server_name>`**
    * **[反向工程]** 扫描一个已注册的服务器目录，尽最大努力从中“提取”出一个 `server.yml` 定义文件。

* **`lmcp build <template_file> --name <new_server_name>`**
    * **[构建]** 读取一个模板文件，自动下载所有依赖（服务端核心、Mods、插件），生成配置文件，并创建一个完整的、可随时运行的服务端实例。

* **`lmcp down`**
    * 安全地关闭并移除所有由 `lmcp` 启动的容器。

* **`lmcp status`**
    * 查看当前群组服中所有服务的运行状态。

* **`lmcp logs <server_name>`**
    * 单独查看某一个特定服务的日志。

---

## 🛠️ 安装 (Installation)

**先决条件:**
* Podman/Docker
* podman-compose/docker-compose
* Python 3.12+

```bash
# 本项目未来将发布到PyPI
pip install lazymc-panel
```

## 快速开始 (Quick Start)

[Quick-Start](docs/quick-start.md)