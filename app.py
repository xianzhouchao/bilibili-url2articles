"""
app.py - B站视频转文字 GUI
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 确保能找到同目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from downloader import download_audio
from transcriber import transcribe
from output import save_txt
from summarizer import summarize


# 打包成 exe 后，__file__ 在 _internal 里；用 exe 所在目录作为根目录
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("B站视频转文字")
        self.resizable(False, False)
        self._build_ui()
        self._running = False

    # ------------------------------------------------------------------ UI --

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        # URL 输入
        frm_url = ttk.LabelFrame(self, text="B站视频链接")
        frm_url.pack(fill="x", **pad)
        self.url_var = tk.StringVar()
        ttk.Entry(frm_url, textvariable=self.url_var, width=60).pack(
            fill="x", padx=8, pady=6
        )

        # 选项行
        frm_opt = ttk.LabelFrame(self, text="选项")
        frm_opt.pack(fill="x", **pad)

        ttk.Label(frm_opt, text="识别设备:").grid(row=0, column=0, padx=8, pady=4, sticky="w")
        self.device_var = tk.StringVar(value="cuda")
        ttk.Combobox(
            frm_opt, textvariable=self.device_var,
            values=["cuda", "cpu"], width=8, state="readonly"
        ).grid(row=0, column=1, padx=4, pady=4, sticky="w")

        ttk.Label(frm_opt, text="模型:").grid(row=0, column=2, padx=8, pady=4, sticky="w")
        self.model_var = tk.StringVar(value="medium")
        ttk.Combobox(
            frm_opt, textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large-v3"], width=10, state="readonly"
        ).grid(row=0, column=3, padx=4, pady=4, sticky="w")

        self.summarize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frm_opt, text="完成后自动生成精华文章", variable=self.summarize_var
        ).grid(row=0, column=4, padx=16, pady=4, sticky="w")

        # 按钮行
        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill="x", padx=12, pady=4)

        self.btn_run = ttk.Button(frm_btn, text="开始处理", command=self._on_run, width=16)
        self.btn_run.pack(side="left", padx=4)

        ttk.Button(frm_btn, text="打开输出目录", command=self._open_dir, width=16).pack(
            side="left", padx=4
        )

        self.progress = ttk.Progressbar(frm_btn, mode="indeterminate", length=200)
        self.progress.pack(side="right", padx=4)

        # 日志输出
        frm_log = ttk.LabelFrame(self, text="运行日志")
        frm_log.pack(fill="both", expand=True, **pad)
        self.log = scrolledtext.ScrolledText(
            frm_log, width=72, height=18, state="disabled",
            font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white"
        )
        self.log.pack(fill="both", expand=True, padx=6, pady=6)

        # API Key 设置
        frm_key = ttk.LabelFrame(self, text="豆包 API Key 设置")
        frm_key.pack(fill="x", padx=12, pady=(0, 8))
        self.key_var = tk.StringVar(value=self._load_api_key())
        ttk.Entry(frm_key, textvariable=self.key_var, width=52, show="*").pack(
            side="left", padx=8, pady=6
        )
        ttk.Button(frm_key, text="保存", command=self._save_api_key, width=8).pack(
            side="left", padx=4
        )

    # --------------------------------------------------------------- 事件 ---

    def _on_run(self):
        url = self.url_var.get().strip()
        if not url:
            self._log("请先输入 B站视频链接\n", color="red")
            return
        if self._running:
            return
        self._running = True
        self.btn_run.config(state="disabled")
        self.progress.start(10)
        threading.Thread(target=self._run_pipeline, args=(url,), daemon=True).start()

    def _run_pipeline(self, url: str):
        try:
            audio_dir      = os.path.join(BASE_DIR, "audio")
            transcript_dir = os.path.join(BASE_DIR, "transcripts")

            # Step 1
            self._log("【1/3】下载音频...\n", color="cyan")
            audio_path = download_audio(url, output_dir=audio_dir)
            self._log(f"  音频: {audio_path}\n")

            # Step 2
            self._log("【2/3】语音识别（GPU 约 3~5 分钟）...\n", color="cyan")
            segments = transcribe(
                audio_path,
                model_size=self.model_var.get(),
                device=self.device_var.get(),
            )
            import re
            base_name = re.sub(r'[\\/:*?"<>|]', "_", os.path.splitext(os.path.basename(audio_path))[0])[:50]
            txt_path = os.path.join(transcript_dir, base_name + ".txt")
            save_txt(segments, txt_path)
            self._log(f"  逐字稿: {txt_path}\n")

            # Step 3（可选）
            if self.summarize_var.get():
                self._log("【3/3】生成精华文章...\n", color="cyan")
                md_path = summarize(txt_path)
                self._log(f"  精华文章: {md_path}\n")

            self._log("\n全部完成！\n", color="green")

        except Exception as e:
            self._log(f"\n错误: {e}\n", color="red")
        finally:
            self._running = False
            self.after(0, self._on_done)

    def _on_done(self):
        self.progress.stop()
        self.btn_run.config(state="normal")

    def _open_dir(self):
        os.startfile(BASE_DIR)

    def _env_path(self):
        return os.path.join(BASE_DIR, ".env")

    def _load_api_key(self) -> str:
        env = self._env_path()
        if os.path.isfile(env):
            for line in open(env, encoding="utf-8"):
                if line.startswith("DOUBAO_API_KEY="):
                    return line.strip().split("=", 1)[1]
        return ""

    def _save_api_key(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("提示", "API Key 不能为空")
            return
        env = self._env_path()
        # 读取现有内容，更新或追加 DOUBAO_API_KEY
        lines = []
        found = False
        if os.path.isfile(env):
            for line in open(env, encoding="utf-8"):
                if line.startswith("DOUBAO_API_KEY="):
                    lines.append(f"DOUBAO_API_KEY={key}\n")
                    found = True
                else:
                    lines.append(line)
        if not found:
            lines.append(f"DOUBAO_API_KEY={key}\n")
        with open(env, "w", encoding="utf-8") as f:
            f.writelines(lines)
        messagebox.showinfo("已保存", "API Key 保存成功")

    def _log(self, msg: str, color: str = "white"):
        color_map = {
            "white": "#d4d4d4",
            "cyan":  "#4ec9b0",
            "green": "#6a9955",
            "red":   "#f44747",
        }
        tag = color
        self.log.config(state="normal")
        self.log.tag_config(tag, foreground=color_map.get(color, "#d4d4d4"))
        self.log.insert("end", msg, tag)
        self.log.see("end")
        self.log.config(state="disabled")
        self.update_idletasks()


if __name__ == "__main__":
    app = App()
    app.mainloop()
