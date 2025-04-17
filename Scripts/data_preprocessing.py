import re
import os
import requests

os.makedirs("data", exist_ok=True)

url = "https://www.gutenberg.org/files/100/100-0.txt"
output_path = "data/shakespeare.txt"

print("\nDownloading Shakespeare's complete works...\n")
response = requests.get(url)
text = response.text

def clean_gutenberg(text):
    
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK 100 ***"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK 100 ***"

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        text = text[start_idx + len(start_marker):end_idx]


    text = re.sub(r"^[A-Z ,’';\-]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"\b\d+\b", "", text)
    text = text.strip()

    return text

cleaned_text = clean_gutenberg(text)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print(f"Dataset saved to {output_path}\n")
