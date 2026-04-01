"""
transcriber.py - 使用 faster-whisper 将音频转为文字
"""

import os
import site

# 使用国内镜像下载 Whisper 模型，解决 HuggingFace 访问超时问题
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from faster_whisper import WhisperModel

# 自动把 nvidia CUDA 运行库路径加入 PATH（Windows 下 GPU 推理需要）
def _add_cuda_paths():
    import os
    for p in site.getsitepackages():
        nvidia_bin = os.path.join(p, "nvidia", "cublas", "bin")
        if os.path.isdir(nvidia_bin) and nvidia_bin not in os.environ.get("PATH", ""):
            os.environ["PATH"] = nvidia_bin + os.pathsep + os.environ.get("PATH", "")
        cudnn_bin = os.path.join(p, "nvidia", "cudnn", "bin")
        if os.path.isdir(cudnn_bin) and cudnn_bin not in os.environ.get("PATH", ""):
            os.environ["PATH"] = cudnn_bin + os.pathsep + os.environ.get("PATH", "")

_add_cuda_paths()


def transcribe(audio_path: str, model_size: str = "medium", device: str = "cpu") -> list[dict]:
    """
    对音频文件进行语音识别，返回分段文本列表。

    :param audio_path: WAV 音频文件路径
    :param model_size: 模型大小，可选 tiny / base / small / medium / large-v3
    :param device: 运行设备，cpu 或 cuda（有 GPU 时用 cuda 更快）
    :return: [{"start": 0.0, "end": 3.5, "text": "..."}, ...]
    """
    print(f"[transcriber] 加载模型: {model_size}  设备: {device}")
    print("[transcriber] 首次运行会自动下载模型，请耐心等待...")

    compute_type = "float16" if device == "cuda" else "int8"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"[transcriber] 开始识别: {audio_path}")
    segments, info = model.transcribe(
        audio_path,
        language="zh",          # 指定中文，跳过语言检测，更快更准
        beam_size=5,
        vad_filter=True,        # 开启静音过滤，跳过无声片段
        vad_parameters={"min_silence_duration_ms": 500},
    )

    print(f"[transcriber] 检测语言: {info.language}  时长: {info.duration:.1f}s")

    results = []
    for seg in segments:
        results.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })
        print(f"  [{seg.start:6.2f}s -> {seg.end:6.2f}s] {seg.text.strip()}")

    print(f"[transcriber] 识别完成，共 {len(results)} 段")
    return results


if __name__ == "__main__":
    import sys
    audio = sys.argv[1] if len(sys.argv) > 1 else input("请输入 WAV 文件路径: ").strip()
    transcribe(audio)
