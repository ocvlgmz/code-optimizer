import streamlit as st
import openai
import requests
from langdetect import detect
import os

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access your environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
# print(openai_api_key)

# Function to fetch files from the GitHub repository
def fetch_files_from_github(repo_url):
    api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/git/trees/master?recursive=1"
    response = requests.get(api_url)
    
    print(f"API URL: {api_url}")  # Debug print
    print(f"Response Status: {response.status_code}")  # Debug print
    print(f"Response Content: {response.json()}")  # Debug print

    if response.status_code == 200:
        file_tree = response.json().get("tree", [])
        return [file["path"] for file in file_tree if file["type"] == "blob"]  # Only include files
    return []

# Function to fetch file content
def fetch_file_content(repo_url, file_path):
    raw_url = repo_url.replace("https://github.com/", "https://raw.githubusercontent.com/") + f"/master/{file_path}"
    response = requests.get(raw_url)
    if response.status_code == 200:
        return response.text
    return None

# Function to detect language
def detect_language(code):
    return detect(code)

# Function to get code recommendations
def get_code_recommendations(code, language):
    openai.api_key = openai_api_key  # Replace with your OpenAI API key

    # Create the messages structure for the chat model
    messages = [
        {
            "role": "user",
            "content": f"Here is a {language} code snippet:\n\n{code}\n\nPlease provide optimizations and improvements for this code."
        }
    ]

    # Use the chat model for the request
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or your chosen chat model
            messages=messages,
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()  # Adjust for chat model response structure
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while getting recommendations."

# Main function to run the Streamlit app
def main():
    st.title("Repository Code Optimization AI")

    # Input for the GitHub repository URL
    github_repo_url = st.text_input("Enter the GitHub repository URL", "")

    if github_repo_url:
        with st.spinner("Fetching files from the repository..."):
            file_paths = fetch_files_from_github(github_repo_url)

        if file_paths:
            if st.button("Get Recommendations for All Files"):
                with st.spinner("Analyzing the repository code..."):
                    for file_path in file_paths:
                        file_content = fetch_file_content(github_repo_url, file_path)
                        if file_content:
                            language = detect_language(file_content)
                            recommendations = get_code_recommendations(file_content, language)
                            st.write(f"\n**Recommendations for {file_path}:**")
                            st.write(recommendations)
                        else:
                            st.write(f"Couldn't fetch content for {file_path}")

if __name__ == "__main__":
    main()
