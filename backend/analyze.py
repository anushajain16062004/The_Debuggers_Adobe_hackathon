import fitz
import os
import json
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


class PDFAnalyzer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.persona_config = {
            "Travel Planner": {
                "keywords": {"itinerary": 3, "accommodation": 2, "transport": 2},
                "min_font_size": 11
            },
            "HR Professional": {
                "keywords": {"form": 3, "onboarding": 2, "compliance": 2},
                "min_font_size": 10
            },
            "Food Contractor": {
                "keywords": {"recipe": 3, "ingredients": 2, "vegetarian": 2},
                "min_font_size": 11
            }
        }

    def extract_title(self, doc):
        title = doc.metadata.get("title", "").strip()
        if title: return title
        first_page = doc[0].get_text().strip()
        return first_page.split('\n')[0][:100] if first_page else "Untitled"

    def analyze_text(self, span, persona):
        config = self.persona_config.get(persona, {})
        font_size = span["size"]
        is_bold = "bold" in span["font"].lower()
        return (font_size >= config.get("min_font_size", 11) and is_bold)

    def process_pdf(self, file_path, persona):
        with fitz.open(file_path) as doc:
            sections = []
            for page_num, page in enumerate(doc, 1):
                blocks = page.get_text("dict").get("blocks", [])
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            if text and self.analyze_text(span, persona):
                                sections.append({
                                    "text": text,
                                    "page": page_num,
                                    "document": os.path.basename(file_path)
                                })
            return sections

@app.route('/api/analyze', methods=['POST'])
def analyze_collection():
    analyzer = PDFAnalyzer()
    collection_name = request.json.get('collection')
    collection_path = f"./collections/{collection_name}"
    
    if not os.path.exists(collection_path):
        return jsonify({"error": "Collection not found"}), 404

    with open(f"{collection_path}/input.json") as f:
        config = json.load(f)
    
    results = {"sections": [], "connections": []}
    all_texts = []
    
    for filename in os.listdir(f"{collection_path}/PDFs"):
        if filename.endswith(".pdf"):
            pdf_results = analyzer.process_pdf(
                f"{collection_path}/PDFs/{filename}",
                config["persona"]["role"]
            )
            results["sections"].extend(pdf_results)
            all_texts.extend([s["text"] for s in pdf_results])
    
    # Find semantic connections
    if all_texts:
        embeddings = analyzer.model.encode(all_texts)
        for i, emb1 in enumerate(embeddings):
            for j, emb2 in enumerate(embeddings[i+1:], i+1):
                sim = util.cos_sim(emb1, emb2).item()
                if sim > 0.7:  # Threshold
                    results["connections"].append({
                        "source": i,
                        "target": j,
                        "strength": sim
                    })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
else:
    # This is needed for Gunicorn
    application = app