# Intelligent Invoice Processing System

This project demonstrates an intelligent agent-based system designed to classify and process various formats of invoice data. It leverages a modular architecture with specialized agents for different tasks, including format classification, data extraction from plain text, JSON, and email content, and a shared memory for maintaining context.

## ✨ Features

* **Intelligent Classification:** A dedicated `InvoiceClassifierAgent` to automatically detect the format (plain text, JSON, email) of incoming invoice data.

* **Modular Agent Design:**

    * `InvoiceProcessingAgent`: Processes plain text invoices, extracting structured data.

    * `JSONAgent`: Handles structured JSON invoice payloads, transforming them to a target schema and flagging anomalies.

    * `EmailAgent`: Extracts invoice details from email content, including sender and subject.

* **Shared Memory:** A `SharedMemory` module to store and retrieve interaction-specific data across different agents.

* **Extensible:** Designed to be easily extended with new agents or improved classification/processing logic.

* **LLM Integration (Optional):** Supports integration with Large Language Models (like Google Gemini) for more advanced intent classification (currently commented out but ready for activation).

## 📂 Project Structure

' ' ' ' ' 
.
├── main.py                     # Main entry point for the application
├── memory.py                   # Implements the SharedMemory class
└── agents/                     # Directory containing all specialized agents
├── init.py             # Makes 'agents' a Python package
├── classifier_agent.py     # Handles input classification and routing
├── email_agent.py          # Processes email content containing invoices
├── invoice_processing_agent.py # Processes plain text invoices
└── json_agent.py           # Processes JSON invoice payloads
├── .env.example                # Example file for environment variables (e.g., API keys)
├── dummyplain.txt              # Example plain text invoice file
├── dummyjson.txt               # Example JSON invoice file
└── dummyemail.txt              # Example email with invoice content
' ' ' ' '

# Tech Stacks
![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54)
![Gemini LLM](https://img.shields.io/badge/Gemini-3670A0?style=plastic&logo=Gemini&logoColor=ff0000)
## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

* Python 3.8+

* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**

    ```
    git clone [https://github.com/your-username/intelligent-invoice-system.git](https://github.com/your-username/intelligent-invoice-system.git)
    cd intelligent-invoice-system
    
    ```

    *(Replace `your-username` with your actual GitHub username or the repository's URL)*

2.  **Create a virtual environment (recommended):**

    ```
    python -m venv .venv
    
    ```

3.  **Activate the virtual environment:**

    * **On Windows:**

        ```
        .venv\Scripts\activate
        
        ```

    * **On macOS/Linux:**

        ```
        source .venv/bin/activate
        
        ```

4.  **Install dependencies:**

    ```
    pip install -r requirements.txt
    
    ```

    *(If `requirements.txt` doesn't exist, you'll need to create it with `pip freeze > requirements.txt` after installing necessary packages like `google-generativeai`, `python-dotenv`.)*

    ```
    # Manually install if requirements.txt is not provided yet:
    pip install google-generativeai python-dotenv
    
    ```

### API Key Setup (for LLM Integration)

If you plan to use the LLM-based intent classification feature:

1.  Obtain an API key for Google Gemini (or your chosen LLM provider).

2.  Create a file named `.env` in the root directory of your project.

3.  Add your API key to the `.env` file:

    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    
    ```

    *(Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual key)*

## 💡 Usage

Run the `main.py` script and follow the prompts to provide invoice data.


python main.py


The application will prompt you to enter the path to an invoice file.

**Example Interactions:**

1.  **Processing a Plain Text Invoice:**

    * **Prompt:** `Enter the path to the invoice file, or 'exit':`

    * **Input:** `dummyplain.txt` (or the full path to your plain text invoice file)

    * **Expected Output:** The classifier will identify it as `plain_invoice`, and the `InvoiceProcessingAgent` will extract and print the structured data.

2.  **Processing a JSON Invoice:**

    * **Prompt:** `Enter the path to the invoice file, or 'exit':`

    * **Input:** `dummyjson.txt` (or the full path to your JSON invoice file)

    * **Expected Output:** The classifier will identify it as `json`, and the `JSONAgent` will process and print the reformatted data and any anomalies.

3.  **Processing an Email with Invoice Content:**

    * **Prompt:** `Enter the path to the invoice file, or 'exit':`

    * **Input:** `dummyemail.txt` (or the full path to your email invoice file)

    * **Expected Output:** The classifier will identify it as `email`, and the `EmailAgent` will extract sender, subject, and invoice details from the email body.

## 👥 Agents Overview

* **`SharedMemory` (`memory.py`):**

    * A simple in-memory key-value store to maintain context and share data between different agents based on a unique `interaction_id`.

* **`InvoiceClassifierAgent` (`agents/classifier_agent.py`):**

    * **Role:** The entry point for classification. It determines the format (plain, JSON, email) of the input invoice data.

    * **Logic:** Uses string checks and basic regular expressions for format detection. Can be extended to use an LLM for more nuanced intent classification.

    * **Routing:** Directs the input to the appropriate specialized processing agent.

* **`InvoiceProcessingAgent` (`agents/invoice_processing_agent.py`):**

    * **Role:** Processes highly structured plain text invoices.

    * **Logic:** Uses specific regular expressions to extract fields like invoice number, date, seller/buyer details, line items, and totals. Includes basic validation and formatting for downstream use.

* **`JSONAgent` (`agents/json_agent.py`):**

    * **Role:** Handles invoice data provided in a JSON format.

    * **Logic:** Parses the JSON, extracts data according to a predefined target schema, and flags missing fields or structural anomalies. Supports recursive extraction for nested JSON.

* **`EmailAgent` (`agents/email_agent.py`):**

    * **Role:** Extracts invoice-related information from email content.

    * **Logic:** Identifies the sender, subject, and then uses regular expressions to pull out invoice numbers, dates, amounts, and line items from the email body. Designed for emails where the invoice details are structured within the plain text body.

## 🔮 Future Enhancements

* **Advanced Classifier:**

    * Integrate and fine-tune LLMs for more accurate and nuanced format and intent classification, especially for ambiguous inputs.

    * Implement confidence scores for classification.

* **Robust Email Parsing:** Use Python's built-in `email` library or `mail-parser` for more robust handling of complex email structures (MIME types, attachments, HTML bodies).

* **PDF Processing:** Add a dedicated agent or integrate a library (e.g., `pdfplumber`, `PyPDF2`, `Camelot`) for extracting text and tables from PDF invoice attachments.

* **Data Validation & Normalization:** Implement more comprehensive validation rules (e.g., date formats, currency consistency, numerical range checks) and data normalization across agents.

* **Database Integration:** Replace `SharedMemory` with a persistent database (e.g., SQLite, PostgreSQL, Firestore) for long-term storage of extracted invoice data and interaction logs.

* **Web Interface:** Develop a simple web UI (e.g., using Flask or FastAPI) to upload files or paste content for processing.

* **Anomaly Detection:** Implement more sophisticated anomaly detection logic (e.g., using machine learning) to identify unusual values or patterns in extracted data.

* **Configuration Files:** Externalize regex patterns, keywords, and target schemas into configuration files (e.g., YAML, JSON) for easier management and updates.

## 🤝 Contributing

Contributions are welcome! If you have suggestions or improvements, please feel free to:

1.  Fork the repository.

2.  Create a new branch (`git checkout -b feature/your-feature-name`).

3.  Make your changes.

4.  Commit your changes (`git commit -m 'feat: Add new feature'`).

5.  Push to the branch (`git push origin feature/your-feature-name`).

6.  Open a Pull Request.

