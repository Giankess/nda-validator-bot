# NDA Validator AI Assistant

An AI-powered NDA validation tool that helps review and improve Non-Disclosure Agreements using the legal-bert model.

## Features

- Upload and analyze NDA documents
- AI-powered suggestions for problematic clauses
- Redline document generation with suggested changes
- User feedback system for continuous improvement
- Long-term memory for learning from past NDAs
- Self-reflection through dual-model validation

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- legal-bert-base-uncased model
- ChromaDB for long-term memory
- python-docx for document handling

### Frontend
- React
- Material-UI
- Hubersuhner corporate design
- React Router
- Axios for API communication

## Setup

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Upload an NDA document (.docx format)
3. Review the AI suggestions
4. Choose to either:
   - Accept all suggestions to get a clean version
   - Provide feedback for further refinement
5. Download the final document

## API Endpoints

- `POST /upload` - Upload an NDA document
- `POST /analyze/{document_id}` - Analyze document and get suggestions
- `POST /feedback` - Submit feedback on suggestions
- `POST /accept/{document_id}` - Accept suggestions and get clean version
- `GET /download/{document_id}` - Download document

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 