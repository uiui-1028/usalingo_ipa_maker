#!/usr/bin/env python3
"""
既存のCMU辞書データを活用しつつ、不足している単語のIPAデータを補完するスクリプト
"""

import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
import requests
import time

class EnhancedIPAProcessor:
    def __init__(self):
        self.cmu_dict = {}
        self.words_with_ipa = set()
        self.words_without_ipa = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def load_cmu_dict(self, cmu_file: str):
        """
        CMU辞書を読み込む
        """
        print(f"Loading CMU dictionary from {cmu_file}...")
        
        try:
            with open(cmu_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            word = parts[0].lower()
                            ipa = parts[1]
                            self.cmu_dict[word] = ipa
                            self.words_with_ipa.add(word)
            
            print(f"Loaded {len(self.cmu_dict)} entries from CMU dictionary")
            
        except Exception as e:
            print(f"Error loading CMU dictionary: {e}")
    
    def load_words_from_csv(self, csv_file: str) -> List[str]:
        """
        CSVファイルから単語を読み込む
        """
        words = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row.get('word', '').strip().lower()
                    if word:
                        words.append(word)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        
        return words
    
    def identify_missing_words(self, words: List[str]) -> List[str]:
        """
        IPAデータが不足している単語を特定する
        """
        missing_words = []
        
        for word in words:
            if word not in self.words_with_ipa:
                missing_words.append(word)
                self.words_without_ipa.add(word)
        
        print(f"Found {len(missing_words)} words without IPA data")
        return missing_words
    
    def generate_ipa_from_word(self, word: str) -> Optional[str]:
        """
        単語から基本的なIPAを生成する（ルールベース）
        """
        # 基本的な発音ルールを適用
        ipa = word.lower()
        
        # 一般的な英語の発音ルール
        rules = [
            (r'c([ei])', r's\1'),  # c before e/i -> s
            (r'ph', r'f'),          # ph -> f
            (r'qu', r'kw'),         # qu -> kw
            (r'th', r'θ'),          # th -> θ
            (r'sh', r'ʃ'),          # sh -> ʃ
            (r'ch', r'tʃ'),         # ch -> tʃ
            (r'ng', r'ŋ'),          # ng -> ŋ
            (r'oo', r'u'),          # oo -> u
            (r'ee', r'i'),          # ee -> i
            (r'ay', r'eɪ'),         # ay -> eɪ
            (r'ey', r'eɪ'),         # ey -> eɪ
            (r'ow', r'oʊ'),         # ow -> oʊ
            (r'ou', r'aʊ'),         # ou -> aʊ
        ]
        
        for pattern, replacement in rules:
            ipa = re.sub(pattern, replacement, ipa)
        
        # 母音の基本的な変換
        vowel_rules = [
            (r'a$', r'ə'),          # a at end -> ə
            (r'e$', r'ə'),          # e at end -> ə
            (r'i$', r'i'),          # i at end -> i
            (r'o$', r'oʊ'),         # o at end -> oʊ
            (r'u$', r'u'),          # u at end -> u
        ]
        
        for pattern, replacement in vowel_rules:
            ipa = re.sub(pattern, replacement, ipa)
        
        # アクセント記号を追加（最初の音節に）
        if ipa and not ipa.startswith(('ˈ', 'ˌ')):
            ipa = 'ˈ' + ipa
        
        return ipa if ipa != word else None
    
    def get_ipa_from_online_source(self, word: str) -> Optional[str]:
        """
        オンラインソースからIPAを取得する（フォールバック）
        """
        try:
            # 簡単なオンライン辞書APIを試す
            # 実際の実装では、利用可能なAPIを使用
            time.sleep(0.1)  # レート制限を避ける
            return None  # 現在は実装していない
        except:
            return None
    
    def process_missing_words(self, missing_words: List[str]) -> Dict[str, str]:
        """
        不足している単語のIPAデータを生成する
        """
        print(f"Processing {len(missing_words)} missing words...")
        
        generated_ipa = {}
        
        for i, word in enumerate(missing_words, 1):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(missing_words)}")
            
            # ルールベースでIPAを生成
            ipa = self.generate_ipa_from_word(word)
            
            if ipa:
                generated_ipa[word] = ipa
            else:
                # オンラインソースを試す
                online_ipa = self.get_ipa_from_online_source(word)
                if online_ipa:
                    generated_ipa[word] = online_ipa
        
        print(f"Generated IPA for {len(generated_ipa)} words")
        return generated_ipa
    
    def create_enhanced_dataset(self, words: List[str], output_file: str):
        """
        拡張されたIPAデータセットを作成する
        """
        print("Creating enhanced IPA dataset...")
        
        # 不足している単語を特定
        missing_words = self.identify_missing_words(words)
        
        # 不足している単語のIPAを生成
        generated_ipa = self.process_missing_words(missing_words)
        
        # 結果を統合
        enhanced_data = []
        
        for word in words:
            if word in self.cmu_dict:
                # CMU辞書から既存のIPAを使用
                enhanced_data.append({
                    'word': word,
                    'ipa': self.cmu_dict[word],
                    'source': 'cmu_dict'
                })
            elif word in generated_ipa:
                # 生成されたIPAを使用
                enhanced_data.append({
                    'word': word,
                    'ipa': generated_ipa[word],
                    'source': 'generated'
                })
            else:
                # IPAが見つからない場合
                enhanced_data.append({
                    'word': word,
                    'ipa': '',
                    'source': 'none'
                })
        
        # CSVファイルに保存
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['word', 'ipa', 'source'])
                writer.writeheader()
                writer.writerows(enhanced_data)
            
            print(f"Enhanced dataset saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving enhanced dataset: {e}")
        
        return enhanced_data
    
    def print_statistics(self, enhanced_data: List[Dict]):
        """
        統計情報を表示する
        """
        total_words = len(enhanced_data)
        cmu_words = sum(1 for item in enhanced_data if item['source'] == 'cmu_dict')
        generated_words = sum(1 for item in enhanced_data if item['source'] == 'generated')
        no_ipa_words = sum(1 for item in enhanced_data if item['source'] == 'none')
        
        print(f"\nStatistics:")
        print(f"Total words: {total_words}")
        print(f"Words with CMU IPA: {cmu_words} ({cmu_words/total_words*100:.1f}%)")
        print(f"Words with generated IPA: {generated_words} ({generated_words/total_words*100:.1f}%)")
        print(f"Words without IPA: {no_ipa_words} ({no_ipa_words/total_words*100:.1f}%)")
        print(f"Total coverage: {(cmu_words + generated_words)/total_words*100:.1f}%")

def main():
    """
    メイン処理
    """
    print("Enhanced IPA Processor")
    print("=" * 50)
    
    # 設定
    cmu_file = "../data/cmudict-0.7b-ipa.txt"
    input_csv = "../data/words.csv"
    output_csv = "../output/enhanced_words_with_ipa.csv"
    
    # プロセッサーを初期化
    processor = EnhancedIPAProcessor()
    
    # CMU辞書を読み込み
    if Path(cmu_file).exists():
        processor.load_cmu_dict(cmu_file)
    else:
        print(f"CMU dictionary file {cmu_file} not found")
        return
    
    # 単語を読み込み
    print(f"Loading words from {input_csv}...")
    words = processor.load_words_from_csv(input_csv)
    print(f"Loaded {len(words)} words")
    
    if not words:
        print("No words found in CSV file")
        return
    
    # 拡張されたデータセットを作成
    enhanced_data = processor.create_enhanced_dataset(words, output_csv)
    
    # 統計を表示
    processor.print_statistics(enhanced_data)

if __name__ == "__main__":
    main()
