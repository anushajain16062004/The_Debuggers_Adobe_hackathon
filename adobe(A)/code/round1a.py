import fitz  
import re
import os
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilenames


def extract_title(doc):
    first_page=doc[0]
    blocks=first_page.get_text("dict")["blocks"]

    potential_title_parts=[]
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text=span["text"].strip()
                if not text:
                    continue

                if len(text.encode("utf-8"))<3:
                    continue

                font_size=span["size"]
                font_name=span["font"].lower()
                is_bold="bold" in font_name or "black" in font_name
                y_position=span["bbox"][1]

                if (is_bold or font_size>13) and y_position<250:
                    potential_title_parts.append((y_position, span["bbox"][0], text))  

    potential_title_parts.sort()

    from collections import Counter
    text_list=[text for _, _, text in potential_title_parts]
    counts=Counter(text_list)
    cleaned_list=[]
    seen=set()

    for text in text_list:
        if counts[text]>2:
            continue

        if text not in seen:
            cleaned_list.append(text)
            seen.add(text)

    title= " ".join(cleaned_list)
    return re.sub(r"\s+", " ", title).strip()




def extract_toc_based_headings(doc):
    toc=doc.get_toc(simple=True)
    headings=[]
    for item in toc:
        level, title, page=item
        text=title.strip()
        if len(text)>=3:
            headings.append({
                "level": f"H{level}",
                "text": text,
                "page": page
            })
    return headings

def detect_headings_by_layout(doc, extracted_title=""):
    headings=[]
    seen_texts=set()
    for page_number, page in enumerate(doc, start=1):
        blocks= page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                full_line_text=" ".join(span["text"].strip() for span in line.get("spans", []) if span["text"].strip())
                if not full_line_text or len(full_line_text.encode("utf-8"))<3:
                    continue

                if full_line_text in seen_texts or full_line_text==extracted_title:
                    continue
                seen_texts.add(full_line_text)

                font_sizes= [span["size"] for span in line["spans"]]
                font_names= [span["font"].lower() for span in line["spans"]]

                avg_font_size= sum(font_sizes)/len(font_sizes)
                is_bold= any("bold" in name or "black" in name for name in font_names)
                is_heading_like= avg_font_size>10 and (is_bold or avg_font_size>12)

                match= re.match(r"^([0-9０-９]+(\.[0-9０-９]+)*)", full_line_text)


                if is_heading_like:
                    level= "H2"
                    if match:
                        level= f"H{match.group(1).count('.') + 1}"
                    elif page_number<=5:
                        level= "H1"
                    headings.append({
                        "level": level,
                        "text": full_line_text,
                        "page": page_number
                    })
    return headings

def process_pdf(file_path, filename):
    with fitz.open(file_path) as doc:
        title= extract_title(doc)

        outline= detect_headings_by_layout(doc, extracted_title=title)

        if not outline:
            outline= detect_headings_by_layout(doc, extracted_title=title)

        return {
            "title": title,
            "outline": outline
        }


if __name__ == "__main__":
    print("Please select PDF files to process...")
    root= Tk()
    root.withdraw() 
    selected_files= askopenfilenames(title="Select PDF files", filetypes=[("PDF Files", "*.pdf")])

    final_output= {}
    for path in selected_files:
        filename= os.path.basename(path)
        final_output[filename]= process_pdf(path, filename)

    print(json.dumps(final_output, indent=4, ensure_ascii=False))
