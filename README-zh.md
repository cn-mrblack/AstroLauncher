[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Downloads][downloads-shield]][downloads-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<br />
<p align="center">
  <img src="https://raw.githubusercontent.com/JoeJoeTV/AstroLauncher/master/assets/astrolauncherlogo.ico" width="128px">
  <h3 align="center">AstroLauncher - Dedicated Server Launcher</h3>
  <h3 align="center">AstroLauncher - 专用服务器启动器</h3>
  <p align="center">
    An all-in-one server management tool for Astroneer Dedicated Servers.
    <br />
    一个用于Astroneer专用服务器的一体化服务器管理工具。
  </p>
  <p align="center">
    <b>This is a fork to fix some issues, since the <a href="https://github.com/ricky-davis/AstroLauncher">original repository</a> has been archived</b>
    <br />
    <b>这是一个修复了一些问题的分支，因为<a href="https://github.com/ricky-davis/AstroLauncher">原始仓库</a>已被归档</b>
  </p>

  <p align="center">
    <a href="https://github.com/JoeJoeTV/AstroLauncher/issues">AstroLauncher Bugs</a>
    ·
    <a href="https://github.com/JoeJoeTV/AstroLauncher/issues">Request Feature</a>
    <br />
    <a href="https://github.com/JoeJoeTV/AstroLauncher/issues">AstroLauncher 错误报告</a>
    ·
    <a href="https://github.com/JoeJoeTV/AstroLauncher/issues">功能请求</a>
  </p>
</p>
<img src = "https://user-images.githubusercontent.com/48695279/88715011-3bf09e80-d0e3-11ea-9c3e-f14e6c1758fe.png">
<img src = "https://user-images.githubusercontent.com/48695279/88715683-896d0b80-d0e3-11ea-9a1e-e57e46430c6a.png">
<!-- TABLE OF CONTENTS -->

## Table of Contents
## 目录

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [What does it do?](#what-does-it-do)
- [INI File options](#ini-file-options)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Building an EXE](#building-an-exe)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

- [目录](#table-of-contents)
- [概述](#overview)
- [它能做什么？](#what-does-it-do)
- [INI文件选项](#ini-file-options)
- [快速开始](#getting-started)
  - [先决条件](#prerequisites)
  - [安装](#installation)
- [使用方法](#usage)
  - [构建EXE文件](#building-an-exe)
- [贡献](#contributing)
- [许可证](#license)
- [联系方式](#contact)

## Overview
## 概述

This tool is perfect for you if you are hosting your own dedicated server for Astroneer. It has many features to make hosting a lot easier like automatic restarts, advanced logging, and a webinterface.

如果你正在为Astroneer托管自己的专用服务器，这个工具非常适合你。它有许多功能可以让托管变得更加容易，比如自动重启、高级日志记录和Web界面。

## What does it do?
## 它能做什么？

1. Automatic initial download and updating of your server to the latest version!
2. Verifies your network settings to check for Port Forwarding/NAT Loopback
3. Automatically sets up the base Config files
4. Fixes the double server problem in the server list
5. Starts, and automatically restarts the server
6. Displays when users join/leave the server
7. Keeps a log of everything in the logs folder
8. Ability to send all logs to a Discord webhook!
9. Auto Restart every X hours
10. Backup Retention for X hours
11. Web Interface w/ login to monitor server data, force saves and restarts, and manage users (kick, ban, whitelist, admin)

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

## INI File options
## INI文件选项

Below are the descriptions and defaults for the INI file options. Do not copy/paste this into the INI file, allow the INI file to be automatically generated. Every option must be present and set, and there must be no comments or extra options.

以下是INI文件选项的描述和默认值。不要将此复制/粘贴到INI文件中，让INI文件自动生成。每个选项都必须存在并设置，并且不能有注释或额外选项。

```python
# Enables/Disables Auto Update for the Launcher
AutoUpdateLauncherSoftware = True

# Enables/Disables Auto Update for the Server.
AutoUpdateServerSoftware = True

# Allows the launcher and server to auto update every time the server restarts
UpdateOnServerRestart = True

# Disable the server console popup window.
HideServerConsoleWindow = False

# Disable the Launcher console popup window.
HideLauncherConsoleWindow = False



# Specifies how often the launcher will check for players joining/leaving
ServerStatusFrequency = 2

# Specifies how often the launcher will check for server registration status
PlayfabAPIFrequency = 2

# How many times to allow Playfab to fail before restarting the server
HeartBeatFailRestartServer = 8



# Disable Backup Retention
DisableBackupRetention = False

# How many hours of saves should the launcher retain
BackupRetentionPeriodHours= 72

# Location to backup the save files to
BackupRetentionFolderLocation = Astro\Saved\Backup\LauncherBackups



# Enable auto restart
EnableAutoRestart = False

# Timestamp you want to synchronize with. 00:00 or "midnight" work for midnight. Disable with "False". No quotes.
# Example: If set to 03:35, with AutoRestartEveryHours set to 6, it will restart at 03:35, 09:35, 15:35, and 21:35 every day
AutoRestartSyncTimestamp = 00:00

# After the first restart specified above, how often do you want to restart?
AutoRestartEveryHours = 24



# Disable the Port Forward / NAT Loopback check on startup
DisableNetworkCheck = False

# Always Overwrite the PublicIP setting in AstroServerSettings.ini
OverwritePublicIP = True

# Enable/Disable showing server FPS in console. This will probably spam your console when playing are in your server
ShowServerFPSInConsole = True

# When launched in Administrator Mode, Astro Launcher will attempt to automatically configure the firewall settings
AdminAutoConfigureFirewall = True

# How long to keep server logs before removing them. This does not control debug logs.
LogRetentionDays = 7



# Discord Webhook URL to display AstroLauncher console data in a discord channel
DiscordWebHookURL: str = ""

# Discord Webhook Log Level, all / cmd / chat
DiscordWebHookLevel: str = "cmd"

# This is the URL the webserver serves to interact with the webhook.
RODataURL: str = secrets.token_hex(16)



# Disable the Web Management Server
DisableWebServer = False

# Set the port you want the Web Management Server to run on
WebServerPort = 5000

# Automatically generated SHA256 password hash for the admin panel in the webserver
WebServerPasswordHash =

# The Base URL that the Web Server hosts at. '/astroneer' would be https://example.com/astroneer/ . Must start with and end with a /
WebServerBaseURL = /

# Enable HTTPS for the webserver. If no/wrong Cert/Key files are specified, defaults to False
EnableWebServerSSL = False

# Port you want to use if SSL works
SSLPort = 443

# Paths to Cert and Key files
SSLCertFile =
SSLKeyFile =



# CPU Affinity - Specify logical cores to run on. Automatically chooses if empty.
# ex:
#  CPUAffinity=0,1,3,5,9
CPUAffinity =

```

<!-- GETTING STARTED -->

## Getting Started
## 快速开始

**Recommended: Most people will want to just run the .exe, check out the [Latest Release](https://github.com/JoeJoeTV/AstroLauncher/releases/latest) for a download of the executable.**

**推荐：大多数人会想要直接运行.exe文件，请查看[最新发布](https://github.com/JoeJoeTV/AstroLauncher/releases/latest)下载可执行文件。**


<br/>
To get a local "from-source" copy up and running follow these simple steps:
<br/>
<br/>

要获取本地"从源代码"副本并运行，请遵循以下简单步骤：
<br/>
<br/>

### Prerequisites
### 先决条件

- Python 3.7
- pip / pipenv

- Python 3.7
- pip / pipenv

### Installation
### 安装

1. Clone the AstroLauncher repository

```sh
git clone https://github.com/JoeJoeTV/AstroLauncher.git
```

2. Install python modules using pip or pipenv

```sh
pip install -r requirements.txt
```

```sh
pipenv install
```

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

## Usage
## 使用方法

Run the server launcher using the following command

```sh
pipenv run python AstroLauncher.py
```

<br /><br />
If not placed in the same directory as the server files, you can specify a server folder location like so

```sh
python AstroLauncher.py --path "steamapps\common\ASTRONEER Dedicated Server"
```

```sh
pipenv run python AstroLauncher.py -p "steamapps\common\ASTRONEER Dedicated Server"
```

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

### Building an EXE
### 构建EXE文件

1. If you want to turn this project into an executable, make sure to install pyinstaller using one of the following methods

```sh
pip install pyinstaller
```

```sh
pipenv install -d
```

2. Run pyinstaller with the all-in-one flag

```sh
pyinstaller AstroLauncher.py -F --add-data "assets;./assets" --icon=assets/astrolauncherlogo.ico
```

or just run the BuildEXE.py which automatically cleans up afterwards

```sh
python BuildEXE.py
```

1. Move the executable (in the new `dist` folder) to the directory of your choice. (If you want you can now delete the `dist` and `build` folders, as well as the `.spec` file)
2. Run AstroLauncher.exe

```sh
AstroLauncher.exe -p "steamapps\common\ASTRONEER Dedicated Server"
```

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

<!-- CONTRIBUTING -->

## Contributing
## 贡献

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

贡献是使开源社区成为学习、启发和创造的绝佳场所的原因。您的任何贡献都**非常感谢**。

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

<!-- LICENSE -->

## License
## 许可证

Distributed under the MIT License. See `LICENSE` for more information.

根据MIT许可证分发。有关更多信息，请参阅`LICENSE`。

<!-- CONTACT -->

## Contact
## 联系方式

If you have any questions you can join the [Astroneer discord] (discord.gg/Astroneer) and ask in the #self_host_talk channel

Project Link: [https://github.com/JoeJoeTV/AstroLauncher](https://github.com/JoeJoeTV/AstroLauncher)

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