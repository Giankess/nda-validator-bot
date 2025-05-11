import os
import glob
import json
import requests
from typing import List, Dict
import argparse

def find_training_documents(base_dir: str) -> Dict[str, List[str]]:
    """Find all training documents in the specified directory."""
    documents = {
        "original": [],
        "redline": [],
        "clean": []
    }
    
    # Look for documents in subdirectories
    for doc_type in documents.keys():
        pattern = os.path.join(base_dir, doc_type, "*.docx")
        documents[doc_type] = sorted(glob.glob(pattern))
    
    return documents

def validate_training_data(documents: Dict[str, List[str]]) -> bool:
    """Validate that we have matching sets of documents."""
    lengths = [len(docs) for docs in documents.values()]
    if not all(length == lengths[0] for length in lengths):
        print("Error: Unequal number of documents in each category")
        return False
    
    # Check that document names match across categories
    for i in range(len(documents["original"])):
        orig_name = os.path.basename(documents["original"][i])
        redline_name = os.path.basename(documents["redline"][i])
        clean_name = os.path.basename(documents["clean"][i])
        
        base_name = orig_name.replace("_original.docx", "")
        if not (redline_name.startswith(base_name) and clean_name.startswith(base_name)):
            print(f"Error: Document names don't match for index {i}")
            return False
    
    return True

def train_model(base_dir: str, api_url: str = "http://localhost:8000"):
    """Train the model using the documents in the specified directory."""
    # Find all training documents
    documents = find_training_documents(base_dir)
    
    # Validate the training data
    if not validate_training_data(documents):
        return
    
    print(f"Found {len(documents['original'])} sets of training documents")
    
    # Prepare training data
    training_data = {
        "original_docs": documents["original"],
        "redline_docs": documents["redline"],
        "clean_docs": documents["clean"]
    }
    
    # Send training request
    try:
        response = requests.post(f"{api_url}/train", json=training_data)
        response.raise_for_status()
        
        results = response.json()
        print("\nTraining Results:")
        print(f"Model saved to: {results['model_dir']}")
        print(f"Number of training samples: {results['num_training_samples']}")
        print("\nEvaluation Results:")
        print(json.dumps(results['evaluation_results'], indent=2))
        
        # Load the trained model
        load_response = requests.post(f"{api_url}/load-model", json={"model_dir": results['model_dir']})
        load_response.raise_for_status()
        print("\nModel loaded successfully")
        
    except requests.exceptions.RequestException as e:
        print(f"Error during training: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Train the NDA Validator model")
    parser.add_argument("--data-dir", required=True, help="Directory containing training documents")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL for the backend")
    
    args = parser.parse_args()
    train_model(args.data_dir, args.api_url)

if __name__ == "__main__":
    main() 