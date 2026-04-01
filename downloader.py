"""
downloader.py - 从 B 站下载音频
"""

import os
import sys
import yt_dlp


def _get_ffmpeg_path() -> str:
    """打包成 exe 后优先使用同目录的 ffmpeg.exe，否则用系统 PATH"""
    if getattr(sys, "frozen", False):
        candidate = os.path.join(os.path.dirname(sys.executable), "ffmpeg.exe")
        if os.path.isfile(candidate):
            return candidate
    return "ffmpeg"


def download_audio(url: str, output_dir: str = "downloads") -> str:
    """
    下载 B 站视频的音频，返回音频文件路径。

    :param url: B 站视频链接
    :param output_dir: 音频保存目录
    :return: 下载后的音频文件路径
    """
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "ffmpeg_location": _get_ffmpeg_path(),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
        # 伪装浏览器 UA，避免被 B 站拦截
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "audio")
        # yt-dlp 转码后扩展名变为 wav
        audio_path = os.path.join(output_dir, f"{title}.wav")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"音频文件未找到: {audio_path}")

    print(f"[downloader] 下载完成: {audio_path}")
    return audio_path


if __name__ == "__main__":
    # 简单测试：替换为真实 B 站链接
    test_url = input("请输入 B 站视频链接: ").strip()
    path = download_audio(test_url)
    print(f"音频路径: {path}")
