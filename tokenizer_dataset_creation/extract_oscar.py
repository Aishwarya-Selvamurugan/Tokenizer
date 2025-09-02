import os
from datasets import load_dataset

LANGUAGE_CODES = {
    "Yoruba": "unshuffled_deduplicated_yo",
    "Arabic": "unshuffled_deduplicated_ar",
    "Mandarin Chinese": "unshuffled_deduplicated_zh",
    "Russian": "unshuffled_deduplicated_ru",
    "Hindi": "unshuffled_deduplicated_hi",
    "Japanese": "unshuffled_deduplicated_ja",
    "Swahili": "unshuffled_deduplicated_sw",
    "Bengali": "unshuffled_deduplicated_bn",
    "Turkish": "unshuffled_deduplicated_tr",
}

def extract_oscar_language(language_name, lang_code, limit_chars=50_000_000, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"oscar_{language_name.replace(' ', '_').lower()}_50M.txt")
    
    print(f"\n🔤 Processing {language_name}...")

    try:
        dataset = load_dataset(
            "oscar",
            lang_code,
            split="train",
            streaming=True,
            trust_remote_code=True
        )

        total_chars = 0
        doc_count = 0

        with open(output_path, "w", encoding="utf-8") as f:
            for sample in dataset:
                text = sample["text"].strip()
                if not text:
                    continue

                remaining = limit_chars - total_chars
                if remaining <= 0:
                    break

                if len(text) > remaining:
                    text = text[:remaining]

                f.write(text + "\n")
                total_chars += len(text)
                doc_count += 1

        print(f"✅ {language_name}: Extracted {total_chars:,} characters from {doc_count:,} documents.")
        print(f"📄 Saved to: {output_path}")
    except Exception as e:
        print(f"❌ Failed to process {language_name}: {e}")

def extract_all_languages():
    for lang_name, code in LANGUAGE_CODES.items():
        extract_oscar_language(lang_name, code)

# === Run the full extraction ===
extract_all_languages()
