from secure_llm_mcp.local_pii import scan_text_for_pii


def test_email_detection() -> None:
    result = scan_text_for_pii("Email: test@example.com")
    assert result["pii_found"] is True
    assert any(item["type"] == "email" for item in result["findings"])
