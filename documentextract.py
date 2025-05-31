import os
import pdfplumber
import json
import re

def extract_text_from_pdf(pdf_path):
    all_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text += text + "\n\n"  # Add newlines to separate pages
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
    except Exception as e:
        print(f"An error occurred during PDF text extraction: {e}")
    return all_text.strip()

if __name__ == "__main__":
    pdf_file_path = r"C:\Users\ravik\Downloads\Document Extraction 1.pdf"  # Replace with your PDF path
    output_text_file = "extracted_text.txt"  # Output text file path

    extracted_text = extract_text_from_pdf(pdf_file_path)

    if extracted_text:
        with open(output_text_file, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)
        print(f"Text successfully extracted and saved to {output_text_file}")
    else:
        print("Text extraction failed.")