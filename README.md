# Code Optimization Recommender

This application analyzes GitHub repositories and provides recommendations for code optimization on a per-file basis.

## Features

- Accepts GitHub repository URLs as input
- Analyzes code structure and patterns
- Generates optimization suggestions for each file
- Supports multiple programming languages

## How It Works

1. User submits a GitHub repository URL through the Streamlit interface.
2. The application fetches the file structure of the repository using the GitHub API.
3. For each file in the repository:
   - The file content is retrieved from the raw GitHub URL.
   - The programming language of the file is detected using the langdetect library.
   - The code is sent to OpenAI's GPT-3.5-turbo model for analysis.
   - The AI generates optimization and improvement recommendations for the code.
4. The application displays the recommendations for each file in the Streamlit interface.
5. The process is repeated for all files in the repository when the user clicks the "Get Recommendations for All Files" button.

This application uses the GitHub API to access repository contents, the langdetect library for language detection, and OpenAI's GPT-3.5-turbo model for code analysis and recommendation generation. It's built using Streamlit for the user interface, allowing for easy interaction and display of results.

## Installation

```bash
git clone https://github.com/yourusername/code-optimization-recommender.git
cd code-optimization-recommender
pip install -r requirements.txt

## Run
To run the application, use the following command:
streamlit run app.py
