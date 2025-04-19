import os
import re
import requests

os.makedirs("data", exist_ok=True)

BOOKS = {

    "grammar": {
        "english_grammar": "https://www.gutenberg.org/files/37134/37134-0.txt",  
        "how_to_speak_write": "https://www.gutenberg.org/files/64078/64078-0.txt",  
        "kirkham_lectures": "https://www.gutenberg.org/files/14070/14070-0.txt",  
        "goold_brown_grammar": "https://www.gutenberg.org/files/11615/11615-0.txt", 
        "baskervill_sewell": "https://www.gutenberg.org/files/14006/14006-0.txt"  
    },

    "simple": {
        "aesop_fables": "https://www.gutenberg.org/files/19994/19994-0.txt",
        "alice": "https://www.gutenberg.org/files/11/11-0.txt",
        "peter_pan": "https://www.gutenberg.org/files/16/16-0.txt",
        "oz": "https://www.gutenberg.org/files/55/55-0.txt",
        "the_velveteen_rabbit": "https://www.gutenberg.org/files/11757/11757-0.txt",
        "little_princess": "https://www.gutenberg.org/files/16389/16389-0.txt",
        "wind_in_willows": "https://www.gutenberg.org/files/289/289-0.txt",
        "black_beauty": "https://www.gutenberg.org/files/271/271-0.txt"
    },

    "intermediate": {
        "gullivers_travels": "https://www.gutenberg.org/files/829/829-0.txt",
        "sherlock_holmes": "https://www.gutenberg.org/files/1661/1661-0.txt",
        "pride_and_prejudice": "https://www.gutenberg.org/files/1342/1342-0.txt",
        "bible": "https://www.gutenberg.org/files/10/10-0.txt",
        "milton": "https://www.gutenberg.org/files/20/20-0.txt",
        "jane_eyre": "https://www.gutenberg.org/files/1260/1260-0.txt",
        "dracula": "https://www.gutenberg.org/files/345/345-0.txt",
        "frankenstein": "https://www.gutenberg.org/files/84/84-0.txt",
        "great_expectations": "https://www.gutenberg.org/files/1400/1400-0.txt"
    },

    "complex": {
        "shakespeare": "https://www.gutenberg.org/files/100/100-0.txt",
        "poe_poems": "https://www.gutenberg.org/files/25343/25343-0.txt",
        "marlowe": "https://www.gutenberg.org/files/779/779-0.txt",
        "chaucer": "https://www.gutenberg.org/files/2383/2383-0.txt",
        "spenser_faerie_queen": "https://www.gutenberg.org/files/15272/15272-0.txt",
        "ulysses": "https://www.gutenberg.org/files/4300/4300-0.txt",
        "dubliners": "https://www.gutenberg.org/files/2814/2814-0.txt",
        "wasteland_eliot": "https://www.gutenberg.org/files/1321/1321-0.txt",
        "don_quixote": "https://www.gutenberg.org/files/996/996-0.txt"
    }
}

def clean_book(text):

    text = re.sub(r'<.*?>', '', text) 
    text = re.sub(r"\*\*\* START OF.*?\*\*\*", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*\* END OF.*?\*\*\*", "", text, flags=re.DOTALL)

    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"(ACT|SCENE) [IVX]+", "", text)

    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"^[A-Z][A-Z \-']+$", "", text, flags=re.MULTILINE)

    text = text.replace("’", "'")
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()

def download_and_clean_book(url, name):

    try:
        response = requests.get(url)

        if response.status_code == 200:

            print(f"Successfully downloaded {name} from {url}")
            return clean_book(response.text)
        
        else:
            print(f"Warning: Could not download {name} from {url} (Status code: {response.status_code})")
            return None
        
    except Exception as e:

        print(f"Error downloading {name}: {e}")
        return None

for level, books in BOOKS.items():

    combined = ""

    for name, url in books.items():
        
        print(f"Downloading {name} for level: {level}...")

        cleaned = download_and_clean_book(url, name)

        if cleaned:
            combined += f"\n\n### START OF {name.upper()} ###\n\n"
            combined += cleaned
            combined += f"\n\n### END OF {name.upper()} ###\n\n"

        else:
            print(f"Skipping {name} due to download issues.")

    with open(f"data/{level}.txt", "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"> Saved data/{level}.txt ({len(combined) // 1024} KB)\n")