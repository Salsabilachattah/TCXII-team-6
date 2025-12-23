# TCXII-team-6

This project contains a **backend** and **frontend** for an AI ticketing system agent.

### Getting Started

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the server:
    ```bash
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

### Features

- **Multi-document OCR** - Supports PDF, TXT, and image file processing
- **Intelligent Ticket Pipeline** - Streamlined workflow for:
  - Processing client tickets
  - Responding based on knowledge base
  - Escalating to human support with documented reasons


