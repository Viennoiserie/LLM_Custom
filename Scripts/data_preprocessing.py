import os
import re
import requests

os.makedirs("../Data", exist_ok=True)

BOOKS = {

    "grammar": {     "english_grammar_stewart": "https://www.gutenberg.org/files/76768/76768-0.txt",  
                     "how_to_speak_write": "https://www.gutenberg.org/files/64078/64078-0.txt",  
                     "kirkham_lectures": "https://www.gutenberg.org/files/14070/14070-0.txt",  
                     "goold_brown_grammar": "https://www.gutenberg.org/files/11615/11615-0.txt", 
                     "baskervill_sewell": "https://www.gutenberg.org/files/14006/14006-0.txt"},

    "simple": {      "aesop_fables": "https://www.gutenberg.org/files/21/21-0.txt",
                     "alice": "https://www.gutenberg.org/files/11/11-0.txt",
                     "peter_pan": "https://www.gutenberg.org/files/16/16-0.txt",
                     "oz": "https://www.gutenberg.org/files/55/55-0.txt",
                     "the_velveteen_rabbit": "https://www.gutenberg.org/files/11757/11757-0.txt",
                     "little_princess": "https://www.gutenberg.org/files/16389/16389-0.txt",
                     "wind_in_willows": "https://www.gutenberg.org/files/289/289-0.txt",
                     "black_beauty": "https://www.gutenberg.org/files/271/271-0.txt"},

    "dialogue": {    "emma": "https://www.gutenberg.org/files/158/158-0.txt",
                     "sense_sensibility": "https://www.gutenberg.org/files/161/161-0.txt",
                     "little_women": "https://www.gutenberg.org/files/514/514-0.txt",
                     "anne_of_green_gables": "https://www.gutenberg.org/files/45/45-0.txt",
                     "tom_sawyer": "https://www.gutenberg.org/files/74/74-0.txt",
                     "adventures_huck_finn": "https://www.gutenberg.org/files/76/76-0.txt"},

    "intermediate": {"gullivers_travels": "https://www.gutenberg.org/files/829/829-0.txt",
                     "sherlock_holmes": "https://www.gutenberg.org/files/1661/1661-0.txt",
                     "pride_and_prejudice": "https://www.gutenberg.org/files/1342/1342-0.txt",
                     "jane_eyre": "https://www.gutenberg.org/files/1260/1260-0.txt",
                     "dracula": "https://www.gutenberg.org/files/345/345-0.txt",
                     "frankenstein": "https://www.gutenberg.org/files/84/84-0.txt",
                     "great_expectations": "https://www.gutenberg.org/files/1400/1400-0.txt",
                     "wuthering_heights": "https://www.gutenberg.org/files/768/768-0.txt"
    },

    "complex": {     "shakespeare": "https://www.gutenberg.org/files/100/100-0.txt",
                     "poe_poems": "https://www.gutenberg.org/files/10031/10031-0.txt",
                     "marlowe": "https://www.gutenberg.org/files/779/779-0.txt",
                     "ulysses": "https://www.gutenberg.org/files/4300/4300-0.txt",
                     "dubliners": "https://www.gutenberg.org/files/2814/2814-0.txt",
                     "don_quixote": "https://www.gutenberg.org/files/996/996-0.txt"}
}

# region : Helper Functions

def clean_book(text):

    """ Nettoie le texte en préservant la structure conversationnelle """

    # Retirer les balises HTML
    text = re.sub(r'<.*?>', '', text)
    
    # Retirer les en-têtes et pieds de page Gutenberg
    text = re.sub(r"\*\*\* START OF.*?\*\*\*", "", text, flags=re.DOTALL)
    text = re.sub(r"\*\*\* END OF.*?\*\*\*", "", text, flags=re.DOTALL)
    
    # Retirer les notes entre crochets
    text = re.sub(r"\[.*?\]", "", text)
    
    # Retirer les indications de scène (mais garder les dialogues de théâtre)
    text = re.sub(r"(ACT|SCENE|CHAPTER) [IVXLCDM]+\.?", "", text)
    text = re.sub(r"^[A-Z][A-Z \-']+:(?!\w)", "", text, flags=re.MULTILINE)  # Noms de personnages suivis de :
    
    # Normaliser les apostrophes
    text = text.replace("'", "'")
    text = text.replace("`", "'")
    text = text.replace("'", "'")
     
    # Normaliser les espaces multiples (mais garder les retours à la ligne)
    text = re.sub(r" {2,}", " ", text)
    
    # Réduire les multiples sauts de ligne à maximum 2 (pour séparer les paragraphes)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    
    return text

def extract_dialogues(text):

    """ Extrait et structure les dialogues pour améliorer l'apprentissage conversationnel """

    # Patterns pour identifier les dialogues
    dialogue_patterns = [r'"([^"]+)"',  # Guillemets anglais
                         r'«([^»]+)»',  # Guillemets français
                         r'—([^—\n]+)'] # Tirets de dialogue
    
    dialogues = []

    for pattern in dialogue_patterns:
        matches = re.findall(pattern, text)
        dialogues.extend(matches)
    
    structured_dialogues = []

    for i, dialogue in enumerate(dialogues):

        dialogue = dialogue.strip()

        if len(dialogue) > 10:  # Ignorer les dialogues très courts

            # Alterner entre <user> et <assistant> pour simuler une conversation
            marker = "<user>" if i % 2 == 0 else "<assistant>"
            structured_dialogues.append(f"{marker} {dialogue}")
    
    return "\n".join(structured_dialogues)

def download_book(url, name):

    """ Télécharge et nettoie un livre """

    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"Downloaded {name}")
            return clean_book(response.text)
        
        else:
            print(f"Could not download {name} (Status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"Error downloading {name}: {e}")
        return None

def process_stage(level, books):

    """ Traite un stage complet et crée les fichiers """

    print(f"\n{'='*60}")
    print(f"Processing stage: {level.upper()}")
    print(f"{'='*60}")
    
    combined_text = ""
    combined_dialogues = ""
    
    for name, url in books.items():

        print(f"  Downloading {name}...", end=" ")
        cleaned = download_book(url, name)
        
        if cleaned:

            # Ajouter le texte complet
            combined_text += f"\n\n### START OF {name.upper()} ###\n\n"
            combined_text += cleaned
            combined_text += f"\n\n### END OF {name.upper()} ###\n\n"
            
            # Extraire les dialogues si c'est le stage "dialogue" ou "intermediate"
            if level in ["dialogue", "intermediate"]:

                dialogues = extract_dialogues(cleaned)

                if dialogues:
                    combined_dialogues += f"\n\n{dialogues}\n\n"
            
            print(f"({len(cleaned)} chars)")

        else:
            print(f"Skipped")
    
    # Sauvegarder le texte complet
    text_path = f"../Data/{level}.txt"
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(combined_text)

    print(f"\nSaved: {text_path} ({len(combined_text):,} chars)")
    
# endregion

print("\n" + "="*60)
print("DOWNLOADING TRAINING DATA FOR CONVERSATIONAL LLM")
print("="*60)

for level, books in BOOKS.items():
    process_stage(level, books)

print("\n" + "="*60)
print("ALL DOWNLOADS COMPLETE")
print("="*60)

print("\nDataset Statistics:")
for level in BOOKS.keys():

    path = f"../Data/{level}.txt"

    if os.path.exists(path):
        size = os.path.getsize(path)

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            words = len(content.split())
            
        print(f"  {level:15s}: {size:>10,} bytes | {words:>10,} words")