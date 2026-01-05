from litellm import completion

from config import LLM_CONFIG
from log import logger


def get_response_by_llm(message, model_name: str = LLM_CONFIG.base_model):
    try:
        response = completion(
            model=LLM_CONFIG.provider + "/" + model_name,
            messages=[{"content": message, "role": "user"}],
            api_base=LLM_CONFIG.base_url,
            api_key=LLM_CONFIG.api_key,
        )
        return response.choices[0].message.content
    except ValueError as e:
        logger.error(f"LLM配置错误: {e}")
        raise
    except Exception as e:
        logger.exception(f"调用LLM失败: {e}")
        return None


if __name__ == "__main__":
    prompt = "你是谁？"
    response = get_response_by_llm(prompt)
    logger.debug(response)
