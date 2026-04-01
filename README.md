# bilibili-url2articles

给一个 B 站链接，自动提取音频、转为文字、再用 AI 生成精华文章。

## 效果

- 22 分钟视频 → GPU 识别约 3 分钟 → 1500 字精华文章
- 中文识别准确率高，支持各类免费 B 站视频

---

## 使用方式（.exe 版本）

### 第一步：获取豆包 API Key

1. 打开 [火山方舟控制台](https://console.volcengine.com/ark)
2. 注册/登录后，在左侧「API Key 管理」点击「创建 API Key」
3. 复制生成的 Key（格式类似 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

> 注册后有免费额度，日常使用完全够用

---

### 第二步：下载并运行

1. 下载最新 Release 中的压缩包，解压得到 `B站转文字/` 文件夹
2. 双击文件夹内的 **`B站转文字.exe`** 运行
3. 在界面底部「豆包 API Key 设置」输入框中粘贴你的 Key，点击「保存」

> Key 保存后下次打开自动读取，无需重复填写

---

### 第三步：开始使用

1. 在顶部输入框粘贴 B 站视频链接
2. 选择识别设备：
   - 有 NVIDIA 显卡 → 选 `cuda`（快，约 3~5 分钟）
   - 没有显卡 → 选 `cpu`（慢，约 30~45 分钟）
3. 勾选「完成后自动生成精华文章」
4. 点击「开始处理」

处理完成后，结果保存在 `B站转文字.exe` 同目录下：

```
B站转文字/
├── audio/          # 音频文件
├── transcripts/    # 原始逐字稿 .txt
└── articles/       # 精华文章 .md
```

点击「打开输出目录」按钮可直接跳转。

---

## 注意事项

- **首次运行**会自动下载 Whisper 语音识别模型（约 1.5GB），请保持网络畅通，之后不再重复下载
- **ffmpeg 已内置**，无需额外安装任何环境
- 大会员付费视频无法下载，普通免费视频均可
- 推荐使用 NVIDIA 显卡（GTX 1060 以上）加速识别

---

## 从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/xianzhouchao/bilibili-url2articles.git
cd bilibili-url2articles

# 2. 安装依赖
pip install faster-whisper yt-dlp openai python-dotenv

# 3. 配置 Key
cp .env.example .env
# 编辑 .env，填入 DOUBAO_API_KEY=你的Key

# 4. 运行（命令行）
python main.py https://www.bilibili.com/video/BVxxxxxx --device cuda
python summarizer.py transcripts/视频名.txt

# 或运行 GUI
python app.py
```

---

## 技术栈

| 模块 | 工具 |
|------|------|
| 音频下载 | yt-dlp |
| 语音识别 | faster-whisper (Whisper medium) |
| AI 总结 | 豆包 Doubao-Seed-2.0-lite |
| GUI | tkinter + PyInstaller |
