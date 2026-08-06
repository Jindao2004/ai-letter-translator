# AI 写信翻译

一款本地运行的写信与来信翻译工具，支持 Emoji 和用户自定义 OpenAI 兼容接口。

## 快速启动

在 Windows 中双击 `启动写信翻译.vbs`（无黑色窗口）或 `start.bat`。需要预先安装 Python 3，程序不依赖第三方库。

也可以在项目目录运行：

```powershell
python main.py
```

## 首次使用

1. 点击右上角“接口设置”。
2. 填写 OpenAI 兼容接口地址、API Key 和模型名称。
3. 点击“测试连接”，成功后保存。
4. 在“写信”或“翻译来信”页面输入内容并点击“AI 翻译”。

接口配置和自动保存的草稿位于 Windows 当前用户的本地应用数据目录，不会上传到本项目或开发者服务器。

## 从 GitHub 更新

在“接口设置”的“GitHub 更新仓库”中填写公开仓库地址，例如
`https://github.com/your-name/ai-letter-translator`，然后点击“检查更新”。程序读取该仓库最新的 GitHub Release；其版本标签高于当前版本时，可以下载、安装并自动重启。

发布新版本前，需要修改 `main.py` 顶部的 `APP_VERSION`，并在 GitHub 创建相同版本号的 Release，例如 `v1.1.0`。
