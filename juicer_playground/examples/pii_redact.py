"""pii_redact.py — PII redaction example: identify and redact sensitive personal info"""
import os
from openai import OpenAI

client = OpenAI(base_url=os.getenv("JUICER_BASE_URL", "http://localhost:8000/v1"), api_key="EMPTY")

PII_RECIPE = """Apply these operations exactly in order:
1. Remove or mask email addresses, phone numbers, street addresses, government IDs, and access tokens.
2. Keep non-sensitive surrounding content when it remains useful.
3. If the text is mostly sensitive credentials or private identifiers, return DROP."""

samples = [
    "张先生住在北京市朝阳区建国路88号，手机号是13812345678，可以联系他确认合同。",
    "Please contact Jane at jane.doe@company.com or call +1-415-555-0123.",
    "Password: MyS3cret! SSN: 123-45-6789 Card: 4111-1111-1111-1111",
]

for text in samples:
    prompt = (
        f"Task:\n{PII_RECIPE}\n\n"
        f"Raw input text:\n<input>\n{text}\n</input>\n\n"
        "Return tagged output only.\n"
        "Use exactly this format: <status>KEEP|DROP</status><clean_text>...</clean_text>\n"
    )
    resp = client.chat.completions.create(
        model=os.getenv("JUICER_MODEL", "juicer"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0, max_tokens=4096,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    print(f"Input:  {text}")
    print(f"Output: {resp.choices[0].message.content}\n")
