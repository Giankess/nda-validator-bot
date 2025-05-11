from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Any, List
import numpy as np
from docx import Document

class AIService:
    def __init__(self):
        self.model_name = "nlpaueb/legal-bert-base-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.validation_model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # Define problematic clause patterns
        self.problematic_patterns = [
            "confidentiality",
            "non-disclosure",
            "intellectual property",
            "termination",
            "liability",
            "warranty",
            "indemnification"
        ]

    async def check_document(self, document: Document) -> Dict[str, Any]:
        """Analyze the document for problematic clauses."""
        analysis = {}
        
        for paragraph in document.paragraphs:
            if not paragraph.text.strip():
                continue
                
            # Check for problematic patterns
            is_problematic = any(pattern in paragraph.text.lower() 
                               for pattern in self.problematic_patterns)
            
            if is_problematic:
                # Get model prediction
                inputs = self.tokenizer(paragraph.text, return_tensors="pt", 
                                      truncation=True, max_length=512)
                outputs = self.model(**inputs)
                prediction = torch.softmax(outputs.logits, dim=1)
                
                analysis[paragraph.text] = {
                    "is_problematic": True,
                    "confidence": float(prediction[0][1]),
                    "context": self._get_context(document, paragraph)
                }
        
        return analysis

    async def make_suggestions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate suggestions for problematic clauses."""
        suggestions = {}
        
        for clause, details in analysis.items():
            if details["is_problematic"]:
                # Generate suggestion based on the clause and context
                suggestion = self._generate_suggestion(clause, details["context"])
                suggestions[clause] = {
                    "suggestion": suggestion,
                    "confidence": details["confidence"]
                }
        
        return suggestions

    async def validate_suggestions(self, suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate suggestions using a second model."""
        validated_suggestions = {}
        
        for clause, details in suggestions.items():
            # Validate the suggestion
            inputs = self.tokenizer(details["suggestion"], return_tensors="pt",
                                  truncation=True, max_length=512)
            outputs = self.validation_model(**inputs)
            validation_score = float(torch.softmax(outputs.logits, dim=1)[0][1])
            
            if validation_score > 0.7:  # High confidence threshold
                validated_suggestions[clause] = details
            else:
                # If validation fails, keep original suggestion but mark it
                validated_suggestions[clause] = {
                    **details,
                    "needs_review": True
                }
        
        return validated_suggestions

    async def interpret_feedback(self, feedback: str) -> Dict[str, Any]:
        """Interpret user feedback and extract key points."""
        # Tokenize and analyze feedback
        inputs = self.tokenizer(feedback, return_tensors="pt",
                              truncation=True, max_length=512)
        outputs = self.model(**inputs)
        
        # Extract sentiment and key points
        sentiment = float(torch.softmax(outputs.logits, dim=1)[0][1])
        
        return {
            "sentiment": sentiment,
            "feedback_text": feedback,
            "key_points": self._extract_key_points(feedback)
        }

    async def adjust_suggestions(self, document_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust suggestions based on user feedback."""
        # Implementation would depend on the specific feedback and document context
        # This is a placeholder for the actual implementation
        return {}

    def _get_context(self, document: Document, paragraph) -> List[str]:
        """Get surrounding context for a paragraph."""
        context = []
        current_paragraph = paragraph
        
        # Get previous paragraph
        if current_paragraph._element.getprevious() is not None:
            prev_para = current_paragraph._element.getprevious()
            if prev_para.text.strip():
                context.append(prev_para.text)
        
        # Get next paragraph
        if current_paragraph._element.getnext() is not None:
            next_para = current_paragraph._element.getnext()
            if next_para.text.strip():
                context.append(next_para.text)
        
        return context

    def _generate_suggestion(self, clause: str, context: List[str]) -> str:
        """Generate a suggestion for a problematic clause."""
        # This is a simplified version - in practice, this would use more sophisticated
        # language generation techniques
        return f"Suggested revision: {clause}"

    def _extract_key_points(self, feedback: str) -> List[str]:
        """Extract key points from user feedback."""
        # Simple implementation - in practice, this would use NLP techniques
        # to identify key points and concerns
        return [point.strip() for point in feedback.split('.') if point.strip()] 