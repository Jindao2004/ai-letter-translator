import json
import os
import queue
import re
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


APP_NAME = "AI 写信翻译"
APP_VERSION = "1.0.0"
APP_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "AI写信翻译"
SETTINGS_FILE = APP_DIR / "settings.json"
DRAFT_FILE = APP_DIR / "draft.json"

LANGUAGES = [
    "简体中文", "繁体中文", "英语", "日语", "韩语", "法语", "德语", "西班牙语",
    "葡萄牙语", "意大利语", "俄语", "乌克兰语", "波兰语", "荷兰语", "阿拉伯语",
    "希伯来语", "波斯语", "土耳其语", "印地语", "孟加拉语", "乌尔都语", "泰语",
    "越南语", "印度尼西亚语", "马来语", "瑞典语", "丹麦语", "挪威语", "芬兰语",
    "希腊语", "捷克语", "罗马尼亚语", "匈牙利语",
]

EMOJI_GROUPS = {
    "热门": "😀 😂 🤣 😊 🥰 😍 😘 😎 🤔 🥺 😭 😡 🥳 🤗 🫡 ❤️ 💕 💔 👍 👏 🙏 💪 🎉 ✨ 🔥 ✅ 🌹 💌",
    "表情与情感": (
        "😀 😃 😄 😁 😆 😅 🤣 😂 🙂 🙃 🫠 😉 😊 😇 🥰 😍 🤩 😘 😗 ☺️ 😚 😙 🥲 "
        "😋 😛 😜 🤪 😝 🤑 🤗 🤭 🫢 🫣 🤫 🤔 🫡 🤐 🤨 😐 😑 😶 🫥 😶‍🌫️ 😏 😒 🙄 😬 😮‍💨 🤥 "
        "😌 😔 😪 🤤 😴 😷 🤒 🤕 🤢 🤮 🤧 🥵 🥶 🥴 😵 😵‍💫 🤯 🤠 🥳 🥸 😎 🤓 🧐 😕 🫤 😟 "
        "🙁 ☹️ 😮 😯 😲 😳 🥺 🥹 😦 😧 😨 😰 😥 😢 😭 😱 😖 😣 😞 😓 😩 😫 🥱 😤 😡 😠 🤬 "
        "😈 👿 💀 ☠️ 💩 🤡 👹 👺 👻 👽 👾 🤖 😺 😸 😹 😻 😼 😽 🙀 😿 😾 🙈 🙉 🙊 "
        "💋 💌 💘 💝 💖 💗 💓 💞 💕 💟 ❣️ 💔 ❤️‍🔥 ❤️‍🩹 ❤️ 🩷 🧡 💛 💚 💙 🩵 💜 🤎 🖤 🩶 🤍"
    ),
    "人物与身体": (
        "👋 🤚 🖐️ ✋ 🖖 🫱 🫲 🫳 🫴 🫷 🫸 👌 🤌 🤏 ✌️ 🤞 🫰 🤟 🤘 🤙 👈 👉 👆 🖕 👇 ☝️ "
        "🫵 👍 👎 ✊ 👊 🤛 🤜 👏 🙌 🫶 👐 🤲 🤝 🙏 ✍️ 💅 🤳 💪 🦾 🦿 🦵 🦶 👂 🦻 👃 🧠 🫀 🫁 🦷 🦴 👀 👁️ 👅 👄 🫦 "
        "👶 🧒 👦 👧 🧑 👱 👨 🧔 👩 🧓 👴 👵 🙍 🙎 🙅 🙆 💁 🙋 🧏 🙇 🤦 🤷 🧑‍⚕️ 🧑‍🎓 🧑‍🏫 🧑‍⚖️ "
        "🧑‍🌾 🧑‍🍳 🧑‍🔧 🧑‍🏭 🧑‍💼 🧑‍🔬 🧑‍💻 🧑‍🎤 🧑‍🎨 🧑‍✈️ 🧑‍🚀 🧑‍🚒 👮 🕵️ 💂 🥷 👷 🫅 🤴 👸 "
        "👳 👲 🧕 🤵 👰 🤰 🫃 🫄 🤱 👼 🎅 🤶 🦸 🦹 🧙 🧚 🧛 🧜 🧝 🧞 🧟 💆 💇 🚶 🧍 🧎 🏃 💃 🕺 👯 🧖 🧗 🤺 🏇 ⛷️ 🏂 🏌️ 🏄 🚣 🏊 ⛹️ 🏋️ 🚴 🚵 🤸 🤼 🤽 🤾 🤹 🧘 🛀 🛌 "
        "🧑‍🤝‍🧑 👭 👫 👬 💏 💑 👪 🗣️ 👤 👥 🫂"
    ),
    "动物与自然": (
        "🐵 🐒 🦍 🦧 🐶 🐕 🦮 🐕‍🦺 🐩 🐺 🦊 🦝 🐱 🐈 🐈‍⬛ 🦁 🐯 🐅 🐆 🐴 🫎 🫏 🐎 🦄 🦓 🦌 🦬 🐮 🐂 🐃 🐄 🐷 🐖 🐗 🐽 🐏 🐑 🐐 🐪 🐫 🦙 🦒 🐘 🦣 🦏 🦛 🐭 🐁 🐀 🐹 🐰 🐇 🐿️ 🦫 🦔 🦇 🐻 🐻‍❄️ 🐨 🐼 🦥 🦦 🦨 🦘 🦡 🐾 "
        "🦃 🐔 🐓 🐣 🐤 🐥 🐦 🐧 🕊️ 🦅 🦆 🦢 🦉 🦤 🪶 🦩 🦚 🦜 🪽 🐦‍⬛ 🪿 🐸 🐊 🐢 🦎 🐍 🐲 🐉 🦕 🦖 "
        "🐳 🐋 🐬 🦭 🐟 🐠 🐡 🦈 🐙 🐚 🪸 🪼 🐌 🦋 🐛 🐜 🐝 🪲 🐞 🦗 🪳 🕷️ 🕸️ 🦂 🦟 🪰 🪱 🦠 "
        "💐 🌸 💮 🪷 🏵️ 🌹 🥀 🌺 🌻 🌼 🌷 🪻 🌱 🪴 🌲 🌳 🌴 🌵 🌾 🌿 ☘️ 🍀 🍁 🍂 🍃 🍄 🪨 🪵 "
        "🌍 🌎 🌏 🌐 🗺️ 🗾 🧭 🏔️ ⛰️ 🌋 🗻 🏕️ 🏖️ 🏜️ 🏝️ 🏞️ 🌅 🌄 🌠 🎇 🎆 🌈 ☀️ 🌤️ ⛅ 🌥️ ☁️ 🌦️ 🌧️ ⛈️ 🌩️ 🌨️ ❄️ ☃️ ⛄ 🌬️ 💨 🌪️ 🌫️ 🌊 💧 💦 ☔ ⚡"
    ),
    "食物与饮料": (
        "🍏 🍎 🍐 🍊 🍋 🍋‍🟩 🍌 🍉 🍇 🍓 🫐 🍈 🍒 🍑 🥭 🍍 🥥 🥝 🍅 🍆 🥑 🫛 🥦 🥬 🥒 🌶️ 🫑 🌽 🥕 🫒 🧄 🧅 🥔 🍠 🫚 🫘 "
        "🥐 🥯 🍞 🥖 🫓 🥨 🥞 🧇 🧀 🍖 🍗 🥩 🥓 🍔 🍟 🍕 🌭 🥪 🌮 🌯 🫔 🥙 🧆 🥚 🍳 🥘 🍲 🫕 🥣 🥗 🍿 🧈 🧂 🥫 "
        "🍱 🍘 🍙 🍚 🍛 🍜 🍝 🍠 🍢 🍣 🍤 🍥 🥮 🍡 🥟 🥠 🥡 🦀 🦞 🦐 🦑 🦪 "
        "🍦 🍧 🍨 🍩 🍪 🎂 🍰 🧁 🥧 🍫 🍬 🍭 🍮 🍯 "
        "🍼 🥛 ☕ 🫖 🍵 🍶 🍾 🍷 🍸 🍹 🍺 🍻 🥂 🥃 🫗 🥤 🧋 🧃 🧉 🧊 🥢 🍽️ 🍴 🥄 🔪 🫙"
    ),
    "旅行与地点": (
        "🏠 🏡 🏘️ 🏚️ 🏗️ 🏭 🏢 🏬 🏣 🏤 🏥 🏦 🏨 🏪 🏫 🏩 💒 🏛️ ⛪ 🕌 🛕 🕍 ⛩️ 🕋 ⛲ ⛺ 🌁 🌃 🏙️ 🌆 🌇 🌉 ♨️ 🎠 🛝 🎡 🎢 💈 🎪 "
        "🚂 🚃 🚄 🚅 🚆 🚇 🚈 🚉 🚊 🚝 🚞 🚋 🚌 🚍 🚎 🚐 🚑 🚒 🚓 🚔 🚕 🚖 🚗 🚘 🚙 🛻 🚚 🚛 🚜 🏎️ 🏍️ 🛵 🦽 🦼 🛺 🚲 🛴 🛹 🛼 🚏 🛣️ 🛤️ 🛢️ ⛽ 🛞 🚨 🚥 🚦 🛑 🚧 "
        "⚓ 🛟 ⛵ 🛶 🚤 🛳️ ⛴️ 🛥️ 🚢 ✈️ 🛩️ 🛫 🛬 🪂 💺 🚁 🚟 🚠 🚡 🛰️ 🚀 🛸 "
        "⌛ ⏳ ⌚ ⏰ ⏱️ ⏲️ 🕰️ 🕛 🕐 🕑 🕒 🕓 🕔 🕕 🕖 🕗 🕘 🕙 🕚 🌑 🌒 🌓 🌔 🌕 🌖 🌗 🌘 🌙 🌛 🌜 ⭐ 🌟 ✨"
    ),
    "活动": (
        "🎃 🎄 🎆 🎇 🧨 ✨ 🎈 🎉 🎊 🎋 🎍 🎎 🎏 🎐 🎑 🧧 🎀 🎁 🎗️ 🎟️ 🎫 🎖️ 🏆 🏅 🥇 🥈 🥉 "
        "⚽ ⚾ 🥎 🏀 🏐 🏈 🏉 🎾 🥏 🎳 🏏 🏑 🏒 🥍 🏓 🏸 🥊 🥋 🥅 ⛳ ⛸️ 🎣 🤿 🎽 🎿 🛷 🥌 🎯 🪀 🪁 🔫 🎱 🔮 🪄 🎮 🕹️ 🎰 🎲 🧩 🧸 🪅 🪩 🪆 ♠️ ♥️ ♦️ ♣️ ♟️ 🃏 🀄 🎴 "
        "🎭 🖼️ 🎨 🧵 🪡 🧶 🪢 👓 🕶️ 🥽 🥼 🦺 👔 👕 👖 🧣 🧤 🧥 🧦 👗 👘 🥻 🩱 🩲 🩳 👙 👚 🪭 👛 👜 👝 🛍️ 🎒 🩴 👞 👟 🥾 🥿 👠 👡 🩰 👢 🪮 👑 👒 🎩 🎓 🧢 🪖 ⛑️ 📿 💄 💍 💎"
    ),
    "物品": (
        "🔇 🔈 🔉 🔊 📢 📣 📯 🔔 🔕 🎼 🎵 🎶 🎙️ 🎚️ 🎛️ 🎤 🎧 📻 🎷 🪗 🎸 🎹 🎺 🎻 🪕 🥁 🪘 🪇 🪈 "
        "📱 📲 ☎️ 📞 📟 📠 🔋 🪫 🔌 💻 🖥️ 🖨️ ⌨️ 🖱️ 🖲️ 💽 💾 💿 📀 🧮 🎥 🎞️ 📽️ 🎬 📺 📷 📸 📹 📼 🔍 🔎 🕯️ 💡 🔦 🏮 🪔 "
        "📔 📕 📖 📗 📘 📙 📚 📓 📒 📃 📜 📄 📰 🗞️ 📑 🔖 🏷️ 💰 🪙 💴 💵 💶 💷 💸 💳 🧾 💹 ✉️ 📧 📨 📩 📤 📥 📦 📫 📪 📬 📭 📮 🗳️ "
        "✏️ ✒️ 🖋️ 🖊️ 🖌️ 🖍️ 📝 💼 📁 📂 🗂️ 📅 📆 🗒️ 🗓️ 📇 📈 📉 📊 📋 📌 📍 📎 🖇️ 📏 📐 ✂️ 🗃️ 🗄️ 🗑️ "
        "🔒 🔓 🔏 🔐 🔑 🗝️ 🔨 🪓 ⛏️ ⚒️ 🛠️ 🗡️ ⚔️ 💣 🪃 🏹 🛡️ 🪚 🔧 🪛 🔩 ⚙️ 🗜️ ⚖️ 🦯 🔗 ⛓️ 🪝 🧰 🧲 🪜 "
        "⚗️ 🧪 🧫 🧬 🔬 🔭 📡 💉 🩸 💊 🩹 🩼 🩺 🩻 🚪 🛗 🪞 🪟 🛏️ 🛋️ 🪑 🚽 🪠 🚿 🛁 🪤 🪒 🧴 🧷 🧹 🧺 🧻 🪣 🧼 🫧 🪥 🧽 🧯 🛒 🚬 ⚰️ 🪦 ⚱️ 🗿 🪧 🪪"
    ),
    "符号": (
        "🏧 🚮 🚰 ♿ 🚹 🚺 🚻 🚼 🚾 🛂 🛃 🛄 🛅 ⚠️ 🚸 ⛔ 🚫 🚳 🚭 🚯 🚱 🚷 📵 🔞 ☢️ ☣️ "
        "⬆️ ↗️ ➡️ ↘️ ⬇️ ↙️ ⬅️ ↖️ ↕️ ↔️ ↩️ ↪️ ⤴️ ⤵️ 🔃 🔄 🔙 🔚 🔛 🔜 🔝 🛐 ⚛️ 🕉️ ✡️ ☸️ ☯️ ✝️ ☦️ ☪️ ☮️ 🕎 🔯 ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ⛎ "
        "▶️ ⏩ ⏭️ ⏯️ ◀️ ⏪ ⏮️ 🔼 ⏫ 🔽 ⏬ ⏸️ ⏹️ ⏺️ ⏏️ 🎦 🔅 🔆 📶 🛜 📳 📴 ♀️ ♂️ ⚧️ ✖️ ➕ ➖ ➗ 🟰 ♾️ ‼️ ⁉️ ❓ ❔ ❕ ❗ 〰️ 💱 💲 "
        "⚕️ ♻️ ⚜️ 🔱 📛 🔰 ⭕ ✅ ☑️ ✔️ ❌ ❎ ➰ ➿ 〽️ ✳️ ✴️ ❇️ ©️ ®️ ™️ #️⃣ *️⃣ 0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟 🔠 🔡 🔢 🔣 🔤 🅰️ 🆎 🅱️ 🆑 🆒 🆓 ℹ️ 🆔 Ⓜ️ 🆕 🆖 🅾️ 🆗 🅿️ 🆘 🆙 🆚 🈁 🈂️ 🈷️ 🈶 🈯 🉐 🈹 🈚 🈲 🉑 🈸 🈴 🈳 ㊗️ ㊙️ 🈺 🈵 🔴 🟠 🟡 🟢 🔵 🟣 🟤 ⚫ ⚪ 🟥 🟧 🟨 🟩 🟦 🟪 🟫 ⬛ ⬜ ◼️ ◻️ ◾ ◽ ▪️ ▫️ 🔶 🔷 🔸 🔹 🔺 🔻 💠 🔘 🔳 🔲"
    ),
    "旗帜": (
        "🏁 🚩 🎌 🏴 🏳️ 🏳️‍🌈 🏳️‍⚧️ 🏴‍☠️ 🇨🇳 🇭🇰 🇲🇴 🇹🇼 🇯🇵 🇰🇷 🇸🇬 🇲🇾 🇹🇭 🇻🇳 🇮🇩 🇵🇭 🇮🇳 🇵🇰 🇧🇩 🇱🇰 🇳🇵 🇲🇳 "
        "🇺🇸 🇨🇦 🇲🇽 🇧🇷 🇦🇷 🇨🇱 🇨🇴 🇵🇪 🇨🇺 🇬🇧 🇫🇷 🇩🇪 🇮🇹 🇪🇸 🇵🇹 🇳🇱 🇧🇪 🇨🇭 🇦🇹 🇸🇪 🇳🇴 🇩🇰 🇫🇮 🇮🇸 🇮🇪 🇵🇱 🇨🇿 🇬🇷 🇷🇴 🇭🇺 🇺🇦 🇷🇺 🇹🇷 "
        "🇸🇦 🇦🇪 🇶🇦 🇮🇱 🇮🇷 🇮🇶 🇪🇬 🇿🇦 🇳🇬 🇰🇪 🇲🇦 🇦🇺 🇳🇿 🇺🇳"
    ),
}


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_github_repo(value):
    value = value.strip().rstrip("/")
    match = re.fullmatch(r"(?:https?://github\.com/)?([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?", value)
    if not match:
        raise ValueError("请填写仓库地址，例如：https://github.com/用户名/仓库名")
    return match.group(1), match.group(2)


def compare_versions(left, right):
    def parts(value):
        numbers = [int(item) for item in re.findall(r"\d+", value)]
        return tuple((numbers + [0, 0, 0])[:3])
    return (parts(left) > parts(right)) - (parts(left) < parts(right))


def github_request(url):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": f"AI-Letter-Translator/{APP_VERSION}",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def get_latest_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        return json.loads(github_request(url).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
        # GitHub 对“没有 Release”和“仓库不存在/无权访问”都返回 404，
        # 再检查一次仓库本身，给用户显示真正的原因。
        repo_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            github_request(repo_url)
        except urllib.error.HTTPError as repo_exc:
            if repo_exc.code == 404:
                raise ValueError(
                    "找不到这个 GitHub 仓库。请检查地址是否正确，并确认仓库是 Public（公开）。"
                ) from repo_exc
            raise
        raise ValueError(
            "仓库已经找到，但还没有已发布的 GitHub Release。请在仓库的 Releases 页面创建并发布版本，例如 v1.0.0。"
        ) from exc


def download_release(release):
    url = release.get("zipball_url")
    if not url:
        raise ValueError("这个 Release 没有可下载的源代码包。")
    APP_DIR.mkdir(parents=True, exist_ok=True)
    update_dir = Path(tempfile.mkdtemp(prefix="update-", dir=APP_DIR))
    archive = update_dir / "release.zip"
    archive.write_bytes(github_request(url))
    extracted = update_dir / "files"
    extracted.mkdir()
    with zipfile.ZipFile(archive) as package:
        root = extracted.resolve()
        for member in package.infolist():
            target = (extracted / member.filename).resolve()
            if root not in target.parents and target != root:
                raise ValueError("发布包包含不安全的文件路径，已停止更新。")
        package.extractall(extracted)
    candidates = list(extracted.rglob("main.py"))
    if not candidates:
        raise ValueError("发布包中没有找到 main.py，无法确认它是有效更新。")
    source_dir = candidates[0].parent
    if not (source_dir / "updater.py").exists():
        raise ValueError("发布包中没有 updater.py，更新包不完整。")
    return source_dir


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, current, on_save):
        super().__init__(parent)
        self.title("AI 接口设置")
        self.geometry("660x535")
        self.minsize(610, 500)
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save
        self.vars = {
            "base_url": tk.StringVar(value=current.get("base_url", "https://api.openai.com/v1")),
            "api_key": tk.StringVar(value=current.get("api_key", "")),
            "model": tk.StringVar(value=current.get("model", "gpt-4.1-mini")),
            "temperature": tk.StringVar(value=str(current.get("temperature", 0.2))),
            "timeout": tk.StringVar(value=str(current.get("timeout", 60))),
            "github_repo": tk.StringVar(value=current.get("github_repo", "")),
        }
        self.show_key = tk.BooleanVar(value=False)
        self._build()
        parent.apply_theme_to(self)

    def _build(self):
        body = ttk.Frame(self, padding=22)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="配置 OpenAI 兼容接口", font=("Microsoft YaHei UI", 15, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 18))
        labels = [("接口地址", "base_url"), ("API Key", "api_key"), ("模型名称", "model"),
                  ("Temperature", "temperature"), ("超时时间（秒）", "timeout"),
                  ("GitHub 更新仓库", "github_repo")]
        for row, (label, key) in enumerate(labels, 1):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=7)
            entry = ttk.Entry(body, textvariable=self.vars[key], width=48)
            if key == "api_key":
                entry.configure(show="●")
                self.key_entry = entry
            entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=7)
        ttk.Checkbutton(body, text="显示 API Key", variable=self.show_key,
                        command=lambda: self.key_entry.configure(show="" if self.show_key.get() else "●")).grid(
            row=7, column=1, sticky="w", pady=(0, 12))
        note = "提示：设置只保存在本机。接口地址可填写官方地址或其他 OpenAI 兼容服务地址。"
        ttk.Label(body, text=note, wraplength=520).grid(
            row=8, column=0, columnspan=3, sticky="w", pady=(6, 18))
        actions = ttk.Frame(body)
        actions.grid(row=9, column=0, columnspan=3, sticky="e")
        ttk.Button(actions, text="导入 JSON", command=self.import_json).pack(side="left", padx=5)
        ttk.Button(actions, text="测试连接", command=self.test_connection).pack(side="left", padx=5)
        ttk.Button(actions, text="检查更新", command=self.check_update).pack(side="left", padx=5)
        ttk.Button(actions, text="取消", command=self.destroy).pack(side="left", padx=5)
        ttk.Button(actions, text="保存", command=self.save).pack(side="left", padx=5)
        body.columnconfigure(1, weight=1)

    def values(self):
        try:
            temperature = float(self.vars["temperature"].get())
            timeout = int(self.vars["timeout"].get())
        except ValueError as exc:
            raise ValueError("Temperature 和超时时间必须是数字") from exc
        return {"base_url": self.vars["base_url"].get().strip().rstrip("/"),
                "api_key": self.vars["api_key"].get().strip(),
                "model": self.vars["model"].get().strip(),
                "temperature": temperature, "timeout": timeout,
                "github_repo": self.vars["github_repo"].get().strip()}

    def import_json(self):
        path = filedialog.askopenfilename(parent=self, filetypes=[("JSON 配置", "*.json")])
        if not path:
            return
        data = read_json(Path(path), {})
        aliases = {"baseURL": "base_url", "apiKey": "api_key"}
        for old, new in aliases.items():
            if old in data and new not in data:
                data[new] = data[old]
        for key, var in self.vars.items():
            if key in data:
                var.set(str(data[key]))

    def test_connection(self):
        try:
            config = self.values()
        except ValueError as exc:
            messagebox.showerror("设置有误", str(exc), parent=self)
            return
        if not all(config.get(k) for k in ("base_url", "api_key", "model")):
            messagebox.showwarning("信息不完整", "请填写接口地址、API Key 和模型名称。", parent=self)
            return
        self.config(cursor="watch")
        threading.Thread(target=self._test_worker, args=(config,), daemon=True).start()

    def _test_worker(self, config):
        try:
            call_ai(config, [{"role": "user", "content": "请只回复：连接成功"}], max_tokens=20)
            self.after(0, lambda: messagebox.showinfo("测试成功", "AI 接口连接成功。", parent=self))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("连接失败", friendly_error(exc), parent=self))
        finally:
            self.after(0, lambda: self.config(cursor=""))

    def save(self):
        try:
            config = self.values()
        except ValueError as exc:
            messagebox.showerror("设置有误", str(exc), parent=self)
            return
        self.on_save(config)
        self.destroy()

    def check_update(self):
        repo = self.vars["github_repo"].get().strip()
        try:
            owner, name = parse_github_repo(repo)
            self.on_save(self.values())
        except ValueError as exc:
            messagebox.showwarning("仓库地址有误", str(exc), parent=self)
            return
        self.config(cursor="watch")
        threading.Thread(target=self._update_worker, args=(owner, name), daemon=True).start()

    def _update_worker(self, owner, name):
        try:
            release = get_latest_release(owner, name)
            self.after(0, lambda: self._handle_release(release))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("检查更新失败", friendly_error(exc), parent=self))
        finally:
            self.after(0, lambda: self.config(cursor=""))

    def _handle_release(self, release):
        latest = release.get("tag_name", "").lstrip("vV")
        if not latest:
            messagebox.showerror("检查更新失败", "GitHub Release 没有有效的版本标签。", parent=self)
            return
        if compare_versions(latest, APP_VERSION) <= 0:
            messagebox.showinfo("已是最新版本", f"当前版本：v{APP_VERSION}\n最新版本：v{latest}", parent=self)
            return
        notes = (release.get("body") or "暂无更新说明").strip()
        if not messagebox.askyesno("发现新版本", f"当前版本：v{APP_VERSION}\n最新版本：v{latest}\n\n{notes[:500]}\n\n是否下载并安装？", parent=self):
            return
        self.config(cursor="watch")
        threading.Thread(target=self._download_worker, args=(release,), daemon=True).start()

    def _download_worker(self, release):
        try:
            source_dir = download_release(release)
            self.after(0, lambda: self._install_update(source_dir))
        except Exception as exc:
            self.after(0, lambda: messagebox.showerror("更新失败", friendly_error(exc), parent=self))
            self.after(0, lambda: self.config(cursor=""))

    def _install_update(self, source_dir):
        updater = Path(__file__).resolve().parent / "updater.py"
        if not updater.exists():
            messagebox.showerror("更新失败", "程序目录中缺少 updater.py。", parent=self)
            self.config(cursor="")
            return
        command = [sys.executable, str(updater), str(os.getpid()), str(source_dir),
                   str(Path(__file__).resolve().parent)]
        subprocess.Popen(command, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.destroy()


def call_ai(config, messages, max_tokens=12000):
    url = config["base_url"].rstrip("/") + "/chat/completions"
    request_data = {"model": config["model"], "messages": messages,
                    "temperature": config.get("temperature", 0.2),
                    "max_tokens": max_tokens}
    # DeepSeek V4 默认启用思考模式。翻译不需要推理过程，关闭它可避免长信的
    # 输出额度被 reasoning_content 用完，导致最终 content 为空。
    if "deepseek.com" in config["base_url"].lower():
        request_data["thinking"] = {"type": "disabled"}
    payload = json.dumps(request_data, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config["api_key"],
    })
    with urllib.request.urlopen(request, timeout=config.get("timeout", 60)) as response:
        result = json.loads(response.read().decode("utf-8"))
    choices = result.get("choices") or []
    if not choices:
        raise ValueError("接口没有返回任何翻译结果，请稍后重试。")
    choice = choices[0]
    message = choice.get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    content = (content or "").strip()
    if not content:
        finish_reason = choice.get("finish_reason", "未知")
        reasoning_tokens = (result.get("usage", {}).get("completion_tokens_details", {})
                            .get("reasoning_tokens", 0))
        if finish_reason == "length":
            raise ValueError("模型的输出长度已达到上限，没有生成最终译文。请缩短原文后重试。")
        if reasoning_tokens:
            raise ValueError("模型只返回了思考过程，没有生成最终译文，请重新翻译。")
        raise ValueError(f"接口返回了空译文（结束原因：{finish_reason}），请重新翻译。")
    return content


def friendly_error(exc):
    if isinstance(exc, urllib.error.HTTPError):
        try:
            data = json.loads(exc.read().decode("utf-8"))
            error = data.get("error") or {}
            detail = error.get("message") or data.get("message") or exc.reason or "未知错误"
        except Exception:
            detail = exc.reason or "未知错误"
        if exc.code == 403:
            return f"GitHub 拒绝了请求（403）：{detail}。请稍后重试，可能触发了访问频率限制。"
        return f"服务器返回错误 {exc.code}：{detail}"
    if isinstance(exc, urllib.error.URLError):
        return f"无法连接接口：{exc.reason}"
    detail = str(exc).strip()
    return f"请求失败：{detail or type(exc).__name__}"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(900, 620)
        self.settings = read_json(SETTINGS_FILE, {})
        self.theme = self.settings.get("theme", "light")
        self.events = queue.Queue()
        self.translating = False
        self.last_focused_text = None
        self.autosave_id = None
        self._style()
        self._build()
        self.apply_theme()
        self._load_draft()
        self.after(150, self._poll_events)
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _style(self):
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        self.style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=(10, 6))
        self.style.configure("TLabel", font=("Microsoft YaHei UI", 10))
        self.style.configure("Header.TLabel", font=("Microsoft YaHei UI", 18, "bold"))

    def _build(self):
        header = ttk.Frame(self, padding=(18, 14, 18, 10))
        header.pack(fill="x")
        ttk.Label(header, text="AI 写信翻译", style="Header.TLabel").pack(side="left")
        ttk.Button(header, text="⚙ 接口设置", command=self.open_settings).pack(side="right")
        ttk.Button(header, text="😊 Emoji", command=self.show_emoji).pack(side="right", padx=8)
        self.theme_button = ttk.Button(header, command=self.toggle_theme)
        self.theme_button.pack(side="right")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        self.write_tab = ttk.Frame(self.tabs, padding=12)
        self.incoming_tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(self.write_tab, text="  写信  ")
        self.tabs.add(self.incoming_tab, text="  翻译来信  ")
        self._build_write_tab()
        self._build_incoming_tab()

        self.status = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self, textvariable=self.status, padding=(16, 4))
        self.status_label.pack(fill="x")

    def _translation_bar(self, parent, command, allow_replace=False):
        bar = ttk.Frame(parent)
        ttk.Label(bar, text="翻译为").pack(side="left")
        target = ttk.Combobox(bar, values=LANGUAGES, state="readonly", width=14)
        target.set("简体中文" if parent is self.incoming_tab else "英语")
        target.pack(side="left", padx=(6, 14))
        ttk.Label(bar, text="风格").pack(side="left")
        tone = ttk.Combobox(bar, values=["自然", "正式", "礼貌"], state="readonly", width=9)
        tone.set("自然")
        tone.pack(side="left", padx=(6, 14))
        ttk.Button(bar, text="AI 翻译", command=lambda: command(target.get(), tone.get())).pack(side="left")
        if allow_replace:
            ttk.Button(bar, text="用译文替换原文", command=self.replace_letter).pack(side="left", padx=8)
        return bar

    def _text_panel(self, parent, title):
        frame = ttk.LabelFrame(parent, text=title, padding=8)
        text = tk.Text(frame, wrap="word", undo=True, font=("Microsoft YaHei UI", 11),
                       padx=10, pady=10, relief="flat")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        text.bind("<FocusIn>", lambda _e, widget=text: setattr(self, "last_focused_text", widget))
        return frame, text

    def _build_write_tab(self):
        meta = ttk.Frame(self.write_tab)
        meta.pack(fill="x", pady=(0, 8))
        ttk.Label(meta, text="标题").pack(side="left")
        self.subject = ttk.Entry(meta)
        self.subject.pack(side="left", fill="x", expand=True, padx=8)
        self.subject.bind("<KeyRelease>", self._schedule_save)
        ttk.Button(meta, text="打开文本", command=self.open_text_file).pack(side="left", padx=4)
        ttk.Button(meta, text="保存为 TXT", command=self.save_text_file).pack(side="left", padx=4)

        self._translation_bar(self.write_tab, self.translate_letter, allow_replace=True).pack(fill="x", pady=(0, 8))
        panes = ttk.Panedwindow(self.write_tab, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left, self.letter_text = self._text_panel(panes, "信件正文")
        right, self.letter_result = self._text_panel(panes, "AI 译文")
        panes.add(left, weight=1); panes.add(right, weight=1)
        self.letter_text.bind("<KeyRelease>", self._schedule_save)

    def _build_incoming_tab(self):
        top = self._translation_bar(self.incoming_tab, self.translate_incoming)
        top.pack(fill="x", pady=(0, 8))
        ttk.Button(top, text="粘贴剪贴板", command=self.paste_incoming).pack(side="left", padx=8)
        ttk.Button(top, text="导入 TXT/MD", command=self.open_incoming_file).pack(side="left")
        ttk.Button(top, text="复制译文", command=lambda: self.copy_text(self.incoming_result)).pack(side="right")
        panes = ttk.Panedwindow(self.incoming_tab, orient="horizontal")
        panes.pack(fill="both", expand=True)
        left, self.incoming_text = self._text_panel(panes, "收到的信件")
        right, self.incoming_result = self._text_panel(panes, "中文或目标语言译文")
        panes.add(left, weight=1); panes.add(right, weight=1)

    def open_settings(self):
        SettingsDialog(self, self.settings, self.save_settings)

    def save_settings(self, config):
        config["theme"] = self.theme
        self.settings = config
        write_json(SETTINGS_FILE, config)
        self.status.set("接口设置已保存在本机")

    def palette(self):
        if self.theme == "dark":
            return {"bg": "#17191c", "panel": "#22252a", "field": "#292d33",
                    "fg": "#f2f2f2", "muted": "#b6bbc3", "select": "#365f91",
                    "button": "#30343b", "border": "#454a52"}
        return {"bg": "#f4f5f7", "panel": "#ffffff", "field": "#ffffff",
                "fg": "#16181b", "muted": "#5f6368", "select": "#b9d7ff",
                "button": "#ffffff", "border": "#d6d9de"}

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.settings["theme"] = self.theme
        write_json(SETTINGS_FILE, self.settings)
        self.apply_theme()

    def apply_theme(self):
        self.apply_theme_to(self)
        self.theme_button.configure(text="☀ 浅色" if self.theme == "dark" else "🌙 深色")

    def apply_theme_to(self, window):
        colors = self.palette()
        try:
            window.configure(bg=colors["bg"])
        except tk.TclError:
            pass
        self.style.configure("TFrame", background=colors["bg"])
        self.style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("Header.TLabel", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
        self.style.configure("TButton", background=colors["button"], foreground=colors["fg"],
                             bordercolor=colors["border"])
        self.style.map("TButton", background=[("active", colors["select"]),
                                               ("pressed", colors["select"])])
        self.style.configure("TEntry", fieldbackground=colors["field"], foreground=colors["fg"],
                             insertcolor=colors["fg"])
        self.style.configure("TCombobox", fieldbackground=colors["field"], foreground=colors["fg"],
                             arrowcolor=colors["fg"])
        self.style.map("TCombobox", fieldbackground=[("readonly", colors["field"])],
                       foreground=[("readonly", colors["fg"])])
        self.style.configure("TNotebook", background=colors["bg"], bordercolor=colors["border"])
        self.style.configure("TNotebook.Tab", background=colors["button"], foreground=colors["fg"])
        self.style.map("TNotebook.Tab", background=[("selected", colors["panel"])])
        self.style.configure("Vertical.TScrollbar", background=colors["button"],
                             troughcolor=colors["bg"])
        if hasattr(self, "status_label"):
            self.status_label.configure(foreground=colors["muted"])

        def recolor(widget):
            if isinstance(widget, tk.Text):
                widget.configure(bg=colors["field"], fg=colors["fg"], insertbackground=colors["fg"],
                                 selectbackground=colors["select"], selectforeground=colors["fg"])
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=colors["bg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors["button"], fg=colors["fg"],
                                 activebackground=colors["select"], activeforeground=colors["fg"])
            for child in widget.winfo_children():
                recolor(child)
        recolor(window)

    def _translate(self, source_widget, result_widget, target, tone):
        if self.translating:
            messagebox.showinfo("正在翻译", "请等待当前翻译完成。")
            return
        try:
            selected = source_widget.get("sel.first", "sel.last").strip()
        except tk.TclError:
            selected = ""
        source = selected or source_widget.get("1.0", "end-1c").strip()
        if not source:
            messagebox.showwarning("没有内容", "请先输入或粘贴需要翻译的信件。")
            return
        if not all(self.settings.get(k) for k in ("base_url", "api_key", "model")):
            messagebox.showwarning("请配置接口", "首次使用前，请在“接口设置”中填写 AI 接口信息。")
            self.open_settings()
            return
        prompt = (f"你是一名专业书信翻译。请自动识别原文语言，并将下面的信件翻译成{target}。"
                  f"采用{tone}的表达风格，准确保留称呼、段落、语气、姓名和日期。"
                  "只输出译文，不要解释，也不要添加原文中不存在的信息。\n\n原文：\n" + source)
        self.translating = True
        self.status.set("AI 正在翻译…")
        threading.Thread(target=self._translate_worker,
                         args=(prompt, result_widget), daemon=True).start()

    def _translate_worker(self, prompt, result_widget):
        try:
            result = call_ai(self.settings, [{"role": "user", "content": prompt}])
            self.events.put(("success", result_widget, result))
        except Exception as exc:
            self.events.put(("error", friendly_error(exc)))

    def _poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                self.translating = False
                if event[0] == "success":
                    widget, result = event[1], event[2]
                    widget.delete("1.0", "end")
                    widget.insert("1.0", result)
                    self.status.set("翻译完成")
                else:
                    self.status.set("翻译失败")
                    messagebox.showerror("翻译失败", event[1])
        except queue.Empty:
            pass
        self.after(150, self._poll_events)

    def translate_letter(self, target, tone):
        self._translate(self.letter_text, self.letter_result, target, tone)

    def translate_incoming(self, target, tone):
        self._translate(self.incoming_text, self.incoming_result, target, tone)

    def replace_letter(self):
        result = self.letter_result.get("1.0", "end-1c").strip()
        if not result:
            messagebox.showwarning("没有译文", "请先完成翻译。")
            return
        self.letter_text.delete("1.0", "end")
        self.letter_text.insert("1.0", result)
        self._schedule_save()

    def show_emoji(self):
        popup = tk.Toplevel(self)
        popup.title("EmojiAll Emoji 列表")
        popup.geometry("620x520")
        popup.minsize(480, 400)

        toolbar = ttk.Frame(popup, padding=(12, 12, 12, 6))
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="分类").pack(side="left")
        category = ttk.Combobox(toolbar, values=list(EMOJI_GROUPS), state="readonly", width=16)
        category.set("热门")
        category.pack(side="left", padx=(6, 16))
        ttk.Label(toolbar, text="快速查找").pack(side="left")
        search = ttk.Entry(toolbar)
        search.pack(side="left", fill="x", expand=True, padx=(6, 0))

        outer = ttk.Frame(popup, padding=(12, 4, 12, 12))
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        grid = ttk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=grid, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def fit_grid(event):
            canvas.itemconfigure(window_id, width=event.width)

        def update_scroll(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def render(_event=None):
            for child in grid.winfo_children():
                child.destroy()
            selected = category.get()
            query = search.get().strip()
            if query:
                emojis = [emoji for values in EMOJI_GROUPS.values() for emoji in values.split()
                          if query in emoji]
            else:
                emojis = EMOJI_GROUPS[selected].split()
            # 去重，同时保留 EmojiAll/Unicode 的显示顺序。
            emojis = list(dict.fromkeys(emojis))
            columns = 10
            for index, emoji in enumerate(emojis):
                tk.Button(grid, text=emoji, font=("Segoe UI Emoji", 17), relief="flat",
                          width=3, height=1, cursor="hand2",
                          command=lambda value=emoji: self.insert_emoji(value)).grid(
                    row=index // columns, column=index % columns, padx=2, pady=2, sticky="nsew")
            for column in range(columns):
                grid.columnconfigure(column, weight=1)
            grid.update_idletasks()
            canvas.yview_moveto(0)
            update_scroll()

        canvas.bind("<Configure>", fit_grid)
        grid.bind("<Configure>", update_scroll)
        category.bind("<<ComboboxSelected>>", render)
        search.bind("<KeyRelease>", render)
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units"))
        popup.protocol("WM_DELETE_WINDOW", lambda: (canvas.unbind_all("<MouseWheel>"), popup.destroy()))
        render()
        self.apply_theme_to(popup)

    def insert_emoji(self, emoji):
        widget = self.last_focused_text or self.letter_text
        widget.insert("insert", emoji)
        widget.focus_set()
        self._schedule_save()

    def paste_incoming(self):
        try:
            value = self.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("剪贴板为空", "没有找到可粘贴的文字。")
            return
        self.incoming_text.delete("1.0", "end")
        self.incoming_text.insert("1.0", value)

    def open_text_file(self):
        self._open_file_into(self.letter_text)

    def open_incoming_file(self):
        self._open_file_into(self.incoming_text)

    def _open_file_into(self, widget):
        path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt *.md"), ("所有文件", "*.*")])
        if not path:
            return
        try:
            content = Path(path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = Path(path).read_text(encoding="gb18030")
        except OSError as exc:
            messagebox.showerror("无法打开", str(exc)); return
        widget.delete("1.0", "end"); widget.insert("1.0", content)

    def save_text_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("文本文件", "*.txt")])
        if path:
            try:
                Path(path).write_text(self.letter_text.get("1.0", "end-1c"), encoding="utf-8")
                self.status.set("信件已保存")
            except OSError as exc:
                messagebox.showerror("保存失败", str(exc))

    def copy_text(self, widget):
        value = widget.get("1.0", "end-1c")
        self.clipboard_clear(); self.clipboard_append(value)
        self.status.set("译文已复制")

    def _schedule_save(self, _event=None):
        if self.autosave_id:
            self.after_cancel(self.autosave_id)
        self.autosave_id = self.after(800, self._save_draft)

    def _save_draft(self):
        self.autosave_id = None
        write_json(DRAFT_FILE, {"subject": self.subject.get(),
                                "body": self.letter_text.get("1.0", "end-1c")})
        self.status.set("草稿已自动保存")

    def _load_draft(self):
        data = read_json(DRAFT_FILE, {})
        self.subject.insert(0, data.get("subject", ""))
        self.letter_text.insert("1.0", data.get("body", ""))
        self.last_focused_text = self.letter_text

    def _close(self):
        self._save_draft()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
