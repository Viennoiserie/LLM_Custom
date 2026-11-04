# Conversational Language Model Pipeline

This repository is a from-scratch autoregressive language-modeling experiment using classical English literature, with progressive curriculum learning and transfer learning between stages. The current corpus does not support claims of reliable assistant-style conversation.

---

## 📁 Project Structure

- **`Scripts/data_preprocessing.py`**

  Downloads and processes public-domain texts from Project Gutenberg into five stages. One complete book per stage is held out for validation. Quoted passages are retained as unlabeled text; the preprocessor does not infer user/assistant roles from nearby sentences.

- **`model_train.ipynb`** 

  Handles the complete training pipeline:

  - Single unified BPE tokenizer trained on training data only
  - Transformer model with causal masking
  - Dataset preparation and whole-book validation
  - Sequential training with transfer learning between stages
  - Early stopping and best-checkpoint selection using validation loss

- **`model_use.ipynb`**

  Interactive prompted-text-generation interface featuring:

  - Model selection from trained checkpoints
  - Rolling prompt history (up to the model context window)
  - Top-k & top-p sampling for diverse generation
  - A consistent `<user>` / `<assistant>` prompt template
  - Model-specific tokenizer loading

  **Limitation:** the Gutenberg corpus does not provide reliable speaker labels or authentic assistant responses. The interface maintains and formats context, but useful conversational behavior requires a separate, carefully labeled conversation dataset.

---

## 📚 Curriculum Learning Stages

Books are organized into 5 progressive difficulty stages for optimal learning:

1. **Grammar** (Foundation)
   - English grammar textbooks
   - Linguistic rules and structures
   - ~5 reference books

2. **Simple** (Basic Narratives)
   - Children's literature
   - Clear, straightforward language
   - Alice in Wonderland, Peter Pan, Aesop's Fables, etc.
   - ~8 books

3. **Dialogue** (Conversational Focus) 
   - Dialogue-rich novels
   - Quoted speech from dialogue-rich novels
   - Emma, Little Women, Tom Sawyer, Huckleberry Finn, etc.
   - ~6 books; quoted utterances are unlabelled

4. **Intermediate** (Consolidation)
   - Classic novels
   - Rich vocabulary and complex narratives
   - Sherlock Holmes, Pride & Prejudice, Jane Eyre, etc.
   - ~8 books

5. **Complex** (Advanced Literature)
   - Shakespeare, Joyce, Marlowe
   - Sophisticated literary style
   - ~6 advanced texts

Each stage builds upon the previous one through **transfer learning**, with the model loading weights from the prior stage before fine-tuning.

---

## 🧠 Model Architecture

Transformer architecture for autoregressive text generation:

- **Token & Position Embeddings** (512 dimensions)
- **12 Transformer Encoder Layers** with:
  - 8 multi-head attention mechanisms
  - 2048-dimensional feedforward networks
  - Causal masking for autoregressive generation
  - Layer normalization and residual connections
- **Output projection** to 30,000-token vocabulary

### Hyperparameters

| Parameter           | Value       | Purpose                                    |
|---------------------|-------------|--------------------------------------------|
| Vocabulary Size     | 30,000      | BPE tokens covering all training data      |
| Embedding Dimension | 512         | Rich semantic representations              |
| Transformer Layers  | 12          | Deep hierarchical feature learning         |
| Attention Heads     | 8           | Multiple attention perspectives            |
| Hidden Dimension    | 2048        | Feedforward network capacity               |
| Sequence Length     | 256         | Context window (~200 words)                |
| Batch Size          | 16          | Training efficiency                        |
| Max Epochs          | 100         | With early stopping (patience=5)           |
| Learning Rate       | 5e-4 → 5e-5 | From scratch → Fine-tuning                 |
| Warmup Steps        | 500         | Gradual LR increase for stability          |

### Special Tokens

```python
<pad>        # Padding for variable-length sequences
<unk>        # Unknown tokens
<bos>        # Begin of sequence
<eos>        # End of sequence / paragraph separator
<user>       # Reserved prompt marker; not learned as a real role in Gutenberg data
<assistant>  # Reserved prompt marker; not learned as a real role in Gutenberg data
```

---

## 🔄 Training Pipeline

### 1. Training-only Tokenizer

A **single BPE tokenizer** is trained on training files only (not the held-out books):
- Ensures vocabulary consistency across all stages
- Enables seamless transfer learning
- Includes six reserved tokens; user/assistant roles are not present in the literary training data
- Saved as `Models/Tokenizer/tokenizer_30000_book_split_v2.json` for inference

### 2. Sequential Stage Training

```
Stage 1: Grammar
├─ Train from scratch (LR = 5e-4)
├─ Learn linguistic foundations
└─ Save best model weights
      ↓
Stage 2: Simple
├─ Load Grammar weights (LR = 5e-5)
├─ Learn basic narratives
└─ Transfer learning advantage
      ↓
Stage 3: Dialogue ⭐
├─ Load Simple weights (LR = 5e-5)
├─ Continue language modeling on books and unlabeled quotes
└─ Does not learn verified user/assistant roles
      ↓
Stage 4: Intermediate
├─ Load Dialogue weights (LR = 5e-5)
├─ Enrich vocabulary
└─ Consolidate understanding
      ↓
Stage 5: Complex
├─ Load Intermediate weights (LR = 5e-5)
├─ Refine with literary style
└─ Final literature-trained text model
```

### 3. Training Features

- **Transfer Learning**: Each stage inherits knowledge from previous stages
- **Early Stopping**: Halts training after 5 epochs without improvement
- **Gradient Clipping**: Prevents exploding gradients (max norm = 1.0)
- **Learning Rate Scheduling**: Linear decay with 500-step warmup
- **Checkpoint selection**: Saves the best model per stage by held-out validation loss
- **Logging**: Comprehensive training logs for analysis

---

## 💾 File Structure

```
project/
├── Data/
│   ├── grammar.txt
│   ├── grammar_validation.txt
│   ├── simple.txt
│   ├── simple_validation.txt
│   ├── dialogue.txt
│   ├── dialogue_validation.txt
│   ├── dialogue_dialogues.txt      # Unlabeled quoted utterances
│   ├── intermediate.txt
│   ├── intermediate_validation.txt
│   ├── intermediate_dialogues.txt  # Unlabeled quoted utterances
│   ├── complex.txt
│   └── complex_validation.txt
│
├── Models/
│   ├── Tokenizer/
│   │   └── tokenizer_30000_book_split_v2.json
│   │
│   ├── book_split_v2/
│   │   ├── grammar_best.pth
│   │   ├── grammar_best_settings.json
│   └── ...
│
├── Scripts/
│   ├── data_preprocessing.py
│   ├── model_train.ipynb
│   ├── model_use.ipynb
│   └── Logs/training.log
└── README.md
```

---

## 🧪 Usage

### 1. Data Preprocessing

```powershell
python Scripts\data_preprocessing.py
```

**What it does:**
- Downloads books from Project Gutenberg
- Cleans text and writes stage datasets under `Data\`
- Holds out one complete book per stage for validation
- Extracts quoted utterances without inventing speaker labels
- Displays statistics (file sizes, word counts)

---

### 2. Model Training

Open and run `Scripts/model_train.ipynb` from top to bottom. It trains/loads the versioned tokenizer, trains all five stages, selects each best checkpoint by held-out validation loss, and stops after five consecutive epochs without improvement.

---

### 3. Interactive Inference

Open and run `Scripts/model_use.ipynb` from top to bottom. It lists available checkpoints, loads the tokenizer recorded for the selected model, and generates from a rolling prompt. The model context window limits retained history.

---

## 🗣️ Interactive Features

### Prompt Management
- **Context Retention**: Maintains recent turns up to the model's configured token window
- **Clear Command**: Reset context with `clear`
- **Graceful Exit**: Use `quit` or `exit` to leave

### Generation Parameters
- **Temperature** (0.8): Controls randomness (lower = more focused)
- **Top-k** (40): Considers top 40 most likely tokens
- **Top-p** (0.9): Nucleus sampling for diversity
- **Max Length** (80 tokens): Generation limit
- **Stop Tokens**: Automatically stops at `<eos>` or `<pad>`

---

## 🔧 Dependencies

```bash
pip install torch>=2.0.0
pip install transformers>=4.30.0
pip install tokenizers>=0.13.0
pip install tqdm>=4.65.0
pip install numpy>=1.24.0
pip install requests>=2.31.0
```

**System Requirements:**
- Python 3.8+
- CUDA-capable GPU recommended (16GB+ VRAM for training)
- ~10GB disk space for datasets and models

---


## 🎯 Design Choices

### Why Curriculum Learning ?

1. **Progressive Complexity**: Training follows a gradual difficulty progression
2. **Transfer Learning**: Each stage benefits from previous knowledge
3. **Quoted Text**: The dialogue stage adds quoted utterances, without claiming their speakers are known
4. **Robustness**: Exposure to diverse text styles creates versatile model

### Why This Architecture ?

- **512 dimensions**: Balances expressiveness and computational efficiency
- **12 layers**: Sufficient depth for language understanding
- **256 context**: Reasonable conversation history without memory issues
- **Causal masking**: Essential for autoregressive text generation

---

## 📜 Data Sources

All texts are from [Project Gutenberg](https://www.gutenberg.org) and are in the public domain.

**Notable Works Included:**
- Grammar: Comprehensive English grammar textbooks
- Simple: Alice in Wonderland, Peter Pan, The Wizard of Oz
- Dialogue: Emma, Little Women, Tom Sawyer
- Intermediate: Pride & Prejudice, Sherlock Holmes, Dracula
- Complex: Complete Shakespeare, Ulysses, Don Quixote

---

The `<user>` / `<assistant>` template and rolling context make inference inputs consistent, but they do not make a literature-trained model conversational. Add real, accurately speaker-labeled conversations before treating its output as assistant responses.

## 🚀 Future Improvements

- [ ] Add a verified, speaker-labeled conversation dataset and fine-tune on it
- [ ] Implement beam search for more coherent long responses
- [ ] Fine-tune on modern conversational datasets
- [ ] Add response quality metrics
- [ ] Implement conversation summary for very long chats
- [ ] Multi-turn conversation training strategy
- [ ] Persona conditioning with additional tokens