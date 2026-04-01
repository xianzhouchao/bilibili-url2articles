"""
summarizer.py - 用豆包 API 将逐字稿重构为精华文章
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "doubao-seed-2-0-lite-260215"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

PROMPT_TEMPLATE = """你是一位专业的内容编辑，擅长将视频逐字稿重构为高质量的精华文章。

【任务】
将下面这份口语化的视频逐字稿，重构为一篇结构严谨、细节丰满的精华文章。

【要求】
1. **保留所有核心观点和关键细节**，不得遗漏重要信息
2. **去除口语化废话**：语气词、重复表达、过渡性寒暄等
3. **重构逻辑结构**：按主题分段，每段有清晰的小标题（Markdown 格式）
4. **保持原作者的核心立场和观点**，不要加入自己的判断
5. **字数控制在 1000~1500 字**，宁可详细也不要过度压缩
6. **语言风格**：书面化但不刻板，读起来流畅自然
7. 输出格式：Markdown，包含标题、各级小标题、正文段落

【逐字稿原文】
{transcript}

【输出精华文章】
"""


def summarize(txt_path: str, output_path: str = None) -> str:
    """
    读取 txt 逐字稿，调用豆包生成精华文章。

    :param txt_path: 逐字稿 txt 文件路径
    :param output_path: 输出 md 文件路径，默认与 txt 同目录同名加"_精华"
    :return: 输出文件路径
    """
    api_key = os.getenv("DOUBAO_API_KEY")
    if not api_key:
        raise ValueError("未找到 DOUBAO_API_KEY，请检查 .env 文件")

    with open(txt_path, encoding="utf-8") as f:
        transcript = f.read()

    print(f"[summarizer] 逐字稿字数: {len(transcript)} 字")
    print(f"[summarizer] 使用模型: {MODEL}")
    print("[summarizer] 正在生成精华文章，请稍候...")

    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": PROMPT_TEMPLATE.format(transcript=transcript)}
        ],
        temperature=0.4,
        max_tokens=4096,
    )
    article = response.choices[0].message.content

    if output_path is None:
        # 默认存到同级 articles/ 目录
        base_name = os.path.splitext(os.path.basename(txt_path))[0]
        articles_dir = os.path.join(os.path.dirname(os.path.dirname(txt_path)), "articles")
        os.makedirs(articles_dir, exist_ok=True)
        output_path = os.path.join(articles_dir, base_name + "_精华.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"[summarizer] 完成！输出: {output_path}")
    print(f"[summarizer] 文章字数: {len(article)} 字")
    return output_path


if __name__ == "__main__":
    txt = sys.argv[1] if len(sys.argv) > 1 else input("请输入逐字稿 txt 文件路径: ").strip()
    out = summarize(txt)

    print("\n--- 文章预览（前500字）---")
    with open(out, encoding="utf-8") as f:
        print(f.read()[:500])
    print("...")
