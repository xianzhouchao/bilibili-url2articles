# B站视频文本提取 & 总结

给一个 B 站链接，自动提取音频、转为文字、再用 AI 生成精华文章。

## 效果

- 22 分钟视频 → GPU 识别约 3 分钟 → 1500 字精华文章
- 中文识别准确率高，支持各类 B 站视频

---

## 使用方式（.exe 版本）

### 第一步：环境准备

**1. 安装 ffmpeg**

下载地址：https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip

解压后把 `bin/` 文件夹路径加入系统环境变量 PATH，重启终端后执行：
```
ffmpeg -version
```
看到版本号即安装成功。

**2. 获取豆包 API Key**

1. 打开 [火山方舟控制台](https://console.volcengine.com/ark)
2. 注册/登录后，在「API Key 管理」创建一个 Key
3. 记下这个 Key，下一步会用到

---

### 第二步：配置 API Key

在 `B站转文字.exe` 同目录下，找到 `.env.example` 文件，复制一份并重命名为 `.env`，填入你的 Key：

```
DOUBAO_API_KEY=你的豆包APIKey
```

> ⚠️ `.env` 文件包含你的私钥，不要分享给别人

---

### 第三步：运行

双击 `B站转文字.exe`，在界面中：

1. 粘贴 B 站视频链接
2. 选择识别设备（有 N 卡选 `cuda`，没有选 `cpu`）
3. 勾选「完成后自动生成精华文章」
4. 点击「开始处理」

处理完成后，结果文件保存在 exe 同目录下：

```
B站转文字/
├── audio/          # 音频文件
├── transcripts/    # 原始逐字稿 .txt
└── articles/       # 精华文章 .md
```

点击「打开输出目录」按钮可以直接跳转到该文件夹。

---

## 注意事项

- **首次运行**会自动下载 Whisper 模型（约 1.5GB），请保持网络畅通，之后不再重复下载
- **大会员视频**无法下载，普通免费视频均可
- CPU 模式下，识别速度约为实时的 1/3，20 分钟视频需要约 40 分钟；GPU 模式约 3~5 分钟
- 推荐使用 NVIDIA 显卡（GTX 1060 以上）

---

## 从源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/xianzhouchao/bilibili视频文本提取-总结.git
cd bilibili视频文本提取-总结

# 2. 安装依赖
pip install faster-whisper yt-dlp openai python-dotenv

# 3. 配置 Key
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 4. 运行
python main.py https://www.bilibili.com/video/BVxxxxxx --device cuda
python summarizer.py transcripts/视频名.txt
```

---

## 技术栈

| 模块 | 工具 |
|------|------|
| 音频下载 | yt-dlp |
| 语音识别 | faster-whisper (Whisper medium) |
| AI 总结 | 豆包 Doubao-Seed-2.0-lite |
| GUI | tkinter + PyInstaller |
