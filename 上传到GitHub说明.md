# 上传和发布更新

## 一、首次上传

1. 登录 GitHub，点击右上角 `+`，选择 `New repository`。
2. 仓库名可填写 `ai-letter-translator`，可见性选择 `Public`。
3. 不要勾选自动创建 README、`.gitignore` 或 License，然后创建仓库。
4. 在本项目文件夹空白处按住 Shift 点击鼠标右键，选择“在终端中打开”。
5. 依次运行以下命令，把 `你的用户名` 替换成自己的 GitHub 用户名：

```powershell
git init
git add .
git commit -m "发布 v1.0.0"
git branch -M main
git remote add origin https://github.com/你的用户名/ai-letter-translator.git
git push -u origin main
```

GitHub 不再接受账户密码进行 Git 推送。登录提示出现时，请使用浏览器登录、Git Credential Manager 或 Personal Access Token。

## 二、创建第一个可更新版本

1. 打开 GitHub 仓库页面。
2. 点击右侧 `Releases`，再点击 `Draft a new release`。
3. 在 `Choose a tag` 中输入 `v1.0.0`，选择创建新标签。
4. 标题填写 `v1.0.0`，说明中填写本次功能。
5. 点击 `Publish release`。
6. 打开软件的“接口设置”，在“GitHub 更新仓库”填写完整仓库地址并保存。

## 三、以后发布新版本

假设要发布 `v1.1.0`：

1. 修改 `main.py` 顶部的版本：

```python
APP_VERSION = "1.1.0"
```

2. 保存代码后，在项目目录运行：

```powershell
git add .
git commit -m "发布 v1.1.0"
git push
```

3. 在 GitHub 的 Releases 页面创建并发布标签 `v1.1.0`。
4. 旧版软件点击“检查更新”后即可发现、下载并安装这个版本。

版本标签必须高于旧版，并建议使用 `v主版本.次版本.修订版本`，例如 `v1.0.1`、`v1.1.0`、`v2.0.0`。

## 注意事项

- 自动更新目前支持公开 GitHub 仓库。
- 不要把 API Key 写入项目文件或上传到 GitHub。
- API Key 和草稿保存在 Windows 的 `%LOCALAPPDATA%\AI写信翻译`，不在项目目录中。
- 发布 Release 前先在本机启动并测试程序。
