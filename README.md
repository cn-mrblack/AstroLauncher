[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Downloads][downloads-shield]][downloads-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<br />
<p align="center">
  <img src="https://raw.githubusercontent.com/JoeJoeTV/AstroLauncher/master/assets/astrolauncherlogo.ico" width="128px">
  <h3 align="center">AstroLauncher - 专用服务器启动器</h3>
  <p align="center">
    一个用于Astroneer专用服务器的一体化服务器管理工具。
  </p>
  <p align="center">
    <b>这是一个修复了一些问题的分支，因为<a href="https://github.com/ricky-davis/AstroLauncher">原始仓库</a>已被归档</b>
  </p>

  <p align="center">
    <a href="https://github.com/JoeJoeTV/AstroLauncher/issues">AstroLauncher 错误报告</a>
    ·
    <a href="https://github.com/JoeJoeTV/AstroLauncher/issues">功能请求</a>
  </p>
</p>
<img src = "https://user-images.githubusercontent.com/48695279/88715011-3bf09e80-d0e3-11ea-9c3e-f14e6c1758fe.png">
<img src = "https://user-images.githubusercontent.com/48695279/88715683-896d0b80-d0e3-11ea-9a1e-e57e46430c6a.png">
<!-- 目录 -->

## 目录

- [目录](#目录)
- [概述](#概述)
- [它能做什么？](#它能做什么)
- [INI文件选项](#ini文件选项)
- [快速开始](#快速开始)
  - [先决条件](#先决条件)
  - [安装](#安装)
- [使用方法](#使用方法)
  - [构建EXE文件](#构建exe文件)
- [贡献](#贡献)
- [许可证](#许可证)
- [联系方式](#联系方式)

## 概述

如果你正在为Astroneer托管自己的专用服务器，这个工具非常适合你。它有许多功能可以让托管变得更加容易，比如自动重启、高级日志记录和Web界面。

## 它能做什么？

1. 自动初始下载并将服务器更新到最新版本！
2. 验证你的网络设置，检查端口转发/NAT回环
3. 自动设置基础配置文件
4. 修复服务器列表中的双重服务器问题
5. 启动并自动重启服务器
6. 显示用户加入/离开服务器的时间
7. 在日志文件夹中记录所有内容
8. 能够将所有日志发送到Discord webhook！
9. 每X小时自动重启
10. 保留X小时的备份
11. 带登录功能的Web界面，用于监控服务器数据、强制保存和重启，以及管理用户（踢人、 banning、白名单、管理员）

## INI文件选项

以下是INI文件选项的描述和默认值。不要将此复制/粘贴到INI文件中，让INI文件自动生成。每个选项都必须存在并设置，并且不能有注释或额外选项。

```python
# 启用/禁用启动器的自动更新
AutoUpdateLauncherSoftware = True

# 启用/禁用服务器的自动更新。
AutoUpdateServerSoftware = True

# 允许启动器和服务器在每次服务器重启时自动更新
UpdateOnServerRestart = True

# 禁用服务器控制台弹出窗口。
HideServerConsoleWindow = False

# 禁用启动器控制台弹出窗口。
HideLauncherConsoleWindow = False



# 指定启动器检查玩家加入/离开的频率
ServerStatusFrequency = 2

# 指定启动器检查服务器注册状态的频率
PlayfabAPIFrequency = 2

# 在重启服务器之前允许Playfab失败的次数
HeartBeatFailRestartServer = 8



# 禁用备份保留
DisableBackupRetention = False

# 启动器应保留多少小时的保存
BackupRetentionPeriodHours= 72

# 保存文件的备份位置
BackupRetentionFolderLocation = Astro\Saved\Backup\LauncherBackups



# 启用自动重启
EnableAutoRestart = False

# 要同步的时间戳。00:00或"midnight"表示午夜。使用"False"禁用，不带引号。
# 示例：如果设置为03:35，AutoRestartEveryHours设置为6，它将每天在03:35, 09:35, 15:35和21:35重启
AutoRestartSyncTimestamp = 00:00

# 在上述第一次重启后，您希望多久重启一次？
AutoRestartEveryHours = 24



# 禁用启动时的端口转发/NAT回环检查
DisableNetworkCheck = False

# 始终覆盖AstroServerSettings.ini中的PublicIP设置
OverwritePublicIP = True

# 启用/禁用在控制台中显示服务器FPS。当玩家在您的服务器中时，这可能会刷屏您的控制台
ShowServerFPSInConsole = True

# 以管理员模式启动时，Astro Launcher将尝试自动配置防火墙设置
AdminAutoConfigureFirewall = True

# 在删除服务器日志之前保留多长时间。这不控制调试日志。
LogRetentionDays = 7



# Discord Webhook URL，用于在Discord频道中显示AstroLauncher控制台数据
DiscordWebHookURL: str = ""

# Discord Webhook日志级别，all / cmd / chat
DiscordWebHookLevel: str = "cmd"

# 这是Web服务器用于与webhook交互的URL。
RODataURL: str = secrets.token_hex(16)



# 禁用Web管理服务器
DisableWebServer = False

# 设置您希望Web管理服务器运行的端口
WebServerPort = 5000

# 为webserver中的管理面板自动生成的SHA256密码哈希
WebServerPasswordHash =

# Web服务器托管的基础URL。'/astroneer'将是https://example.com/astroneer/。必须以/开头并以/结尾
WebServerBaseURL = /

# 为webserver启用HTTPS。如果未指定/指定错误的Cert/Key文件，默认为False
EnableWebServerSSL = False

# 如果SSL工作，您想要使用的端口
SSLPort = 443

# Cert和Key文件的路径
SSLCertFile =
SSLKeyFile =



# CPU亲和力 - 指定要运行的逻辑核心。如果为空则自动选择。
# 示例：
#  CPUAffinity=0,1,3,5,9
CPUAffinity =

```

<!-- 快速开始 -->

## 快速开始

**推荐：大多数人会想要直接运行.exe文件，请查看[最新发布](https://github.com/JoeJoeTV/AstroLauncher/releases/latest)下载可执行文件。**


<br/>
要获取本地"从源代码"副本并运行，请遵循以下简单步骤：
<br/>
<br/>

### 先决条件

- Python 3.7
- pip / pipenv

### 安装

1. 克隆AstroLauncher仓库

```sh
git clone https://github.com/JoeJoeTV/AstroLauncher.git
```

2. 使用pip或pipenv安装Python模块

```sh
pip install -r requirements.txt
```

```sh
pipenv install
```

<br />

## 使用方法

使用以下命令运行服务器启动器

```sh
pipenv run python AstroLauncher.py
```

<br /><br />
如果未与服务器文件放在同一目录中，您可以像这样指定服务器文件夹位置

```sh
python AstroLauncher.py --path "steamapps\common\ASTRONEER Dedicated Server"
```

```sh
pipenv run python AstroLauncher.py -p "steamapps\common\ASTRONEER Dedicated Server"
```

<br />

### 构建EXE文件

1. 如果要将此项目转换为可执行文件，请确保使用以下方法之一安装pyinstaller

```sh
pip install pyinstaller
```

```sh
pipenv install -d
```

2. 使用all-in-one标志运行pyinstaller

```sh
pyinstaller AstroLauncher.py -F --add-data "assets;./assets" --icon=assets/astrolauncherlogo.ico
```

或者直接运行BuildEXE.py，它会自动清理

```sh
python BuildEXE.py
```

1. 将可执行文件（在新的`dist`文件夹中）移动到您选择的目录。（如果需要，您现在可以删除`dist`和`build`文件夹，以及`.spec`文件）
2. 运行AstroLauncher.exe

```sh
AstroLauncher.exe -p "steamapps\common\ASTRONEER Dedicated Server"
```

<!-- 贡献 -->

## 贡献

贡献是使开源社区成为学习、启发和创造的绝佳场所的原因。您的任何贡献都**非常感谢**。

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

<!-- 许可证 -->

## 许可证

根据MIT许可证分发。有关更多信息，请参阅`LICENSE`。

<!-- 联系方式 -->

## 联系方式

如果您有任何问题，您可以加入[Astroneer discord] (discord.gg/Astroneer)并在#self_host_talk频道中提问

项目链接：[https://github.com/JoeJoeTV/AstroLauncher](https://github.com/JoeJoeTV/AstroLauncher)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[astroneer discord]: https://discord.com/invite/astroneer
[contributors-shield]: https://img.shields.io/github/contributors/JoeJoeTV/AstroLauncher.svg?style=flat-square
[contributors-url]: https://github.com/JoeJoeTV/AstroLauncher/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/JoeJoeTV/AstroLauncher.svg?style=flat-square
[forks-url]: https://github.com/JoeJoeTV/AstroLauncher/network/members
[downloads-shield]: https://img.shields.io/github/downloads/JoeJoeTV/AstroLauncher/total
[downloads-url]: https://github.com/JoeJoeTV/AstroLauncher/releases/latest
[stars-shield]: https://img.shields.io/github/stars/JoeJoeTV/AstroLauncher.svg?style=flat-square
[stars-url]: https://github.com/JoeJoeTV/AstroLauncher/stargazers
[issues-shield]: https://img.shields.io/github/issues/JoeJoeTV/AstroLauncher.svg?style=flat-square
[issues-url]: https://github.com/JoeJoeTV/AstroLauncher/issues
[license-shield]: https://img.shields.io/github/license/JoeJoeTV/AstroLauncher.svg?style=flat-square
[license-url]: https://github.com/JoeJoeTV/AstroLauncher/blob/master/LICENSE.txt