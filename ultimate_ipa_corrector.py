#!/usr/bin/env python3
"""
究極のIPA修正スクリプト - ストレス記号の重複問題を完全に解決
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple

class UltimateIPACorrector:
    def __init__(self):
        pass
    
    def completely_fix_stress_marks(self, ipa: str) -> str:
        """
        ストレス記号を完全に修正する
        """
        if not ipa:
            return ""
        
        # すべてのストレス記号を一時的に除去
        no_stress = re.sub(r'[ˈˌ]', '', ipa)
        
        # 単語の最初にストレス記号を追加
        if no_stress:
            # 最初の母音の前にストレス記号を追加
            first_vowel = re.search(r'[aeiouæɑɔʊʌɪɛəɜ]', no_stress)
            if first_vowel:
                pos = first_vowel.start()
                result = no_stress[:pos] + 'ˈ' + no_stress[pos:]
            else:
                result = 'ˈ' + no_stress
        else:
            result = no_stress
        
        return result
    
    def clean_ipa_pronunciation(self, ipa: str) -> str:
        """
        IPA発音記号をクリーンアップする
        """
        if not ipa:
            return ""
        
        # 基本的なクリーンアップ
        cleaned = ipa.strip()
        
        # ストレス記号を完全に修正
        cleaned = self.completely_fix_stress_marks(cleaned)
        
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
            
            print(f"Ultimate corrected data saved to: {output_file}")
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
    print("Ultimate IPA Corrector")
    print("=" * 50)
    
    corrector = UltimateIPACorrector()
    
    # 修正されたデータを処理
    input_file = "/Users/art0/development/usalingo_words_ipa/output/corrected_words_with_ipa.csv"
    output_file = "/Users/art0/development/usalingo_words_ipa/output/ultimate_corrected_words_with_ipa.csv"
    
    if Path(input_file).exists():
        valid_count, invalid_count = corrector.process_data(input_file, output_file)
        
        if valid_count > 0:
            print(f"\nUltimate correction completed successfully!")
            print(f"Coverage: {valid_count/(valid_count + invalid_count)*100:.1f}%")
        else:
            print("Ultimate correction failed!")
    else:
        print(f"Input file not found: {input_file}")

if __name__ == "__main__":
    main()
