# Conversational Language Model Pipeline

This repository implements a complete pipeline for training and deploying a transformer-based conversational language model using classical English literature, with progressive curriculum learning and transfer learning between stages.

---

## 📁 Project Structure

- **`data_preprocessing.py`** 

  Downloads and processes public domain texts from Project Gutenberg, organizing them into 5 curriculum stages with special emphasis on conversational content. Extracts dialogues and structures them for optimal conversational learning.

- **`model_train.ipynb`** 

  Handles the complete training pipeline:

  - Single unified BPE tokenizer training across all datasets
  - Transformer model with causal masking
  - Dataset preparation with special tokens for conversation
  - Sequential training with transfer learning between stages
  - Early stopping, checkpointing, and learning rate scheduling

- **`model_use.ipynb`**

  Interactive inference interface featuring:

  - Model selection from trained checkpoints
  - Conversation history management
  - Top-k & top-p sampling for diverse generation
  - Special tokens handling (`<user>`, `<assistant>`, `<eos>`)
  - Context-aware response generation

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
   - Natural conversation patterns
   - Emma, Little Women, Tom Sawyer, Huckleberry Finn, etc.
   - ~6 books with extracted dialogue structures

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

Enhanced transformer architecture optimized for conversational AI:

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
<user>       # User message marker
<assistant>  # Model response marker
```

---

## 🔄 Training Pipeline

### 1. Unified Tokenizer Training

A **single BPE tokenizer** is trained on all datasets combined:
- Ensures vocabulary consistency across all stages
- Enables seamless transfer learning
- Includes 6 special tokens for conversation structure
- Saved as `tokenizer_30000.json` for inference

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
├─ Learn conversational patterns
└─ Core objective achieved
      ↓
Stage 4: Intermediate
├─ Load Dialogue weights (LR = 5e-5)
├─ Enrich vocabulary
└─ Consolidate understanding
      ↓
Stage 5: Complex
├─ Load Intermediate weights (LR = 5e-5)
├─ Refine with literary style
└─ Final conversational model
```

### 3. Training Features

- **Transfer Learning**: Each stage inherits knowledge from previous stages
- **Early Stopping**: Halts training after 5 epochs without improvement
- **Gradient Clipping**: Prevents exploding gradients (max norm = 1.0)
- **Learning Rate Scheduling**: Linear decay with 500-step warmup
- **Checkpointing**: Saves model every 10 epochs + best model per stage
- **Logging**: Comprehensive training logs for analysis

---

## 💾 File Structure

```
project/
├── data/
│   ├── grammar.txt
│   ├── simple.txt
│   ├── dialogue.txt
│   ├── dialogue_dialogues.txt      # Extracted conversations
│   ├── intermediate.txt
│   ├── intermediate_dialogues.txt  # Extracted conversations
│   └── complex.txt
│
├── Models/
│   ├── Tokenizer/
│   │   └── tokenizer_30000.json    # Unified tokenizer
│   │
│   ├── grammar_epoch_15.pth
│   ├── grammar_epoch_15_settings.json
│   ├── simple_epoch_8.pth
│   ├── simple_epoch_8_settings.json
│   ├── dialogue_epoch_12.pth       # Best conversational model
│   ├── dialogue_epoch_12_settings.json
│   └── ...
│
├── data_preprocessing.py
├── training.py
├── inference.py
├── training.log
└── README.md
```

---

## 🧪 Usage

### 1. Data Preprocessing

```bash
python data_preprocessing.py
```

**What it does:**
- Downloads books from Project Gutenberg
- Cleans and structures text (preserves dialogues)
- Extracts conversations from dialogue-rich stages
- Saves organized datasets to `data/` directory
- Displays statistics (file sizes, word counts)

---

### 2. Model Training

```bash
python training.py
```

**What it does:**
- Trains/loads unified tokenizer (runs once)
- Trains model sequentially through all 5 stages
- Applies transfer learning between stages
- Saves best model from each stage
- Logs all training metrics

---

### 3. Interactive Inference

```bash
python inference.py
```

**What it does:**
- Loads tokenizer and displays available models
- User selects trained model
- Enters conversation mode with context management
- Generates responses using the trained model

---

## 🗣️ Interactive Features

### Conversation Management
- **Context Retention**: Maintains conversation history up to ~150 tokens
- **Clear Command**: Reset context with `clear`
- **Graceful Exit**: Use `quit` or `exit` to leave

### Generation Parameters
- **Temperature** (0.8): Controls randomness (lower = more focused)
- **Top-k** (40): Considers top 40 most likely tokens
- **Top-p** (0.9): Nucleus sampling for diversity
- **Max Length** (50 tokens): Response length limit
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

1. **Progressive Complexity**: Models learn better with gradual difficulty increase
2. **Transfer Learning**: Each stage benefits from previous knowledge
3. **Specialization**: Dialogue stage focuses on conversational patterns
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

## 🚀 Future Improvements

- [ ] Add validation set for better early stopping
- [ ] Implement beam search for more coherent long responses
- [ ] Fine-tune on modern conversational datasets
- [ ] Add response quality metrics
- [ ] Implement conversation summary for very long chats
- [ ] Multi-turn conversation training strategy
- [ ] Persona conditioning with additional tokens
