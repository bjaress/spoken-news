import behave as bhv

import time
import requests
import logging

@bhv.given("the app is running")
def app_running(context):
    poll(
        context,
        f"confirming app is up",
        200,
        lambda: requests.get(f"{context.prop.app.url}/health").status_code,
    )

@bhv.given("{mock_name} is available")
def app_running(context, mock_name):
    mock_url = context.prop.__dict__[mock_name.lower()].url
    poll(
        context,
        f"confirming/resetting {mock_name}",
        200,
        lambda: requests.post(f"{mock_url}/__admin/reset", timeout=1).status_code,
    )


def poll(context, description, expected, action):
    # setup_logging() must be called in every step that uses logging,
    # unless you want to ignore the log level in the config file. :(
    context.config.setup_logging()
    exception = Exception(f"Exhausted attempts at {description}")
    is_expected = (
        expected if callable(expected) else lambda x: x == expected
        )
    result = None
    for attempt in range(300):
        try:
            result = action()
            logging.debug(result)
            if is_expected(result):
                logging.debug(
                    f"Attempt {attempt} at {description} succeeded.")
                return result
            message = result
        except Exception as e:
            exception = e
            message = e
        logging.debug(f"Attempt {attempt} at {description} failed with {message}.")
        # exponential backoff, capped at around ten seconds
        time.sleep(0.01 * (2 ** min(10, attempt)))
        logging.debug(f"Trying again at {description}.")

    raise (exception)
