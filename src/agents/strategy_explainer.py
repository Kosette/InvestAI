from config import LLM_CONFIG, STRATEGY_CONFIG
from utils.json import to_pretty_json

from .llm import get_response_by_llm
from .prompts.helper import get_prompt_from_template


def explain_strategy(current_strategy: dict):
    prompt = get_prompt_from_template(
        "strategy_explainer.md", {"current_strategy": to_pretty_json(current_strategy)}
    )
    response = get_response_by_llm(prompt, model_name=LLM_CONFIG.base_model)
    return response


if __name__ == "__main__":
    print(explain_strategy(STRATEGY_CONFIG))
