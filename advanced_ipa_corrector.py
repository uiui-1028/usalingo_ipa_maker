#!/usr/bin/env python3
"""
高度なIPA修正スクリプト - ストレス記号の重複問題を解決
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple

class AdvancedIPACorrector:
    def __init__(self):
        pass
    
    def fix_duplicate_stress_marks(self, ipa: str) -> str:
        """
        重複するストレス記号を修正する
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
        
        return cleaned
    
    def fix_stress_placement(self, ipa: str) -> str:
        """
        ストレス記号の配置を修正する
        """
        if not ipa:
            return ""
        
        # 不適切な位置のストレス記号を除去
        # 子音の前のストレス記号を除去
        cleaned = re.sub(r'([pbtdkgfvθðszʃʒmnlrwj])[ˈˌ]', r'\1', ipa)
        
        # 重複するストレス記号を除去
        cleaned = re.sub(r'[ˈˌ]+', lambda m: m.group(0)[0], cleaned)
        
        # 単語の最初にストレス記号がない場合は追加
        if cleaned and not cleaned.startswith(('ˈ', 'ˌ')):
            # 最初の母音の前にストレス記号を追加
            first_vowel = re.search(r'[aeiouæɑɔʊʌɪɛəɜ]', cleaned)
            if first_vowel:
                pos = first_vowel.start()
                cleaned = cleaned[:pos] + 'ˈ' + cleaned[pos:]
        
        return cleaned
    
    def clean_ipa_pronunciation(self, ipa: str) -> str:
        """
        IPA発音記号をクリーンアップする
        """
        if not ipa:
            return ""
        
        # 基本的なクリーンアップ
        cleaned = ipa.strip()
        
        # 重複するストレス記号を修正
        cleaned = self.fix_duplicate_stress_marks(cleaned)
        
        # ストレス記号の配置を修正
        cleaned = self.fix_stress_placement(cleaned)
        
        # 不適切な文字を除去
        cleaned = re.sub(r'[\[\]{}]', '', cleaned)
        
        # 複数のスペースを単一のスペースに
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 前後の空白を除去
        cleaned = cleaned.strip()
        
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
    
    def process_data(self, input_file: str, output_file: str):
        """
        データを処理して最終的なIPA形式に修正する
        """
        print(f"Processing data: {input_file}")
        
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
                    cleaned_ipa = self.clean_ipa_pronunciation(ipa)
                    
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
            print(f"Error processing data: {e}")
            return 0, 0

def main():
    """
    メイン処理
    """
    print("Advanced IPA Corrector")
    print("=" * 50)
    
    corrector = AdvancedIPACorrector()
    
    # 修正されたデータを処理
    input_file = "/Users/art0/development/usalingo_words_ipa/output/corrected_words_with_ipa.csv"
    output_file = "/Users/art0/development/usalingo_words_ipa/output/advanced_corrected_words_with_ipa.csv"
    
    if Path(input_file).exists():
        valid_count, invalid_count = corrector.process_data(input_file, output_file)
        
        if valid_count > 0:
            print(f"\nAdvanced correction completed successfully!")
            print(f"Coverage: {valid_count/(valid_count + invalid_count)*100:.1f}%")
        else:
            print("Advanced correction failed!")
    else:
        print(f"Input file not found: {input_file}")

if __name__ == "__main__":
    main()
