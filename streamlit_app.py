import streamlit as st
import logging
import re
import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
from langchain_ollama.llms import OllamaLLM
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ColumnInfo:
    name: str
    data_type: str
    is_nullable: bool
    is_primary: bool
    foreign_key: Optional[str] = None

class LocalDatabaseAssistant:
    def __init__(self, model_name: str = "codellama"):
        self.db_path = "database.db"
        self.conn = None
        self.schema_info: Dict[str, List[ColumnInfo]] = {}
        self.relationships = {}
        try:
            self.llm = OllamaLLM(model=model_name, temperature=0.1)
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise
        self.system_prompt = (
            "You are a precise SQL query generator that converts natural language to SQL.\n"
            "Follow these rules strictly:\n"
            "1. Only generate SELECT statements.\n"
            "2. Use exact column names from the schema.\n"
            "3. Include JOIN conditions only when the query requires data from more than one table.\n"
            "4. Add appropriate WHERE clauses for filtering.\n"
            "5. Use appropriate aggregation functions when necessary.\n"
            "6. Always alias complex columns for readability.\n"
            "7. Return ONLY the SQL query without any explanation or markdown."
        )


    def _validate_query(self, query: str) -> bool:
        """
        Validate generated SQL query. Returns True if no unsafe patterns are found,
        otherwise returns False.
        """
        if not query or not isinstance(query, str):
            return False
        unsafe_patterns = [
            r";\s*\w",  # Disallow multiple statements
            r"--",      # Disallow comments
            r"/\*",     # Disallow block comments
            r"\bUNION\b",
            r"\bINTO\b",
            r"\bDROP\b",
            r"\bDELETE\b",
            r"\bUPDATE\b",
            r"\bINSERT\b",
            r"\bALTER\b",
            r"\bCREATE\b",
            r"\bTRUNCATE\b"
        ]
        for pattern in unsafe_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Unsafe SQL pattern detected: {pattern}")
                return False
        return True

    def _generate_sql_query(self, user_query: str) -> str:
        """Generate SQL query using the LLM."""
        # Build schema text from current schema_info
        schema_text = "Database Schema:\n"
        for table, columns in self.schema_info.items():
            schema_text += f"\nTable: {table}\n"
            for col in columns:
                schema_text += f"- {col.name} ({col.data_type})"
                if col.foreign_key:
                    schema_text += f" -> {col.foreign_key}"
                schema_text += "\n"
        prompt = (
            f"<system>{self.system_prompt}</system>\n"
            f"Generate a SQL query for: \"{user_query}\"\n"
            f"Using this schema:\n{schema_text}\n"
            "Return ONLY the SQL query without any explanations or markdown."
        )
        generated_query = self.llm(prompt).strip()
        # Remove markdown formatting if present
        if "```sql" in generated_query:
            match = re.search(r"```sql\n(.*?)\n```", generated_query, re.DOTALL)
            if match:
                generated_query = match.group(1).strip()
        logger.info(f"Generated SQL query: {generated_query}")
        return generated_query

    def initialize_database(self):
        """Connect to the pre-created database and load schema information."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._analyze_schema()
        self._detect_relationships()
        logger.info("Database initialized successfully")

    def _analyze_schema(self):
        """Analyze database schema and store column details."""
        if not self.conn:
            raise Exception("Database connection not initialized")
        cursor = self.conn.cursor()
        for table in ['Employees', 'Departments']:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = cursor.fetchall()
            self.schema_info[table] = []
            for col in columns:
                column_info = ColumnInfo(
                    name=col[1],
                    data_type=col[2].upper(),
                    is_nullable=not col[3],
                    is_primary=bool(col[5])
                )
                for fk in foreign_keys:
                    if fk[3] == column_info.name:
                        column_info.foreign_key = f"{fk[2]}.{fk[4]}"
                self.schema_info[table].append(column_info)

    def _detect_relationships(self):
        """Detect and store foreign key relationships."""
        cursor = self.conn.cursor()
        for table in self.schema_info.keys():
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = cursor.fetchall()
            self.relationships[table] = [
                {
                    'from_table': table,
                    'to_table': fk[2],
                    'from_column': fk[3],
                    'to_column': fk[4]
                }
                for fk in foreign_keys
            ]
        logger.info("Table relationships detected successfully")

    def process_query(self, user_query: str, force_execute: bool = False) -> Dict:
        """
        Generate, validate, and execute SQL query from a natural language query.
        If the generated query is unsafe and force_execute is False, it returns a warning.
        Returns a dictionary with keys: 'sql_query', 'results' (as a DataFrame or None), and 'warning' if any.
        """
        if not self.conn:
            return {"error": "Please initialize the database first."}
        try:
            sql_query = self._generate_sql_query(user_query)
            unsafe = not self._validate_query(sql_query)
            result = {"sql_query": sql_query}
            if unsafe and not force_execute:
                result["warning"] = "The generated SQL query contains potentially unsafe code. Do you really wish to proceed?"
                return result
            logger.info(f"Executing SQL Query: {sql_query}")
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA query_timeout = 5000")
            cursor.execute(sql_query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                result["results"] = None
            else:
                df = pd.DataFrame(rows, columns=columns)
                result["results"] = df
            return result
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            return {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {"error": f"Error processing query: {str(e)}"}

    def close(self):
        if self.conn:
            self.conn.close()

# --- Streamlit UI Section ---

st.set_page_config(page_title="Database Query Assistant", page_icon="🤖", layout="wide")
st.title("🤖 Natural Language Database Query Assistant")
st.markdown("This assistant converts your natural language queries into SQL queries using an LLM, then executes them on a pre-created SQLite database.")

# Initialize session state for the assistant if not already done
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
    st.session_state.is_initialized = False

with st.sidebar:
    st.header("Configuration")
    model_name = st.selectbox("Select LLM Model", options=["codellama", "llama2"], index=0)
    if st.button("Initialize Database"):
        try:
            assistant = LocalDatabaseAssistant(model_name=model_name)
            assistant.initialize_database()
            st.session_state.assistant = assistant
            st.session_state.is_initialized = True
            st.success("Database initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing database: {str(e)}")

if st.session_state.is_initialized:
    with st.expander("View Database Schema"):
        for table, columns in st.session_state.assistant.schema_info.items():
            st.subheader(f"Table: {table}")
            col_data = [
                [col.name, col.data_type, "Yes" if col.is_nullable else "No",
                 "Yes" if col.is_primary else "No", col.foreign_key or "None"]
                for col in columns
            ]
            st.table({
                "Column": [c[0] for c in col_data],
                "Type": [c[1] for c in col_data],
                "Nullable": [c[2] for c in col_data],
                "Primary Key": [c[3] for c in col_data],
                "Foreign Key": [c[4] for c in col_data]
            })

    user_query = st.text_area("Enter your query in natural language:", height=100,
                              placeholder="Example: What is the average salary in the Marketing department?")
    if st.button("Run Query"):
        if user_query:
            try:
                with st.spinner("Processing query..."):
                    # Generate and display the SQL query
                    result = st.session_state.assistant.process_query(user_query)
                    sql_query = result.get("sql_query", "")
                    with st.expander("View Generated SQL"):
                        st.code(sql_query, language="sql")
                    # Check for unsafe query warning
                    if "warning" in result:
                        st.warning(result["warning"])
                        proceed = st.checkbox("I confirm that I wish to proceed with this query")
                        if not proceed:
                            st.info("Query execution aborted by user.")
                        else:
                            # Force execution by reprocessing with force_execute=True
                            result = st.session_state.assistant.process_query(user_query, force_execute=True)
                    # Display query results if available
                    if result.get("results") is None:
                        st.info("No results found.")
                    elif "error" in result:
                        st.error(result["error"])
                    else:
                        st.subheader("Query Results")
                        st.dataframe(result["results"])
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please enter a query.")
else:
    st.info("Please initialize the database using the sidebar button.")
