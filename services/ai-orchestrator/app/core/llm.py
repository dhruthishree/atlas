from typing import Tuple
from google import genai
from google.genai import types
from app.core.config import settings

def calculate_token_cost(in_tokens: int, out_tokens: int) -> float:
    c_in = (in_tokens / 1_000_000.0) * settings.COST_PER_1M_INPUT_TOKENS
    c_out = (out_tokens / 1_000_000.0) * settings.COST_PER_1M_OUTPUT_TOKENS
    return round(c_in + c_out, 6)

class GeminiService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            self.client = None

    def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, int, int]:
        if not self.client:
            # Deterministic fallback reasoning for testing
            if "SQL Query Agent" in system_prompt:
                return "SELECT department, allocated_budget, actual_spend FROM budgets WHERE actual_spend > allocated_budget;", 40, 20
            elif "Query Planning Agent" in system_prompt:
                return '{"requires_sql": true, "requires_docs": true, "reasoning": "Question asks for numerical budget variance and documented narrative reasons."}', 60, 25
            elif "Answer Generation Agent" in system_prompt:
                return "Based on Q3 financial records, Engineering and Marketing exceeded their allocated budgets. Engineering's $140,000 variance was driven by accelerated cloud migration and redundant database cutovers [1], while Marketing's $120,000 variance was caused by international ad campaigns [2].", 120, 35
            return "Simulated response with evidence [1].", 50, 20

        try:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                max_output_tokens=2048
            )
            response = self.client.models.generate_content(
                model=settings.GENERATION_MODEL,
                contents=user_prompt,
                config=config
            )
            text = response.text or ""
            in_tokens = 0
            out_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                in_tokens = response.usage_metadata.prompt_token_count or 0
                out_tokens = response.usage_metadata.candidates_token_count or 0
            else:
                in_tokens = (len(system_prompt) + len(user_prompt)) // 4
                out_tokens = len(text) // 4
            return text, in_tokens, out_tokens
        except Exception as e:
            return f"Error executing model: {str(e)}", 0, 0
