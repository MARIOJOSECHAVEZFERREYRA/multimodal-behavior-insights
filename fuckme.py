from openai import OpenAI
import os

API_KEY = "AQ.Ab8RN6KqHJQ1xqqOzHlErmXaRYd04J1-sKzoG_FRW6ZBl1hjUQ"

# Common Chinese OpenAI-compatible providers and their default models
endpoints = [
    ("ZhipuAI (GLM)", "https://open.bigmodel.cn/api/paas/v4/", "glm-4-flash"),
    ("Moonshot (Kimi)", "https://api.moonshot.cn/v1", "moonshot-v1-8k"),
    ("Alibaba Qwen (DashScope)", "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-turbo"),
    ("01.AI (Yi)", "https://api.lingyiwanwu.com/v1", "yi-large"),
    ("DeepSeek (retry)", "https://api.deepseek.com/v1", "deepseek-chat"),
    ("StepFun", "https://api.stepfun.com/v1", "step-1-8k"),
    ("Minimax", "https://api.minimax.chat/v1", "abab6.5s-chat"),
    ("Tencent Hunyuan", "https://api.hunyuan.cloud.tencent.com/v1", "hunyuan-lite"),
]

for name, base_url, model in endpoints:
    try:
        client = OpenAI(api_key=API_KEY, base_url=base_url)
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
        )
        print(f"✅ SUCCESS with {name} | base_url: {base_url} | model: {model}")
        print("Response:", r.choices[0].message.content)
        break
    except Exception as e:
        print(f"❌ {name} failed: {e}")