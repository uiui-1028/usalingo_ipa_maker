#!/usr/bin/env python3
"""
修正されたIPAデータの最終的なクリーンアップと検証
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple

class FinalIPACorrector:
    def __init__(self):
        pass
    
    def clean_stress_marks(self, ipa: str) -> str:
        """
        ストレス記号をクリーンアップする
        """
        if not ipa:
            return ""
        
        # 重複するストレス記号を除去
        cleaned = re.sub(r'[ˈˌ]+', lambda m: m.group(0)[0], ipa)
        
        # 単語の最初にストレス記号がない場合は追加
        if cleaned and not cleaned.startswith(('ˈ', 'ˌ')):
            # 最初の母音の前にストレス記号を追加
            first_vowel = re.search(r'[aeiouæɑɔʊʌɪɛəɜ]', cleaned)
            if first_vowel:
                pos = first_vowel.start()
                cleaned = cleaned[:pos] + 'ˈ' + cleaned[pos:]
        
        # 不適切なストレス記号の配置を修正
        # 連続する子音の間にストレス記号がある場合は修正
        cleaned = re.sub(r'([pbtdkgfvθðszʃʒmnlrwj])[ˈˌ]([pbtdkgfvθðszʃʒmnlrwj])', r'\1\2', cleaned)
        
        return cleaned
    
    def validate_ipa_format(self, ipa: str) -> bool:
        """
        IPA形式を検証する
        """
        if not ipa:
            return False
        
        # 基本的なチェック
        if len(ipa.strip()) < 2:
            return False
        
        # 明らかに無効な文字が含まれていないかチェック
        invalid_chars = ['<', '>', '&', '"', "'", '(', ')', '[', ']', '{', '}']
        if any(char in ipa for char in invalid_chars):
            return False
        
        # 基本的なIPA記号が含まれているかチェック
        ipa_indicators = ['ˈ', 'ˌ', 'ə', 'ɪ', 'ɛ', 'æ', 'ɑ', 'ɔ', 'ʊ', 'ʌ', '/', 'ː', 'ɜ', 'r']
        if not any(indicator in ipa for indicator in ipa_indicators):
            # 英数字のみの場合は長さで判断
            if len(ipa) < 3:
                return False
        
        return True
    
    def process_corrected_data(self, input_file: str, output_file: str):
        """
        修正されたデータを最終的にクリーンアップする
        """
        print(f"Processing corrected data: {input_file}")
        
        corrected_entries = []
        invalid_count = 0
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    word = row.get('word', '').strip()
                    ipa = row.get('ipa', '').strip()
                    source = row.get('source', '').strip()
                    original_ipa = row.get('original_ipa', '').strip()
                    
                    # IPAをクリーンアップ
                    cleaned_ipa = self.clean_stress_marks(ipa)
                    
                    # 検証
                    if self.validate_ipa_format(cleaned_ipa):
                        corrected_entries.append({
                            'word': word,
                            'ipa': cleaned_ipa,
                            'source': source,
                            'original_ipa': original_ipa
                        })
                    else:
                        invalid_count += 1
                        print(f"Invalid IPA for '{word}': {cleaned_ipa}")
            
            # 結果をCSVファイルに保存
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['word', 'ipa', 'source', 'original_ipa'])
                writer.writeheader()
                writer.writerows(corrected_entries)
            
            print(f"Final corrected data saved to: {output_file}")
            print(f"Valid entries: {len(corrected_entries)}")
            print(f"Invalid entries: {invalid_count}")
            
            return len(corrected_entries), invalid_count
            
        except Exception as e:
            print(f"Error processing corrected data: {e}")
            return 0, 0
    
    def compare_with_original(self, original_file: str, corrected_file: str):
        """
        元のデータと修正されたデータを比較する
        """
        print(f"Comparing original and corrected data...")
        
        try:
            # 元のデータを読み込み
            original_data = {}
            with open(original_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row.get('word', '').strip().lower()
                    ipa = row.get('ipa', '').strip()
                    original_data[word] = ipa
            
            # 修正されたデータを読み込み
            corrected_data = {}
            with open(corrected_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row.get('word', '').strip().lower()
                    ipa = row.get('ipa', '').strip()
                    corrected_data[word] = ipa
            
            # 比較
            changed_count = 0
            same_count = 0
            
            for word in original_data:
                if word in corrected_data:
                    if original_data[word] != corrected_data[word]:
                        changed_count += 1
                    else:
                        same_count += 1
            
            print(f"Words with changes: {changed_count}")
            print(f"Words unchanged: {same_count}")
            print(f"Change rate: {changed_count/(changed_count + same_count)*100:.1f}%")
            
        except Exception as e:
            print(f"Error comparing data: {e}")

def main():
    """
    メイン処理
    """
    print("Final IPA Corrector")
    print("=" * 50)
    
    corrector = FinalIPACorrector()
    
    # 修正されたデータを処理
    input_file = "/Users/art0/development/usalingo_words_ipa/output/corrected_words_with_ipa.csv"
    output_file = "/Users/art0/development/usalingo_words_ipa/output/final_corrected_words_with_ipa.csv"
    
    if Path(input_file).exists():
        valid_count, invalid_count = corrector.process_corrected_data(input_file, output_file)
        
        if valid_count > 0:
            print(f"\nFinal validation completed successfully!")
            print(f"Coverage: {valid_count/(valid_count + invalid_count)*100:.1f}%")
            
            # 元のデータと比較
            original_file = "/Users/art0/development/usalingo_words_ipa/output/final_words_with_ipa.csv"
            if Path(original_file).exists():
                corrector.compare_with_original(original_file, output_file)
        else:
            print("Final validation failed!")
    else:
        print(f"Input file not found: {input_file}")

if __name__ == "__main__":
    main()
