from leadhunter.ai.llm_client import LLMClient

client = LLMClient()

result = client.generate_json(
    system_prompt="Return JSON only.",
    user_prompt="Return a JSON object with one key called ok and value true.",
    max_output_tokens=300,
)

print("GEMINI JSON TEST:")
print(result)