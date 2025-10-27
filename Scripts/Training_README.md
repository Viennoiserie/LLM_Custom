# I - Configuration du Modèle

## Architecture

Transformer avec :
- **12 couches** de traitement
- **8 têtes d'attention** parallèles
- **512 dimensions** d'embedding
- **2048 neurones** dans la couche cachée

> *Capacité de contexte : 256 tokens (~200 mots)*

---

## Vocabulaire

- **30 000 tokens** appris par tokenizer BPE
- Tokens spéciaux : `<user>`, `<assistant>`, `<eos>`

---

## Entraînement

- **Batch size :** 16 séquences
- **Epochs :** Max 100 (avec early stopping, patience=5)
- **Learning rate :** 
  - Initial : `5e-4` (0.0005)
  - Fine-tuning : `5e-5` (0.00005)

---

## Optimisation

| Paramètre | Valeur |
|-----------|--------|
| Warmup | 500 étapes |
| Gradient clipping | 1.0 |
| Optimizer | AdamW + scheduler linéaire |
| Checkpoints | Tous les 10 epochs |

---

## Curriculum Learning

Progression en 5 stages avec transfer learning :

*simple → grammar → complex → dialogue → intermediate*


> Ordre recommandé : `grammar` → `simple` → `dialogue` → `intermediate` → `complex`

---

## Infrastructure

- **Device :** GPU CUDA (si disponible) ou CPU
- **Sauvegarde :**
  - Modèles : `../Models/`
  - Tokenizer : `../Models/Tokenizer/`

---

# II - Formating the Dataset

## TextDataset : 

C'est une classe qui prépare les données textuelles pour l'entraînement du modèle. 

Elle hérite de **torch.utils.data.Dataset**, ce qui permet à PyTorch de charger les données efficacement par batches.

---

## Étape 1 : Lecture du fichier

```python
with open(file_path, 'r', encoding='utf-8') as f:
   text = f.read()
```
- Ouvre le fichier en mode lecture avec encodage UTF-8
- Charge **tout le texte en mémoire** dans la variable `text`

**Exemple :**

text = " Alice was beginning to get very tired. She was sitting by her sister. \n\n Suddenly a white rabbit ran past."

---

## Étape 2 : Ajout des marqueurs de fin de séquence

```python
text = text.replace('\n\n', ' <eos> ')
```
- Remplace les doubles sauts de ligne (fin de paragraphe) par le token spécial `<eos>`
- Pourquoi ? Pour que le modèle apprenne où se terminent les phrases/idées

**Exemple :**

*Avant :*  "Alice was tired.\n\nSuddenly a rabbit"

*Après  :* "Alice was tired. <eos> Suddenly a rabbit"

---

## Étape 3 : Tokenization
```python
self.tokens = tokenizer.encode(text).ids
```
- Convertit tout le texte en une liste d'entiers (IDs des tokens)
- `.encode(text)` → objet Encoding
- `.ids` → liste Python des IDs

**Exemple :**

text = "Hello world <eos> How are you"

self.tokens = [5421, 1923, 2, 1054, 812, 6543]

Equivalent : Hello world `<eos>` How  are  you

---

## Étape 4 : Stocker la longueur de séquence

```python
self.seq_len = seq_len
```

Garde en mémoire la taille des chunks (256 tokens)

Méthode `_len_` : Donne le nombre d'exemples

```python
def __len__(self):
   return max(1, (len(self.tokens) - 1) // self.seq_len)
```

---

**Calcul du nombre d'exemples d'entraînement :**

Nombre d'exemples = (nombre_total_tokens - 1) ÷ seq_len

---

**Principe de l'apprentissage autorégressif :**

Le modèle doit prédire le **token suivant** à chaque position.

**Exemple visuel :**

chunk = [10, 20, 30, 40, 50]

input_ids  = [10, 20, 30, 40]     ← Ce que voit le modèle
target_ids = [20, 30, 40, 50]     ← Ce qu'il doit prédire

Position 0: voir 10 → prédire 20
Position 1: voir 20 → prédire 30
Position 2: voir 30 → prédire 40
Position 3: voir 40 → prédire 50

---

## Étape 5 : Convertir en tenseurs PyTorch

```python
return torch.tensor(input_ids, dtype=torch.long), torch.tensor(target_ids, dtype=torch.long)
```

Convertit les listes Python en tenseurs PyTorch.

```dtype=torch.long ```: entiers 64 bits (ils sont requis pour les indices d'embeddings)

Retourne un tuple :

```python
(tensor([10, 20, 30, 40]), tensor([20, 30, 40, 50]))
```

---

## Résumé de l'opération

> **1** - Fichier texte

   
> **2** - Lecture : "Alice was tired. \n\n Suddenly..."


> **3** - Ajout `<eos>` : "Alice was tired. `<eos>` Suddenly..."


> **4** - Tokenization : [5421, 1923, 543, 2, 1054, ...]


> **5** - Découpage en chunks de 256 tokens


> **6** - Pour chaque chunk : **input**  = *[token₀, token₁, ..., token₂₅₅]* | **target** = *[token₁, token₂, ..., token₂₅₆]*


> **7** - Tenseurs PyTorch prêts pour l'entraînement

---

## Exemple Concret 

**- Fichier : simple.txt**

"
The cat sat on the mat.

The dog barked loudly.
"

**- Execution : `replace('\n\n', ' <eos> ')`**

"The cat sat on the mat. `<eos>` The dog barked loudly."


**- Tokenization :**

[234, 567, 891, 123, 456, 789, 2, 234, 999, 111, 222]

[The, cat, sat, on, the, mat, `<eos>`, The, dog, barked, loudly]


**- Execution : seq_len=5, idx=0 :**

chunk = [234, 567, 891, 123, 456, 789]  # 6 tokens (5+1)

input_ids  = [234, 567, 891, 123, 456]

target_ids = [567, 891, 123, 456, 789]

**- Le modèle apprend :**

Voir "The" → prédire "cat"

Voir "cat" → prédire "sat"

Voir "sat" → prédire "on"

etc...

---

# III - Training the Tokenizer

## Fonction `train_tokenizer`

## Objectif

Crée **un seul tokenizer** entraîné sur **toutes les données** pour garantir un vocabulaire cohérent entre tous les stages d'apprentissage.

---

## Étape 1 : Concaténer tous les textes

```python
print(f"Training new tokenizer on all stages...")

all_texts = []

for stage, path in STAGE_DATA_PATHS.items():

    if os.path.exists(path):

        with open(path, 'r', encoding='utf-8') as f:
            all_texts.append(f.read())
```

- Parcourt tous les stages : `grammar`, `simple`, `dialogue`, `intermediate`, `complex`
- Pour chaque fichier existant → lit **tout son contenu** et l'ajoute à `all_texts`

**Exemple :**

```python
all_texts = ["contenu de grammar.txt...",
             "contenu de simple.txt...",
             "contenu de dialogue.txt..."]

combined_text = "\n\n".join(all_texts)
```

---

## Étape 2 : Définir les tokens spéciaux

```python
special_tokens = ["<pad>",         # Padding (compléter les séquences courtes)
                  "<unk>",         # Unknown (mots inconnus)
                  "<bos>",         # Begin of sequence (début de texte)
                  "<eos>",         # End of sequence (fin de paragraphe/phrase)
                  "<user>",        # Marqueur utilisateur dans dialogue
                  "<assistant>"]   # Marqueur assistant dans dialogue

```

Ces tokens ont des IDs réservés (généralement 0, 1, 2, 3, 4, 5) et ne sont **jamais divisés** en sous-tokens.

---

## Étape 3 : Configurer le tokenizer BPE

```python
tokenizer = Tokenizer(models.BPE())
```

Crée un tokenizer basé sur **Byte-Pair Encoding** (BPE) :

- Algorithme qui apprend les paires de caractères les plus fréquentes
- Fusionne progressivement ces paires pour créer des sous-mots

```python
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
```

Découpe d'abord le texte sur les **espaces blancs** avant d'appliquer BPE.

**Exemple :**

"Hello world" → ["Hello", "world"] → puis BPE sur chaque mot

---

## Étape 4 : Configurer l'entraînement

```python
trainer = trainers.BpeTrainer(vocab_size=vocab_size,           # 30 000 tokens au total
                              special_tokens=special_tokens,   # 6 tokens spéciaux protégés
                              show_progress=True)              # Affiche barre de progression
```

Configure l'algorithme pour apprendre **30 000 tokens** incluant les 6 spéciaux.

---

## Étape 5 : Entraîner le tokenizer

```python
tokenizer.train_from_iterator([combined_text], trainer=trainer)
```

Lance l'apprentissage BPE sur le texte combiné :
1. Compte la fréquence de tous les caractères
2. Fusionne les paires les plus fréquentes
3. Répète jusqu'à avoir 30 000 tokens

**Résultat :** Le tokenizer sait maintenant découper n'importe quel texte en tokens connus.

---

## Étape 6 : Sauvegarder le tokenizer

```python
tokenizer.save(tokenizer_path)
print(f"Tokenizer saved to {tokenizer_path}")
```

Sauvegarde dans `../Models/Tokenizer/tokenizer_30000.json` :

- Vocabulaire complet (30 000 tokens)
- Règles de fusion BPE
- Mapping token ↔ ID

---

## Étape 7 : Retourner le tokenizer

```python
return tokenizer
```

Renvoie le tokenizer prêt à l'emploi pour encoder/décoder du texte.

---

## Résumé du Flow

> **1** - Vérifie si `tokenizer_30000.json` existe → si oui, charge et retourne

> **2** - Sinon, lit **tous** les fichiers : `grammar.txt`, `simple.txt`, etc.

> **3** - Combine en un seul texte géant séparé par `\n\n`

> **4** - Définit 6 tokens spéciaux : `<pad>`, `<unk>`, `<bos>`, `<eos>`, `<user>`, `<assistant>`

> **5** - Configure BPE avec pré-découpage sur espaces

> **6** - Entraîne pour apprendre 30 000 tokens (incluant les spéciaux)

> **7** - Sauvegarde dans `../Models/Tokenizer/tokenizer_30000.json`

> **8** - Retourne le tokenizer prêt pour encoder/décoder

---

# IV - Building the LLM (transformer model)

## Classe `SimpleTransformer`

## Objectif

Architecture de modèle Transformer pour la génération de texte autorégressif. 
Prédit le token suivant à partir d'une séquence d'entrée.

---

## Méthode `__init__` : Construction du Modèle

### Paramètres

```python
def __init__(self, vocab_size, embed_dim, num_heads, hidden_dim, num_layers, seq_len):
```

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| `vocab_size` | 30 000 | Taille du vocabulaire (nombre de tokens différents) |
| `embed_dim` | 512 | Dimension des vecteurs d'embedding |
| `num_heads` | 8 | Nombre de têtes d'attention parallèles |
| `hidden_dim` | 2048 | Dimension de la couche feedforward |
| `num_layers` | 12 | Nombre de couches Transformer empilées |
| `seq_len` | 256 | Longueur maximale de séquence (contexte) |

---

### Étape 1 : Initialisation de la classe parent

```python
super(SimpleTransformer, self).__init__()
```

Hérite de `nn.Module` (classe de base PyTorch pour tous les réseaux de neurones).

---

### Étape 2 : Embedding des tokens

```python
self.embedding = nn.Embedding(vocab_size, embed_dim)
```

**Rôle :** Convertit les IDs de tokens en vecteurs denses de 512 dimensions.

**Exemple :**

```python
Token ID : 5421 (mot "Hello")
    ↓
Vecteur : [0.234, -0.891, 0.456, ..., 0.123]  # 512 nombres
```

**Détails :**
- Matrice de taille `[30000, 512]`
- Chaque ligne = représentation vectorielle d'un token
- Ces vecteurs sont **appris** pendant l'entraînement

---

### Étape 3 : Embedding des positions

```python
self.position_embedding = nn.Embedding(seq_len, embed_dim)
```

**Rôle :** Encode la position de chaque token dans la séquence.

**Pourquoi ?** Les Transformers n'ont pas de notion d'ordre naturel, il faut l'ajouter explicitement.

**Exemple :**

```python
Position 0 → [0.123, 0.456, ...]  # vecteur position 0
Position 1 → [0.789, -0.234, ...] # vecteur position 1
Position 2 → [0.345, 0.678, ...]  # vecteur position 2
```

**Détails :**
- Matrice de taille `[256, 512]`
- Position 0 = début de séquence, Position 255 = fin

---

### Étape 4 : Couches Transformer

```python
self.transformer_blocks = nn.ModuleList([
    nn.TransformerEncoderLayer(d_model=embed_dim,           # 512 dimensions
                               nhead=num_heads,             # 8 têtes d'attention
                               dim_feedforward=hidden_dim,  # 2048 neurones
                               batch_first=False) for _ in range(num_layers)])
```

**Rôle :** Liste de 12 couches Transformer identiques empilées.

**Chaque couche contient :**

1. **Multi-Head Attention** : 8 têtes qui regardent différents aspects du texte
2. **Feedforward Network** : 2 couches denses (512→2048→512)
3. **Layer Normalization** : Stabilise l'apprentissage
4. **Residual Connections** : Préserve l'information des couches précédentes

**Pourquoi `batch_first=False` ?**
- Format attendu : `[seq_len, batch, embed_dim]`
- On transpose avant/après pour respecter ce format

---

### Étape 5 : Normalisation finale

```python
self.norm = nn.LayerNorm(embed_dim)
```

**Rôle :** Normalise les activations après toutes les couches Transformer.

**Formule :**

```
x_normalized = (x - mean) / std
```

Stabilise les valeurs pour la couche de sortie.

---

### Étape 6 : Couche de sortie

```python
self.fc = nn.Linear(embed_dim, vocab_size)
```

**Rôle :** Projette les 512 dimensions vers 30 000 scores (un par token du vocabulaire).

**Transformation :**

```python
Vecteur [512 dim] → Scores [30000 dim]
                 ↓
    [0.23, -1.45, 2.78, ..., 0.91]
       ↓      ↓      ↓          ↓
    Token0 Token1 Token2 ... Token29999
```

Le token avec le **score le plus élevé** est le plus probable.

---

## Méthode `forward` :

### Étape 1 : Créer les embeddings de position

```python
positions = torch.arange(0, x.size(1), device=x.device).unsqueeze(0)
```

**Opération :**

```python
x.size(1) = 256  # longueur de séquence

torch.arange(0, 256) → [0, 1, 2, 3, ..., 255]

.unsqueeze(0) → [[0, 1, 2, 3, ..., 255]]  # shape: [1, 256]
```

**Pourquoi `unsqueeze(0)` ?** Pour broadcaster sur tout le batch.

---

### Étape 2 : Combiner embeddings de tokens + positions

```python
x = self.embedding(x) + self.position_embedding(positions)
```

**Opération détaillée :**

**Input :**
```python
x = [[234, 567, 891, 123]]  # batch=1, seq_len=4
```

**Token embeddings :**
```python
self.embedding(x) → [[[0.12, 0.45, ...],   # token 234
                      [0.67, -0.23, ...],  # token 567
                      [0.34, 0.89, ...],   # token 891
                      [0.56, -0.12, ...]]] # token 123
```

**Position embeddings :**

```python
positions = [[0, 1, 2, 3]]

self.position_embedding(positions) → [[[0.23, 0.11, ...],  # position 0
                                       [0.45, -0.33, ...], # position 1
                                       [0.67, 0.22, ...],  # position 2
                                       [0.89, -0.44, ...]]]# position 3
```

**Addition (élément par élément) :**

```python
x = token_embed + position_embed
```

Chaque token a maintenant **son contenu + sa position** encodés.

---

### Étape 3 : Transposer pour les couches Transformer

```python
x = x.transpose(0, 1)  # [batch, seq, embed] → [seq, batch, embed]
```

**Transformation :**

```python
Avant : [1, 256, 512]  # [batch, seq_len, embed_dim]
Après : [256, 1, 512]  # [seq_len, batch, embed_dim]
```

**Pourquoi ?** Les `TransformerEncoderLayer` avec `batch_first=False` attendent ce format.

---

### Étape 4 : Créer le masque causal

```python
mask = torch.triu(torch.ones(x.size(0), x.size(0), device=x.device) * float('-inf'), diagonal=1)
```

**Rôle :** Empêche le modèle de "tricher" en regardant les tokens futurs.

**Construction du masque pour seq_len=4 :**

**1. Créer une matrice carrée de 1 :**

```python
torch.ones(4, 4) = [[1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1],
                    [1, 1, 1, 1]]
```

**2. Triangle supérieur (diagonal=1) :**

```python
torch.triu(..., diagonal=1) = [[0, 1, 1, 1],
                               [0, 0, 1, 1],
                               [0, 0, 0, 1],
                               [0, 0, 0, 0]]
```

**3. Multiplier par -inf :**

```python
mask = [[0,    -inf, -inf, -inf],
        [0,    0,    -inf, -inf],
        [0,    0,    0,    -inf],
        [0,    0,    0,    0   ]]
```

**Interprétation :**

- Position 0 : voit seulement token 0
- Position 1 : voit tokens 0 et 1
- Position 2 : voit tokens 0, 1, 2
- Position 3 : voit tokens 0, 1, 2, 3

**Visualisation :**

```
Token 0: "The"     → peut voir : ["The"]
Token 1: "cat"     → peut voir : ["The", "cat"]
Token 2: "sat"     → peut voir : ["The", "cat", "sat"]
Token 3: "on"      → peut voir : ["The", "cat", "sat", "on"]
```

Le modèle génère **de gauche à droite** sans voir le futur ! 

---

### Étape 5 : Passer à travers les 12 couches Transformer

```python
for block in self.transformer_blocks:
    x = block(x, src_mask=mask)
```

**Opération répétée 12 fois :**

Chaque couche transforme `x` avec :

1. **Self-Attention** (avec masque causal)
2. **Feedforward Network**
3. **Normalizations + Residuals**

**Flow :**

```
x [256, 1, 512]
    ↓
Couche 1 (attention + feedforward)
    ↓
Couche 2 (attention + feedforward)
    ↓
...
    ↓
Couche 12 (attention + feedforward)
    ↓
x [256, 1, 512]  # Représentations enrichies
```

---

### Étape 6 : Re-transposer

```python
x = x.transpose(0, 1)  # [seq, batch, embed] → [batch, seq, embed]
```

**Transformation :**

```python
Avant : [256, 1, 512]
Après : [1, 256, 512]
```

Retour au format standard `[batch, seq_len, embed_dim]`.

---

### Étape 7 : Normalisation finale

```python
x = self.norm(x)
```

Normalise les activations avant la projection finale.

---

### Étape 8 : Projection vers vocabulaire

```python
return self.fc(x)
```

**Transformation finale :**

```python
x : [1, 256, 512]
    ↓
self.fc(x) : [1, 256, 30000]
```

**Sortie :**

Pour chaque position (256) :
- 30 000 scores (un par token du vocabulaire)
- Le plus haut score = token le plus probable

**Exemple pour position 5 :**

```python
logits[0, 5, :] = [-2.3, 4.5, 1.2, ..., -0.8]
                     ↓     ↓    ↓          ↓
                  Token0 Token1 Token2 ... Token29999

Token le plus probable : Token1 (score 4.5)
```

---

## Résumé du Flow Complet

```
Input: [batch=1, seq_len=256] de token IDs
    ↓
[1] Token Embedding [1, 256, 512]
    ↓
[2] + Position Embedding [1, 256, 512]
    ↓
[3] Transpose → [256, 1, 512]
    ↓
[4] Créer masque causal [256, 256]
    ↓
[5] 12× Transformer Layers (avec masque)
    ↓
[6] Transpose → [1, 256, 512]
    ↓
[7] Layer Norm
    ↓
[8] Linear → [1, 256, 30000]
    ↓
Output: Scores pour chaque token du vocabulaire à chaque position
```

---

# V - Training the LLM

# Fonction `train_on_stage`

## Objectif
Entraîne le modèle sur un stage spécifique (grammar, simple, dialogue, etc.) avec support du **transfer learning** et **early stopping**.

---

## Paramètres

```python
def train_on_stage(stage_name, data_path, model_settings, tokenizer, previous_model_path=None):
```

| Paramètre | Type | Description |
|-----------|------|-------------|
| `stage_name` | str | Nom du stage ("grammar", "simple", "dialogue", etc.) |
| `data_path` | str | Chemin vers le fichier de données (`../Data/simple.txt`) |
| `model_settings` | dict | Configuration du modèle (vocab_size, embed_dim, etc.) |
| `tokenizer` | Tokenizer | Tokenizer BPE pré-entraîné |
| `previous_model_path` | str (optionnel) | Chemin vers le modèle du stage précédent |

**Retourne :** Chemin vers le meilleur modèle sauvegardé, ou `None` si échec.

---

## Phase 1 : Initialisation

### Étape 1 : Affichage du stage

```python
print(f"\n{'='*60}")
print(f"Training Stage: {stage_name.upper()}")
print(f"{'='*60}")
```

**Exemple de sortie :**

```
============================================================
Training Stage: DIALOGUE
============================================================
```

---

### Étape 2 : Vérification du fichier de données

```python
if not os.path.exists(data_path):
    print(f"Warning: {data_path} not found. Skipping stage.")
    return None
```

- Vérifie si le fichier existe
- Si non → affiche un warning et retourne `None`
- **Évite les crashs** si un stage est manquant

---

### Étape 3 : Chargement des données

```python
dataset = TextDataset(data_path, tokenizer)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
```

**`TextDataset(data_path, tokenizer)` :**

- Charge le fichier texte
- Ajoute les marqueurs `<eos>`
- Tokenize tout en IDs
- Crée des chunks de 256 tokens

**`DataLoader(..., batch_size=16, shuffle=True)` :**

- Charge les données par batches de 16 séquences
- `shuffle=True` : mélange les exemples à chaque epoch
- **Pourquoi mélanger ?** Évite que le modèle apprenne l'ordre des données

**Exemple :**

```python
# Un batch contient 16 séquences de 256 tokens
batch = next(iter(dataloader))
input_ids, target_ids = batch
# input_ids.shape = [16, 256]
# target_ids.shape = [16, 256]
```

---

### Étape 4 : Création du modèle

```python
model = SimpleTransformer(vocab_size=VOCAB_SIZE,      
                          embed_dim=EMBED_DIM,        
                          num_heads=NUM_HEADS,        
                          hidden_dim=HIDDEN_DIM,      
                          num_layers=NUM_LAYERS,      
                          seq_len=SEQ_LEN).to(DEVICE)
```

- Crée une nouvelle instance du modèle Transformer
- `.to(DEVICE)` : déplace le modèle sur GPU/CPU
- **Important :** Modèle initialisé avec des poids **aléatoires** (sauf si transfer learning)

---

## Phase 2 : Transfer Learning

### Étape 5 : Charger les poids du stage précédent

```python
if previous_model_path and os.path.exists(previous_model_path):
    print(f"Loading weights from previous stage: {previous_model_path}")
    
    try:
        model.load_state_dict(torch.load(previous_model_path, 
                                        map_location=DEVICE, 
                                        weights_only=True))
        current_lr = FINE_TUNE_LR  # 5e-5 (plus petit)
        print(f"Transfer learning enabled (LR: {current_lr})")
    
    except Exception as e:
        print(f"Could not load previous model: {e}")
        current_lr = LEARNING_RATE  # 5e-4 (normal)

else:
    current_lr = LEARNING_RATE
    print(f"🆕 Training from scratch (LR: {current_lr})")
```

**Logique du Transfer Learning :**

| Condition | Action | Learning Rate |
|-----------|--------|---------------|
| `previous_model_path` existe | Charge les poids | `5e-5` (fine-tuning) |
| Chargement échoue | Continue sans charger | `5e-4` (normal) |
| Pas de modèle précédent | Entraînement from scratch | `5e-4` (normal) |

**Pourquoi LR plus petit pour fine-tuning ?**

- Le modèle a déjà appris des choses utiles
- On veut **affiner** sans tout casser
- Changements plus délicats et progressifs

**Exemple de flow :**

```
Stage 1 (grammar)  : Train from scratch (LR=5e-4)
       ↓
Stage 2 (simple)   : Load grammar weights (LR=5e-5)
       ↓
Stage 3 (dialogue) : Load simple weights (LR=5e-5)
```

---

## Phase 3 : Configuration de l'Optimisation

### Étape 6 : Fonction de perte

```python
loss_fn = nn.CrossEntropyLoss(ignore_index=0)
```

**CrossEntropyLoss :**

- Compare les prédictions du modèle avec les vraies valeurs
- `ignore_index=0` : ignore les tokens de padding `<pad>`

**Fonctionnement :**

```python
# Pour chaque position, on a 30 000 scores
predictions = [2.3, -1.2, 4.5, ..., 0.8]  # scores bruts (logits)
target = 567                              # ID du vrai token

# La loss mesure à quel point le modèle s'est trompé
# Plus le score du bon token est élevé → loss faible
# Plus le score du bon token est bas → loss élevée
```

---

### Étape 7 : Optimiseur

```python
optimizer = AdamW(model.parameters(), lr=current_lr)
```

**AdamW :**

- Algorithme d'optimisation avancé
- Ajuste les poids du modèle pour réduire la loss
- Version améliorée d'Adam avec weight decay

**`lr=current_lr` :**

- `5e-4` pour premier stage
- `5e-5` pour transfer learning

---

### Étape 8 : Scheduler de Learning Rate

```python
num_training_steps = len(dataloader) * EPOCHS

lr_scheduler = get_scheduler("linear",
                             optimizer=optimizer,
                             num_warmup_steps=WARMUP_STEPS,     
                             num_training_steps=num_training_steps)
```

**Calcul du nombre d'étapes :**
```python
num_batches = 10000 / 16 = 625 batches par epoch
num_training_steps = 625 * 100 = 62 500 étapes totales
```

**Scheduler linéaire avec warmup :**

```
Learning Rate
    ↑
5e-4│         ╱────────────────────╲
    │        ╱                      ╲
    │       ╱                        ╲
    │      ╱                          ╲
    │     ╱                            ╲
0   │____╱                              ╲____
    └─────────────────────────────────────────→ Steps
         500          Milieu          62500
       (warmup)                    (fin training)
```

**Phase 1 (0→500 steps) :** LR augmente progressivement (warmup)
**Phase 2 (500→62500 steps) :** LR diminue linéairement jusqu'à 0

**Pourquoi ?**

- Warmup : stabilise l'entraînement au début
- Décroissance : affine les poids en fin d'entraînement

---

### Étape 9 : Configuration du modèle et early stopping

```python
model.train()        # Mode entraînement (active dropout, batch norm, etc.)
max_grad_norm = 1.0  # Gradient c
