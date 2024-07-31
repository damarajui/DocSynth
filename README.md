# DocSynth: Concise Setup Guide Generator

DocSynth is an advanced Retrieval-Augmented Generation (RAG) system designed to synthesize long and short developer documentation into concise, user-friendly quick setup instructions.

## Features

- Intelligent document parsing and information extraction
- Multi-document summarization using state-of-the-art NLP techniques
- Customizable output formats for different user needs
- Continuous learning from user feedback
- Support for multiple programming languages and frameworks

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/docsynth.git
   cd docsynth
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your `.env` file with necessary API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   REDIS_URL=redis://localhost:6379
   CHROMA_DB_PATH=./data/chroma_db
   ```

5. Run the API:
   ```
   uvicorn app.main:app --reload
   ```

6. In a separate terminal, run the Streamlit UI:
   ```
   streamlit run ui/streamlit_app.py
   ```

## Usage

1. Open your web browser and go to `http://localhost:8501` to access the Streamlit UI.
2. Enter documentation URLs or upload files.
3. Select the project type from the available options: Web, Mobile, Desktop, API, or Other.
4. Click "Generate Setup Guide" to create a concise guide based on the input.
5. Review the generated guide and provide feedback using the rating slider and comments section.

## Project Structure

- `app/`: Contains the main application code
  - `main.py`: FastAPI application entry point
  - `database.py`: ChromaDB integration for document storage and retrieval
  - `models.py`: Pydantic models for data validation
  - `summarizer.py`: Text summarization and guide generation logic
  - `feedback_handler.py`: Handles user feedback and guide improvements
- `ui/`: Contains the Streamlit user interface
  - `streamlit_app.py`: Streamlit application for user interaction
- `tests/`: Contains test files for the application

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.