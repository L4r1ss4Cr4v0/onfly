"""Testes adicionais: validaçao da amostra por meio das regras de negócio."""

import csv

from helpers import PROJECT_ROOT, run_cli


def test_validation_sample_matches_readme(tmp_path):
    """A amostra data/exemplo-validacao.csv reproduz as tabelas de validação do README."""
    sample_path = PROJECT_ROOT / "data" / "exemplo-validacao.csv"
    with sample_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    report = run_cli(tmp_path, rows)

    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert report["by_month"] == [
        {
            "month": "2025-01",
            "reservations": 8,
            "room_nights": 25,
            "total_brl": "6684.00",
        },
        {
            "month": "2025-02",
            "reservations": 1,
            "room_nights": 3,
            "total_brl": "882.00",
        },
    ]
    assert report["top_hotels"] == [
        {
            "hotel_id": "H01",
            "hotel_name": "Hotel Aurora Paulista",
            "room_nights": 3,
            "total_brl": "1200.00",
        },
        {
            "hotel_id": "H02",
            "hotel_name": "Hotel Mirante",
            "room_nights": 2,
            "total_brl": "1084.00",
        },
        {
            "hotel_id": "H12",
            "hotel_name": "Hotel Miami Beach",
            "room_nights": 1,
            "total_brl": "1000.00",
        },
        {
            "hotel_id": "H10",
            "hotel_name": "Hotel Madrid, Gran Vía",
            "room_nights": 4,
            "total_brl": "900.00",
        },
        {
            "hotel_id": "H09",
            "hotel_name": "Hotel Lisboa, Centro",
            "room_nights": 3,
            "total_brl": "882.00",
        },
    ]
