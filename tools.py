import os
import json
import http.client
import dotenv
from firecrawl import FirecrawlApp
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()

# Initialize Firecrawl App
try:
    firecrawl_api_key = os.environ["FIRECRAWL_API_KEY"]
    if not firecrawl_api_key:
        raise ValueError("FIRECRAWL_API_KEY is not set in the environment.")
    firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
except KeyError:
    logger.error("FIRECRAWL_API_KEY not found in .env file.")
    raise
except ValueError as e:
    logger.error(e)
    raise


def search(query: str, num_results: int = 5) -> str:
    """Search for a query on Google using Serper and return the results as a JSON string.

    Args:
        query: The search query string.
        num_results: The number of search results to return (default 5).

    Returns:
        A JSON string containing the search results, or an error message.
    """
    logger.info(f"Performing search for query: '{query}'")
    conn = http.client.HTTPSConnection("google.serper.dev")
    try:
        serper_api_key = os.environ["SERPER_API_KEY"]
        if not serper_api_key:
            raise ValueError("SERPER_API_KEY is not set in the environment.")

        payload = json.dumps({"q": query, "num": num_results})
        headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json",
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        decoded_data = data.decode("utf-8")
        logger.info(f"Search successful for query: '{query}'")
        # Return the raw JSON string as context for the agent
        return decoded_data
    except KeyError:
        logger.error("SERPER_API_KEY not found in .env file.")
        return json.dumps({"error": "SERPER_API_KEY not found"})
    except ValueError as e:
        logger.error(e)
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.error(f"Error during Serper search for '{query}': {str(e)}")
        return json.dumps({"error": f"Search failed: {str(e)}"})


def scrape(url: str) -> str:
    """Scrape a webpage using Firecrawl and return its markdown content.

    Args:
        url: The URL to scrape.

    Returns:
        The markdown content of the page, or an error message.
    """
    logger.info(f"Scraping URL: {url}")
    try:
        params = {
            "formats": ["markdown"],
            "excludeTags": [
                "script",
                "style",
                "svg",
                "iframe",
                "footer",
                "nav",
                "header",
            ],
            "onlyMainContent": True,  # Focus on the main article content
            "waitFor": 1000,
        }
        scrape_result = firecrawl_app.scrape_url(url, params=params)
        markdown_content = scrape_result.get("markdown", "")
        if markdown_content:
            logger.info(f"Successfully scraped URL: {url}")
            # Limit content length slightly to prevent excessive context
            max_length = 10000
            if len(markdown_content) > max_length:
                logger.warning(
                    f"Scraped content from {url} truncated to {max_length} characters."
                )
                markdown_content = markdown_content[:max_length] + "... (truncated)"
            return markdown_content
        else:
            logger.warning(f"No markdown content found for URL: {url}")
            return json.dumps({"warning": "No markdown content found"})
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")
        return json.dumps({"error": f"Scraping failed: {str(e)}"})


if __name__ == "__main__":
    # Example usage (for testing)
    test_query = "latest advancements in AI"
    print(f"--- Testing Search ---")
    search_results = search(test_query)
    print(f"Search results for '{test_query}':")
    try:
        # Pretty print the JSON if possible
        print(json.dumps(json.loads(search_results), indent=2))
    except json.JSONDecodeError:
        print(search_results)  # Print raw string if not valid JSON

    print(f"\n--- Testing Scrape ---")
    # Find a URL from the search results to test scraping
    test_url = None
    try:
        results_data = json.loads(search_results)
        if "organic" in results_data and len(results_data["organic"]) > 0:
            test_url = results_data["organic"][0].get("link")
    except json.JSONDecodeError:
        pass  # Can't parse search results

    if test_url:
        print(f"Attempting to scrape URL: {test_url}")
        scrape_result = scrape(test_url)
        print(
            f"Scrape result for '{test_url}':\n{scrape_result[:500]}..."
        )  # Print first 500 chars
    else:
        # Fallback URL if search fails or returns no results
        fallback_url = "https://example.com"
        print(
            f"Search did not yield a URL. Testing scrape with fallback: {fallback_url}"
        )
        scrape_result = scrape(fallback_url)
        print(f"Scrape result for '{fallback_url}':\n{scrape_result}")
