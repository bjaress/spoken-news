def check_response(response):
    try:
        response.raise_for_status()
    except Exception as cause:
        raise ValueError(f"{response.status_code} {response.text}") from cause
