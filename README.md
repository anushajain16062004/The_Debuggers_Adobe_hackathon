# PDF Analysis Toolkit

This repository provides two complementary PDF analysis tools:

- **`adobe(A)`** – A standalone script (`round1a.py`) that extracts titles and headings from PDFs using layout heuristics and table of contents (TOC).
- **`adobe(B)`** – A Flask-based API (`analyze.py`) that extracts and semantically analyzes section headings from PDFs based on user persona configurations.

---

## adobe(A) – Local PDF Title and Heading Extractor

### Functionality

- Extracts the **document title** based on font size and boldness from the first page.
- Detects **headings** from:
  - **Table of Contents (TOC)** if available
  - **Font size and layout patterns** otherwise

---

## adobe(B) – Flask API for Persona-Based PDF Analysis

### Functionality

- Extracts **text spans** relevant to the specified persona using:
  - Minimum font size
  - Boldness
  - Keywords
- Computes **semantic similarity** between sections using **Sentence Transformers**
- Returns **sections** and their **connections** (if similarity > 0.7)

---

## Docker Support

Both `adobe(A)` and `adobe(B)` are Dockerized.

### Running with Docker Compose

From root directories:

```bash
# For adobe(A)
cd adobe(A)/code
docker-compose up --build

# For adobe(B)
cd adobe(B)
docker-compose up --build
```
# Dependencies

Both tools require the following Python libraries:

- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)** – For PDF text extraction
- **[Flask](https://flask.palletsprojects.com/)** – Web backend server (only used in `adobe(B)`)
- **[sentence-transformers](https://www.sbert.net/)** – For computing semantic similarity between text segments
- **[Flask-CORS](https://flask-cors.readthedocs.io/)** – Enables Cross-Origin Resource Sharing in the Flask app
- **regex, json** – Built-in Python modules used for pattern matching and data serialization



