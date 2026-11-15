"""Testes adicionais: regressão ponta a ponta do relatório completo."""

from helpers import run_cli


def test_regression_full_report(tmp_path):
    """Relatório completo com moedas, quartos, viradas de mês/ano, status, agregação e empate."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "amount": "1000.00",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-13",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H03",
                "hotel_name": "Hotel C",
                "currency": "EUR",
                "amount": "200.00",
                "checkin_date": "2024-12-30",
                "checkout_date": "2025-01-02",
            },
            {
                "reservation_id": "R-3",
                "hotel_id": "H02",
                "hotel_name": "Hotel B",
                "currency": "USD",
                "amount": "100.00",
                "checkin_date": "2025-01-20",
                "checkout_date": "2025-01-22",
                "rooms": "2",
            },
            {
                "reservation_id": "R-4",
                "hotel_id": "H01",
                "hotel_name": "Hotel A",
                "amount": "500.00",
                "checkin_date": "2025-02-27",
                "checkout_date": "2025-03-01",
            },
            {
                "reservation_id": "R-5",
                "hotel_id": "H06",
                "hotel_name": "Hotel F",
                "amount": "542.00",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-11",
            },
            {
                "reservation_id": "R-6",
                "hotel_id": "H04",
                "hotel_name": "Hotel D",
                "status": "CANCELLED",
                "amount": "5000.00",
                "checkin_date": "2025-03-01",
                "checkout_date": "2025-03-05",
            },
            {
                "reservation_id": "R-7",
                "hotel_id": "H05",
                "hotel_name": "Hotel E",
                "status": "NO_SHOW",
                "currency": "EUR",
                "amount": "3000.00",
                "checkin_date": "2025-04-01",
                "checkout_date": "2025-04-03",
            },
        ],
        top=3,
    )
    report.pop("generated_at")
    assert report == {
        "report_version": "1.0",
        "summary": {
            "total_reservations": 7,
            "confirmed_reservations": 5,
            "cancelled_reservations": 1,
            "no_show_reservations": 1,
            "total_room_nights": 13,
            "total_amount_brl": "3760.00",
            "average_nightly_rate_brl": "289.23",
        },
        "by_month": [
            {"month": "2024-12", "reservations": 1, "room_nights": 3, "total_brl": "1176.00"},
            {"month": "2025-01", "reservations": 2, "room_nights": 7, "total_brl": "1542.00"},
            {"month": "2025-02", "reservations": 2, "room_nights": 3, "total_brl": "1042.00"},
        ],
        "top_hotels": [
            {"hotel_id": "H01", "hotel_name": "Hotel A", "room_nights": 5, "total_brl": "1500.00"},
            {"hotel_id": "H03", "hotel_name": "Hotel C", "room_nights": 3, "total_brl": "1176.00"},
            {"hotel_id": "H02", "hotel_name": "Hotel B", "room_nights": 4, "total_brl": "542.00"},
        ],
    }


def test_regression_rounds_half_up_only_on_serialization(tmp_path):
    """Soma valores exatos e arredonda só na saída, com half-up."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "0.005"},
            {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "0.005"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "0.01"
    assert report["summary"]["average_nightly_rate_brl"] == "0.01"
    assert report["by_month"][0]["total_brl"] == "0.01"
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["0.01", "0.01"]


def test_regression_report_without_billable_reservations(tmp_path):
    """Sem reservas CONFIRMED, totais zerados, média "0.00" e listas vazias."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CANCELLED", "amount": "300.00"},
            {"reservation_id": "R-2", "status": "NO_SHOW", "amount": "200.00"},
        ],
    )
    assert report["summary"] == {
        "total_reservations": 2,
        "confirmed_reservations": 0,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []
