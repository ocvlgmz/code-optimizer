import streamlit as st
import openai
import requests
from langdetect import detect
import os
from dotenv import load_dotenv
from fpdf import FPDF

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


def generate_pdf(recommendations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Code Optimization Recommendations", ln=True, align='C')
    pdf.ln(10)  # Line break

    for rec in recommendations:
        pdf.multi_cell(0, 10, txt=rec)

    # Save the PDF to a file
    pdf_file_path = "recommendations.pdf"
    pdf.output(pdf_file_path)

    return pdf_file_path

def main():
    st.title("Repository Code Optimization AI")

    # Input for the GitHub repository URL
    github_repo_url = st.text_input("Enter the GitHub repository URL", "")

    # List of allowed code file extensions
    allowed_extensions = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.rb', '.go', '.php']

    if github_repo_url:
        # Extracting repository name from the URL
        repo_name = github_repo_url.split("/")[-1]  # Get the last part of the URL
        repo_name = repo_name.split(".")[0]  # Remove the ".git" if it exists

        file_paths = fetch_files_from_github(github_repo_url)
        if file_paths:
            st.subheader("Files Detected in the Repository")
            code_file_paths = []  # To hold only code files
            
            for file_path in file_paths:
                # Check if the file has an allowed extension
                if any(file_path.endswith(ext) for ext in allowed_extensions):
                    code_file_paths.append(file_path)
                    st.write(f"Code File: {file_path}")
                else:
                    st.write(f"Ignored File: {file_path}")  # Show ignored files

            if st.button("Get Recommendations for All Code Files"):
                with st.spinner("Analyzing the repository code..."):
                    recommendations = []
                    for file_path in code_file_paths:
                        file_content = fetch_file_content(github_repo_url, file_path)
                        if file_content:
                            language = detect_language(file_content, file_path)
                            st.write(f"\n**File: {file_path}**")
                            st.write(f"Detected Language: {language}")
                            recommendation = get_code_recommendations(file_content, language)
                            st.write(recommendation)  # Display recommendation on the webpage
                            recommendations.append(f"File: {file_path}\nRecommendation: {recommendation}")
                        else:
                            st.write(f"Couldn't fetch content for {file_path}")

                    # Generate PDF after getting all recommendations
                    pdf_file = generate_pdf(recommendations)

                    # Creating a dynamic file name with the repository name
                    pdf_file_name = f"{repo_name}_recommendations.pdf"
                    st.success("Recommendations saved to PDF!")
                    st.download_button(
                        label="Download PDF",
                        data=open(pdf_file, "rb").read(),
                        file_name=pdf_file_name,  # Use the dynamic file name here
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()
