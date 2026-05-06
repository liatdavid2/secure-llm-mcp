import json
from pathlib import Path

from secure_llm_mcp.metrics_reader import read_latest_artifacts


def test_read_latest_artifacts(tmp_path: Path) -> None:
    metrics_path = tmp_path / "prompt_injection_input_guard" / "runs" / "2026-01-01T00-00-00" / "metrics.json"
    metrics_path.parent.mkdir(parents=True)
    metrics_path.write_text(json.dumps({"validation": {"accuracy": 0.9}}), encoding="utf-8")

    result = read_latest_artifacts(tmp_path)

    assert result["source"] == "local_artifacts"
    assert "prompt_injection_input_guard" in result["guards"]
    assert result["guards"]["prompt_injection_input_guard"]["metrics"]["validation"]["accuracy"] == 0.9
