import os
import dotenv
import logging
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool

from tools import search, scrape  # Import the tools we defined

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()


class ArticleGenerator:
    """Generates an HTML article on a given topic using a ReAct agent.

    Uses search and scrape tools to gather information and an LLM to synthesize
    the article.
    """

    def __init__(self, model_name: str = "gpt-4.1", max_iterations: int = 15):
        """Initializes the ArticleGenerator.

        Args:
            model_name: The OpenAI model to use (defaults to "gpt-4.1").
            max_iterations: Maximum steps the agent can take.
        """
        try:
            openai_api_key = os.environ["OPENAI_API_KEY"]
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set in the environment.")

            self.llm = OpenAI(model=model_name, api_key=openai_api_key)
            logger.info(f"Using LLM model: {model_name}")

            # Create FunctionTool instances for the agent
            search_tool = FunctionTool.from_defaults(fn=search)
            scrape_tool = FunctionTool.from_defaults(fn=scrape)

            self.agent = ReActAgent.from_tools(
                [search_tool, scrape_tool],
                llm=self.llm,
                max_iterations=max_iterations,
                verbose=True,  # Enable logging of agent steps
            )
            logger.info(f"ReActAgent initialized with search and scrape tools.")

        except KeyError:
            logger.error("OPENAI_API_KEY not found in .env file.")
            raise
        except ValueError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Error initializing ArticleGenerator: {e}")
            raise

    def generate(self, keywords: str) -> str:
        """Generates an HTML article based on the provided keywords.

        Args:
            keywords: The keywords or topic for the article.

        Returns:
            The generated article as an HTML string, or an error message.
        """
        logger.info(f"Generating article for keywords: '{keywords}'")

        # Define the prompt for the ReAct agent
        # Instructing it to use search and scrape, and format as HTML
        prompt = f"""
        You are an expert writer tasked with creating a comprehensive and engaging article.
        Your goal is to synthesize information from multiple reliable sources to produce a single, well-structured HTML article about: "{keywords}".

        Follow these steps:
        1.  Use the 'search' tool to find relevant articles and sources about "{keywords}". Aim for 3-5 diverse and reputable sources if possible.
        2.  Analyze the search results. Identify promising URLs that likely contain detailed information.
        3.  Use the 'scrape' tool to extract the main content (in markdown format) from the selected URLs. Scrape at least 2-3 different sources to ensure a comprehensive overview. **Keep track of the URLs you successfully scrape content from.**
        4.  Synthesize the information gathered from the scraped content.
        5.  Write a single, coherent article based *only* on the information you scraped. Do not add information not present in the sources.
        6.  Format the final article strictly as HTML. Use appropriate tags like <h1>, <h2>, <p>, <ul>, <li>, <strong>, etc. for structure and readability.
        7.  The article should be informative, well-organized, and easy to read.
        8.  Include a brief introductory paragraph and a concluding summary.
        9.  **At the end of the article, add a section titled 'Sources' (e.g., using an <h2> tag). Under this heading, list the URLs you successfully scraped content from in step 3, ideally as an unordered list (<ul><li><a>...</a></li></ul>).**
        10. Do NOT include any preamble like "Here is the HTML article:". Just output the raw HTML starting with the <h1> tag and ending with the sources list.
        11. If you encounter errors during search or scraping, try alternative queries or URLs, but if you cannot gather sufficient information after a reasonable number of attempts, state that you were unable to generate the article due to lack of sources (as a simple HTML paragraph).

        Generate the HTML article now.
        """

        try:
            response = self.agent.chat(prompt)
            # The agent's final response should be the HTML article
            article_html = response.response
            logger.info(f"Successfully generated article for keywords: '{keywords}'")
            # Basic check if the output looks like HTML
            if not article_html.strip().startswith("<"):
                logger.warning(
                    "Agent response doesn't look like HTML. Wrapping in <p> tags."
                )
                article_html = f"<p>{article_html}</p>"
            return article_html
        except Exception as e:
            logger.error(f"Error during article generation for '{keywords}': {e}")
            return f"<p>Error generating article: {e}</p>"


if __name__ == "__main__":
    # Example usage (for testing)
    generator = ArticleGenerator()
    test_keywords = "the future of renewable energy in Europe"
    print(f"--- Generating Article ---")
    print(f"Keywords: {test_keywords}")
    html_article = generator.generate(test_keywords)
    print("\n--- Generated HTML Article ---")
    print(html_article)
