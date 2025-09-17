def print_response_details(response):
    """
    Print detailed information about a FastAPI TestClient response.

    Args:
        response: The response object from FastAPI's TestClient
    """
    print("\n=== Response Details ===")
    print(f"Status Code: {response.status_code}")
    print("\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print("\nBody:")
    try:
        print(response.json())
    except Exception:
        print(response.text)
    print("=====================\n")
