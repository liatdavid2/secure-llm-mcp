from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .audit import write_audit_event
from .gateway_client import call_optional_endpoint, gateway_health as check_gateway_health, run_chat
from .local_pii import scan_text_for_pii
from .metrics_reader import get_metrics
from .settings import settings

mcp = FastMCP("secure-llm-gateway")


def _with_audit(tool_name: str, payload: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    write_audit_event(tool_name=tool_name, payload=payload, result=result)
    return result


@mcp.tool()
def gateway_health() -> Dict[str, Any]:
    """
    Check whether the Secure LLM Gateway API is reachable.
    """
    payload: Dict[str, Any] = {}
    result = check_gateway_health()
    return _with_audit("gateway_health", payload, result)


@mcp.tool()
def run_secure_chat(
    prompt: str,
    model_name: str = settings.default_model_name,
    temperature: float = settings.default_temperature,
    max_tokens: int = settings.default_max_tokens,
    disabled_steps: Optional[List[str]] = None,
    prompt_injection_threshold: float = 0.70,
    harmful_content_threshold: float = 0.70,
    pii_output_threshold: float = 0.70,
    system_prompt_leakage_output_threshold: float = 0.70,
) -> Dict[str, Any]:
    """
    Run a prompt through the Secure LLM Gateway chat endpoint.

    The result should include the final response, guard decisions, blocking status,
    and latency fields if the gateway returns them.
    """
    payload = {
        "prompt": prompt,
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "disabled_steps": disabled_steps or [],
        "prompt_injection_threshold": prompt_injection_threshold,
        "harmful_content_threshold": harmful_content_threshold,
        "pii_output_threshold": pii_output_threshold,
        "system_prompt_leakage_output_threshold": system_prompt_leakage_output_threshold,
    }
    result = run_chat(payload)
    return _with_audit("run_secure_chat", payload, result)


@mcp.tool()
def scan_prompt(
    prompt: str,
    model_name: str = settings.default_model_name,
    prompt_injection_threshold: float = 0.70,
    harmful_content_threshold: float = 0.70,
) -> Dict[str, Any]:
    """
    Scan a prompt with the Secure LLM Gateway input guards.

    If PROMPT_SCAN_PATH is configured, this tool calls that endpoint.
    Otherwise it uses the existing chat endpoint while disabling output guards.
    """
    payload = {
        "prompt": prompt,
        "model_name": model_name,
        "prompt_injection_threshold": prompt_injection_threshold,
        "harmful_content_threshold": harmful_content_threshold,
    }

    direct_result = call_optional_endpoint(settings.prompt_scan_path, payload)
    if direct_result is not None:
        return _with_audit("scan_prompt", payload, direct_result)

    chat_payload = {
        "prompt": prompt,
        "model_name": model_name,
        "temperature": 0.0,
        "max_tokens": 32,
        "disabled_steps": [
            "pii_output_guard",
            "system_prompt_leakage_output_guard",
        ],
        "prompt_injection_threshold": prompt_injection_threshold,
        "harmful_content_threshold": harmful_content_threshold,
        "pii_output_threshold": 0.70,
        "system_prompt_leakage_output_threshold": 0.70,
    }
    result = run_chat(chat_payload)
    result["scan_mode"] = "chat_endpoint_with_output_guards_disabled"
    return _with_audit("scan_prompt", chat_payload, result)


@mcp.tool()
def scan_response_for_pii(response_text: str) -> Dict[str, Any]:
    """
    Scan text for PII.

    If PII_SCAN_PATH is configured, this tool calls the gateway PII endpoint.
    Otherwise it uses a local regex fallback for demo and audit purposes.
    """
    payload = {"response_text": response_text}

    direct_result = call_optional_endpoint(settings.pii_scan_path, payload)
    if direct_result is not None:
        return _with_audit("scan_response_for_pii", payload, direct_result)

    result = scan_text_for_pii(response_text)
    return _with_audit("scan_response_for_pii", payload, result)


@mcp.tool()
def get_guard_metrics() -> Dict[str, Any]:
    """
    Return latest guard model metrics from a gateway endpoint or local artifacts.
    """
    payload: Dict[str, Any] = {}
    result = get_metrics()
    return _with_audit("get_guard_metrics", payload, result)


@mcp.tool()
def create_security_issue_draft(
    title: str,
    finding_summary: str,
    severity: str = "medium",
    affected_tool: str = "unknown",
) -> Dict[str, Any]:
    """
    Create a structured GitHub issue draft for a security finding.

    This tool does not call GitHub. It returns markdown that can be copied into an issue
    or later connected to a GitHub API integration.
    """
    body = f"""## Summary
{finding_summary}

## Severity
{severity}

## Affected MCP Tool
{affected_tool}

## Recommended Action
Review the blocked request, check the audit log, and decide whether the policy or guard threshold should be updated.

## Evidence
Attach the relevant MCP audit event and Secure LLM Gateway response.
"""
    result = {
        "title": title,
        "severity": severity,
        "affected_tool": affected_tool,
        "issue_body_markdown": body,
    }
    return _with_audit(
        "create_security_issue_draft",
        {
            "title": title,
            "finding_summary": finding_summary,
            "severity": severity,
            "affected_tool": affected_tool,
        },
        result,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
