"""Testes fornecidos: regras de status."""

from helpers import run_cli


def test_status_rules_exclude_cancelled_and_no_show(tmp_path):
    """Somente CONFIRMED entra nos totais financeiros."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"},
            {"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"},
            {"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"},
        ],
    )
    assert report["summary"]["total_reservations"] == 3
    assert report["summary"]["confirmed_reservations"] == 1
    assert report["summary"]["cancelled_reservations"] == 1
    assert report["summary"]["no_show_reservations"] == 1
    assert report["summary"]["total_amount_brl"] == "100.00"
    assert report["summary"]["total_room_nights"] == 1


def test_no_show_is_excluded_from_by_month_and_top_hotels(tmp_path):
    """NO_SHOW conta no summary, mas não aparece em by_month nem em top_hotels."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "amount": "100.00",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "status": "NO_SHOW",
                "amount": "999.00",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-12",
            },
        ],
    )
    assert report["summary"]["no_show_reservations"] == 1
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "100.00"}
    ]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]
