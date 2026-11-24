"""Pruebas de contrato para POST y GET /v1/events.

Requiere iniciar server.py en otra terminal:
    python3 server.py

Ejecutar:
    python3 -m unittest -v test_events.py
"""
import json
import unittest
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8765"


def request_json(method, path, payload=None, client_id=None):
    """Ejecuta una solicitud HTTP y devuelve (status, body)."""
    headers = {}
    data = None

    if client_id is not None:
        headers["X-Client-ID"] = client_id

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        BASE_URL + path,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8")
        return error.code, json.loads(body) if body else {}


def valid_event(client_id, event_id, device_id="gps-compartido", occurred_at=None):
    if occurred_at is None:
        occurred_at = datetime.now(timezone.utc).isoformat()

    return {
        "client_id": client_id,
        "event_id": event_id,
        "device_id": device_id,
        "occurred_at": occurred_at,
        "lat": 4.7110,
        "lon": -74.0721,
    }


class EventContractTests(unittest.TestCase):

    def setUp(self):
        status, body = request_json("DELETE", "/_test/reset")
        self.assertEqual(status, 200, f"No fue posible limpiar datos: {body}")

    def test_events_are_isolated_between_clients(self):
        """Un cliente no debe consultar eventos pertenecientes a otro."""
        event_a = valid_event("cliente-a", "evento-a")
        event_b = valid_event("cliente-b", "evento-b")

        status_a, _ = request_json(
            "POST", "/v1/events", event_a, client_id="cliente-a"
        )
        status_b, _ = request_json(
            "POST", "/v1/events", event_b, client_id="cliente-b"
        )

        self.assertEqual(status_a, 201)
        self.assertEqual(status_b, 201)

        status, response = request_json(
            "GET", "/v1/events?device_id=gps-compartido",
            client_id="cliente-a"
        )

        self.assertEqual(status, 200)
        returned_ids = [item["event_id"] for item in response["items"]]
        self.assertEqual(returned_ids, ["evento-a"])

    def test_same_event_retry_returns_conflict_without_duplicate(self):
        """El mismo cliente/event_id no debe persistirse dos veces."""
        first_event = valid_event("cliente-a", "evento-duplicado")
        changed_retry = valid_event(
            "cliente-a",
            "evento-duplicado",
            device_id="gps-diferente",
        )
        changed_retry["lat"] = 5.0

        first_status, _ = request_json(
            "POST", "/v1/events", first_event, client_id="cliente-a"
        )
        retry_status, _ = request_json(
            "POST", "/v1/events", changed_retry, client_id="cliente-a"
        )

        self.assertEqual(first_status, 201)
        self.assertEqual(retry_status, 409)

        status, response = request_json(
            "GET", "/v1/events?device_id=gps-compartido",
            client_id="cliente-a"
        )
        self.assertEqual(status, 200)
        self.assertEqual(
            [item["event_id"] for item in response["items"]],
            ["evento-duplicado"],
        )

        other_status, other_response = request_json(
            "GET", "/v1/events?device_id=gps-diferente",
            client_id="cliente-a"
        )
        self.assertEqual(other_status, 200)
        self.assertEqual(other_response["items"], [])

    def test_timestamp_more_than_five_minutes_in_future_is_rejected(self):
        """Un evento con más de cinco minutos de anticipación debe rechazarse."""
        future_timestamp = (
            datetime.now(timezone.utc) + timedelta(minutes=6)
        ).isoformat()
        event = valid_event(
            "cliente-a",
            "evento-futuro",
            occurred_at=future_timestamp,
        )

        status, _ = request_json(
            "POST", "/v1/events", event, client_id="cliente-a"
        )
        self.assertEqual(status, 422)

        get_status, response = request_json(
            "GET", "/v1/events?device_id=gps-compartido",
            client_id="cliente-a"
        )
        self.assertEqual(get_status, 200)
        self.assertEqual(response["items"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
