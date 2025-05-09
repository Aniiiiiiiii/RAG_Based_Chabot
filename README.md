# Chatbot Using RAG

Chatbot Using RAG (Retrieval-Augmented Generation) is a project that leverages web search, document scraping, and a fine-tuned Transformer model to generate answers to user questions by retrieving and grounding responses on real-world data.

## Project Structure

- **app/**  
  - **api/**  
    - [answer.py](app/api/endpoints/answer.py): API endpoint that receives questions and returns generated answers.
  - **core/**  
    - [config.py](app/core/config.py): Loads environment variables.  
    - [utils.py](app/core/utils.py): Contains helper functions such as keyword extraction and question hashing.
  - **database/**  
    - [connection.py](app/database/connection.py): Database connection and session management.  
    - [models.py](app/database/models.py): SQLAlchemy models, including the `ScrapedParagraph` model.
  - **services/**  
    - [search.py](app/services/search.py): Contains functions for generating search queries, performing Google searches, and generating answers using Transformers.  
    - [scraping.py](app/services/scraping.py): Contains functions for scraping web content and managing scraped data.
- **main.py**: Main entry point for running a standalone search-and-answer script.
- **custom_script.py**: A utility script to sync environment dependencies with build configuration.
- **environment.yml**: Conda environment file listing dependencies.
- **pyproject.toml**: Build configuration for the project.
- **testing.ipynb** & **training.ipynb**: Jupyter notebooks for testing and training the model.

## Setup & Installation

1. **Clone the repository:**
   ```sh
   git clone <repository_url>
   cd RAG_Based_Chabot
   ```

2. **Create the Environment:**
   Use the provided Conda environment file:
   ```sh
   conda env create -f environment.yml
   conda activate <your_env_name>
   ```
   Alternatively, you can install the pip dependencies listed in the `pyproject.toml` if you prefer a pip install.

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory with the following content:
   ```
   DATABASE_URL="postgresql://myuser:mypassword@192.168.49.2:32533/ragmodel"
   GOOGLE_API_KEY="your_google_api_key"
   GOOGLE_CX_ID="your_google_cx_id"
   ```

## Running the Project

- **FastAPI Server:**  
  To start the API server run:
  ```sh
  uvicorn app.main:app --host <your_host> --port 8000
  ```
- **Standalone Script:**  
  You can also run the main script to test the retrieval and answer generation:
  ```sh
  python main.py
  ```

## Training & Testing

- **Training:**  
  Use the [training.ipynb](training.ipynb) notebook to train the model.
- **Testing:**  
  Use the [testing.ipynb](testing.ipynb) notebook for interactive testing and evaluation.

## Usage

The primary API endpoint `/answer` accepts a JSON payload containing a user's question and returns a generated answer. See [answer.py](app/api/endpoints/answer.py) for implementation details.

## Customization

- **Services:**  
  Modify search or scraping behavior in [search.py](app/services/search.py) and [scraping.py](app/services/scraping.py).
- **Database:**  
  Update database models and connection parameters in [models.py](app/database/models.py) and [connection.py](app/database/connection.py).

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request with your improvements.

## License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.