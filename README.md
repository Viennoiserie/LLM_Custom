
# Shakespearean Language Model Pipeline

This repository implements a full pipeline for training and using a transformer-based language model on classical English texts, culminating in an interactive Shakespeare-like text generator.

---

## 📁 Project Structure

- **`data_preprocessing.py`**  
  Downloads and cleans public domain texts from Project Gutenberg, organizing them by difficulty level (`grammar`, `simple`, `intermediate`, `complex`).

- **`training.ipynb`**  
  Handles:
  - Tokenizer training using BPE
  - Transformer model definition
  - Dataset preparation
  - Training with logging, saving, early stopping

- **`model_use.ipynb`**  
  Loads the trained model and settings. Interactively generates Shakespearean-style text using:
  - Top-k & top-p sampling
  - User prompts

---

## 📚 Datasets

Books are categorized into 4 difficulty stages:
- **Grammar**
- **Simple**
- **Intermediate**
- **Complex**

Each category is downloaded and saved as a single `.txt` file in the `data/` directory.

---

## 🧠 Model Architecture

A simplified transformer-based architecture:
- Embedding + Positional Encoding
- N Transformer blocks
- Causal Masking for autoregression
- Final Linear layer for vocabulary prediction

### Hyperparameters

| Parameter        | Value    |
|------------------|----------|
| Vocabulary Size  | 30,000   |
| Embedding Dim    | 256      |
| Layers           | 8        |
| Attention Heads  | 8        |
| Hidden Dimension | 512      |
| Sequence Length  | 128      |
| Batch Size       | 16       |
| Epochs           | 100      |
| Learning Rate    | 5e-4     |

---

## 💾 Model Saving

- **Settings JSON**: Saves model architecture and training parameters
- **Checkpointing**: Every N epochs or best loss
- **Final Models**: Stored in `../Models/`

---

## 🧪 Usage

1. **Preprocess**:
   ```bash
   python data_preprocessing.py
   ```

2. **Train** (from `training.ipynb`):
   Trains on each difficulty stage sequentially.

3. **Run Model** (from `model_use.ipynb`):
   Interactively chat with Shakespeare.

---

## 🗣️ Interactive Inference

Model can be prompted with any sentence:
```text
You: Wherefore art thou
Shakespeare: Wherefore art thou gone, sweet soul of mine, that I may seek thee still.
```

Exit with `quit`.

---

## 🔧 Dependencies

- `torch`
- `transformers`
- `tokenizers`
- `tqdm`
- `numpy`
- `requests`

---

## 📜 License

All books used are from [Project Gutenberg](https://www.gutenberg.org), in the public domain.
