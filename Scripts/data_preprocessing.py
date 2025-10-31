import os
import re
import requests

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed


DATA_DIR = "./Data"
os.makedirs(DATA_DIR, exist_ok=True)


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


SYNTHETIC_GRAMMAR = """ GRAMMAR LESSONS : 

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

    """Nettoie le texte Gutenberg et normalise la structure."""

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

    return text.strip()

def download_book(name, url):

    """Télécharge et nettoie un livre"""

    try:
        r = requests.get(url, timeout=30)

        if r.ok:
            cleaned = clean_book(r.text)
            # Nettoyer prononciation seulement pour les livres suspects
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


def extract_speaker_name(context):

    """Détecte le nom du locuteur dans un passage"""

    patterns = [r'(\b[A-Z][a-z]+)\s+(?:said|replied|asked|answered|exclaimed|whispered|shouted|murmured)',
                r'(?:said|replied|asked|answered|exclaimed|whispered|shouted|murmured)\s+(\b[A-Z][a-z]+)',
                r'(\b[A-Z][a-z]+)\s*[:,]\s*$']
    
    for pat in patterns:
        if m := re.search(pat, context[-120:]):
            return m.group(1)
        
    return None

def extract_narrative(text, max_segments=300):

    """Extrait des segments narratifs de 3 phrases (version optimisée)"""

    sentences = re.split(r'(?<=[.!?])\s+', text)
    segments = []

    for i in range(0, min(len(sentences) - 3, max_segments * 3), 3):
        segment = ' '.join(sentences[i:i+3]).strip()
        
        if len(segment.split()) > 10:
            segments.append(f"{segment} <eos>")
            
        if len(segments) >= max_segments:
            break

    return "\n\n".join(segments)

def extract_dialogues(text, max_dialogues=500):

    """Extrait les dialogues et structure user/assistant (version optimisée)"""

    structured = []
    speaker = None
    count = 0

    for para in text.split('\n\n'):

        if count >= max_dialogues:
            break

        for before, quote, after in re.findall(r'([^"]*)"([^"]+)"([^"]*)', para):
            quote = re.sub(r'\s+', ' ', quote.strip())

            if len(quote.split()) < 3:
                continue

            spk = extract_speaker_name(before + after)

            if spk and spk != speaker:
                speaker, count = spk, count + 1

            role = "<user>" if count % 2 == 0 else "<assistant>"
            structured.append(f"{role} {quote} <eos>")

            if count >= max_dialogues:
                break

    return "\n".join(structured)

def extract_question_answer(text, max_pairs=200):

    """Extrait les paires question / réponse (version optimisée)"""

    sents = re.split(r'(?<=[.!?])\s+', text)
    qa = []

    for i, sent in enumerate(sents[:-1]):
        
        if len(qa) >= max_pairs * 2:
            break

        if '?' in sent and len(sent.split()) > 3 and len(sents[i+1].split()) > 3:
            qa += [f"<user> {sent.strip()} <eos>", f"<assistant> {sents[i+1].strip()} <eos>"]

    return "\n".join(qa)


def process_stage(level, books, max_workers=4):

    """Télécharge et traite tous les livres d'un niveau"""

    print(f"\n{'='*60}\nPROCESSING STAGE: {level.upper()}\n{'='*60}")

    combined = {"text": [], "dialogues": [], "qa": [], "narrative": []}
    vocab = {}

    # Ajout de la grammaire "manuelle" au stage 'grammar'
    if level == "grammar":

        combined["text"].append(f"\n### START SYNTHETIC_GRAMMAR ###\n{SYNTHETIC_GRAMMAR}\n### END SYNTHETIC_GRAMMAR ###\n")
        print(f"  synthetic_grammar ({len(SYNTHETIC_GRAMMAR):,} chars)")

        vocab["synthetic_grammar"] = analyze_vocabulary(SYNTHETIC_GRAMMAR)

    # Téléchargements
    with ThreadPoolExecutor(max_workers=max_workers) as ex:

        futures = [ex.submit(download_book, n, u) for n, u in books.items()]

        for f in as_completed(futures):
            name, text = f.result()

            if not text:
                print(f"  Skipped {name}")
                continue

            print(f"  {name} ({len(text):,} chars)")

            vocab[name] = analyze_vocabulary(text)
            combined["text"].append(f"\n### START {name} ###\n{text}\n### END {name} ###\n")

            if level != "grammar":
                if d := extract_dialogues(text, max_dialogues=500):
                    combined["dialogues"].append(d)

            if level in ("grammar", "dialogue", "intermediate"):
                if qa := extract_question_answer(text, max_pairs=200):
                    combined["qa"].append(qa)

            if level in ("simple", "intermediate", "complex"):
                if n := extract_narrative(text, max_segments=300):
                    combined["narrative"].append(n)

    # Enregistrements
    outputs = {}

    for key, content in combined.items():

        if not content:
            continue

        path = os.path.join(DATA_DIR, f"{level}_{key}.txt") if key != "text" else os.path.join(DATA_DIR, f"{level}.txt")
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(content))

        outputs[key] = path

    print("\n  Saved files:")
    for k, v in outputs.items():
        print(f"    - {os.path.basename(v)} ({os.path.getsize(v):,} bytes)")

    print("\n  Vocabulary stats:")
    for name, stats in vocab.items():
        print(f"    {name:25s}: {stats['unique_words']:>7,} uniq / {stats['total_words']:>8,} total "
              f"(richness={stats['richness']:.3f})")

    return outputs

# endregion


if __name__ == "__main__":

    print("\n" + "="*60)
    print("DOWNLOADING TRAINING DATA FOR CONVERSATIONAL LLM")
    print("="*60)

    all_outputs = {lvl: process_stage(lvl, bks) for lvl, bks in BOOKS.items()}

    print("\n" + "="*60)
    print("ALL DOWNLOADS COMPLETE")
    print("="*60 + "\n")

    for lvl, outputs in all_outputs.items():

        txt = outputs.get("text")

        if txt and os.path.exists(txt):
            with open(txt, encoding="utf-8") as f:
                words = len(f.read().split())

            print(f"{lvl:15s}: {os.path.getsize(txt):>10,} bytes | {words:>10,} words")
