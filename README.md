# TCXII-team-6

This project contains the **backend** and the **frontend** for an AI ticketing system agent.

### Getting Started

1. Clone the repository
2. `cd back-end`
3. Install requirements: `pip install -r requirements.txt`
4. Run the server:
    ```bash
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
5. run `cd ../front-end`
6. Install requirements: `npm install`
7. Run the server :  `npm run dev`
8. You can interact with the agent , create tickets and send them via the url shown in the console , eg : [http://localhost:3000](http://localhost:3000) 
### Features

- **Multi-document OCR** - Supports PDF, TXT, and image file processing
- **Intelligent Ticket Pipeline** - Streamlined workflow for:
  - Processing client tickets
  - Responding based on knowledge base
  - Escalating to human support with documented reasons
  - Supports multiple languages
