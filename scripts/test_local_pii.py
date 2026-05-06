from __future__ import annotations

import json

from secure_llm_mcp.local_pii import scan_text_for_pii


def main() -> None:
    text = "Contact Dana at dana@example.com or +972-50-123-4567."
    result = scan_text_for_pii(text)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
