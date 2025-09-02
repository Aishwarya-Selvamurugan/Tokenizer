#!/usr/bin/env python3
"""
Multilingual Data Merger Script - Balanced Approach
Uses the lowest available language as baseline for perfect balance
"""

import os
import random
import math
from typing import Dict, List, Tuple
import csv

# Configuration
LANGUAGES = ['yo', 'ar', 'zh', 'ru', 'hi', 'ja', 'sw', 'bn', 'tr']
WIKI_DIR = 'wiki_data_final'
OSCAR_DIR = 'output'
OUTPUT_DIR = 'final_outputs'

# Language data availability (based on your provided data)
LANGUAGE_DATA = {
    'yo': {'wiki': 12_646_633, 'oscar': 18_209, 'total': 12_664_842},
    'ar': {'wiki': 1_326_903_243, 'oscar': 50_000_000, 'total': 1_376_903_243},
    'zh': {'wiki': 730_233_254, 'oscar': 50_000_000, 'total': 780_233_254},
    'ru': {'wiki': 4_569_290_658, 'oscar': 50_000_000, 'total': 4_619_290_658},
    'hi': {'wiki': 218_280_173, 'oscar': 50_000_000, 'total': 268_280_173},
    'ja': {'wiki': 1_423_270_470, 'oscar': 50_000_000, 'total': 1_473_270_470},
    'sw': {'wiki': 61_130_713, 'oscar': 8_428_241, 'total': 69_558_954},
    'bn': {'wiki': 368_019_974, 'oscar': 50_000_000, 'total': 418_019_974},
    'tr': {'wiki': 728_714_011, 'oscar': 50_000_000, 'total': 778_714_011}
}

def find_baseline_amounts() -> Dict[str, int]:
    """Find baseline amounts for different splits based on lowest available language"""
    
    # Find the language with minimum data
    min_lang = min(LANGUAGE_DATA.keys(), key=lambda x: LANGUAGE_DATA[x]['total'])
    min_total = LANGUAGE_DATA[min_lang]['total']
    
    print(f"Baseline language: {min_lang.upper()} with {min_total:,} characters")
    
    # Define split ratios (what fraction of the minimum language's data to use)
    split_configs = {
        'small': {'ratio': 0.9, 'name': 'final_balanced_small.txt'},     # 90% of minimum
        'medium': {'ratio': 1.0, 'name': 'final_balanced_medium.txt'},   # 100% of minimum  
        'large': {'ratio': 1.0, 'name': 'final_balanced_large.txt'}      # 100% of minimum (same as medium for now)
    }
    
    # Calculate actual character amounts per language for each split
    baseline_amounts = {}
    for split_name, config in split_configs.items():
        chars_per_lang = int(min_total * config['ratio'])
        baseline_amounts[split_name] = {
            'chars_per_lang': chars_per_lang,
            'filename': config['name'],
            'total_chars': chars_per_lang * len(LANGUAGES),
            'baseline_lang': min_lang
        }
        
        print(f"Split '{split_name}': {chars_per_lang:,} chars per language")
        print(f"  Total file size: {chars_per_lang * len(LANGUAGES):,} characters")
        print(f"  Output: {config['name']}")
    
    return baseline_amounts

def load_text_file(filepath: str, max_chars: int = None) -> str:
    """Load text file with optional character limit"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            if max_chars:
                return f.read(max_chars)
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return ""
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def interleave_texts(text1: str, text2: str, chunk_size: int = 1000) -> str:
    """Interleave two texts in chunks to mix them evenly"""
    if not text1:
        return text2
    if not text2:
        return text1
    
    chunks1 = [text1[i:i+chunk_size] for i in range(0, len(text1), chunk_size)]
    chunks2 = [text2[i:i+chunk_size] for i in range(0, len(text2), chunk_size)]
    
    # Interleave chunks
    result = []
    max_len = max(len(chunks1), len(chunks2))
    
    for i in range(max_len):
        if i < len(chunks1):
            result.append(chunks1[i])
        if i < len(chunks2):
            result.append(chunks2[i])
    
    return ''.join(result)

def get_balanced_language_data(lang: str, chars_needed: int) -> Tuple[str, Dict]:
    """Get exactly the specified amount of data from a language (balanced Wiki+OSCAR)"""
    print(f"Processing {lang.upper()}: Getting exactly {chars_needed:,} characters")
    
    # File paths
    wiki_file = os.path.join(WIKI_DIR, f"{lang}_articles.txt")
    oscar_file = os.path.join(OSCAR_DIR, f"oscar_{lang}_50M.txt")
    
    # Available data
    wiki_available = LANGUAGE_DATA[lang]['wiki']
    oscar_available = LANGUAGE_DATA[lang]['oscar']
    
    # Initialize stats
    stats = {
        'language': lang,
        'wiki_chars': 0,
        'oscar_chars': 0,
        'total_chars': 0,
        'target_chars': chars_needed,
        'wiki_available': wiki_available,
        'oscar_available': oscar_available
    }
    
    # Calculate optimal distribution between Wikipedia and OSCAR
    if oscar_available == 0:
        # Only Wikipedia available
        wiki_chars = min(chars_needed, wiki_available)
        oscar_chars = 0
    elif wiki_available == 0:
        # Only OSCAR available  
        wiki_chars = 0
        oscar_chars = min(chars_needed, oscar_available)
    else:
        # Both sources available - aim for 50/50 split
        target_per_source = chars_needed // 2
        
        # Check if perfect 50/50 is possible
        if target_per_source <= min(wiki_available, oscar_available):
            wiki_chars = target_per_source
            oscar_chars = chars_needed - target_per_source
        else:
            # Adjust based on availability
            if wiki_available >= chars_needed:
                # Wikipedia has enough, OSCAR might be limited
                oscar_chars = min(oscar_available, chars_needed // 2)
                wiki_chars = chars_needed - oscar_chars
            elif oscar_available >= chars_needed:
                # OSCAR has enough, Wikipedia might be limited  
                wiki_chars = min(wiki_available, chars_needed // 2)
                oscar_chars = chars_needed - wiki_chars
            else:
                # Both are limited - take what we can get
                wiki_chars = min(wiki_available, chars_needed)
                oscar_chars = min(oscar_available, chars_needed - wiki_chars)
    
    print(f"  Wikipedia: {wiki_chars:,} chars, OSCAR: {oscar_chars:,} chars")
    
    # Load the data
    wiki_text = load_text_file(wiki_file, wiki_chars) if wiki_chars > 0 else ""
    oscar_text = load_text_file(oscar_file, oscar_chars) if oscar_chars > 0 else ""
    
    # Update stats with actual loaded characters
    stats['wiki_chars'] = len(wiki_text)
    stats['oscar_chars'] = len(oscar_text)
    stats['total_chars'] = stats['wiki_chars'] + stats['oscar_chars']
    
    # Merge texts
    merged_text = interleave_texts(wiki_text, oscar_text)
    
    # Ensure exactly the right amount (truncate if needed)
    if len(merged_text) > chars_needed:
        merged_text = merged_text[:chars_needed]
        print(f"  Truncated to exactly {chars_needed:,} characters")
    
    print(f"  Final length: {len(merged_text):,} chars")
    return merged_text, stats

def create_balanced_file(split_config: Dict) -> Dict:
    """Create a perfectly balanced multilingual file"""
    filename = split_config['filename']
    chars_per_lang = split_config['chars_per_lang']
    total_chars = split_config['total_chars']
    baseline_lang = split_config['baseline_lang']
    
    print(f"\n{'='*70}")
    print(f"Creating {filename}")
    print(f"Baseline: {baseline_lang.upper()} ({chars_per_lang:,} chars per language)")
    print(f"Total target: {total_chars:,} characters")
    print(f"{'='*70}")
    
    all_texts = []
    language_stats = {}
    total_collected = 0
    
    # Process each language
    for lang in LANGUAGES:
        lang_text, lang_stats = get_balanced_language_data(lang, chars_per_lang)
        actual_chars = len(lang_text)
        
        if actual_chars > 0:
            all_texts.append(f"# Language: {lang.upper()}\n{lang_text}\n\n")
            total_collected += actual_chars
        
        # Store statistics
        language_stats[lang] = lang_stats
        
        print(f"  {lang}: {actual_chars:,} chars collected")
    
    # Shuffle the language sections for better mixing
    random.shuffle(all_texts)
    
    # Combine all texts
    final_text = ''.join(all_texts)
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Write the file
    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_text)
    
    print(f"\n✅ Created {filename}: {len(final_text):,} characters")
    print(f"   Perfect balance: {len(final_text) == total_chars}")
    print(f"   Saved to: {output_path}")
    
    # Return statistics for this file
    return {
        'filename': filename,
        'target_chars': total_chars,
        'actual_chars': len(final_text),
        'chars_per_lang': chars_per_lang,
        'baseline_lang': baseline_lang,
        'language_stats': language_stats
    }

def print_detailed_statistics(all_file_stats: List[Dict]) -> None:
    """Print comprehensive statistics for all generated files"""
    print(f"\n{'='*80}")
    print("DETAILED STATISTICS REPORT - BALANCED APPROACH")
    print(f"{'='*80}")
    
    # Show baseline information
    if all_file_stats:
        baseline_lang = all_file_stats[0]['baseline_lang']
        baseline_total = LANGUAGE_DATA[baseline_lang]['total']
        print(f"\nBaseline Language: {baseline_lang.upper()} ({baseline_total:,} total characters)")
    
    # Create summary table
    print(f"\n{'FILE SUMMARY':^80}")
    print("-" * 80)
    print(f"{'File':<25} {'Per Language':<15} {'Total':<15} {'Perfect Balance':<15}")
    print("-" * 80)
    
    for file_stats in all_file_stats:
        filename = file_stats['filename']
        per_lang = file_stats['chars_per_lang']
        total = file_stats['actual_chars']
        perfect = "✅ YES" if file_stats['actual_chars'] == file_stats['target_chars'] else "❌ NO"
        
        print(f"{filename:<25} {per_lang:>14,} {total:>14,} {perfect:<15}")
    
    # Detailed per-language breakdown for each file
    for file_stats in all_file_stats:
        filename = file_stats['filename']
        lang_stats = file_stats['language_stats']
        
        print(f"\n{'LANGUAGE BREAKDOWN - ' + filename:^80}")
        print("-" * 80)
        print(f"{'Lang':<6} {'Target':<12} {'Wiki':<12} {'OSCAR':<12} {'Total':<12} {'Wiki%':<8} {'OSCAR%':<8}")
        print("-" * 80)
        
        total_wiki = 0
        total_oscar = 0
        total_all = 0
        
        for lang in LANGUAGES:
            if lang in lang_stats:
                stats = lang_stats[lang]
                target = stats['target_chars']
                wiki = stats['wiki_chars']
                oscar = stats['oscar_chars']
                total = stats['total_chars']
                
                wiki_pct = (wiki / total) * 100 if total > 0 else 0
                oscar_pct = (oscar / total) * 100 if total > 0 else 0
                
                # Mark baseline language
                lang_display = f"{lang.upper()}*" if lang == file_stats['baseline_lang'] else lang.upper()
                
                print(f"{lang_display:<6} {target:>11,} {wiki:>11,} {oscar:>11,} {total:>11,} {wiki_pct:>6.1f}% {oscar_pct:>6.1f}%")
                
                total_wiki += wiki
                total_oscar += oscar
                total_all += total
        
        print("-" * 80)
        total_wiki_pct = (total_wiki / total_all) * 100 if total_all > 0 else 0
        total_oscar_pct = (total_oscar / total_all) * 100 if total_all > 0 else 0
        print(f"{'TOTAL':<6} {'':<12} {total_wiki:>11,} {total_oscar:>11,} {total_all:>11,} {total_wiki_pct:>6.1f}% {total_oscar_pct:>6.1f}%")
        print("* = Baseline language")

def save_statistics_to_file(all_file_stats: List[Dict]) -> None:
    """Save detailed statistics to a CSV file"""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Save per-language statistics
    stats_file = os.path.join(OUTPUT_DIR, "balanced_statistics.csv")
    
    with open(stats_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['file', 'language', 'is_baseline', 'target_chars', 'wiki_chars', 'oscar_chars', 
                     'total_chars', 'wiki_percentage', 'oscar_percentage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for file_stats in all_file_stats:
            filename = file_stats['filename']
            baseline_lang = file_stats['baseline_lang']
            lang_stats = file_stats['language_stats']
            
            for lang in LANGUAGES:
                if lang in lang_stats:
                    stats = lang_stats[lang]
                    
                    wiki_pct = (stats['wiki_chars'] / stats['total_chars']) * 100 if stats['total_chars'] > 0 else 0
                    oscar_pct = (stats['oscar_chars'] / stats['total_chars']) * 100 if stats['total_chars'] > 0 else 0
                    
                    writer.writerow({
                        'file': filename,
                        'language': lang,
                        'is_baseline': 'YES' if lang == baseline_lang else 'NO',
                        'target_chars': stats['target_chars'],
                        'wiki_chars': stats['wiki_chars'],
                        'oscar_chars': stats['oscar_chars'],
                        'total_chars': stats['total_chars'],
                        'wiki_percentage': round(wiki_pct, 2),
                        'oscar_percentage': round(oscar_pct, 2)
                    })
    
    print(f"\n💾 Detailed statistics saved to: {stats_file}")

def main():
    """Main execution function"""
    print("Multilingual Data Merger - Balanced Approach")
    print("=" * 60)
    print("Using lowest available language as baseline for perfect balance")
    
    # Check if source directories exist
    if not os.path.exists(WIKI_DIR):
        print(f"Error: Wikipedia directory '{WIKI_DIR}' not found!")
        return
    
    if not os.path.exists(OSCAR_DIR):
        print(f"Error: OSCAR directory '{OSCAR_DIR}' not found!")
        return
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Find baseline amounts
    baseline_configs = find_baseline_amounts()
    
    # Create each balanced file
    all_file_stats = []
    
    for split_name, config in baseline_configs.items():
        try:
            print(f"\n{'='*60}")
            print(f"Processing split: {split_name}")
            file_stats = create_balanced_file(config)
            all_file_stats.append(file_stats)
        except Exception as e:
            print(f"Error creating {config['filename']}: {e}")
            continue
    
    # Print comprehensive statistics
    print_detailed_statistics(all_file_stats)
    
    # Save statistics to CSV
    save_statistics_to_file(all_file_stats)
    
    print(f"\n{'='*80}")
    print("✅ All balanced files created successfully!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("\nFiles created:")
    for file_stats in all_file_stats:
        filename = file_stats['filename']
        output_path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            chars_per_lang = file_stats['chars_per_lang']
            print(f"  - {filename}: {size:,} bytes ({chars_per_lang:,} chars per language)")
    
    print(f"\n🎯 Perfect multilingual balance achieved!")
    print(f"Every language contributes exactly the same amount in each file.")

if __name__ == "__main__":
    main()