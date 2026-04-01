"""
output.py - 将识别结果输出为不同格式
支持：纯文本 .txt、字幕 .srt、结构化 .json
"""

import json
import os


def _format_srt_time(seconds: float) -> str:
    """将秒数转为 SRT 时间格式：00:00:00,000"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save_txt(segments: list[dict], output_path: str) -> str:
    """
    输出纯文本，每段一行。

    :param segments: transcribe() 返回的分段列表
    :param output_path: 输出文件路径（.txt）
    :return: 实际写入的文件路径
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(seg["text"] + "\n")
    print(f"[output] TXT 已保存: {output_path}")
    return output_path


def save_srt(segments: list[dict], output_path: str) -> str:
    """
    输出 SRT 字幕文件，带时间戳，可直接导入视频播放器。

    :param segments: transcribe() 返回的分段列表
    :param output_path: 输出文件路径（.srt）
    :return: 实际写入的文件路径
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            f.write(f"{i}\n")
            f.write(f"{_format_srt_time(seg['start'])} --> {_format_srt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
    print(f"[output] SRT 已保存: {output_path}")
    return output_path


def save_json(segments: list[dict], output_path: str) -> str:
    """
    输出 JSON 文件，保留完整时间戳信息，便于二次处理。

    :param segments: transcribe() 返回的分段列表
    :param output_path: 输出文件路径（.json）
    :return: 实际写入的文件路径
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"[output] JSON 已保存: {output_path}")
    return output_path


def save_all(segments: list[dict], base_path: str) -> dict:
    """
    一次性输出全部三种格式，base_path 不含扩展名。

    :param segments: transcribe() 返回的分段列表
    :param base_path: 输出文件基础路径，如 "output/result"
    :return: {"txt": ..., "srt": ..., "json": ...}
    """
    return {
        "txt":  save_txt(segments,  base_path + ".txt"),
        "srt":  save_srt(segments,  base_path + ".srt"),
        "json": save_json(segments, base_path + ".json"),
    }


if __name__ == "__main__":
    # 用假数据测试格式是否正确
    test_segments = [
        {"start": 0.0,  "end": 3.06, "text": "大家好，欢迎来到本期视频"},
        {"start": 3.06, "end": 8.44, "text": "今天我们来聊一聊快速调研的方法"},
        {"start": 8.44, "end": 11.78, "text": "首先我们需要明确调研的目标"},
    ]

    paths = save_all(test_segments, "output/test")
    print("\n生成文件：")
    for fmt, path in paths.items():
        print(f"  {fmt}: {path}")

    # 预览 SRT 内容
    print("\n--- SRT 预览 ---")
    with open(paths["srt"], encoding="utf-8") as f:
        print(f.read())
