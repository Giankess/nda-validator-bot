from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import os
from docx import Document
import json
from datetime import datetime

class NDADataset(Dataset):
    def __init__(self, texts: List[str], labels: List[int], tokenizer):
        self.encodings = tokenizer(texts, truncation=True, padding=True, max_length=512)
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

class TrainingService:
    def __init__(self):
        self.model_name = "nlpaueb/legal-bert-base-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.training_dir = "training_data"
        os.makedirs(self.training_dir, exist_ok=True)

    def prepare_training_data(self, original_docs: List[str], redline_docs: List[str], clean_docs: List[str]) -> Tuple[List[str], List[int]]:
        """Prepare training data from original, redline, and clean documents."""
        texts = []
        labels = []

        for orig, redline, clean in zip(original_docs, redline_docs, clean_docs):
            # Extract paragraphs from documents
            orig_paras = self._extract_paragraphs(orig)
            redline_paras = self._extract_paragraphs(redline)
            clean_paras = self._extract_paragraphs(clean)

            # Create training pairs
            for orig_para, redline_para, clean_para in zip(orig_paras, redline_paras, clean_paras):
                if orig_para != clean_para:  # Only include changed paragraphs
                    texts.append(orig_para)
                    # Label 1 if the change was accepted in clean version, 0 if not
                    labels.append(1 if clean_para == redline_para else 0)

        return texts, labels

    def train_model(self, texts: List[str], labels: List[int], output_dir: str = "fine_tuned_model"):
        """Fine-tune the model on the prepared data."""
        # Create dataset
        dataset = NDADataset(texts, labels, self.tokenizer)

        # Split into train and validation sets
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=100,
            save_strategy="steps",
            save_steps=100,
            load_best_model_at_end=True,
        )

        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
        )

        # Train the model
        trainer.train()

        # Save the model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)

        # Save training metadata
        metadata = {
            "training_date": datetime.now().isoformat(),
            "num_samples": len(texts),
            "model_name": self.model_name,
            "training_args": training_args.to_dict(),
        }
        with open(f"{output_dir}/training_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return output_dir

    def _extract_paragraphs(self, doc_path: str) -> List[str]:
        """Extract paragraphs from a Word document."""
        doc = Document(doc_path)
        return [para.text for para in doc.paragraphs if para.text.strip()]

    def evaluate_model(self, test_texts: List[str], test_labels: List[int]) -> Dict[str, float]:
        """Evaluate the fine-tuned model on test data."""
        test_dataset = NDADataset(test_texts, test_labels, self.tokenizer)
        
        # Get predictions
        predictions = []
        self.model.eval()
        with torch.no_grad():
            for item in test_dataset:
                outputs = self.model(**{k: v.unsqueeze(0) for k, v in item.items() if k != 'labels'})
                predictions.append(torch.argmax(outputs.logits, dim=1).item())

        # Calculate metrics
        correct = sum(p == l for p, l in zip(predictions, test_labels))
        accuracy = correct / len(test_labels)
        
        return {
            "accuracy": accuracy,
            "num_samples": len(test_labels),
            "correct_predictions": correct
        }

    def load_trained_model(self, model_dir: str):
        """Load a fine-tuned model."""
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir) 