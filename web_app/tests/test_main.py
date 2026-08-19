"""Unit tests for the FastAPI application."""

from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from web_app.main import app

CLIENT = TestClient(app)


def test_home_page() -> None:
    """Verify that the home page loads."""
    response = CLIENT.get("/")

    assert response.status_code == 200
    assert "City Coordinate Finder" in response.text


@patch("web_app.main.httpx.get")
def test_get_coordinates(mock_get: Mock) -> None:
    """Verify that coordinates are returned for a valid location."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "lat": 40.4406968,
                "lon": -80.0025666,
            }
        ]
    }
    mock_get.return_value = mock_response

    response = CLIENT.post("/coordinates/Pittsburgh/Pennsylvania")

    assert response.status_code == 200
    assert response.json() == {
        "city": "Pittsburgh",
        "state": "Pennsylvania",
        "latitude": 40.4406968,
        "longitude": -80.0025666,
    }


@patch("web_app.main.httpx.get")
def test_location_not_found(mock_get: Mock) -> None:
    """Verify the response when Geoapify finds no location."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}
    mock_get.return_value = mock_response

    response = CLIENT.post("/coordinates/UnknownCity/Pennsylvania")

    assert response.status_code == 200
    assert response.json() == {"message": "The city and state were not found."}


@patch("web_app.main.httpx.get")
def test_geocoding_service_unavailable(mock_get: Mock) -> None:
    """Verify the response when Geoapify returns an error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    response = CLIENT.post("/coordinates/Pittsburgh/Pennsylvania")

    assert response.status_code == 200
    assert response.json() == {"message": "The geocoding service is unavailable."}


def test_invalid_city() -> None:
    """Verify that FastAPI rejects a city that is too short."""
    response = CLIENT.post("/coordinates/P/Pennsylvania")

    assert response.status_code == 422


def test_missing_state() -> None:
    """Verify that the state path parameter is required."""
    response = CLIENT.post("/coordinates/Pittsburgh")

    assert response.status_code == 404
