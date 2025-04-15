# AI Article Generator

This Streamlit application uses an AI agent (LlamaIndex ReActAgent with GPT-4.1) to generate HTML articles based on user-provided keywords. The agent searches the web for relevant information using Serper and scrapes content using Firecrawl before synthesizing the final article.

## Features

*   Enter keywords to define the article topic.
*   AI agent searches the web for relevant sources.
*   AI agent scrapes content from selected sources.
*   AI agent synthesizes information and writes an article in HTML format.
*   Displays the generated HTML article directly in the app.

## Setup

1.  **Clone the repository (or ensure you have the files):**
    ```bash
    # If you have git installed
    # git clone <repository_url>
    # cd <repository_directory>
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    *Note: Since you are using fish, use `source venv/bin/activate.fish`*

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create and populate the `.env` file:**
    *   Make sure you have a file named `.env` in the project's root directory.
    *   Add your API keys to this file:
        ```dotenv
        OPENAI_API_KEY="sk-..."
        SERPER_API_KEY="..."
        FIRECRAWL_API_KEY="..."
        ```
    *   Replace the placeholder values with your actual keys.

## Running the Application

1.  **Ensure your virtual environment is activated.**

2.  **Run the Streamlit app from your terminal:**
    ```bash
    streamlit run app.py
    ```

3.  Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

4.  Enter keywords in the text box and click "Generate Article". Wait for the process to complete.

## Files

*   `app.py`: The main Streamlit application file.
*   `article_generator.py`: Contains the `ArticleGenerator` class, which manages the AI agent and article generation logic.
*   `tools.py`: Defines the `search` (Serper) and `scrape` (Firecrawl) functions used by the agent.
*   `requirements.txt`: Lists the required Python packages.
*   `.env`: Stores API keys (needs to be created manually).
*   `README.md`: This file. 