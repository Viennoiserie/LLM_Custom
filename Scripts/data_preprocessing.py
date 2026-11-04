import os
import re
import requests

from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA_DIR = Path(__file__).resolve().parents[1] / "Data"
os.makedirs(DATA_DIR, exist_ok=True)

HELD_OUT_BOOKS = {"grammar": "english_lessons",
                  "simple": "alice",
                  "dialogue": "emma",
                  "intermediate": "sherlock_holmes",
                  "complex": "shakespeare"}

BOOKS = {

    "grammar": {     "english_lessons": "https://www.gutenberg.org/files/22091/22091-0.txt",
                     "practical_english": "https://www.gutenberg.org/files/63001/63001-0.txt",
                     "sentence_structure": "https://www.gutenberg.org/files/13715/13715-0.txt",
                     "word_study": "https://www.gutenberg.org/files/42846/42846-0.txt"},

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
                     "wuthering_heights": "https://www.gutenberg.org/files/768/768-0.txt"},

    "complex": {     "shakespeare": "https://www.gutenberg.org/files/100/100-0.txt",
                     "poe_poems": "https://www.gutenberg.org/files/10031/10031-0.txt",
                     "marlowe": "https://www.gutenberg.org/files/779/779-0.txt",
                     "ulysses": "https://www.gutenberg.org/files/4300/4300-0.txt",
                     "dubliners": "https://www.gutenberg.org/files/2814/2814-0.txt",
                     "don_quixote": "https://www.gutenberg.org/files/996/996-0.txt"}}

SYNTHETIC_GRAMMAR = """ # GRAMMAR LESSONS

## Nouns
A noun is a word that names a person, place, thing, or idea.
Examples: teacher, London, book, happiness, democracy

Common nouns: dog, city, computer, love
Proper nouns: John, Paris, Microsoft, Monday

## Verbs
A verb expresses action or a state of being.
Examples: run, think, be, have, become

Action verbs: jump, write, speak, dance
Linking verbs: is, are, was, were, seem, appear
Helping verbs: can, could, will, would, shall, should

## Adjectives
An adjective describes or modifies a noun.
Examples: beautiful, large, happy, ancient, intelligent

Descriptive adjectives: red car, tall building
Limiting adjectives: three books, many people

## Adverbs
An adverb modifies a verb, adjective, or another adverb.
Examples: quickly, very, often, well, extremely

Manner: He runs quickly.
Time: She arrived yesterday.
Place: They live here.
Degree: It's very cold.

## Pronouns
A pronoun replaces a noun.
Examples: I, you, he, she, it, we, they, who, which

Personal pronouns: I, me, you, he, him, she, her
Possessive pronouns: my, mine, your, yours, his, her, hers
Demonstrative pronouns: this, that, these, those

## Prepositions
A preposition shows the relationship between a noun and other words.
Examples: in, on, at, by, with, from, to, about

Location: in the house, on the table, at school
Time: in January, on Monday, at noon
Direction: to the store, from home, toward the city

## Conjunctions
A conjunction connects words, phrases, or clauses.
Examples: and, but, or, nor, for, so, yet

Coordinating: and, but, or, nor, for, so, yet
Subordinating: because, although, if, when, while, since

## Interjections
An interjection expresses emotion.
Examples: Oh! Wow! Hey! Oops! Hurray!


# SENTENCE STRUCTURE

## Simple Sentences
A simple sentence contains one independent clause.
Examples:
- The cat sleeps.
- Mary reads books every day.
- The old man walked slowly down the street.

## Compound Sentences
A compound sentence contains two or more independent clauses.
Examples:
- I like tea, but she prefers coffee.
- The sun was shining, and the birds were singing.
- He studied hard, so he passed the exam.

## Complex Sentences
A complex sentence contains an independent clause and one or more dependent clauses.
Examples:
- When it rains, we stay inside.
- Although she was tired, she finished her work.
- The book that I bought yesterday is interesting.


# VERB TENSES

## Present Tense
Simple present: I walk, he walks
Present continuous: I am walking, he is walking
Present perfect: I have walked, he has walked

## Past Tense
Simple past: I walked, he walked
Past continuous: I was walking, he was walking
Past perfect: I had walked, he had walked

## Future Tense
Simple future: I will walk, he will walk
Future continuous: I will be walking
Future perfect: I will have walked


# COMMON GRAMMAR RULES

## Subject-Verb Agreement
The subject and verb must agree in number.
Correct: She walks to school.
Incorrect: She walk to school.

Correct: They walk to school.
Incorrect: They walks to school.

## Articles
Use "a" before consonant sounds: a book, a university
Use "an" before vowel sounds: an apple, an hour

Definite article "the": the book, the apple

## Capitalization
Capitalize the first word of a sentence.
Capitalize proper nouns: John, Paris, Monday.
Capitalize titles: Dr. Smith, President Lincoln.


# QUESTION FORMATION

## Yes/No Questions
Statement: You are happy.
Question: Are you happy?

Statement: She likes coffee.
Question: Does she like coffee?

## Wh- Questions
Who: Who is that person?
What: What is your name?
Where: Where do you live?
When: When did you arrive?
Why: Why are you late?
How: How do you do this?


# CONDITIONALS

## Zero Conditional
If you heat water to 100°C, it boils.

## First Conditional
If it rains tomorrow, I will stay home.

## Second Conditional
If I had a million dollars, I would travel the world.

## Third Conditional
If I had studied harder, I would have passed the exam.


# MODALS

## Can/Could
Ability: I can swim.
Permission: Can I go now?
Possibility: It could rain tomorrow.

## May/Might
Permission: May I leave early?
Possibility: It may rain.

## Must/Have to
Obligation: You must wear a seatbelt.
Necessity: I have to finish this today.

## Should
Advice: You should see a doctor.
Expectation: They should arrive soon.

## Would
Polite requests: Would you help me?
Hypothetical: I would go if I had time.


# COMPARATIVE AND SUPERLATIVE

## Adjectives
Positive: tall, beautiful, good
Comparative: taller, more beautiful, better
Superlative: tallest, most beautiful, best

## Adverbs
Positive: quickly, carefully, well
Comparative: more quickly, more carefully, better
Superlative: most quickly, most carefully, best


# ACTIVE VS PASSIVE VOICE

## Active Voice
The subject performs the action.
Example: The cat caught the mouse.

## Passive Voice
The subject receives the action.
Example: The mouse was caught by the cat.


# WORD ORDER

Standard English word order: Subject + Verb + Object
Example: The cat caught the mouse.

With adverbs:
- Manner: She sings beautifully.
- Place: He works here.
- Time: They arrived yesterday.
- Frequency: I always eat breakfast.

"""

# region : Helper Functions

def clean_book(text):

    """
    Nettoie le texte Gutenberg et normalise la structure
    
    """

    text = strip_gutenberg_headers(text)

    replacements = {"—": "--", 
                    "–": "--", 
                    "'": "'", 
                    """: '"', 
                    """: '"', 
                    "´": "'",
                    "'": "'", 
                    "`": "'", 
                    "′": "'"}
    
    for k, v in replacements.items():
        text = text.replace(k, v)

    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\*\*\* (START|END) OF.*?\*\*\*", "", text, flags=re.DOTALL)
    text = re.sub(r"\[(Illustration|Footnote).*?\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if m := re.search(r"\bCHAPTER\s+[I1VXLC]+\b", text, re.IGNORECASE):
        text = text[m.start():]

    return text.strip()

def download_book(name, url):

    """
    Télécharge et nettoie un livre
    
    """

    try:
        r = requests.get(url, timeout=30)

        if r.ok:
            cleaned = clean_book(r.text)
    
            if any(x in name for x in ['grammar', 'speak', 'kirkham', 'brown']):
                cleaned = remove_pronunciation(cleaned)
                
            return name, cleaned
        
    except Exception as e:
        print(f"  [!] Error {name}: {e}")

    return name, None

def analyze_vocabulary(text):

    """Retourne les stats lexicales"""

    words = re.findall(r'\b[a-z]+\b', text.lower())
    freq = Counter(words)
    total = len(words)
    uniq = len(freq)

    return dict(total_words=total,
                unique_words=uniq,
                richness=uniq / total if total else 0,
                most_common=freq.most_common(15))

def remove_pronunciation(text):
    
    """Retire les notations phonétiques archaïques des vieux livres de grammaire."""

    text = re.sub(r'NOTE \d+\.--.*?(?=\n\n[A-Z]|\Z)', '', text, flags=re.DOTALL)
    
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:

        if len(line) > 0:
            digit_ratio = sum(c.isdigit() for c in line) / len(line)
            dash_ratio = line.count('-') / len(line)

            if digit_ratio < 0.25 and dash_ratio < 0.35:
                clean_lines.append(line)
    
    return '\n'.join(clean_lines)


def is_play_script(text):

    """
    Détecte si un texte est un script de pièce de théâtre:
    Les pièces ont beaucoup de lignes commençant par des noms en MAJUSCULES.
    """

    character_lines = 0
    lines = [l.strip() for l in text.split('\n') if l.strip()][:200] 

    for line in lines:

        # Pattern: CARACTERE. ou CARACTERE: ou juste CARACTERE tout seul
        if re.match(r'^[A-Z][A-Z\s]{2,}[\.:]?\s*$', line):
            character_lines += 1

        # Pattern: CARACTERE suivi de dialogue
        elif re.match(r'^[A-Z][A-Z\s]{2,}\.\s+[A-Z]', line):
            character_lines += 1
    
    # Si plus de 10% des lignes sont des noms de personnages, c'est une pièce
    return (character_lines / len(lines)) > 0.1 if lines else False

def clean_play_to_narrative(text):

    """
    Convertit un script de pièce en prose narrative.
    Retire les noms de personnages et les indications scéniques.
    """

    cleaned = []
    lines = text.split('\n')

    for line in lines:

        line = line.strip()
        
        if not line:
            continue
        
        # Ignore les indications scéniques [Enter X], [Exit Y], etc.
        if re.match(r'^\[.*\]$', line):
            continue
        
        # Ignore les lignes qui sont juste des noms de personnages
        if re.match(r'^[A-Z][A-Z\s]{2,}[\.:]?\s*$', line):
            continue
        
        # Retirer les noms de personnages au début des lignes
        line = re.sub(r'^[A-Z][A-Z\s]{2,}[\.:]\s+', '', line)
        
        # Retirer les numéros de notes de bas de page [1], [2], etc.
        line = re.sub(r'\[\d+\]', '', line)

        if line and len(line.split()) > 2:
            cleaned.append(line)
    
    return '\n'.join(cleaned)

def extract_narrative(text, max_segments=300):

    """
    Extrait la narration (ensemble de phrase quie se suivent)
    
    """
    
    # On ignore les abbréviations comme potentiel délimiteurs
    protected = text
    protected = re.sub(r'\bDr\.', 'Dr__ABBR__', protected)
    protected = re.sub(r'\bMr\.', 'Mr__ABBR__', protected)
    protected = re.sub(r'\bMs\.', 'Ms__ABBR__', protected)
    protected = re.sub(r'U\.S\.', 'US__ABBR__', protected)
    protected = re.sub(r'U\.K\.', 'UK__ABBR__', protected)
    protected = re.sub(r'\bMrs\.', 'Mrs__ABBR__', protected)
    
    # On split les phrases par la ponctuation
    sentences = re.split(r'(?<=[.!?])\s+', protected)
    segments = []

    for i in range(0, min(len(sentences) - 3, max_segments * 3), 3):

        segment = ' '.join(sentences[i:i+3]).strip()
        
        # On restaure les abbréviations pour garder le sens des phrases
        segment = segment.replace('Dr__ABBR__', 'Dr.')
        segment = segment.replace('Mr__ABBR__', 'Mr.')
        segment = segment.replace('Ms__ABBR__', 'Ms.')
        segment = segment.replace('US__ABBR__', 'U.S.')
        segment = segment.replace('UK__ABBR__', 'U.K.')
        segment = segment.replace('Mrs__ABBR__', 'Mrs.')
        
        if len(segment.split()) > 10:
            segments.append(f"{segment} <eos>")
            
        if len(segments) >= max_segments:
            break

    return "\n\n".join(segments)

def extract_dialogues(text, max_dialogues=500):

    """
    Extract quoted utterances without guessing who is speaking.
    
    """

    utterances = []
    paragraphs = text.split('\n\n')

    for para in paragraphs:

        if len(utterances) >= max_dialogues:
            break
        
        quotes = re.findall(r'"([^"]{10,500})"|“([^”]{10,500})”', para)

        for straight_quote, curly_quote in quotes:
            utterance = (straight_quote or curly_quote).strip()

            if len(utterance.split()) > 3:
                utterances.append(f"{utterance} <eos>")

                if len(utterances) >= max_dialogues:
                    break

    return "\n".join(utterances)


def strip_gutenberg_headers(text: str) -> str:

    text = re.sub(r'(?s).*?(\*\*\*\s*START OF.*?\*\*\*)', '', text)
    text = re.sub(r'(?s)(\*\*\*\s*END OF.*)', '', text)

    text = re.sub(r'(?s)Information about donations to the Project Gutenberg.*?(?=\n\n|$)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?s)Right of Replacement or Refund.*?(?=\n\n|$)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?s)Plain Vanilla ASCII.*?(?=\n\n|$)', '', text, flags=re.IGNORECASE)

    return text.strip()

def process_stage(level, books, max_workers=5):

    """
    Télécharge et traite tous les livres d'un niveau
    
    """

    print(f"\n{'='*60}\nPROCESSING STAGE: {level.upper()}\n{'='*60}")

    vocab = {}
    validation = []
    held_out_book = HELD_OUT_BOOKS[level]
    combined = {"text": [], "dialogues": [], "narrative": []}

    if level == "grammar":
        combined["text"].append(f"\n### START SYNTHETIC_GRAMMAR ###\n{SYNTHETIC_GRAMMAR}\n### END SYNTHETIC_GRAMMAR ###\n")

        print(f"  synthetic_grammar ({len(SYNTHETIC_GRAMMAR):,} chars)")
        vocab["synthetic_grammar"] = analyze_vocabulary(SYNTHETIC_GRAMMAR)

    downloaded = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_book, name, url): name for name, url in books.items()}

        for future in as_completed(futures):

            name, text = future.result()
            downloaded[name] = text

    for idx, (name, url) in enumerate(books.items(), 1):

        text = downloaded[name]

        if not text:

            print(f"  Skipped {name}")
            continue

        print(f"  {name} ({len(text):,} chars)")
        vocab[name] = analyze_vocabulary(text)

        if name == held_out_book:

            validation.append(f"\n### HELD-OUT {name} ###\n{text}\n### END HELD-OUT {name} ###\n")
            continue

        combined["text"].append(f"\n### START {name} ###\n{text}\n### END {name} ###\n")

        if level in ("dialogue", "intermediate"):

            if d := extract_dialogues(text, max_dialogues=300):

                print(f"    -> Extracted {len(d.split(chr(10)))} dialogue lines")
                combined["dialogues"].append(d)

        if level in ("simple", "intermediate", "complex"):
            
            if n := extract_narrative(text, max_segments=250):

                print(f"    -> Extracted {len(n.split(chr(10)+chr(10)))} narrative segments")
                combined["narrative"].append(n)

    outputs = {}

    if not validation:
        raise RuntimeError(f"Held-out book '{held_out_book}' was not downloaded for stage '{level}'.")

    combined["validation"] = validation

    for key, content in combined.items():
        
        if not content:
            continue

        filename = f"{level}_{key}.txt" if key not in ("text", "validation") else (f"{level}.txt" if key == "text" else f"{level}_validation.txt")
        path = os.path.join(DATA_DIR, filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(content))

        outputs[key] = path

    print("\n  Saved files:")
    
    for k, v in outputs.items():
        print(f"    - {os.path.basename(v)} ({os.path.getsize(v):,} bytes)")

    print("\n  Vocabulary stats:")
    
    for name, stats in vocab.items():
        print(f"    {name:25s}: {stats['unique_words']:>7,} uniq / {stats['total_words']:>8,} total (richness={stats['richness']:.3f})")

    return outputs

# endregion

if __name__ == "__main__":

    print("\n" + "="*60)
    print("DOWNLOADING TRAINING DATA FOR CONVERSATIONAL LLM")
    print("="*60)

    all_outputs = {lvl: process_stage(lvl, bks, max_workers=5) for lvl, bks in BOOKS.items()}

    print("\n" + "="*60)
    print("ALL DOWNLOADS COMPLETE")
    print("="*60 + "\n")

    for lvl, outputs in all_outputs.items():

        txt = outputs.get("text")

        if txt and os.path.exists(txt):
            with open(txt, encoding="utf-8") as f:
                words = len(f.read().split())

            print(f"{lvl:15s}: {os.path.getsize(txt):>10,} bytes | {words:>10,} words")