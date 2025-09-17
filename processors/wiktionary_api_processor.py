#!/usr/bin/env python3
"""
Wiktionary APIを使用してIPAデータを取得するスクリプト
既存のCMU辞書データと組み合わせて使用
"""

import json
import csv
import sys
import os
import time
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re

class WiktionaryProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.delay = 1.0  # API制限を避けるための遅延
    
    def get_wiktionary_page(self, word: str) -> Optional[Dict]:
        """
        Wiktionaryから指定された単語のページ情報を取得する
        """
        try:
            # Wiktionary APIを使用してページ内容を取得
            url = f"https://en.wiktionary.org/api/rest_v1/page/source/{word}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    'word': word,
                    'content': response.text,
                    'status': 'success'
                }
            else:
                return {
                    'word': word,
                    'content': '',
                    'status': f'error_{response.status_code}'
                }
                
        except Exception as e:
            return {
                'word': word,
                'content': '',
                'status': f'error_{str(e)}'
            }
    
    def extract_ipa_from_content(self, content: str) -> List[str]:
        """
        WikitextからIPA情報を抽出する
        """
        ipa_patterns = []
        
        # {{IPA|...}} テンプレートを検索
        ipa_templates = re.findall(r'\{\{IPA\|[^}]*\|([^}]+)\}\}', content)
        for template in ipa_templates:
            # パイプで分割して各部分をチェック
            parts = template.split('|')
            for part in parts:
                part = part.strip()
                # IPA記号を含む可能性のある部分を抽出
                if any(char in part for char in ['ˈ', 'ˌ', 'ə', 'ɪ', 'ɛ', 'æ', 'ɑ', 'ɔ', 'ʊ', 'ʌ', '/']):
                    # 不要な文字を除去
                    clean_ipa = re.sub(r'[\[\]{}]', '', part)
                    if clean_ipa and len(clean_ipa) > 1:
                        ipa_patterns.append(clean_ipa)
        
        # {{enPR|...}} テンプレートもチェック
        enpr_templates = re.findall(r'\{\{enPR\|[^}]*\|([^}]+)\}\}', content)
        for template in enpr_templates:
            parts = template.split('|')
            for part in parts:
                part = part.strip()
                if any(char in part for char in ['ˈ', 'ˌ', 'ə', 'ɪ', 'ɛ', 'æ', 'ɑ', 'ɔ', 'ʊ', 'ʌ', '/']):
                    clean_ipa = re.sub(r'[\[\]{}]', '', part)
                    if clean_ipa and len(clean_ipa) > 1:
                        ipa_patterns.append(clean_ipa)
        
        # 重複を除去
        return list(set(ipa_patterns))
    
    def process_word(self, word: str) -> Tuple[str, List[str], str]:
        """
        単語を処理してIPA情報を取得する
        """
        print(f"Processing word: {word}")
        
        # ページ情報を取得
        page_data = self.get_wiktionary_page(word)
        
        if page_data['status'] != 'success':
            return word, [], page_data['status']
        
        # IPA情報を抽出
        ipa_patterns = self.extract_ipa_from_content(page_data['content'])
        
        # API制限を避けるため少し待機
        time.sleep(self.delay)
        
        return word, ipa_patterns, page_data['status']
    
    def load_words_from_csv(self, csv_file: str, limit: int = 50) -> List[str]:
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
    
    def save_results(self, results: List[Tuple[str, List[str], str]], output_file: str):
        """
        結果をCSVファイルに保存する
        """
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['word', 'ipa_patterns', 'ipa_count', 'status'])
                
                for word, ipa_patterns, status in results:
                    writer.writerow([word, '|'.join(ipa_patterns), len(ipa_patterns), status])
            
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def process_words(self, words: List[str]) -> List[Tuple[str, List[str], str]]:
        """
        複数の単語を処理する
        """
        results = []
        
        for i, word in enumerate(words, 1):
            print(f"\nProgress: {i}/{len(words)}")
            result = self.process_word(word)
            results.append(result)
        
        return results

def main():
    """
    メイン処理
    """
    print("Wiktionary API Processor")
    print("=" * 50)
    
    # 設定
    input_csv = "../data/words.csv"
    output_csv = "../output/wiktionary_api_results.csv"
    limit = 30  # テスト用に30単語に制限
    
    # プロセッサーを初期化
    processor = WiktionaryProcessor()
    
    # 単語を読み込み
    print(f"Loading words from {input_csv}...")
    words = processor.load_words_from_csv(input_csv, limit)
    print(f"Loaded {len(words)} words")
    
    if not words:
        print("No words found in CSV file")
        return
    
    # 単語を処理
    print(f"\nProcessing {len(words)} words...")
    results = processor.process_words(words)
    
    # 結果を保存
    print(f"\nSaving results to {output_csv}...")
    processor.save_results(results, output_csv)
    
    # 統計を表示
    total_words = len(results)
    words_with_ipa = sum(1 for _, ipa, _ in results if ipa)
    successful_requests = sum(1 for _, _, status in results if status == 'success')
    
    print(f"\nStatistics:")
    print(f"Total words processed: {total_words}")
    print(f"Successful API requests: {successful_requests}")
    print(f"Words with IPA found: {words_with_ipa}")
    print(f"API success rate: {successful_requests/total_words*100:.1f}%")
    print(f"IPA extraction rate: {words_with_ipa/successful_requests*100:.1f}%" if successful_requests > 0 else "IPA extraction rate: 0.0%")

if __name__ == "__main__":
    main()
