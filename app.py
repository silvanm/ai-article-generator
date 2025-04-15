import streamlit as st
import logging
import os
import dotenv

# Check for .env and API keys early
dotenv.load_dotenv()

API_KEYS_PRESENT = all(
    key in os.environ
    for key in ["OPENAI_API_KEY", "SERPER_API_KEY", "FIRECRAWL_API_KEY"]
)
API_KEYS_SET = all(
    os.environ.get(key)
    for key in ["OPENAI_API_KEY", "SERPER_API_KEY", "FIRECRAWL_API_KEY"]
)

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Article Generator", layout="wide")

st.title("📝 AI Article Generator")
st.caption("Enter keywords, and the AI will search the web and write an HTML article.")

# --- Sidebar for API Key Status --- #
if not API_KEYS_PRESENT:
    st.sidebar.error("`.env` file not found or missing API keys.")
    st.sidebar.caption(
        "Please create a `.env` file in the root directory with your `OPENAI_API_KEY`, `SERPER_API_KEY`, and `FIRECRAWL_API_KEY`."
    )
    st.stop()

st.sidebar.header("API Key Status")
if API_KEYS_SET:
    st.sidebar.success("API keys loaded successfully from `.env`.")
    # Only import the generator if keys are set
    try:
        from article_generator import ArticleGenerator

        if "article_generator" not in st.session_state:
            st.session_state.article_generator = ArticleGenerator()
            logger.info("ArticleGenerator initialized and stored in session state.")
        generator_ready = True
    except Exception as e:
        st.error(f"Error initializing Article Generator: {e}")
        st.caption(
            "Please check your API keys and ensure required libraries are installed (`pip install -r requirements.txt`)"
        )
        logger.error(f"Failed to initialize ArticleGenerator: {e}")
        generator_ready = False
else:
    st.sidebar.warning("One or more API keys are missing in `.env`.")
    st.sidebar.caption(
        "Please add your `OPENAI_API_KEY`, `SERPER_API_KEY`, and `FIRECRAWL_API_KEY` to the `.env` file."
    )
    generator_ready = False

# --- Main Area --- #
keywords = st.text_input(
    "Enter keywords for the article:",
    placeholder="e.g., future of solar power, impact of AI on healthcare",
)
generate_button = st.button(
    "Generate Article", disabled=not generator_ready or not keywords
)

if "article_html" not in st.session_state:
    st.session_state.article_html = ""

if generate_button and generator_ready:
    if keywords:
        with st.spinner(
            "🔄 Generating article... This may take a minute or two. Please wait."
        ):
            logger.info(f"Generate button clicked. Keywords: '{keywords}'")
            try:
                # Use the generator stored in session state
                st.session_state.article_html = (
                    st.session_state.article_generator.generate(keywords)
                )
                logger.info("Article generation complete.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                logger.error(f"Error calling generator.generate(): {e}")
                st.session_state.article_html = (
                    f"<p>Sorry, an error occurred during generation: {e}</p>"
                )
    else:
        st.warning("Please enter some keywords.")

# Display the generated article (or previous one)
if st.session_state.article_html:
    st.divider()
    st.subheader("Generated Article")
    st.markdown(st.session_state.article_html, unsafe_allow_html=True)
