"""single_clean.py — Minimal Juicer call example: single-text cleaning"""
import os
from openai import OpenAI

client = OpenAI(base_url=os.getenv("JUICER_BASE_URL", "http://localhost:8000/v1"), api_key="EMPTY")

prompt = """Task:
Apply these operations exactly in order:
1. Remove email addresses.
2. Remove duplicate sentences, keeping the first occurrence.
3. Normalize whitespace.

Raw input text:
<input>
Contact ops@example.com for help. Contact ops@example.com for help.   Service is available.
</input>
Return tagged output only.
Use exactly this format: <status>KEEP|DROP</status><clean_text>...</clean_text>
"""

resp = client.chat.completions.create(
    model=os.getenv("JUICER_MODEL", "juicer"),
    messages=[{"role": "user", "content": prompt}],
    temperature=0, max_tokens=4096,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)
print(resp.choices[0].message.content)
