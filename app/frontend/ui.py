import streamlit as st
import requests

from app.config.settings import settings
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

st.set_page_config(page_title="Multi AI Agent", layout="centered")
st.title("Multi AI Agent using Groq and Tavily")

system_prompt = st.text_area("Define your AI Agent: ", height=70)
selected_model = st.selectbox("Select your model: ", settings.ALLOWED_MODEL_NAMES)

allow_websearch = st.checkbox("Allow Web Search")

user_query = st.text_area("Enter your query: ", height=150)

API_URL = "http://127.0.0.1:9999/chat"


def call_backend(api_url: str, payload: dict):
    
    #Helper function to call the backend API and handle errors cleanly.
    
    logger.info(f"Sending request to API at {api_url}")
    logger.debug(f"Payload: {payload}")

    try:
        response = requests.post(api_url, json=payload, timeout=60)

        # Raise for HTTP 4xx/5xx
        response.raise_for_status()

        logger.info("Received response from API")
        return response

    except requests.exceptions.ConnectionError as e:
        logger.exception("Could not connect to backend.")
        raise CustomException("Could not connect to backend. Is the backend running on 127.0.0.1:9999?", e)

    except requests.exceptions.Timeout as e:
        logger.exception("Request to backend timed out.")
        raise CustomException("Request to backend timed out. Please try again.", e)

    except requests.exceptions.HTTPError as e:
        # Include backend error body if available
        logger.exception(
            f"Backend returned HTTP error {e.response.status_code if e.response else 'N/A'}"
        )
        backend_body = e.response.text if e.response is not None else "No response body."
        raise CustomException(
            f"Backend returned an error: {e}. Details: {backend_body}",
            e
        )

    except Exception as e:
        logger.exception("Unexpected error while sending request to API.")
        raise CustomException("Failed to communicate to backend due to an unexpected error.", e)


if st.button("Ask Agent") and user_query.strip():
    payload = {
        "model_name": selected_model,
        "system_prompt": system_prompt,
        "messages": [user_query],
        "allow_search": allow_websearch,
    }

    try:
        response = call_backend(API_URL, payload)

        # Safely parse JSON
        try:
            data = response.json()
        except ValueError:
            logger.error("Backend did not return valid JSON.")
            st.error("Backend did not return valid JSON.")
        else:
            agent_response = data.get("response", "")

            if not agent_response:
                logger.warning("Backend JSON does not contain 'response' key or it's empty.")
                st.warning("Backend returned no 'response' field. Check backend implementation.")
            else:
                st.subheader("Agent Response")
                st.markdown(
                    agent_response.replace("\n", "<br>"),
                    unsafe_allow_html=True
                )

    except CustomException as ce:
        # This will now include the underlying error instead of "Error: None"
        logger.error(f"CustomException: {str(ce)}")
        st.error(str(ce))     