From Bias to Balance: How Multilingual Dataset Composition Affects Tokenizer Performance Across Languages
This repository contains the implementation and experimental setup for the research paper investigating how balanced multilingual datasets impact tokenizer performance across typologically diverse languages.
Overview
This study systematically evaluates three subword tokenization algorithms (BPE, WordPiece, and Unigram) across nine languages using balanced training corpora, assessing both intrinsic tokenization metrics and downstream task performance on POS tagging, NER, and machine translation.
Repository Structure
├── Machine_Translation/       # Machine translation experiments using BART-large
├── NER/                      # Named Entity Recognition task implementation
├── POS/                      # Part-of-Speech tagging experiments
├── Test_data_NSL_Sub_Word_fertility/  # Evaluation scripts for intrinsic metrics
├── tokenizer_dataset_creation/        # Dataset preprocessing and creation scripts
├── Tokenizer.ipynb                   # Main tokenizer training notebook
├── Tokenizer_results.xlsx            # Compiled experimental results
└── tokenizer_nsl_fertility_report.csv # Detailed intrinsic evaluation metrics
Languages Studied

African Languages: Yoruba, Swahili
Asian Languages: Mandarin Chinese, Japanese, Hindi, Bengali
European Languages: Russian, Turkish
Middle Eastern Languages: Arabic

These languages represent diverse writing systems (Latin, Arabic, Devanagari, Cyrillic, CJK), morphological complexity levels, and resource availability.
Tokenization Algorithms

Byte Pair Encoding (BPE) - Frequency-driven character pair merging
WordPiece - Likelihood-based merging with morphological awareness
Unigram Language Model - Probabilistic framework with comprehensive vocabularies

Each algorithm is evaluated across three vocabulary sizes: 15k, 30k, and 50k tokens.
Key Features
Dataset Construction

Balanced multilingual corpora from Wikipedia and OSCAR
Equal per-language character allocations to reduce high-resource bias
Three dataset scales: 100M, 200M, and 400M characters
Comprehensive preprocessing pipeline with Unicode normalization

Evaluation Metrics

Intrinsic: Normalized Sequence Length (NSL) and Subword Fertility
Extrinsic: Performance on downstream NLP tasks

Downstream Tasks

POS Tagging: Token classification using BERT-based models
Named Entity Recognition: Sequence labeling with class weighting
Machine Translation: Multilingual BART-large with custom tokenizers

Installation and Setup
Prerequisites

Python 3.10+
CUDA 11.8+
GPU with at least 16GB VRAM (Tesla T4 or better)
For machine translation: 24GB VRAM recommended (RTX 4090 or equivalent)
