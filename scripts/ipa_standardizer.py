#!/usr/bin/env python3
"""
既存のIPAデータを正式なIPA形式に標準化するスクリプト
IPAへのマッピングルールに基づいて訂正を実行
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class IPAStandardizer:
    def __init__(self):
        # アメリカ英語特有の補正ルール
        self.correction_rules = [
            # 1. /ɝ/ を /ɜːr/ に変換
            (r'ɝ', 'ɜːr'),
            # 2. /ɹ/ を /r/ に統一
            (r'ɹ', 'r'),
            # 3. 連続音の結合
            (r'tj', 'tʃ'),  # T + Y → /tʃ/
            (r'dj', 'dʒ'),  # D + Y → /dʒ/
            # 4. 長音記号の統一
            (r'ːː+', 'ː'),  # 複数の長音記号を単一に
            # 5. 重複する強勢記号を除去
            (r'([ˈˌ])\1+', r'\1'),
            # 6. 不要な空白を除去
            (r'\s+', ' '),
        ]
    
    def standardize_ipa(self, ipa_text: str) -> str:
        """
        IPA文字列を標準化する
        """
        if not ipa_text:
            return ""
        
        # 複数の発音が含まれている場合は分割して処理
        pronunciations = ipa_text.split(', ')
        standardized_pronunciations = []
        
        for pron in pronunciations:
            pron = pron.strip()
            if not pron:
                continue
            
            # 各補正ルールを適用
            standardized = pron
            for pattern, replacement in self.correction_rules:
                standardized = re.sub(pattern, replacement, standardized)
            
            # 前後の空白を除去
            standardized = standardized.strip()
            
            if standardized:
                standardized_pronunciations.append(standardized)
        
        return ', '.join(standardized_pronunciations)
    
    def process_csv_file(self, input_file: str, output_file: str):
        """
        CSVファイルを処理してIPAを標準化する
        """
        print(f"Processing {input_file}...")
        
        standardized_data = []
        changes_made = 0
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    word = row.get('word', '').strip()
                    original_ipa = row.get('ipa', '').strip()
                    source = row.get('source', '').strip()
                    
                    # IPAを標準化
                    standardized_ipa = self.standardize_ipa(original_ipa)
                    
                    # 変更があったかチェック
                    if original_ipa != standardized_ipa:
                        changes_made += 1
                    
                    standardized_data.append({
                        'word': word,
                        'original_ipa': original_ipa,
                        'standardized_ipa': standardized_ipa,
                        'source': source
                    })
            
            # 結果を保存
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['word', 'original_ipa', 'standardized_ipa', 'source'])
                writer.writeheader()
                writer.writerows(standardized_data)
            
            print(f"Standardized IPA data saved to {output_file}")
            print(f"Changes made: {changes_made}")
            
        except Exception as e:
            print(f"Error processing file: {e}")
    
    def print_examples(self, output_file: str, limit: int = 10):
        """
        変更例を表示する
        """
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                print(f"\nExamples of changes (first {limit}):")
                print("-" * 80)
                
                count = 0
                for row in reader:
                    original = row.get('original_ipa', '')
                    standardized = row.get('standardized_ipa', '')
                    
                    if original != standardized:
                        print(f"Word: {row.get('word', '')}")
                        print(f"  Original:    {original}")
                        print(f"  Standardized: {standardized}")
                        print()
                        count += 1
                        
                        if count >= limit:
                            break
                
        except Exception as e:
            print(f"Error reading examples: {e}")
    
    def print_statistics(self, output_file: str):
        """
        統計情報を表示する
        """
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                total_words = 0
                changed_words = 0
                unchanged_words = 0
                
                for row in reader:
                    total_words += 1
                    original = row.get('original_ipa', '')
                    standardized = row.get('standardized_ipa', '')
                    
                    if original != standardized:
                        changed_words += 1
                    else:
                        unchanged_words += 1
                
                print(f"\nStatistics:")
                print(f"Total words processed: {total_words}")
                print(f"Words with changes: {changed_words}")
                print(f"Words unchanged: {unchanged_words}")
                print(f"Change rate: {changed_words/total_words*100:.1f}%")
                
        except Exception as e:
            print(f"Error calculating statistics: {e}")

def main():
    """
    メイン処理
    """
    print("IPA Standardizer - Standard IPA Format")
    print("=" * 50)
    
    # ファイルパス
    input_file = "output/final_words_with_ipa.csv"
    output_file = "output/standardized_words_with_ipa.csv"
    
    # 入力ファイルの存在確認
    if not Path(input_file).exists():
        print(f"Input file {input_file} not found")
        return
    
    # IPA標準化器を初期化
    standardizer = IPAStandardizer()
    
    # CSVファイルを処理
    standardizer.process_csv_file(input_file, output_file)
    
    # 統計を表示
    standardizer.print_statistics(output_file)
    
    # 変更例を表示
    standardizer.print_examples(output_file, 10)
    
    print(f"\nProcessing completed!")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    main()
