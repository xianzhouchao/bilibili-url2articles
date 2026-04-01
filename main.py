"""
main.py - 入口：输入 B 站链接，输出转录文本
用法：
    python main.py <url> [选项]
    python main.py https://www.bilibili.com/video/BVxxxxxx
    python main.py https://www.bilibili.com/video/BVxxxxxx --model small --format srt
"""

import argparse
import os
import re

from downloader import download_audio
from transcriber import transcribe
from output import save_txt, save_srt, save_json, save_all


def slugify(title: str) -> str:
    """将视频标题转为合法文件名"""
    title = re.sub(r'[\\/:*?"<>|]', "_", title)
    return title.strip()[:50]  # 限制长度


def run(url: str, model: str, device: str, fmt: str, base_dir: str):
    audio_dir      = os.path.join(base_dir, "audio")
    transcript_dir = os.path.join(base_dir, "transcripts")

    print("=" * 50)
    print(f"URL    : {url}")
    print(f"模型   : {model}  设备: {device}")
    print(f"输出   : {fmt}")
    print("=" * 50)

    # Step 1: 下载音频
    print("\n[1/3] 下载音频...")
    audio_path = download_audio(url, output_dir=audio_dir)

    # Step 2: 语音识别
    print("\n[2/3] 语音识别...")
    segments = transcribe(audio_path, model_size=model, device=device)

    # Step 3: 保存结果
    print("\n[3/3] 保存结果...")
    base_name = slugify(os.path.splitext(os.path.basename(audio_path))[0])
    base_path = os.path.join(transcript_dir, base_name)

    if fmt == "all":
        paths = save_all(segments, base_path)
        saved = list(paths.values())
    elif fmt == "txt":
        saved = [save_txt(segments, base_path + ".txt")]
    elif fmt == "srt":
        saved = [save_srt(segments, base_path + ".srt")]
    elif fmt == "json":
        saved = [save_json(segments, base_path + ".json")]

    print("\n完成！生成文件：")
    for p in saved:
        print(f"  -> {os.path.abspath(p)}")


def main():
    parser = argparse.ArgumentParser(description="B 站视频语音转文字")
    parser.add_argument("url", help="B 站视频链接")
    parser.add_argument(
        "--model", default="medium",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper 模型大小（默认 medium，中文推荐 medium 或 large-v3）"
    )
    parser.add_argument(
        "--device", default="cpu", choices=["cpu", "cuda"],
        help="运行设备（有 GPU 时用 cuda 更快）"
    )
    parser.add_argument(
        "--format", default="txt", choices=["txt", "srt", "json", "all"],
        dest="fmt", help="输出格式（默认 txt）"
    )
    parser.add_argument(
        "--out", default=".",
        help="项目根目录（默认当前目录，下含 audio/ transcripts/）"
    )
    args = parser.parse_args()
    run(args.url, args.model, args.device, args.fmt, args.out)


if __name__ == "__main__":
    main()
