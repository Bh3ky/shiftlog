from fastapi.testclient import TestClient


def _create_shift(client: TestClient, worker_id: int, start: str, end: str):
    response = client.post(
        "/shifts",
        json={"worker_id": worker_id, "start_time": start, "end_time": end},
    )
    assert response.status_code == 201
    return response.json()


def test_filter_by_worker_id(client: TestClient):
    alice = client.post("/workers", json={"name": "Alice", "role": "Barista"}).json()
    bilal = client.post("/workers", json={"name": "Bilal", "role": "Cashier"}).json()

    _create_shift(client, alice["id"], "2026-08-10T09:00:00", "2026-08-10T17:00:00")
    _create_shift(client, bilal["id"], "2026-08-10T09:00:00", "2026-08-10T17:00:00")

    response = client.get("/shifts", params={"worker_id": alice["id"]})
    assert response.status_code == 200
    shifts = response.json()
    assert len(shifts) == 1
    assert shifts[0]["worker_id"] == alice["id"]


def test_filter_by_date_range(client: TestClient, worker_id: int):
    _create_shift(client, worker_id, "2026-08-10T09:00:00", "2026-08-10T17:00:00")
    _create_shift(client, worker_id, "2026-08-20T09:00:00", "2026-08-20T17:00:00")

    response = client.get(
        "/shifts",
        params={"start_after": "2026-08-15T00:00:00", "end_before": "2026-08-25T00:00:00"},
    )
    assert response.status_code == 200
    shifts = response.json()
    assert len(shifts) == 1
    assert shifts[0]["start_time"].startswith("2026-08-20")


def test_list_shifts_ordered_by_start_time(client: TestClient, worker_id: int):
    _create_shift(client, worker_id, "2026-08-20T09:00:00", "2026-08-20T17:00:00")
    _create_shift(client, worker_id, "2026-08-10T09:00:00", "2026-08-10T17:00:00")

    response = client.get("/shifts")
    shifts = response.json()
    starts = [s["start_time"] for s in shifts]
    assert starts == sorted(starts)
