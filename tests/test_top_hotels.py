"""Testes fornecidos: ranking de hotéis."""

from helpers import run_cli


def test_top_larger_than_hotel_count_returns_only_existing_hotels(tmp_path):
    """Com --top maior que o número de hotéis faturáveis, devolve só os hotéis existentes."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "amount": "300.00",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "amount": "200.00",
            },
            {
                "reservation_id": "R-3",
                "hotel_id": "H03",
                "hotel_name": "Hotel C",
                "status": "CANCELLED",
            },
        ],
        top=10,
    )
    assert len(report["top_hotels"]) == 2
    assert sorted(hotel["hotel_id"] for hotel in report["top_hotels"]) == ["H01", "H02"]
    for hotel in report["top_hotels"]:
        assert set(hotel) == {"hotel_id", "hotel_name", "room_nights", "total_brl"}
        assert hotel["hotel_id"] and hotel["hotel_name"]
        assert hotel["room_nights"] > 0


def test_top_hotels_tie_breaks_by_hotel_id_ascending(tmp_path):
    """Com o mesmo total_brl, o ranking desempata por hotel_id crescente."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H03",
                "hotel_name": "Hotel C",
                "amount": "500.00",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "amount": "500.00",
            },
            {
                "reservation_id": "R-3",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "amount": "900.00",
            },
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == [
        "H02",
        "H01",
        "H03",
    ]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == [
        "900.00",
        "500.00",
        "500.00",
    ]


def test_top_hotels_are_ranked_descending(tmp_path):
    """O ranking mostra os hotéis de maior valor primeiro."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "amount": "1000.00",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "amount": "900.00",
            },
            {
                "reservation_id": "R-3",
                "hotel_id": "H03",
                "hotel_name": "Hotel C",
                "amount": "800.00",
            },
            {
                "reservation_id": "R-4",
                "hotel_id": "H04",
                "hotel_name": "Hotel D",
                "amount": "700.00",
            },
        ],
        top=3,
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == [
        "H01",
        "H02",
        "H03",
    ]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == [
        "1000.00",
        "900.00",
        "800.00",
    ]
