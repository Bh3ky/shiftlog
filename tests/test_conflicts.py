from fastapi.testclient import TestClient


def test_overlapping_shift_is_rejected(client: TestClient, worker_id: int):
    first = client.post(
        "/shifts",
        json={
            "worker_id": worker_id,
            "start_time": "2026-08-10T09:00:00",
            "end_time": "2026-08-10T17:00:00",
        },
    )
    assert first.status_code == 201

    # Overlaps the middle of the first shift.
    second = client.post(
        "/shifts",
        json={
            "worker_id": worker_id,
            "start_time": "2026-08-10T12:00:00",
            "end_time": "2026-08-10T20:00:00",
        },
    )
    assert second.status_code == 409
    assert "conflict" in second.json()["detail"].lower()


def test_back_to_back_shifts_are_not_conflicts(client: TestClient, worker_id: int):
    first = client.post(
        "/shifts",
        json={
            "worker_id": worker_id,
            "start_time": "2026-08-10T09:00:00",
            "end_time": "2026-08-10T17:00:00",
        },
    )
    assert first.status_code == 201

    # Starts exactly when the first one ends - should be allowed.
    second = client.post(
        "/shifts",
        json={
            "worker_id": worker_id,
            "start_time": "2026-08-10T17:00:00",
            "end_time": "2026-08-10T21:00:00",
        },
    )
    assert second.status_code == 201


def test_overlapping_shifts_for_different_workers_are_allowed(client: TestClient):
    alice = client.post("/workers", json={"name": "Alice", "role": "Barista"}).json()
    bilal = client.post("/workers", json={"name": "Bilal", "role": "Cashier"}).json()

    first = client.post(
        "/shifts",
        json={
            "worker_id": alice["id"],
            "start_time": "2026-08-10T09:00:00",
            "end_time": "2026-08-10T17:00:00",
        },
    )
    second = client.post(
        "/shifts",
        json={
            "worker_id": bilal["id"],
            "start_time": "2026-08-10T09:00:00",
            "end_time": "2026-08-10T17:00:00",
        },
    )
    assert first.status_code == 201
    assert second.status_code == 201
