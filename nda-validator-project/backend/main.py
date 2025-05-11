from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from services.document_service import DocumentService
from services.ai_service import AIService
from services.memory_service import MemoryService
from services.training_service import TrainingService

app = FastAPI(title="NDA Validator AI Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
ai_service = AIService()
memory_service = MemoryService()
training_service = TrainingService()

class Feedback(BaseModel):
    document_id: str
    feedback_text: str

class TrainingData(BaseModel):
    original_docs: List[str]
    redline_docs: List[str]
    clean_docs: List[str]

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        document_id = await document_service.parse_document(file)
        return {"document_id": document_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/{document_id}")
async def analyze_document(document_id: str):
    try:
        document = await document_service.get_document(document_id)
        analysis = await ai_service.check_document(document)
        suggestions = await ai_service.make_suggestions(analysis)
        validated_suggestions = await ai_service.validate_suggestions(suggestions)
        redline_doc = await document_service.create_redline_document(document, validated_suggestions)
        return {"redline_document_id": redline_doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/feedback")
async def process_feedback(feedback: Feedback):
    try:
        interpreted_feedback = await ai_service.interpret_feedback(feedback.feedback_text)
        await memory_service.save_feedback(feedback.document_id, interpreted_feedback)
        new_suggestions = await ai_service.adjust_suggestions(feedback.document_id, interpreted_feedback)
        redline_doc = await document_service.create_redline_document(
            await document_service.get_document(feedback.document_id),
            new_suggestions
        )
        return {"redline_document_id": redline_doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accept/{document_id}")
async def accept_suggestions(document_id: str):
    try:
        clean_doc = await document_service.create_clean_document(document_id)
        return {"clean_document_id": clean_doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/{document_id}")
async def download_document(document_id: str):
    try:
        return await document_service.return_document(document_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/train")
async def train_model(training_data: TrainingData):
    try:
        # Prepare training data
        texts, labels = training_service.prepare_training_data(
            training_data.original_docs,
            training_data.redline_docs,
            training_data.clean_docs
        )
        
        # Train the model
        model_dir = training_service.train_model(texts, labels)
        
        # Evaluate the model
        evaluation_results = training_service.evaluate_model(texts[-100:], labels[-100:])  # Use last 100 samples for evaluation
        
        return {
            "model_dir": model_dir,
            "evaluation_results": evaluation_results,
            "num_training_samples": len(texts)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/load-model")
async def load_trained_model(model_dir: str):
    try:
        training_service.load_trained_model(model_dir)
        return {"status": "Model loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 