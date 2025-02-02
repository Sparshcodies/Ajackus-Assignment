# Ajackus-Assignment

Assessment for the role of AI/ML Intern

## Overview

This project demonstrates a natural language SQL query generator and executor. It leverages an LLM (Codellama via Ollama) to convert human-readable queries into SQL, executes those queries on a pre-created SQLite database, and displays the results through an interactive Streamlit GUI.

## Requirements

- Python 3.x
- SQLite (bundled with Python)
- [Ollama](https://ollama.com/download)
- The Codellama model (approximately 4GB in size)
- Streamlit

## Setup Instructions

### 1. Clone the Repository

Clone the repository using the following command:

```bash
git clone https://github.com/Sparshcodies/Ajackus-Assignment.git
```

### 2. Install Python Dependencies

Navigate to the project directory and install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Download and install Ollama on your host system. Visit the [Ollama Download Page](https://ollama.com/download) and follow the installation instructions for your operating system.

### 4. Download the Codellama Model

After installing Ollama, download the Codellama model by running:

```bash
ollama run codellama
```

*Note: The model is approximately 4GB in size, so ensure you have sufficient storage and a stable internet connection.*

### 5. Create the Database

The SQLite database (and its tables) has already been created using the `database_creation.py` script. To recreate or update the database, run:

```bash
python database_creation.py
```

This script creates the necessary tables and imports data from CSV files (make sure the CSV files are present in the project directory).

### 6. Run the Streamlit Interface

Launch the Streamlit GUI with the following command:

```bash
streamlit run app.py
```

Once the GUI is running, enter your natural language queries into the text box. The system will generate the corresponding SQL query (displaying it for review), execute it on the database, and show the results in a formatted table.

## Usage

- **Query Input:** Enter your query (e.g., "List the employee with name starting with 's'") in the provided text area.
- **SQL Generation:** The system converts your query into SQL. If the generated SQL contains potentially unsafe code (e.g., DROP, DELETE), you will be prompted to confirm before execution.
- **Results Display:** Query results are displayed in a neat, tabular format using Streamlit’s data display functions.

## Additional Notes

- **Safety Measures:** Although the system supports all kinds of SQL queries, safety checks are in place. If a query is flagged as unsafe, you'll be asked, "Do you really wish to proceed?" before execution.
- **Local LLM Integration:** This project uses a locally installed LLM (via Ollama) for natural language to SQL conversion.
- **Data Files:** Ensure that your CSV files and the generated `database.db` file are located in the project directory.

