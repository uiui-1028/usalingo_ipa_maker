#!/usr/bin/env python3
"""
CMU辞書から変換されたIPAデータを正式なIPA形式に訂正するスクリプト
IPAへのマッピングルールに基づいて変換を実行
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class IPACorrector:
    def __init__(self):
        # Arpabet → IPA 基本変換表
        self.vowel_mapping = {
            'AA': 'ɑ',
            'AE': 'æ', 
            'AH': 'ʌ',  # 強勢ありの場合は/ʌ/、無強勢の場合は/ə/
            'AO': 'ɔ',
            'AW': 'aʊ',
            'AY': 'aɪ',
            'EH': 'ɛ',
            'ER': 'ɜːr',  # アメリカ英語特有の補正
            'EY': 'eɪ',
            'IH': 'ɪ',
            'IY': 'iː',
            'OW': 'oʊ',
            'OY': 'ɔɪ',
            'UH': 'ʊ',
            'UW': 'uː'
        }
        
        self.consonant_mapping = {
            'P': 'p',
            'B': 'b',
            'T': 't',
            'D': 'd',
            'K': 'k',
            'G': 'ɡ',
            'CH': 'tʃ',
            'JH': 'dʒ',
            'F': 'f',
            'V': 'v',
            'TH': 'θ',
            'DH': 'ð',
            'S': 's',
            'Z': 'z',
            'SH': 'ʃ',
            'ZH': 'ʒ',
            'HH': 'h',
            'M': 'm',
            'N': 'n',
            'NG': 'ŋ',
            'L': 'l',
            'R': 'r',  # アメリカ英語のRをrに統一
            'W': 'w',
            'Y': 'j'
        }
        
        # 数字付きの音素（強勢レベル）のマッピング
        self.stress_mapping = {
            '0': '',      # 無強勢
            '1': 'ˈ',     # 主強勢
            '2': 'ˌ'      # 副強勢
        }
    
    def convert_arpabet_to_ipa(self, arpabet_text: str) -> str:
        """
        Arpabet記法をIPAに変換する
        """
        if not arpabet_text:
            return ""
        
        # 強勢記号を一時的に保存
        stress_marks = []
        text = arpabet_text
        
        # 強勢記号を抽出
        stress_pattern = r'[ˈˌ]'
        stress_marks = re.findall(stress_pattern, text)
        text = re.sub(stress_pattern, '', text)
        
        # 音素を分割（大文字の連続を音素として認識）
        phonemes = []
        current_phoneme = ""
        
        for char in text:
            if char.isupper():
                current_phoneme += char
            elif char.isdigit():
                # 数字は強勢レベル
                if current_phoneme:
                    phonemes.append((current_phoneme, char))
                    current_phoneme = ""
            elif char in [' ', ',', '/']:
                if current_phoneme:
                    phonemes.append((current_phoneme, '0'))  # デフォルトは無強勢
                    current_phoneme = ""
            else:
                if current_phoneme:
                    phonemes.append((current_phoneme, '0'))
                    current_phoneme = ""
        
        if current_phoneme:
            phonemes.append((current_phoneme, '0'))
        
        # 音素をIPAに変換
        ipa_phonemes = []
        for phoneme, stress in phonemes:
            if phoneme in self.vowel_mapping:
                ipa_phoneme = self.vowel_mapping[phoneme]
                # 強勢の判定
                if stress == '1':  # 主強勢
                    ipa_phoneme = 'ˈ' + ipa_phoneme
                elif stress == '2':  # 副強勢
                    ipa_phoneme = 'ˌ' + ipa_phoneme
                ipa_phonemes.append(ipa_phoneme)
            elif phoneme in self.consonant_mapping:
                ipa_phoneme = self.consonant_mapping[phoneme]
                ipa_phonemes.append(ipa_phoneme)
        
        return ''.join(ipa_phonemes)
    
    def apply_american_english_corrections(self, ipa_text: str) -> str:
        """
        アメリカ英語特有の補正ルールを適用する
        """
        if not ipa_text:
            return ""
        
        # 1. /ɝ/ を /ɜːr/ に変換
        ipa_text = re.sub(r'ɝ', 'ɜːr', ipa_text)
        
        # 2. /ɹ/ を /r/ に統一（既にマッピングで処理済み）
        
        # 3. 連続音の結合
        # T + Y → /tʃ/
        ipa_text = re.sub(r'tj', 'tʃ', ipa_text)
        # D + Y → /dʒ/
        ipa_text = re.sub(r'dj', 'dʒ', ipa_text)
        
        # 4. 長音記号の統一
        ipa_text = re.sub(r'ːː+', 'ː', ipa_text)  # 複数の長音記号を単一に
        
        # 5. 不要な重複を除去
        ipa_text = re.sub(r'([ˈˌ])\1+', r'\1', ipa_text)  # 重複する強勢記号を除去
        
        return ipa_text
    
    def correct_ipa_format(self, ipa_text: str) -> str:
        """
        IPA形式を訂正する
        """
        if not ipa_text:
            return ""
        
        # 複数の発音が含まれている場合は分割して処理
        pronunciations = ipa_text.split(', ')
        corrected_pronunciations = []
        
        for pron in pronunciations:
            pron = pron.strip()
            if not pron:
                continue
            
            # Arpabet記法をIPAに変換
            converted = self.convert_arpabet_to_ipa(pron)
            
            # アメリカ英語特有の補正を適用
            corrected = self.apply_american_english_corrections(converted)
            
            if corrected:
                corrected_pronunciations.append(corrected)
        
        return ', '.join(corrected_pronunciations)
    
    def process_csv_file(self, input_file: str, output_file: str):
        """
        CSVファイルを処理してIPAを訂正する
        """
        print(f"Processing {input_file}...")
        
        corrected_data = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    word = row.get('word', '').strip()
                    original_ipa = row.get('ipa', '').strip()
                    source = row.get('source', '').strip()
                    
                    # IPAを訂正
                    corrected_ipa = self.correct_ipa_format(original_ipa)
                    
                    corrected_data.append({
                        'word': word,
                        'original_ipa': original_ipa,
                        'corrected_ipa': corrected_ipa,
                        'source': source
                    })
            
            # 結果を保存
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['word', 'original_ipa', 'corrected_ipa', 'source'])
                writer.writeheader()
                writer.writerows(corrected_data)
            
            print(f"Corrected IPA data saved to {output_file}")
            
        except Exception as e:
            print(f"Error processing file: {e}")
    
    def print_statistics(self, input_file: str, output_file: str):
        """
        統計情報を表示する
        """
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                total_words = 0
                corrected_count = 0
                unchanged_count = 0
                
                for row in reader:
                    total_words += 1
                    original = row.get('original_ipa', '')
                    corrected = row.get('corrected_ipa', '')
                    
                    if original != corrected:
                        corrected_count += 1
                    else:
                        unchanged_count += 1
                
                print(f"\nStatistics:")
                print(f"Total words processed: {total_words}")
                print(f"Words with corrections: {corrected_count}")
                print(f"Words unchanged: {unchanged_count}")
                print(f"Correction rate: {corrected_count/total_words*100:.1f}%")
                
        except Exception as e:
            print(f"Error calculating statistics: {e}")

def main():
    """
    メイン処理
    """
    print("IPA Corrector - CMU to Standard IPA")
    print("=" * 50)
    
    # ファイルパス
    input_file = "output/final_words_with_ipa.csv"
    output_file = "output/corrected_words_with_ipa.csv"
    
    # 入力ファイルの存在確認
    if not Path(input_file).exists():
        print(f"Input file {input_file} not found")
        return
    
    # IPA訂正器を初期化
    corrector = IPACorrector()
    
    # CSVファイルを処理
    corrector.process_csv_file(input_file, output_file)
    
    # 統計を表示
    corrector.print_statistics(input_file, output_file)
    
    print(f"\nProcessing completed!")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    main()
