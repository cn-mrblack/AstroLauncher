console.log("Hi there! Feel to explore the code!");
//let apiURL = 'http://127.0.0.1:80/api'
let baseURL = location.pathname;
let apiURL = baseURL + "api";
let playersTableOriginal = $("#onlinePlayersTable").html();
let saveGamesTableOriginal = $("#saveGamesTable").html();

let webSocket = null;
const createWebSocket = async () => {
    let WSprotocol = location.protocol == "https:" ? "wss" : "ws";
    webSocket = new WebSocket(
        WSprotocol + "://" + location.host + baseURL + "ws"
    );
    webSocket.onmessage = function (evt) {
        tick(evt.data);
    };
    webSocket.onopen = function (evt) {
        console.log("Created Web Socket");
    };
};
const checkWebSocket = async () => {
    if (webSocket.readyState === WebSocket.CLOSED) {
        try {
            createWebSocket();
        } catch {}
    }
};
createWebSocket();

setInterval(checkWebSocket, 5000);

let oldMsg = "";
let oldSettings = {};
let oldPlayers = {};
let oldSaves = {};
let oViewCount = "";
let oInstanceID = "";
let isAdmin = false;
let isRconReady = false;

const statusMsg = (msg) => {
    if (oldMsg != msg) {
        oldMsg = msg;
        $("#serverStatus").removeClass(
            "text-success text-warning text-danger text-info"
        );
        if (msg == "off") {
            $("#serverStatus").text("离线");
            $("#serverStatus").addClass("text-danger");
            $("#msg span").text("服务器已离线");
            $("#msg").collapse("show");
        } else if (msg == "shutdown") {
            $("#serverStatus").text("正在关闭");
            $("#serverStatus").addClass("text-danger");
            $("#msg span").text("服务器正在关闭");
            $("#msg").collapse("hide");
        } else if (msg == "reboot") {
            $("#serverStatus").text("正在重启");
            $("#serverStatus").addClass("text-info");
            $("#msg span").text("服务器正在重启");
            $("#msg").collapse("hide");
        } else if (msg == "starting") {
            $("#serverStatus").text("正在启动");
            $("#serverStatus").addClass("text-warning");
            $("#msg span").text("服务器正在准备");
            $("#msg").collapse("show");
        } else if (msg == "saving") {
            $("#serverStatus").text("正在保存");
            $("#serverStatus").addClass("text-info");
            $("#msg span").text("服务器正在保存");
            $("#msg").collapse("hide");
        } else if (msg == "ready") {
            $("#serverStatus").text("就绪");
            $("#serverStatus").addClass("text-success");
            $("#msg span").text("服务器已就绪");
            $("#msg").collapse("hide");
        } else if (msg == "delsave") {
            $("#serverStatus").text("正在删除存档");
            $("#serverStatus").addClass("text-danger");
            $("#msg span").text("服务器正在删除存档");
            $("#msg").collapse("hide");
        } else if (msg == "loadsave") {
            $("#serverStatus").text("正在加载存档");
            $("#serverStatus").addClass("text-warning");
            $("#msg span").text("服务器正在加载存档");
            $("#msg").collapse("hide");
        } else if (msg == "newsave") {
            $("#serverStatus").text("正在创建新存档");
            $("#serverStatus").addClass("text-success");
            $("#msg span").text("服务器正在创建新存档");
            $("#msg").collapse("hide");
        } else if (msg == "renamesave") {
            $("#serverStatus").text("正在重命名存档");
            $("#serverStatus").addClass("text-warning");
            $("#msg span").text("服务器正在重命名存档");
            $("#msg").collapse("hide");
        }
    }
};
const compareObj = (obj1, obj2) => {
    return JSON.stringify(obj1) === JSON.stringify(obj2);
};

let logList = [];

const tick = async (data) => {
    if (data == {}) {
        return;
    }
    data = JSON.parse(data);
    console.log(data);
    try {
        if (
            (oldMsg == "shutdown" || oldMsg == "reboot") &&
            data.status == "ready"
        ) {
        } else {
            statusMsg(data.status);
        }
        if (oInstanceID === "") {
            oInstanceID = data.instanceID;
        }
        isRconReady = data.rready;
        isAdmin = data.admin;
        if (
            ($("#console").length && !isAdmin) ||
            data.instanceID !== oInstanceID
        ) {
            location.reload();
        }
        if (data.forceUpdate) {
            oldMsg = "";
            oldSettings = {};
            oldPlayers = {};
            oldSaves = {};
            oViewCount = "";
        }
        if (data.viewers !== oViewCount) {
            oViewCount = data.viewers;
            $("#viewCount").text(oViewCount);
        }
        if (data.hasUpdate != false) {
            let ghLink = document.querySelector("#githubLink");
            let tipInstance = ghLink._tippy;
            tipInstance.setContent("更新可用: " + data.hasUpdate);
            tipInstance.show();
        }
        // smart scroll
        if (isAdmin) {
            let log = $("#consoleText")[0];
            let isBottom =
                Math.abs(
                    log.scrollTop - (log.scrollHeight - log.clientHeight)
                ) < 2;

            let sLogs = data.logs.split(/\r?\n/);
            let newLogs = sLogs.filter((i) => !logList.includes(i) && i != "");

            newLogs.forEach((entry) => {
                logList.push(entry);

                let content = "";
                let levelType = "";
                entry = entry.replace(/"|'/g, "");
                entry = linkify(entry);

                if (entry.includes("INFO")) {
                    levelType = "INFO";
                    let parts = entry.split("INFO");
                    content =
                        "<i class='fas fa-info-circle iconInfo'></i> " +
                        parts[0] +
                        //"<span style='color: green;'>INFO</span>" +
                        parts[1];
                } else if (entry.includes("CMD")) {
                    levelType = "CMD";
                    let parts = entry.split("CMD");
                    content =
                        "<i class='fas fa-terminal iconCMD'></i> " +
                        parts[0] +
                        //"<span style='color: cyan;'>CHAT</span>" +
                        parts[1];
                } else if (entry.includes("CHAT")) {
                    levelType = "CHAT";
                    let parts = entry.split("CHAT");
                    content =
                        "<i class='fas fa-comments iconChat'></i> " +
                        parts[0] +
                        //"<span style='color: cyan;'>CHAT</span>" +
                        parts[1];
                } else if (entry.includes("WARNING")) {
                    let parts = entry.split("WARNING");
                    levelType = "WARNING";
                    content =
                        "<i class='fas fa-exclamation-triangle iconWarn'></i> " +
                        parts[0] +
                        //"<span style='color: red;'>WARNING</span>" +
                        parts[1];
                } else {
                    content = entry;
                }

                let row = document.createElement("div");
                row.innerHTML = content;
                if (levelType == "WARNING") {
                    $(row).addClass("warning");
                }

                $("#consoleText").append(row);
            });

            if (isBottom) log.scrollTop = log.scrollHeight - log.clientHeight;
        }

        let s = data.settings;
        if (data.server_version) {
            $("#serverVersion").text(DOMPurify.sanitize(data.server_version));
        }
        if (data.stats) {
            $("#hWL").text(
                DOMPurify.sanitize(data.stats.isEnforcingWhitelist.toString())
            );
            $("#hPW").text(
                DOMPurify.sanitize(data.stats.hasServerPassword.toString())
            );
            $("#hCM").text(
                DOMPurify.sanitize(data.stats.creativeMode.toString())
            );

            $("#serverVersion").text(DOMPurify.sanitize(data.stats.build));
            $("#framerateStats").text(
                DOMPurify.sanitize(
                    parseInt(data.stats.averageFPS) +
                        "/" +
                        parseInt(s.MaxServerFramerate) +
                        " FPS"
                )
            );
        }
        if (!compareObj(oldSettings, s)) {
            oldSettings = s;
            $("#bannerServerName").text(DOMPurify.sanitize(`${s.ServerName}`));
            $("#serverName").text(DOMPurify.sanitize(`${s.ServerName}`));
            $("#serverPort").text(
                DOMPurify.sanitize(`${s.PublicIP}:${s.Port}`)
            );
            $("#owner").text(DOMPurify.sanitize(s.OwnerName));
        }
        if (
            data.status == "starting" ||
            data.status == "off" ||
            data.status == "shutdown"
        ) {
            $("#playersStats").text("");
            $("#framerateStats").text("");
        } else {
            if (data.hasOwnProperty("savegames")) {
                if (!compareObj(oldSaves, data.savegames)) {
                    oldSaves = data.savegames;
                    $("#saveGamesTable").html(saveGamesTableOriginal);
                    if (data.savegames.hasOwnProperty("gameList")) {
                        let gameList = Object.create(data.savegames.gameList);
                        gameList.sort((a, b) =>
                            a.active < b.active
                                ? 1
                                : a.active === b.active
                                ? a.name > b.name
                                    ? 1
                                    : -1
                                : -1
                        );
                        oldSaves.gameList = gameList;
                        gameList.forEach((sg, i) => {
                            let row = document.createElement("tr");
                            sg.active == "Active"
                                ? $(row).addClass("activeSave")
                                : null;
                            row.innerHTML = `
                            <td class="d-md-none p-0 ${
                                sg.active == "Active" ? "activeCell" : ""
                            }"></td>
                            <td class="d-none d-md-table-cell">${DOMPurify.sanitize(
                                sg.active
                            )}</td>
                                <td><span data-name="${
                                    sg.name
                                }" data-index="${i}" class="${
                                sg.active ? "" : "saveName"
                            }">${DOMPurify.sanitize(sg.name)}</span></td>
                                <td>${DOMPurify.sanitize(sg.date)}</td>
                                <td>${sg.bHasBeenFlaggedAsCreativeModeSave}</td>
                                <td>${DOMPurify.sanitize(sg.size)}</td>
                                <td>${createSaveActionButtons(
                                    sg.active,
                                    sg,
                                    i
                                )}</td>`;

                            $("#saveGamesTable>tbody").append(row);
                        });
                    }
                }
            }

            if (!compareObj(oldPlayers, data.players)) {
                /*
                if (oldSettings.OwnerName != "") {
                    data.players.playerInfo.forEach(function (player, index) {
                        if (player.playerName.replace(/\?/g, "") == "") {
                            if (player.playerCategory == "Owner") {
                                this[index].playerName = oldSettings.OwnerName;
                            }
                        }
                    }, data.players.playerInfo);
                }*/
                oldPlayers = data.players;
                $("#onlinePlayersTable").html(playersTableOriginal);
                $("#offlinePlayersTable").html(playersTableOriginal);
                if (data.players.hasOwnProperty("playerInfo")) {
                    $("#playersStats").text(
                        DOMPurify.sanitize(
                            data.players.playerInfo.filter((p) => p.inGame)
                                .length +
                                "/" +
                                s.MaximumPlayerCount
                        )
                    );

                    if (data.players) {
                        data.players.playerInfo.forEach((p) => {
                            let row = document.createElement("tr");
                            row.innerHTML = `<td class="p-2 d-md-none" >
                            ${DOMPurify.sanitize(
                                p.playerName == "" ? " " : p.playerName
                            )}
                            <hr class="m-1">
                            ${DOMPurify.sanitize(p.playerGuid)}</td>

                            <td class="p-2 d-none d-md-table-cell" >
                                ${DOMPurify.sanitize(p.playerName)}
                            </td>
                            <td class="p-2 d-none d-md-table-cell">
                                ${DOMPurify.sanitize(p.playerGuid)}
                            </td>

                            <td class="text-left">${DOMPurify.sanitize(
                                p.playerCategory
                            )}</td>`;

                            if (p.inGame == true) {
                                if (isAdmin) {
                                    row.innerHTML +=
                                        '<td class="text-left">' +
                                        createPlayerActionButtons("online", p) +
                                        "</td>";
                                }
                                $("#onlinePlayersTable>tbody").append(row);
                            } else {
                                $("#offlinePlayersTable>tbody").append(row);
                                if (isAdmin) {
                                    row.innerHTML +=
                                        '<td class="text-left">' +
                                        createPlayerActionButtons(
                                            "offline",
                                            p
                                        ) +
                                        "</td>";
                                }
                            }
                        });
                    }
                }
            }
        }
    } catch (e) {
        console.log(e);
        $("#msg span").text("错误! 10秒后重试");
        $("#msg").collapse("show");
        statusMsg("off");
    }
};

const createSaveActionButtons = function (status, save, index) {
    let dropDownDiv = $("<div/>").attr({ class: "btn-group dropup" });
    let DDButton = $("<button/>")
        .attr({
            type: "button",
            class: "btn btn-secondary dropdown-toggle",
            "data-toggle": "dropdown",
            "aria-haspopup": "true",
            "aria-expanded": "false",
            id: "dropdownMenu2",
        })
        .text("操作");
    let DDMenu = $("<div/>").attr({
        class: "dropdown-menu",
        "aria-labelledby": "dropdownMenu2",
    });
    dropDownDiv.append(DDButton);
    dropDownDiv.append(DDMenu);
    let sButton = $("<button/>").attr({
        type: "button",
        class: "dropdown-item p-1",
        "data-name": save.name,
        "data-index": index,
    });

    let actionButtonBufferList = [];

    let loadButton = sButton
        .clone()
        .attr("data-action", "load")
        .addClass("sBtn")
        .text("加载");
    actionButtonBufferList.push(loadButton);

    let deleteButton = sButton
        .clone()
        .addClass("sdBtn")
        .attr("data-action", "delete")
        .attr("data-toggle", "modal")
        .attr("data-target", "#deleteSaveModal")
        .text("删除");
    actionButtonBufferList.push(deleteButton);

    let renameButton = sButton
        .clone()
        .addClass("sdBtn")
        .attr("data-action", "rename")
        .text("重命名");
    actionButtonBufferList.push(renameButton);

    if (status == "Active") {
        loadButton.addClass("disabled");
        deleteButton.addClass("disabled");
    }
    if (!save.loadable) {
        loadButton.addClass("disabled");
    }

    actionButtonBufferList.forEach((element) => {
        DDMenu.append(element);
    });
    return dropDownDiv.prop("outerHTML");
};

const createPlayerActionButtons = function (status, player) {
    let dropDownDiv = $("<div/>").attr({ class: "btn-group dropup" });
    if (player.playerCategory != "Owner") {
        let DDButton = $("<button/>")
            .attr({
                type: "button",
                class: "btn btn-secondary dropdown-toggle",
                "data-toggle": "dropdown",
                "aria-haspopup": "true",
                "aria-expanded": "false",
                id: "dropdownMenu2",
            })
            .text("Actions");
        let DDMenu = $("<div/>").attr({
            class: "dropdown-menu",
            "aria-labelledby": "dropdownMenu2",
        });
        dropDownDiv.append(DDButton);
        dropDownDiv.append(DDMenu);
        let sButton = $("<button/>").attr({
            type: "button",
            class: "dropdown-item pBtn p-1",
            "data-guid": player.playerGuid,
            "data-name": player.playerName,
        });

        let actionButtonBufferList = [];

        let kickButton = sButton.clone().attr("data-action", "kick").text("踢除");
        actionButtonBufferList.push(kickButton);

        let banButton = sButton.clone().attr("data-action", "ban").text("封禁");
        actionButtonBufferList.push(banButton);

        let WLButton = sButton.clone().attr("data-action", "WL").text("加入白名单");
        actionButtonBufferList.push(WLButton);

        let AdminButton = sButton
            .clone()
            .attr("data-action", "admin")
            .text("授予管理员");
        actionButtonBufferList.push(AdminButton);

        let ResetButton = sButton
            .clone()
            .attr("data-action", "reset")
            .text("重置权限");
        actionButtonBufferList.push(ResetButton);

        /*
        RemoveButton = sButton
            .clone()
            .attr("data-action", "remove")
            .text("Remove");
        actionButtonBufferList.push(RemoveButton);
        */
        if (status != "online") {
            kickButton.addClass("disabled");
        }
        if (player.playerCategory == "Blacklisted") {
            banButton.addClass("disabled");
        }
        if (player.playerCategory == "Whitelisted") {
            WLButton.addClass("disabled");
        }
        if (player.playerCategory == "Admin") {
            AdminButton.addClass("disabled");
        }
        if (player.playerName == "") {
            kickButton.addClass("disabled");
            banButton.addClass("disabled");
            WLButton.addClass("disabled");
            AdminButton.addClass("disabled");
            ResetButton.addClass("disabled");
        }
        actionButtonBufferList.forEach((element) => {
            DDMenu.append(element);
        });
    }
    return dropDownDiv.prop("outerHTML");
};
$(document).on("input", "#WLPlayerInp", function (e) {
    console.log($(e.target).val());
    $("#WLPlayerBtn").attr({ "data-name": $(e.target).val() });
});

$(document).on("click", "button[data-action='rename']", function (e) {
    let oName = $(e.target).attr("data-name");
    let oIndex = $(e.target).attr("data-index");
    let nameSpan = $(`span[data-index='${oIndex}']`);
    let sName = nameSpan.text();
    let swidth = nameSpan.width();
    let parent = nameSpan.parent();
    parent.addClass("inputBox");
    let a = $("<div/>").attr({
        class: "input-group mb-3",
    });
    let b = $("<div/>").attr({
        class: "input-group-append",
    });

    let sInput = $("<input/>").attr({
        type: "text",
        class: "saveNameInput form-control",
        "data-saveOName": sName,
        "data-saveOIndex": oIndex,
    });
    sInput.val(sName);
    let sButton = $("<button/>")
        .attr({
            type: "button",
            class: "saveNameSubmit btn btn-outline-secondary text-white",
            "data-saveOName": sName,
            "data-saveOIndex": oIndex,
        })
        .text("✓");
    parent.html("");
    a.append(sInput);
    b.append(sButton);
    a.append(b);
    parent.append(a);
});

$(document).on("click", ".saveNameSubmit", function (e) {
    e.preventDefault();
    let parent = $(e.target).closest(".inputBox");
    parent.removeClass("inputBox");
    let sInput = parent.find(".saveNameInput");
    let sName = sInput.val();
    let oName = $(e.target).attr("data-saveOName");
    let sIndex = $(e.target).attr("data-saveOIndex");
    let sSave = oldSaves["gameList"][sIndex];
    if (sName.length < 3) {
        sName = oName;
    }
    if (
        !oldSaves.gameList.map((x) => x.name).includes(sName) &&
        oName != sName
    ) {
        $.ajax({
            type: "POST",
            url: apiURL + "/savegame/rename",
            dataType: "json",
            data: JSON.stringify({ save: sSave, nName: sName }),
            success: function (result) {},
            error: function (result) {
                console.log(result);
                alert("错误");
            },
        });
    } else {
        sName = oName;
    }
    let nameSpan = $("<span/>").addClass("saveName").attr("data-name", sName);
    nameSpan.text(sName);
    parent.html(nameSpan);
});

$(document).on("click", ".pBtn", function (e) {
    e.preventDefault();
    let pGuid = $(e.target).attr("data-guid");
    let pName = $(e.target).attr("data-name");
    let pAction = $(e.target).attr("data-action");

    $.ajax({
        type: "POST",
        url: apiURL + "/player",
        dataType: "json",
        data: JSON.stringify({ guid: pGuid, action: pAction, name: pName }),
        success: function (result) {},
        error: function (result) {
            console.log(result);
            alert("Error");
        },
    });
});

$(document).on("click", ".sBtn", function (e) {
    e.preventDefault();
    let sName = $(e.target).attr("data-name");
    let sIndex = $(e.target).attr("data-index");
    let sAction = $(e.target).attr("data-action");
    let sSave = oldSaves["gameList"][sIndex];
    $.ajax({
        type: "POST",
        url: apiURL + "/savegame/" + sAction,
        dataType: "json",
        data: JSON.stringify({ save: sSave }),
        success: function (result) {},
        error: function (result) {
            console.log(result);
            alert("Error");
        },
    });
});

$("#deleteSaveModal").on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget); // Button that triggered the modal
    var saveIndex = button.data("index"); // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var save = oldSaves["gameList"][saveIndex];
    var modal = $(this);
    modal
        .find(".modal-title")
        .text("你确定要删除这个存档吗？ ");
    modal.find(".modal-body").text(DOMPurify.sanitize(save["fileName"]));
    modal
        .find(".modal-footer .btn-danger")
        .attr("data-action", "delete")
        .attr("data-name", save["name"])
        .attr("data-index", saveIndex);
});

const saveLog = function (filename, data) {
    var blob = new Blob([data], { type: "text/csv" });
    if (window.navigator.msSaveOrOpenBlob) {
        window.navigator.msSaveBlob(blob, filename);
    } else {
        var elem = window.document.createElement("a");
        elem.href = window.URL.createObjectURL(blob);
        elem.download = filename;
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);
    }
};

$(".fa-download").click(function (e) {
    e.stopPropagation();

    let fileBuffer = "";
    logList.forEach((entry) => {
        fileBuffer += entry;
        fileBuffer += "\n";
    });

    saveLog("server.log", fileBuffer);
});

$("#saveGameBtn").click(function (e) {
    e.preventDefault();
    if (isRconReady){
        statusMsg("saving");
        $.ajax({
            type: "POST",
            url: apiURL + "/savegame",
            dataType: "json",
            success: function (result) {},
            error: function (result) {
                console.log(result);
                alert("Error");
            },
        });
    }
});

$("#rebootServerBtn").click(function (e) {
    e.preventDefault();
    if (isRconReady){
        statusMsg("reboot");
        $.ajax({
            type: "POST",
            url: apiURL + "/reboot",
            dataType: "json",
            success: function (result) {},
            error: function (result) {
                console.log(result);
                alert("Error");
            },
        });
    }
});

$("#stopLauncherBtn").click(function (e) {
    e.preventDefault();
    let reallyShutdown = confirm(
        "你确定要关闭启动器吗？它将需要手动重新启动。"
    );
    if (reallyShutdown == true) {
        statusMsg("shutdown");
        setTimeout(() => {
            statusMsg("off");
        }, 2000);
        $.ajax({
            type: "POST",
            url: apiURL + "/shutdown",
            dataType: "json",
            success: function (result) {},
            error: function (result) {
                console.log(result);
            },
        });
    }
});

$("#newSaveBtn").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (isRconReady){
        statusMsg("saving");
        $.ajax({
            type: "POST",
            url: apiURL + "/newsave",
            dataType: "json",
            success: function (result) {},
            error: function (result) {
                console.log(result);
                alert("Error");
            },
        });
    }
});

const linkify = (text) => {
    //const exp = /(\b(((https?|ftp|file):\/\/)|[-A-Z0-9+&@#\/%=~_|]*\.)[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gi;
    const exp = /(\b(((https?|ftp|file):\/\/)|[-A-Z+&@#\/%=~_|]+\.)[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gi;
    text = DOMPurify.sanitize(text);
    return text.replace(
        exp,
        `<a href="$1" target="_blank" style="color: #baf;">$1</a>`
    );
};

var clipboard = new ClipboardJS(".ctc");

clipboard.on("success", function (e) {
    e.clearSelection();
});

tippy(".ctc", {
    content: "已复制!",
    trigger: "click",
    onShow(instance) {
        setTimeout(() => {
            instance.hide();
        }, 1500);
    },
    placement: "right",
});

tippy(".ctc", {
    content: "点击复制",
    trigger: "mouseenter focus",
    placement: "right",
    onTrigger(instance, event) {
        if (tippy.currentInput.isTouch) {
            instance.disable();
        } else {
            instance.enable();
        }
    },
});

tippy("#githubLink", {
    content: "更新可用",
    placement: "right-end",
    trigger: "manual",
    hideOnClick: false,
    theme: "update",
    interactive: true,
});
