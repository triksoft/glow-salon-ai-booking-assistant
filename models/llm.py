import time

from google import genai

from config.config import (
    get_gemini_api_key,
    MODEL_NAME,
    FALLBACK_MODEL
)


def get_client():
    """Create and return the Gemini client."""

    api_key = get_gemini_api_key()

    return genai.Client(
        api_key=api_key
    )


def _generate_with_retry(client, model, prompt, attempts=2):
    """
    Try to generate a Gemini response more than once.

    This helps with temporary Gemini 503/high-demand errors.
    """

    last_error = None

    for attempt in range(attempts):

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response is None or not response.text:
                raise RuntimeError(
                    f"Gemini returned an empty response from {model}."
                )

            return response.text

        except Exception as error:

            last_error = error

            print(
                f"Model {model} failed "
                f"(attempt {attempt + 1}/{attempts}): {error}"
            )

            # Wait before retrying, but not after the final attempt.
            if attempt < attempts - 1:

                time.sleep(2)


    raise last_error


def generate_response(prompt):
    """
    Generate a response using Gemini.

    The primary model is tried first.
    If it temporarily fails, it is retried.
    Then the fallback model is tried and retried.
    """

    client = get_client()

    primary_error = None
    fallback_error = None


    # ---------------------------------------------
    # Try primary model
    # ---------------------------------------------

    try:

        return _generate_with_retry(
            client,
            MODEL_NAME,
            prompt,
            attempts=2
        )

    except Exception as error:

        primary_error = error

        print(
            f"Primary model failed after retries: {error}"
        )


    # ---------------------------------------------
    # Try fallback model
    # ---------------------------------------------

    try:

        return _generate_with_retry(
            client,
            FALLBACK_MODEL,
            prompt,
            attempts=2
        )

    except Exception as error:

        fallback_error = error

        print(
            f"Fallback model failed after retries: {error}"
        )


    # ---------------------------------------------
    # Both models failed
    # ---------------------------------------------

    raise RuntimeError(
        "Both Gemini models are temporarily unavailable. "
        "Please try again in a moment. "
        f"Primary error: {primary_error} | "
        f"Fallback error: {fallback_error}"
    ) from fallback_error
