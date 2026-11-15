"""Testes adicionais: leitura completa do arquivo de reservas."""

from helpers import run_cli


def test_reads_all_reservations(tmp_path):
    """Todas as linhas do arquivo entram no relatório, sem limite fixo de leitura."""
    report = run_cli(
        tmp_path,
        [{"reservation_id": f"R-{index}"} for index in range(1, 251)],
    )
    assert report["summary"]["total_reservations"] == 250
    assert report["summary"]["confirmed_reservations"] == 250
    assert report["summary"]["total_room_nights"] == 250
    assert report["summary"]["total_amount_brl"] == "25000.00"
