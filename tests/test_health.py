from app import create_app


def test_health_returns_ok():
    app = create_app()
    client = app.test_client()

    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json() == {"status": "ok"}

