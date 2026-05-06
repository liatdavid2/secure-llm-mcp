from __future__ import annotations

import json

from secure_llm_mcp.gateway_client import gateway_health, run_chat
from secure_llm_mcp.settings import settings


def main() -> None:
    print("Gateway base URL:", settings.gateway_base_url)
    print("Health check:")
    print(json.dumps(gateway_health(), indent=2, ensure_ascii=False))

    payload = {
        "prompt": "Explain prompt injection in one short paragraph.",
        "model_name": settings.default_model_name,
        "temperature": 0.0,
        "max_tokens": 80,
        "disabled_steps": [],
        "prompt_injection_threshold": 0.70,
        "harmful_content_threshold": 0.70,
        "pii_output_threshold": 0.70,
        "system_prompt_leakage_output_threshold": 0.70,
    }

    print("Chat test:")
    print(json.dumps(run_chat(payload), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
