class DependencyResponseError(ValueError):
    def __init__(self, response):
        self.status_code = response.status_code
        super().__init__(f"{response.status_code} {response.text}")


def check_response(response):
    try:
        response.raise_for_status()
    except Exception as cause:
        raise DependencyResponseError(response) from cause
