"""Testes adicionais: formato do contrato do relatório."""

from datetime import datetime, timedelta

from helpers import run_cli


def test_report_contract_version_and_generated_at(tmp_path):
    """report_version é "1.0" e generated_at é ISO 8601 com offset fixo -03:00."""
    report = run_cli(tmp_path, [{"reservation_id": "R-1"}])
    assert report["report_version"] == "1.0"
    generated_at = datetime.fromisoformat(report["generated_at"])
    assert generated_at.utcoffset() == timedelta(hours=-3)
    assert report["generated_at"].endswith("-03:00")
