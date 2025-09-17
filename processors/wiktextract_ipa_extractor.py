#!/usr/bin/env python3
"""
WiktionaryからIPAデータを抽出するスクリプト
wiktextractライブラリを使用して、指定された単語のIPA情報を取得します。
"""

import json
import csv
import sys
import os
from pathlib import Path
import requests
import time
from typing import List, Dict, Tuple, Optional

def get_wiktionary_page(word: str) -> Optional[Dict]:
    """
    Wiktionaryから指定された単語のページ情報を取得する
    """
    try:
        # Wiktionary APIを使用してページ情報を取得
        url = "https://en.wiktionary.org/api/rest_v1/page/summary/{}".format(word)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Warning: Could not fetch page for '{word}' (status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"Error fetching page for '{word}': {e}")
        return None

def extract_ipa_from_wikitext(wikitext: str) -> List[str]:
    """
    WikitextからIPA情報を抽出する
    """
    ipa_patterns = []
    
    # 基本的なIPAパターンを検索
    import re
    
    # {{IPA|...}} テンプレートを検索
    ipa_templates = re.findall(r'\{\{IPA\|([^}]+)\}\}', wikitext)
    for template in ipa_templates:
        # パイプで分割して各部分をチェック
        parts = template.split('|')
        for part in parts:
            part = part.strip()
            # IPA記号を含む可能性のある部分を抽出
            if any(char in part for char in ['ˈ', 'ˌ', 'ə', 'ɪ', 'ɛ', 'æ', 'ɑ', 'ɔ', 'ʊ', 'ʌ']):
                ipa_patterns.append(part)
    
    # {{enPR|...}} テンプレートもチェック
    enpr_templates = re.findall(r'\{\{enPR\|([^}]+)\}\}', wikitext)
    for template in enpr_templates:
        parts = template.split('|')
        for part in parts:
            part = part.strip()
            if any(char in part for char in ['ˈ', 'ˌ', 'ə', 'ɪ', 'ɛ', 'æ', 'ɑ', 'ɔ', 'ʊ', 'ʌ']):
                ipa_patterns.append(part)
    
    return ipa_patterns

def get_wiktionary_content(word: str) -> Optional[str]:
    """
    Wiktionaryから指定された単語の完全なページ内容を取得する
    """
    try:
        # Wiktionary APIを使用してページ内容を取得
        url = "https://en.wiktionary.org/api/rest_v1/page/html/{}".format(word)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.text
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching content for '{word}': {e}")
        return None

def process_word(word: str) -> Tuple[str, List[str]]:
    """
    単語を処理してIPA情報を取得する
    """
    print(f"Processing word: {word}")
    
    # まずページの要約を取得
    page_info = get_wiktionary_page(word)
    if not page_info:
        return word, []
    
    # ページの完全な内容を取得
    content = get_wiktionary_content(word)
    if not content:
        return word, []
    
    # IPA情報を抽出
    ipa_patterns = extract_ipa_from_wikitext(content)
    
    return word, ipa_patterns

def load_words_from_csv(csv_file: str, limit: int = 100) -> List[str]:
    """
    CSVファイルから単語を読み込む
    """
    words = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                word = row.get('word', '').strip()
                if word:
                    words.append(word)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return words

def save_results(results: List[Tuple[str, List[str]]], output_file: str):
    """
    結果をCSVファイルに保存する
    """
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['word', 'ipa_patterns', 'ipa_count'])
            
            for word, ipa_patterns in results:
                writer.writerow([word, '|'.join(ipa_patterns), len(ipa_patterns)])
        
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """
    メイン処理
    """
    # 設定
    input_csv = "../data/words.csv"
    output_csv = "../output/wiktionary_ipa_results.csv"
    limit = 50  # テスト用に50単語に制限
    
    print("Wiktionary IPA Extractor")
    print("=" * 50)
    
    # 単語を読み込み
    print(f"Loading words from {input_csv}...")
    words = load_words_from_csv(input_csv, limit)
    print(f"Loaded {len(words)} words")
    
    if not words:
        print("No words found in CSV file")
        return
    
    # 各単語を処理
    results = []
    for i, word in enumerate(words, 1):
        print(f"\nProgress: {i}/{len(words)}")
        word_result = process_word(word)
        results.append(word_result)
        
        # API制限を避けるため少し待機
        time.sleep(0.5)
    
    # 結果を保存
    print(f"\nSaving results to {output_csv}...")
    save_results(results, output_csv)
    
    # 統計を表示
    total_words = len(results)
    words_with_ipa = sum(1 for _, ipa in results if ipa)
    
    print(f"\nStatistics:")
    print(f"Total words processed: {total_words}")
    print(f"Words with IPA found: {words_with_ipa}")
    print(f"Success rate: {words_with_ipa/total_words*100:.1f}%")

if __name__ == "__main__":
    main()
