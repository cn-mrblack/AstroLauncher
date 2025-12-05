import argparse
import asyncio
import atexit
import ctypes
import dataclasses
from fileinput import filename
import json
import ntpath
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import zipfile
from distutils import dir_util
from threading import Thread

import psutil
from packaging import version
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import cogs.AstroAPI as AstroAPI
import cogs.AstroWebServer as AstroWebServer
import cogs.ValidateSettings as ValidateSettings
from cogs.AstroDaemon import AstroDaemon
from cogs.AstroDedicatedServer import AstroDedicatedServer
from cogs.AstroLogging import AstroLogging
from cogs.MultiConfig import MultiConfig
from cogs.utils import AstroRequests

from cogs.utils import ALVERSION


"""
Build:
pyinstaller AstroLauncher.py -F --add-data "assets;./assets" --icon=assets/astrolauncherlogo.ico
or
python BuildEXE.py
"""


class AstroLauncher:
    """Starts a new instance of the Server Launcher"""

    @dataclasses.dataclass
    class LauncherConfig:
        AutoUpdateLauncherSoftware: bool = True
        AutoUpdateServerSoftware: bool = True
        UpdateOnServerRestart: bool = True
        HideServerConsoleWindow: bool = False
        HideLauncherConsoleWindow: bool = False
        ServerStatusFrequency: float = 2
        PlayfabAPIFrequency: float = 2
        HeartBeatFailRestartServer: int = 8
        DisableBackupRetention: bool = False
        BackupRetentionPeriodHours: float = 72
        BackupRetentionFolderLocation: str = r"Astro\Saved\Backup\LauncherBackups"
        EnableAutoRestart: bool = False
        AutoRestartEveryHours: float = 24
        AutoRestartSyncTimestamp: str = "00:00"
        DisableNetworkCheck: bool = False
        OverwritePublicIP: bool = True
        ShowServerFPSInConsole: bool = True
        AdminAutoConfigureFirewall: bool = True
        LogRetentionDays: int = 7
        DiscordWebHookURL: str = ""
        DiscordWebHookLevel: str = "cmd"
        RODataURL: str = secrets.token_hex(16)

        DisableWebServer: bool = False
        WebServerPort: int = 5000
        WebServerPasswordHash: str = ""
        WebServerBaseURL: str = "/"

        EnableWebServerSSL: bool = False
        SSLPort: int = 443
        SSLCertFile: str = ""
        SSLKeyFile: str = ""

        CPUAffinity: str = ""

        def __post_init__(self):
            # pylint: disable=no-member
            hasError = False
            for field, data in self.__dataclass_fields__.items():
                try:
                    self.__dict__[field] = data.type(self.__dict__[field])
                except ValueError:
                    hasError = True
                    AstroLogging.logPrint(
                        f"INI错误: {field}必须是{data.type.__name__}类型", "critical"
                    )
            if hasError:
                AstroLogging.logPrint("修复您的启动器配置文件!", "critical")
                sys.exit()

    class SaveHandler(FileSystemEventHandler):
        def __init__(self, launcher):
            self.launcher = launcher
            self.astroPath = self.launcher.astroPath
            self.moveToPath = self.launcher.launcherConfig.BackupRetentionFolderLocation
            super().__init__()

        def on_created(self, event):
            # print(event)
            # time.sleep(1)
            try:
                # time.sleep(0.5)
                # dirName = ntpath.dirname(event.src_path)
                # fileNames = [ntpath.join(dirName, f) for f in os.listdir(
                #     dirName) if ntpath.isfile(ntpath.join(dirName, f))]
                # # print(fileNames)
                # fileName = sorted(
                #     fileNames, key=ntpath.getmtime, reverse=True)[0]
                fileName = ntpath.basename(event.src_path)
                AstroLogging.logPrint(
                    f"服务器已保存. {ntpath.basename(fileName)}", dwet="s"
                )
                AstroLogging.logPrint(f"{event.src_path}", msgType="debug")
            except:
                pass
            # self.launcher.saveObserver.stop()

        def on_deleted(self, event):
            fileName = ntpath.basename(event.src_path)
            AstroLogging.logPrint(
                f"服务器已删除保存. {ntpath.basename(fileName)}", dwet="s"
            )
            AstroLogging.logPrint(f"{event.src_path}", msgType="debug")

    class BackupHandler(FileSystemEventHandler):
        def __init__(self, launcher):
            self.launcher = launcher
            self.astroPath = self.launcher.astroPath
            self.moveToPath = self.launcher.launcherConfig.BackupRetentionFolderLocation
            self.retentionPeriodHours = (
                self.launcher.launcherConfig.BackupRetentionPeriodHours
            )
            self.pendingFiles = []
            super().__init__()

        def handle_files(self):
            # print(f"first: {self.pendingFiles}")
            time.sleep(2)
            # print(f"second: {self.pendingFiles}")
            # AstroLogging.logPrint("DEBUG: INSIDE THREAD")

            path = ntpath.join(self.astroPath, self.moveToPath)
            try:
                if not ntpath.exists(path):
                    os.makedirs(path)
            except Exception as e:
                AstroLogging.logPrint(e, "error")
            now = time.time()
            try:
                for f in os.listdir(path):
                    fpath = ntpath.join(path, f)
                    if os.stat(fpath).st_mtime < (
                        now - (self.retentionPeriodHours * 60 * 60)
                    ):
                        os.remove(fpath)
            except Exception as e:
                AstroLogging.logPrint(e, "error")

            AstroLogging.logPrint("正在将备份复制到保留文件夹.", dwet="b")
            # time.sleep(1)
            try:

                dirName = ntpath.dirname(self.pendingFiles[0])
                fileNames = [
                    ntpath.join(dirName, f)
                    for f in os.listdir(dirName)
                    if ntpath.isfile(ntpath.join(dirName, f))
                ]
                for cFile in fileNames:
                    # AstroLogging.logPrint(newFile, "debug")
                    # print(cFile)
                    shutil.copy2(cFile, path)
                    # AstroLogging.logPrint(copiedFile, "debug")
            except FileNotFoundError as e:
                AstroLogging.logPrint(e, "error")
            except Exception as e:
                AstroLogging.logPrint(e, "error")

            self.launcher.backupObserver.stop()
            self.launcher.backup_retention()

        def on_deleted(self, event):
            # AstroLogging.logPrint(event)
            # AstroLogging.logPrint("File in save directory changed")

            # AstroLogging.logPrint("DEBUG: File modified.. Starting thread")

            try:
                self.pendingFiles.append(event.src_path)
                if len(self.pendingFiles) == 1:
                    t = Thread(target=self.handle_files, args=())
                    t.daemon = True
                    t.start()
            except:
                pass

    def __init__(self, astroPath, launcherINI="Launcher.ini", disable_auto_update=None):
        try:
            AstroLogging.setup_logging()
            self.launcherINI = launcherINI
            self.launcherConfig = self.LauncherConfig()
            self.launcherPath = os.getcwd()
            self.refresh_launcher_config()

            # check if path specified
            if astroPath is not None:
                if ntpath.exists(ntpath.join(astroPath, "AstroServer.exe")):
                    self.astroPath = astroPath
                else:
                    AstroLogging.logPrint(
                        "指定的路径不包含服务器可执行文件! (AstroServer.exe)",
                        "critical",
                    )
                    time.sleep(5)
                    return

            # check if executable in current directory
            elif ntpath.exists(ntpath.join(os.getcwd(), "AstroServer.exe")):
                self.astroPath = os.getcwd()

            else:
                AstroLogging.logPrint(
                    "无法在任何地方找到服务器可执行文件! (AstroServer.exe)", "warning"
                )

                # finally, try to install the server
                try:
                    if astroPath is None:
                        self.astroPath = os.getcwd()
                        self.check_for_server_update()
                except Exception as e:
                    AstroLogging.logPrint(e, "critical")
                    return

            # AstroRequests.checkProxies()

            AstroLogging.discordWebhookURL = self.launcherConfig.DiscordWebHookURL
            dwhl = self.launcherConfig.DiscordWebHookLevel.lower()
            dwhl = dwhl if dwhl in ("all", "cmd", "chat") else "cmd"
            AstroLogging.discordWebhookLevel = dwhl
            self.start_WebHookLoop()
            AstroLogging.setup_loggingPath(
                astroPath=self.astroPath,
                logRetention=int(self.launcherConfig.LogRetentionDays),
            )
            if disable_auto_update is not None:
                self.launcherConfig.AutoUpdateLauncherSoftware = not disable_auto_update
            self.version = ALVERSION
            colsize = os.get_terminal_size().columns
            if colsize >= 77:
                vText = "Version " + self.version[1:]
                # pylint: disable=anomalous-backslash-in-string
                print(
                    " __________________________________________________________________________\n"
                    + "|     _        _               _                           _               |\n"
                    + "|    /_\\   ___| |_  _ _  ___  | |    __ _  _  _  _ _   __ | |_   ___  _ _  |\n"
                    + "|   / _ \\ (_-<|  _|| '_|/ _ \\ | |__ / _` || || || ' \\ / _|| ' \\ / -_)| '_| |\n"
                    + "|  /_/ \\_\\/__/ \\__||_|  \\___/ |____|\\__,_| \\_,_||_||_|\\__||_||_|\\___||_|   |\n"
                    + "|                                                                          |\n"
                    + "|"
                    + vText.center(74)
                    + "|\n"
                    + "|__________________________________________________________________________|"
                )

            AstroLogging.logPrint(
                f"AstroLauncher - 非官方专用服务器启动器 {self.version}"
            )
            AstroLogging.logPrint("如果您遇到任何错误，请在以下地址打开新问题:")
            AstroLogging.logPrint("https://github.com/JoeJoeTV/AstroLauncher/issues")
            AstroLogging.logPrint("要安全停止启动器和服务器，请按CTRL+C")

            self.latestURL = "https://github.com/JoeJoeTV/AstroLauncher/releases/latest"
            bName = ntpath.basename(sys.executable)
            if sys.argv[0] == ntpath.splitext(bName)[0]:
                self.isExecutable = True
            else:
                self.isExecutable = ntpath.samefile(sys.executable, sys.argv[0])
            self.cur_server_version = "0.0"
            self.headers = AstroAPI.base_headers
            self.DaemonProcess = None
            self.saveObserver = None
            self.backupObserver = None
            self.hasUpdate = False
            self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            self.affinity = self.launcherConfig.CPUAffinity
            try:
                if self.affinity != "":
                    affinityList = [int(x.strip()) for x in self.affinity.split(",")]
                    p = psutil.Process()
                    p.cpu_affinity(affinityList)
            except ValueError as e:
                AstroLogging.logPrint(f"CPU亲和力错误: {e}", "critical")
                AstroLogging.logPrint("请在您的启动器配置中更正此问题", "critical")
                return

            self.check_for_server_update()

            self.DedicatedServer = AstroDedicatedServer(self.astroPath, self)

            self.check_for_launcher_update()

            AstroLogging.logPrint("正在开始新会话")

            self.validate_playfab_certs()
            self.check_ports_free()

            if self.launcherConfig.AdminAutoConfigureFirewall:
                self.configure_firewall()

            if not self.launcherConfig.DisableNetworkCheck:
                AstroLogging.logPrint("正在检查网络配置..")
                self.check_network_config()

            self.save_reporting()

            if not self.launcherConfig.DisableBackupRetention:
                self.backup_retention()
                AstroLogging.logPrint("备份保留已开始")
            # setup queue for data exchange
            self.webServer = None
            if not self.launcherConfig.DisableWebServer:
                # start http server
                self.webServer = self.start_WebServer()
                self.start_InfoLoop()
                # AstroLogging.logPrint(
                #    f"HTTP Server started at 127.0.0.1:{self.launcherConfig.WebServerPort}")

            if self.launcherConfig.HideLauncherConsoleWindow:
                # hide window
                AstroLogging.logPrint(
                    "已启用HideLauncherConsoleWindow，将在5秒内隐藏窗口..."
                )
                time.sleep(5)
                # pylint: disable=redefined-outer-name
                kernel32 = ctypes.WinDLL("kernel32")
                user32 = ctypes.WinDLL("user32")

                hWnd = kernel32.GetConsoleWindow()
                user32.ShowWindow(hWnd, 0)

            self.start_server(firstLaunch=True)
        except Exception as err:
            ermsg2 = (
                "INIT Error on line {}".format(sys.exc_info()[-1].tb_lineno),
                type(err).__name__,
                err,
            )
            AstroLogging.logPrint(f"{ermsg2}", "critical", True)

    def save_reporting(self):
        if self.saveObserver:
            if not self.saveObserver.is_alive():
                self.saveObserver = None
                self.save_reporting()
        else:
            self.saveObserver = Observer()
            saveGamePath = r"Astro\Saved\SaveGames"
            watchPath = ntpath.join(self.astroPath, saveGamePath)
            try:
                if not ntpath.exists(watchPath):
                    os.makedirs(watchPath)
            except Exception as e:
                AstroLogging.logPrint(e)
            self.saveObserver.schedule(self.SaveHandler(self), watchPath)
            self.saveObserver.start()

    def backup_retention(self):
        if self.backupObserver:
            if not self.backupObserver.is_alive():
                self.backupObserver = None
                self.backup_retention()
        else:
            self.backupObserver = Observer()
            backupSaveGamePath = r"Astro\Saved\Backup\SaveGames"
            watchPath = ntpath.join(self.astroPath, backupSaveGamePath)
            try:
                if not ntpath.exists(watchPath):
                    os.makedirs(watchPath)
            except Exception as e:
                AstroLogging.logPrint(e)
            self.backupObserver.daemon = True

            self.backupObserver.schedule(self.BackupHandler(self), watchPath)
            self.backupObserver.start()

    def refresh_launcher_config(self, lcfg=None):
        field_names = set(f.name for f in dataclasses.fields(self.LauncherConfig))
        cleaned_config = {
            k: v for k, v in self.get_launcher_config(lcfg).items() if k in field_names
        }
        self.launcherConfig = dataclasses.replace(self.launcherConfig, **cleaned_config)

        config = MultiConfig()
        config.read_dict({"AstroLauncher": cleaned_config})
        with open(self.launcherINI, "w") as configfile:
            config.write(configfile)

    def overwrite_launcher_config(self, ovrDict):
        ovrConfig = {"AstroLauncher": ovrDict}
        MultiConfig().overwrite_with(self.launcherINI, ovrConfig)

    def get_launcher_config(self, lfcg=None):
        if not lfcg:
            lfcg = self.LauncherConfig()
        baseConfig = {"AstroLauncher": dataclasses.asdict(lfcg)}
        config = MultiConfig().baseline(self.launcherINI, baseConfig)
        # print(settings)
        settings = config.getdict()["AstroLauncher"]
        return settings

    def validate_playfab_certs(self):
        try:
            AstroLogging.logPrint("正在尝试验证Playfab证书")
            playfabRequestCommand = [
                "powershell",
                "-executionpolicy",
                "bypass",
                "-command",
                "Invoke-WebRequest -uri https://5ea1.playfabapi.com/ -UseBasicParsing",
            ]
            with open(os.devnull, "w") as tempf:
                proc = subprocess.Popen(
                    playfabRequestCommand, stdout=tempf, stderr=tempf
                )
                proc.communicate()
        except Exception as err:
            ermsg3 = (
                "VerifyPlayfabCert Error on line {}".format(
                    sys.exc_info()[-1].tb_lineno
                ),
                type(err).__name__,
                err,
            )
            AstroLogging.logPrint(f"{ermsg3}", "warning", True)

    def update_server(self, latest_version):
        updateLocation = ntpath.join(
            self.astroPath,
            "steamcmd",
            "steamapps",
            "common",
            "ASTRONEER Dedicated Server",
        )
        steamcmdFolder = ntpath.join(self.astroPath, "steamcmd")
        steamcmdExe = ntpath.join(steamcmdFolder, "steamcmd.exe")
        steamcmdZip = ntpath.join(self.astroPath, "steamcmd.zip")
        try:
            if not ntpath.exists(steamcmdFolder):
                if not ntpath.exists(steamcmdExe):
                    if not ntpath.exists(steamcmdZip):
                        url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
                        r = (AstroRequests.get(url)).read()
                        with open(steamcmdZip, "wb") as f:
                            f.write(r)
                    with zipfile.ZipFile(steamcmdZip, "r") as zip_ref:
                        zip_ref.extractall(steamcmdFolder)
            update_downloaded = False

            if ntpath.exists(updateLocation):
                upd_version = "0.0"
                try:
                    with open(ntpath.join(updateLocation, "build.version"), "r") as f:
                        upd_version = (f.readline())[:-10]
                    if upd_version == latest_version:
                        update_downloaded = True
                except:
                    try:
                        shutil.rmtree(updateLocation)
                    except:
                        pass

            if not update_downloaded:
                open("update.p", "wb").write(b"download")
                if ntpath.exists(steamcmdExe):
                    try:
                        os.remove(steamcmdZip)
                    except:
                        pass

                    AstroLogging.logPrint(f"正在自动更新服务器到 {latest_version}...")
                    try:
                        updateCMD = [
                            steamcmdExe,
                            "+login anonymous",
                            "+app_update 728470",
                            "validate",
                            "+quit",
                        ]
                        update = subprocess.Popen(
                            updateCMD, creationflags=subprocess.DETACHED_PROCESS
                        )
                        while update.poll() is None:
                            time.sleep(0.1)
                    except Exception as e:
                        for child in psutil.Process(update.pid).children():
                            try:
                                child.kill()
                            except:
                                pass
                        try:
                            update.kill()
                        except:
                            pass

                        raise Exception("") from e

                upd_version = "0.0"
                try:
                    with open(ntpath.join(updateLocation, "build.version"), "r") as f:
                        upd_version = (f.readline())[:-10]
                except:
                    pass
                if upd_version == latest_version or (latest_version == "unknown"):
                    update_downloaded = True

            if update_downloaded:
                open("update.p", "wb").write(b"transfer")
                dir_util.copy_tree(updateLocation, self.astroPath)
                open("update.p", "wb").write(b"complete")

            cur_version = "0.0"
            with open(ntpath.join(self.astroPath, "build.version"), "r") as f:
                cur_version = (f.readline())[:-10]

            if cur_version == latest_version or (latest_version == "unknown"):
                AstroLogging.logPrint(f"更新到 {latest_version} 成功.")
                steamcmdZip = ntpath.join(self.astroPath, "steamcmd.zip")
                if ntpath.exists(steamcmdZip):
                    os.remove(steamcmdZip)
            try:
                os.remove("update.p")
            except:
                pass
            try:
                shutil.rmtree(updateLocation)
            except:
                pass

        except Exception as e:
            AstroLogging.logPrint(f"更新到 {latest_version} 失败.", "warning")
            AstroLogging.logPrint(
                f"{type(e).__name__}: {str(e)}", msgType="debug", printTraceback=True
            )

    def check_for_server_update(self, serverStart=False, check_only=False):
        try:
            # print('here1')
            if not self.launcherConfig.UpdateOnServerRestart and serverStart:
                return
            else:
                # print('here2')
                needs_update = False
                update_status = None
                if ntpath.exists("update.p"):
                    with open("update.p", "r") as f:
                        update_status = f.read()
                    if update_status != "completed":
                        needs_update = True

                # print('here3')
                cur_version = "0.0"
                try:
                    with open(ntpath.join(self.astroPath, "build.version"), "r") as f:
                        cur_version = (f.readline())[:-10]
                except:
                    pass
                # print(cur_version)
                # print('here4')
                if cur_version == "0.0":
                    needs_update = True
                url = "https://astroservercheck.joejoetv.de/api/stats"
                try:
                    data = json.load(AstroRequests.get(url))
                    # print(data)

                    # print('here6')
                    latest_version = data["stats"]["latestVersion"]
                    if version.parse(latest_version) > version.parse(cur_version):
                        needs_update = True
                    if not ntpath.exists(
                        ntpath.join(self.astroPath, "AstroServer.exe")
                    ):
                        needs_update = True
                    if needs_update:
                        AstroLogging.logPrint(
                            f"服务器更新可用: {cur_version} -> {latest_version}",
                            "warning",
                        )

                        # print('here7')
                        if (
                            self.launcherConfig.AutoUpdateServerSoftware
                            and not check_only
                        ):
                            self.update_server(latest_version)
                        # print('here8')
                        return True, latest_version
                except Exception as e:
                    print(e)
                    AstroLogging.logPrint("无法获取最新版本号!", "warning")

                    if self.launcherConfig.AutoUpdateServerSoftware and not check_only:
                        self.update_server("unknown")

                    with open(ntpath.join(self.astroPath, "build.version"), "r") as f:
                        cur_version = (f.readline())[:-10]

                    return True, cur_version

            cur_version = "0.0"
            with open(ntpath.join(self.astroPath, "build.version"), "r") as f:
                cur_version = (f.readline())[:-10]
            self.cur_server_version = cur_version
            # print('here9')
        except Exception as e:
            print(e)
            AstroLogging.logPrint("检查更新是否可用失败", "warning")

        return False, "0.0"

    def check_for_launcher_update(self, serverStart=False):
        try:
            url = "https://api.github.com/repos/JoeJoeTV/AstroLauncher/releases/latest"
            data = json.load((AstroRequests.get(url)))
            latestVersion = data["tag_name"]

            if version.parse(latestVersion) > version.parse(self.version):
                self.hasUpdate = latestVersion
                AstroLogging.logPrint(
                    f"更新: 有一个更新版本的启动器可用! {latestVersion}"
                )
                AstroLogging.logPrint(f"在 {self.latestURL} 下载")
                aupdate = self.launcherConfig.AutoUpdateLauncherSoftware
                if not self.launcherConfig.UpdateOnServerRestart and serverStart:
                    return

                if self.isExecutable and aupdate:
                    self.autoupdate_launcher(data)
        except:
            AstroLogging.logPrint("无法确定是否有新更新.", msgType="debug")

    def autoupdate_launcher(self, data):
        x = data
        downloadFolder = ntpath.dirname(sys.executable)
        for fileObj in x["assets"]:
            downloadURL = fileObj["browser_download_url"]
            fileName = ntpath.splitext(fileObj["name"])[0]
            downloadPath = ntpath.join(downloadFolder, fileName)

            downloadCMD = [
                "powershell",
                "-executionpolicy",
                "bypass",
                "-command",
                'Write-Host "Downloading latest AstroLauncher.exe..";',
                "wait-process",
                str(os.getpid()),
                ";",
                "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;",
                "$ProgressPreference = 'SilentlyContinue';",
                "Invoke-WebRequest",
                f"'{downloadURL}'",
                "-OutFile",
                f"'{downloadPath + '_new.exe'}'",
                ";",
                "Move-Item",
                "-path",
                f"'{downloadPath + '_new.exe'}'",
                "-destination",
                f"'{downloadPath + '.exe'}'",
                "-Force;",
                'Write-Host "Download complete!";',
                "Start-Process",
                f"'{downloadPath + '.exe'}'",
            ]
            # print(' '.join(downloadCMD))
            subprocess.Popen(
                downloadCMD,
                shell=True,
                creationflags=subprocess.DETACHED_PROCESS,
                stdin=None,
                stdout=None,
                stderr=None,
                close_fds=True,
            )
        time.sleep(2)
        self.DedicatedServer.kill_server("Auto-Update")

    # pylint: disable=unused-argument
    def signal_handler(self, sig, frame):
        self.DedicatedServer.kill_server(
            reason="Launcher shutting down via signal", save=True
        )

    def start_server(self, firstLaunch=False):
        """
        Starts the Dedicated Server process and waits for it to be registered
        """
        if firstLaunch:
            atexit.register(
                self.DedicatedServer.kill_server,
                reason="Launcher shutting down via exit",
                save=True,
            )
            signal.signal(signal.SIGINT, self.signal_handler)
        else:
            self.check_for_server_update(serverStart=True)
            self.check_for_launcher_update(serverStart=True)
            self.DedicatedServer = AstroDedicatedServer(self.astroPath, self)

        self.DedicatedServer.status = "starting"
        self.DedicatedServer.busy = False

        gxAuth = None
        while gxAuth is None:
            try:
                gxAuth = AstroAPI.generate_XAUTH(
                    self.DedicatedServer.settings.ServerGuid
                )
            except:
                AstroLogging.logPrint(
                    "无法生成XAuth令牌... 您是否连接到互联网?", msgType="warning"
                )
                time.sleep(5)
        self.headers["X-Authorization"] = gxAuth
        oldLobbyIDs = self.DedicatedServer.deregister_all_server()
        AstroLogging.logPrint("正在启动服务器进程...")
        if self.launcherConfig.EnableAutoRestart:
            AstroLogging.logPrint(
                f"下一次重启时间是 {self.DedicatedServer.nextRestartTime}"
            )
        # time.sleep(5)
        startTime = time.time()
        try:
            self.DedicatedServer.start()
        except:
            AstroLogging.logPrint("无法启动AstroServer.exe", "critical")
            return False

        reachableProcess = None
        pcounter = 40
        while not reachableProcess:
            try:
                reachableProcess = not bool(self.DedicatedServer.process.poll())
                pcounter -= 1
                time.sleep(0.25)
            except:
                pcounter -= 2
                time.sleep(0.5)
            if pcounter <= 0:
                AstroLogging.logPrint("无法在10秒内启动服务器进程!", "critical")
                return False

        AstroLogging.logPrint(
            f"服务器已启动 ( {self.cur_server_version} )! 正在准备....", ovrDWHL=True
        )

        try:
            self.DaemonProcess = AstroDaemon.launch(
                executable=self.isExecutable,
                consolePID=self.DedicatedServer.process.pid,
            )
        except:
            AstroLogging.logPrint("无法启动监视器守护进程", "warning")
            return False

        # Wait for server to finish registering...
        serverData = None
        oPFF = self.launcherConfig.PlayfabAPIFrequency
        while not self.DedicatedServer.registered:
            AstroLogging.logPrint("正在等待服务器注册...", "debug")
            try:
                serverData = AstroAPI.get_server(
                    self.DedicatedServer.ipPortCombo, self.headers
                )
                serverData = serverData["data"]["Games"]
                lobbyIDs = [x["LobbyID"] for x in serverData]
                if len(set(lobbyIDs) - set(oldLobbyIDs)) == 0:
                    time.sleep(self.launcherConfig.PlayfabAPIFrequency)
                else:
                    now = time.time()
                    if now - startTime > 15:
                        serverData = serverData[0]
                        self.DedicatedServer.registered = True
                        oldLobbyIDs = None
                        self.DedicatedServer.LobbyID = serverData["LobbyID"]

                if self.DedicatedServer.process.poll() is not None:
                    AstroLogging.logPrint("服务器在注册前被强制关闭。正在退出....")
                    return False
            except KeyboardInterrupt:
                self.DedicatedServer.kill_server(
                    "Launcher shutting down via KeyboardInterrupt"
                )
            except:
                AstroLogging.logPrint(
                    "检查服务器失败。可能达到了速率限制。正在后退并重试..."
                )
                if self.launcherConfig.PlayfabAPIFrequency < 30:
                    self.launcherConfig.PlayfabAPIFrequency += 1
                time.sleep(self.launcherConfig.PlayfabAPIFrequency)

        self.launcherConfig.PlayfabAPIFrequency = oPFF
        self.DedicatedServer.serverData = serverData
        doneTime = time.time()
        elapsed = doneTime - startTime
        # AstroLogging.logPrint("This is to show we're in the debug AstroLauncher version", "debug")
        AstroLogging.logPrint(
            f"服务器已准备就绪! 注册耗时 {round(elapsed,2)} 秒.", ovrDWHL=True
        )  # {self.DedicatedServer.LobbyID}
        self.DedicatedServer.status = "ready"
        # AstroLogging.logPrint("Starting server_loop: 1", "debug")
        self.DedicatedServer.server_loop()

    def check_ports_free(self):
        serverPort = False
        sp = int(self.DedicatedServer.settings.Port)

        consolePort = False
        cp = int(self.DedicatedServer.settings.ConsolePort)

        webPort = False
        wp = int(self.launcherConfig.WebServerPort)

        def is_port_in_use(port, tcp=True):
            lc = psutil.net_connections("inet")
            lc = [
                x
                for x in lc
                if x.type == (socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM)
                and x.laddr[1] == port
            ]
            return len(lc) > 0

        serverPort = bool(is_port_in_use(sp, False))
        consolePort = bool(is_port_in_use(cp))

        if not self.launcherConfig.DisableWebServer:
            webPort = bool(is_port_in_use(wp))

        if serverPort:
            AstroLogging.logPrint(
                f"有进程已经在使用您的服务器端口 ( {sp} UDP )", "critical"
            )
        if consolePort:
            AstroLogging.logPrint(
                f"有进程已经在使用您的控制台端口 ( {cp} TCP )", "critical"
            )
        if webPort:
            AstroLogging.logPrint(
                f"有进程已经在使用您的Web端口 ( {wp} TCP )", "critical"
            )
        if serverPort or consolePort or webPort:
            self.kill_launcher()

    def configure_firewall(self):
        if not self.launcherConfig.AdminAutoConfigureFirewall:
            return
        ALRule = None
        ALWRule = None
        ASRule = None
        launcherEXEPath = None
        isFirewallEnabled = None
        with os.popen(
            'netsh advfirewall show currentprofile | findstr /L "State" | findstr /L "ON"'
        ) as fwCheck:
            isFirewallEnabled = fwCheck.read()

        if isFirewallEnabled:
            serverExePath = ntpath.join(
                self.astroPath, "astro\\binaries\\win64\\astroserver-win64-shipping.exe"
            )
            ASRule = os.popen(
                f'netsh advfirewall firewall show rule name=astroserver-win64-shipping.exe verbose | findstr /L "{serverExePath}"'
            ).read()

            if self.isExecutable:
                launcherEXEPath = ntpath.join(os.getcwd(), sys.argv[0])
                ALRule = os.popen(
                    f'netsh advfirewall firewall show rule name=astrolauncher.exe verbose | findstr /L "{launcherEXEPath}"'
                ).read()

                if not self.launcherConfig.DisableWebServer:
                    ALWRule = os.popen(
                        f'netsh advfirewall firewall show rule name=AstroLauncherWeb | findstr /L "{self.launcherConfig.WebServerPort}"'
                    ).read()

            if not self.is_admin:
                if (
                    (not ASRule)
                    or (self.isExecutable and not ALRule)
                    or (
                        not self.launcherConfig.DisableWebServer
                        and self.isExecutable
                        and not ALWRule
                    )
                ):
                    AstroLogging.logPrint(
                        "无法找到防火墙设置! 请以管理员身份重新启动.", "warning"
                    )
            else:
                newRules = False
                if not ASRule:
                    newRules = True
                    subprocess.call(
                        f'netsh advfirewall firewall delete rule name=astroserver-win64-shipping.exe dir=in program="{serverExePath}"'
                        + f'& netsh advfirewall firewall add rule name=astroserver-win64-shipping.exe dir=in action=allow program="{serverExePath}"',
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                if self.isExecutable:
                    if not ALRule:
                        newRules = True
                        subprocess.call(
                            f'netsh advfirewall firewall delete rule name=astrolauncher.exe dir=in program="{launcherEXEPath}"'
                            + f'& netsh advfirewall firewall add rule name=astrolauncher.exe dir=in action=allow program="{launcherEXEPath}"',
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                if not self.launcherConfig.DisableWebServer and not ALWRule:
                    newRules = True
                    subprocess.call(
                        f"netsh advfirewall firewall delete rule name=AstroLauncherWeb dir=in protocol=TCP localport={self.launcherConfig.WebServerPort}"
                        + f"& netsh advfirewall firewall add rule name=AstroLauncherWeb dir=in action=allow protocol=TCP localport={self.launcherConfig.WebServerPort}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                if newRules:
                    AstroLogging.logPrint("正在设置自定义防火墙规则...")

    def check_network_config(self):
        localTest = ValidateSettings.test_network(
            self.DedicatedServer.settings.PublicIP,
            int(self.DedicatedServer.settings.Port),
            False,
        )
        remoteTest = ValidateSettings.test_nonlocal(
            self.DedicatedServer.settings.PublicIP,
            int(self.DedicatedServer.settings.Port),
        )
        testMatrix = [localTest, remoteTest]

        if testMatrix == [True, True]:
            AstroLogging.logPrint("服务器网络配置良好!")
        elif testMatrix == [False, True]:
            AstroLogging.logPrint("您的服务器无法从本地网络访问.", "warning")
            AstroLogging.logPrint("这通常表示NAT回环有问题", "warning")
            AstroLogging.logPrint(
                "检查您的路由器是否支持它，或者使用playit.gg设置您的服务器", "warning"
            )
            AstroLogging.logPrint(
                "设置playit.gg的指南 (11:28): https://youtu.be/SdLNFowq8WI?t=688",
                "warning",
            )
        elif testMatrix == [True, False]:
            AstroLogging.logPrint(
                "您的服务器可以在本地看到，但无法远程访问.", "warning"
            )
            AstroLogging.logPrint("这通常意味着您有一个需要禁用的回环适配器", "warning")
            AstroLogging.logPrint("并且您可能需要进行端口转发/打开防火墙.", "warning")
        elif testMatrix == [False, False]:
            AstroLogging.logPrint("服务器完全无法访问!", "warning")
            AstroLogging.logPrint(
                f"请端口转发 {self.DedicatedServer.settings.Port} UDP 并确保防火墙设置正确.",
                "warning",
            )

        rconNetworkCorrect = not (
            ValidateSettings.test_network(
                self.DedicatedServer.settings.PublicIP,
                int(self.DedicatedServer.settings.ConsolePort),
                True,
            )
        )
        if rconNetworkCorrect:
            AstroLogging.logPrint("远程控制台网络配置良好!")
        else:
            AstroLogging.logPrint(
                f"安全警报: 您的控制台端口 ({self.DedicatedServer.settings.ConsolePort}) 已被端口转发!",
                "warning",
                printToDiscord=False,
            )
            AstroLogging.logPrint(
                "安全警报: 这允许从您的网络外部访问服务器后端.",
                "warning",
                printToDiscord=False,
            )
            AstroLogging.logPrint(
                "安全警报: 请尽快禁用此功能以防止问题.", "warning", printToDiscord=False
            )
            time.sleep(5)

    def start_WebServer(self):
        ws = AstroWebServer.WebServer(self)

        def start_WebServerThread():
            if sys.version_info.minor > 7:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.set_event_loop(asyncio.new_event_loop())
            ws.run()

        t = Thread(target=start_WebServerThread, args=())
        t.daemon = True
        t.start()
        return ws

    def autoUpdate_websockets_Loop(self):
        while True:
            time.sleep(1)
            self.webServer.iterWebSocketConnections()

    def start_InfoLoop(self):
        def start_InfoLoopThread(self):
            if sys.version_info.minor > 7:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.autoUpdate_websockets_Loop()

        t = Thread(target=start_InfoLoopThread, args=(self,))
        t.daemon = True
        t.start()

    def kill_launcher(self):
        time.sleep(5)
        try:
            for child in psutil.Process(os.getpid()).children():
                child.kill()
        except:
            pass
        # Kill current process
        try:
            os.kill(os.getpid(), 9)
        except:
            pass

    def start_WebHookLoop(self):
        t = Thread(target=AstroLogging.sendDiscordReqLoop, args=())
        t.daemon = True
        t.start()


if __name__ == "__main__":
    try:
        os.system("title AstroLauncher - Unofficial Dedicated Server Launcher")
    except:
        pass
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-d",
            "--daemon",
            dest="daemon",
            help="Set the launcher to run as a Daemon",
            action="store_true",
        )
        parser.add_argument(
            "-c",
            "--consolepid",
            help="Set the consolePID for the Daemon",
            type=str.lower,
        )
        parser.add_argument(
            "-l",
            "--launcherpid",
            help="Set the launcherPID for the Daemon",
            type=str.lower,
        )

        parser.add_argument(
            "-p", "--path", help="Set the server folder path", type=str.lower
        )
        parser.add_argument(
            "-U",
            "--noupdate",
            dest="noautoupdate",
            default=None,
            help="Disable autoupdate if running as exe",
            action="store_true",
        )
        parser.add_argument(
            "-i",
            "--ini",
            dest="launcherINI",
            default="Launcher.ini",
            help="Set the location of the Launcher INI",
        )

        args = parser.parse_args()
        if args.daemon:
            if args.consolepid and args.launcherpid:
                kernel32 = ctypes.WinDLL("kernel32")
                user32 = ctypes.WinDLL("user32")
                SW_HIDE = 0
                hWnd = kernel32.GetConsoleWindow()
                if hWnd:
                    user32.ShowWindow(hWnd, SW_HIDE)

                AstroDaemon().daemon(args.launcherpid, args.consolepid)
            else:
                print("Insufficient launch options!")
        else:
            AstroLauncher(
                args.path,
                disable_auto_update=args.noautoupdate,
                launcherINI=args.launcherINI,
            )
    except KeyboardInterrupt:
        pass
    except Exception as err:
        ermsg1 = (
            "FINAL Error on line {}".format(sys.exc_info()[-1].tb_lineno),
            type(err).__name__,
            err,
        )
        AstroLogging.logPrint(f"{ermsg1}", "critical", True)
