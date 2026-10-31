import json

from emporio_agent.tools import orders


def test_order_tool_validates_contact_and_calls_service(monkeypatch):
    captured = {}

    def fake_consult_order(settings, order_id, email, phone):
        captured.update(order_id=order_id, email=email, phone=phone)
        return {"order_id": order_id}

    monkeypatch.setattr(orders, "consult_order", fake_consult_order)

    result = json.loads(orders.TOOL.invoke(None, {
        "order_id": 12,
        "email_ou_telefone": "cliente@example.com",
    }))

    assert result == {"ok": True, "data": {"order_id": 12}}
    assert captured == {"order_id": 12, "email": "cliente@example.com", "phone": None}
