import subprocess
import json
import os
from pathlib import Path
import sys

def install_wikiextractor():
    """Install WikiExtractor if not already installed"""
    try:
        import wikiextractor
        print("WikiExtractor is already installed")
    except ImportError:
        print("Installing WikiExtractor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "wikiextractor"])
        print("WikiExtractor installed successfully")

def extract_wikipedia_dump(dump_file, output_dir, language):
    """Extract Wikipedia dump using WikiExtractor"""
    print(f"Extracting {language} Wikipedia dump: {dump_file}")
    
    # WikiExtractor command with only supported arguments
    cmd = [
        sys.executable, "-m", "wikiextractor.WikiExtractor",
        "--output", output_dir,
        "--bytes", "100M",
        "--json",
        "--processes", "4",
        dump_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Successfully extracted {language} dump")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {language} dump: {e}")
        print(f"Error output: {e.stderr}")
        return False

def process_extracted_json(extracted_dir, language, output_file):
    """Process WikiExtractor JSON output and save title + text"""
    articles = []
    article_count = 0
    
    print(f"Processing extracted files for {language}...")
    
    # Walk through all extracted files
    for root, dirs, files in os.walk(extracted_dir):
        for file in files:
            if file.startswith('wiki_') and file.endswith('.json'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                article = json.loads(line)
                                title = article.get('title', '').strip()
                                text = article.get('text', '').strip()
                                
                                # Filter out disambiguation pages and very short articles
                                if (title and text and len(text) > 100 and 
                                    not title.lower().endswith('disambiguation') and
                                    not title.startswith('List of') and
                                    'may refer to:' not in text[:200].lower()):
                                    
                                    articles.append({
                                        'title': title,
                                        'text': text
                                    })
                                    article_count += 1
                
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    # Save to output file
    if articles:
        with open(output_file, 'w', encoding='utf-8') as f:
            for article in articles:
                f.write(f"TITLE: {article['title']}\n")
                f.write(f"TEXT: {article['text']}\n")
                f.write("=" * 80 + "\n\n")
        
        print(f"Saved {article_count} articles for {language} to {output_file}")
    else:
        print(f"No articles found for {language}")
    
    return article_count

def find_dump_file(language, dump_dir="wiki_dumps"):
    """Find Wikipedia dump file for a language"""
    possible_names = [
        f"{language}wiki-latest-pages-articles.xml.bz2",
        f"{language}wiki-latest-pages-articles.xml.gz",
        f"{language}wiki-latest-pages-articles.xml",
        f"{language}wiki-pages-articles.xml.bz2",
        f"{language}wiki-pages-articles.xml.gz",
        f"{language}wiki-pages-articles.xml"
    ]
    
    for name in possible_names:
        filepath = os.path.join(dump_dir, name)
        if os.path.exists(filepath):
            return filepath
    
    return None

def main():
    # Configuration
    languages = ['yo', 'ar', 'zh', 'ru', 'hi', 'ja', 'sw', 'bn', 'tr']
    dump_directory = "wiki_dumps"
    txt_directory = "txt"
    temp_directory = "temp_extracted"
    
    # Install WikiExtractor
    install_wikiextractor()
    
    # Create directories
    Path(txt_directory).mkdir(exist_ok=True)
    Path(temp_directory).mkdir(exist_ok=True)
    
    # Statistics
    stats = {}
    
    for language in languages:
        print(f"\n{'='*50}")
        print(f"Processing {language.upper()}")
        print(f"{'='*50}")
        
        # Find dump file
        dump_file = find_dump_file(language, dump_directory)
        if not dump_file:
            print(f"No dump file found for {language}")
            stats[language] = 0
            continue
        
        # Extract using WikiExtractor
        temp_output = os.path.join(temp_directory, language)
        success = extract_wikipedia_dump(dump_file, temp_output, language)
        
        if not success:
            stats[language] = 0
            continue
        
        # Process extracted JSON files
        output_file = os.path.join(txt_directory, f"{language}_articles.txt")
        article_count = process_extracted_json(temp_output, language, output_file)
        stats[language] = article_count
        
        # Clean up temporary files
        import shutil
        if os.path.exists(temp_output):
            shutil.rmtree(temp_output)
    
    # Save statistics
    stats_file = os.path.join(txt_directory, "extraction_stats.txt")
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("Wikipedia Article Extraction Statistics\n")
        f.write("=" * 50 + "\n\n")
        
        total_articles = 0
        for lang in languages:
            count = stats.get(lang, 0)
            f.write(f"{lang}: {count:,} articles\n")
            total_articles += count
        
        f.write(f"\nTotal: {total_articles:,} articles\n")
        f.write(f"\nLanguage Details:\n")
        f.write("-" * 20 + "\n")
        for lang in languages:
            count = stats.get(lang, 0)
            lang_names = {
                'yo': 'Yoruba', 'ar': 'Arabic', 'zh': 'Chinese', 
                'ru': 'Russian', 'hi': 'Hindi', 'ja': 'Japanese',
                'sw': 'Swahili', 'bn': 'Bengali', 'tr': 'Turkish'
            }
            f.write(f"{lang_names.get(lang, lang)}: {count:,}\n")
    
    print(f"\n{'='*50}")
    print("EXTRACTION COMPLETE!")
    print(f"{'='*50}")
    print(f"Statistics saved to: {stats_file}")
    print(f"Article files saved to: {txt_directory}/")
    print("\nSummary:")
    total = 0
    for lang in languages:
        count = stats.get(lang, 0)
        print(f"  {lang}: {count:,} articles")
        total += count
    print(f"\nTotal: {total:,} articles extracted")

if __name__ == "__main__":
    main()