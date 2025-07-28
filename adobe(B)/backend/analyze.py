import fitz
import os
import json
import re
import tempfile
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
CORS(app)

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
        is_heading = (font_size >= config.get("min_font_size", 11) and is_bold)
        
        # Calculate importance based on keywords
        importance = 1
        text_lower = span["text"].lower()
        for keyword, weight in config.get("keywords", {}).items():
            if keyword.lower() in text_lower:
                importance = max(importance, weight)
        
        return is_heading, importance

    def process_pdf(self, file_path, persona):
        with fitz.open(file_path) as doc:
            sections = []
            for page_num, page in enumerate(doc, 1):
                blocks = page.get_text("dict").get("blocks", [])
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            if text:
                                is_heading, importance = self.analyze_text(span, persona)
                                if is_heading:
                                    sections.append({
                                        "text": text,
                                        "page": page_num,
                                        "document": os.path.basename(file_path),
                                        "importance": importance,
                                        "is_uploaded": not file_path.startswith("./collections/")
                                    })
            return sections

@app.route('/api/analyze', methods=['POST'])
def analyze_collection():
    analyzer = PDFAnalyzer()
    collection_name = request.form.get('collection')
    uploaded_files = request.files.getlist('files')
    
    results = {
        "metadata": {
            "collection": collection_name,
            "uploaded_files": [f.filename for f in uploaded_files]
        },
        "sections": [],
        "connections": []
    }
    all_texts = []
    persona = None
    
    # Process collection PDFs if specified
    if collection_name:
        collection_path = f"./collections/{collection_name}"
        
        if not os.path.exists(collection_path):
            return jsonify({"error": "Collection not found"}), 404

        with open(f"{collection_path}/input.json") as f:
            config = json.load(f)
            persona = config["persona"]["role"]
        
        for filename in os.listdir(f"{collection_path}/PDFs"):
            if filename.endswith(".pdf"):
                pdf_results = analyzer.process_pdf(
                    f"{collection_path}/PDFs/{filename}",
                    persona
                )
                results["sections"].extend(pdf_results)
                all_texts.extend([(s["text"], idx) for idx, s in enumerate(pdf_results)])
    
    # Process uploaded files
    for uploaded_file in uploaded_files:
        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filepath)
            
            current_persona = persona or list(analyzer.persona_config.keys())[0]
            pdf_results = analyzer.process_pdf(filepath, current_persona)
            results["sections"].extend(pdf_results)
            start_idx = len(all_texts)
            all_texts.extend([(s["text"], idx + start_idx) for idx, s in enumerate(pdf_results)])
    
    # Find semantic connections
    if all_texts:
        texts, indices = zip(*all_texts)
        embeddings = analyzer.model.encode(texts)
        for i, emb1 in enumerate(embeddings):
            for j, emb2 in enumerate(embeddings[i+1:], i+1):
                sim = util.cos_sim(emb1, emb2).item()
                if sim > 0.7:  # Threshold
                    results["connections"].append({
                        "source": indices[i],
                        "target": indices[j],
                        "strength": sim
                    })
    
    # Sort sections by importance
    results["sections"].sort(key=lambda x: x["importance"], reverse=True)
    
    return jsonify(results)

@app.route('/api/personas', methods=['GET'])
def get_personas():
    analyzer = PDFAnalyzer()
    return jsonify(list(analyzer.persona_config.keys()))

@app.route('/api/collections', methods=['GET'])
def get_collections():
    collections = []
    for name in os.listdir("./collections"):
        if os.path.isdir(f"./collections/{name}"):
            collections.append(name)
    return jsonify(collections)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs("./collections", exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    application = app