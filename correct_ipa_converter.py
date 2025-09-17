#!/usr/bin/env python3
"""
CMU辞書のIPAデータを正式なIPA形式に修正するスクリプト
IPAへのマッピングルール文書に基づいて正確な変換を実行
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class CorrectIPAConverter:
    def __init__(self):
        # Arpabet → IPA 基本変換表（文書に基づく）
        self.vowel_mapping = {
            'AA': 'ɑ',
            'AE': 'æ', 
            'AH': 'ʌ',  # 強勢ありの場合は/ʌ/、無強勢の場合は/ə/
            'AO': 'ɔ',
            'AW': 'aʊ',
            'AY': 'aɪ',
            'EH': 'ɛ',
            'ER': 'ɜːr',  # 文書に従って/ɝ/から/ɜːr/に変更
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
            'R': 'r',  # 文書に従って/ɹ/から/r/に変更
            'W': 'w',
            'Y': 'j'
        }
        
        # ストレス記号のマッピング
        self.stress_mapping = {
            '1': 'ˈ',  # 強勢
            '2': 'ˌ',  # 弱勢
            '0': ''    # 無強勢
        }
    
    def parse_cmu_pronunciation(self, cmu_pronunciation: str) -> List[Tuple[str, int]]:
        """
        CMU発音記号を解析して音素とストレスレベルを抽出
        例: "AH0 L ER1 T" → [("AH", 0), ("L", 0), ("ER", 1), ("T", 0)]
        """
        tokens = cmu_pronunciation.split()
        parsed = []
        
        for token in tokens:
            # ストレス番号を分離
            match = re.match(r'([A-Z]+)([0-2])?', token)
            if match:
                symbol = match.group(1)
                stress = int(match.group(2)) if match.group(2) else 0
                parsed.append((symbol, stress))
        
        return parsed
    
    def convert_to_ipa(self, parsed_pronunciation: List[Tuple[str, int]]) -> str:
        """
        解析されたCMU発音記号をIPAに変換
        """
        ipa_parts = []
        
        for symbol, stress in parsed_pronunciation:
            # 母音の場合はストレス記号を考慮
            if symbol in self.vowel_mapping:
                ipa_symbol = self.vowel_mapping[symbol]
                
                # AHの場合は強勢レベルに応じて/ʌ/または/ə/を選択
                if symbol == 'AH':
                    ipa_symbol = 'ʌ' if stress > 0 else 'ə'
                
                # ストレス記号を追加
                stress_mark = self.stress_mapping.get(str(stress), '')
                if stress_mark:
                    ipa_symbol = stress_mark + ipa_symbol
                
                ipa_parts.append(ipa_symbol)
            
            # 子音の場合はそのまま変換
            elif symbol in self.consonant_mapping:
                ipa_symbol = self.consonant_mapping[symbol]
                ipa_parts.append(ipa_symbol)
        
        return ''.join(ipa_parts)
    
    def apply_american_english_corrections(self, ipa: str) -> str:
        """
        アメリカ英語特有の補正ルールを適用
        """
        # /ɝ/ を /ɜːr/ に変換
        ipa = re.sub(r'ɝ', 'ɜːr', ipa)
        
        # /ɹ/ を /r/ に変換
        ipa = re.sub(r'ɹ', 'r', ipa)
        
        # 連続音の変換
        # T + Y → tʃ
        ipa = re.sub(r'tj', 'tʃ', ipa)
        
        # D + Y → dʒ  
        ipa = re.sub(r'dj', 'dʒ', ipa)
        
        # 重複するストレス記号を修正
        ipa = re.sub(r'[ˈˌ]+', lambda m: m.group(0)[0], ipa)
        
        return ipa
    
    def correct_ipa_pronunciation(self, ipa: str) -> str:
        """
        既存のIPA発音記号を正式な形式に修正
        """
        # 基本的な修正ルールを適用
        corrected = ipa
        
        # /ɝ/ を /ɜːr/ に変換
        corrected = re.sub(r'ɝ', 'ɜːr', corrected)
        
        # /ɹ/ を /r/ に変換
        corrected = re.sub(r'ɹ', 'r', corrected)
        
        # 連続するストレス記号を修正
        corrected = re.sub(r'[ˈˌ]+', lambda m: m.group(0)[0], corrected)
        
        # 不適切なストレス記号の配置を修正
        # 単語の最初にストレス記号がない場合は追加
        if corrected and not corrected.startswith(('ˈ', 'ˌ')):
            # 最初の母音の前にストレス記号を追加
            first_vowel = re.search(r'[aeiouæɑɔʊʌɪɛəɜ]', corrected)
            if first_vowel:
                pos = first_vowel.start()
                corrected = corrected[:pos] + 'ˈ' + corrected[pos:]
        
        return corrected
    
    def process_cmu_dict_file(self, input_file: str, output_file: str):
        """
        CMU辞書ファイルを処理して正式なIPA形式に変換
        """
        print(f"Processing CMU dictionary: {input_file}")
        
        corrected_entries = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 10000 == 0:
                        print(f"Processed {line_num} lines...")
                    
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        word = parts[0]
                        ipa = parts[1]
                        
                        # IPAを修正
                        corrected_ipa = self.correct_ipa_pronunciation(ipa)
                        
                        corrected_entries.append({
                            'word': word,
                            'original_ipa': ipa,
                            'corrected_ipa': corrected_ipa,
                            'changes': 'yes' if ipa != corrected_ipa else 'no'
                        })
            
            # 結果をCSVファイルに保存
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['word', 'original_ipa', 'corrected_ipa', 'changes'])
                writer.writeheader()
                writer.writerows(corrected_entries)
            
            print(f"Corrected IPA data saved to: {output_file}")
            print(f"Total entries processed: {len(corrected_entries)}")
            
            # 統計を表示
            changed_count = sum(1 for entry in corrected_entries if entry['changes'] == 'yes')
            print(f"Entries modified: {changed_count} ({changed_count/len(corrected_entries)*100:.1f}%)")
            
        except Exception as e:
            print(f"Error processing CMU dictionary: {e}")
    
    def process_words_csv(self, input_file: str, output_file: str):
        """
        words.csvファイルを処理して正式なIPA形式に変換
        """
        print(f"Processing words CSV: {input_file}")
        
        # CMU辞書を読み込み
        cmu_dict = {}
        try:
            with open('/Users/art0/development/usalingo_words_ipa/data/cmudict-0.7b-ipa.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            word = parts[0].lower()
                            ipa = parts[1]
                            cmu_dict[word] = ipa
        except Exception as e:
            print(f"Error loading CMU dictionary: {e}")
            return
        
        corrected_entries = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    word = row.get('word', '').strip().lower()
                    original_ipa = row.get('ipa', '').strip()
                    source = row.get('source', '').strip()
                    
                    # CMU辞書からIPAを取得
                    if word in cmu_dict:
                        cmu_ipa = cmu_dict[word]
                        corrected_ipa = self.correct_ipa_pronunciation(cmu_ipa)
                    else:
                        corrected_ipa = self.correct_ipa_pronunciation(original_ipa)
                    
                    corrected_entries.append({
                        'word': word,
                        'ipa': corrected_ipa,
                        'source': source,
                        'original_ipa': original_ipa
                    })
            
            # 結果をCSVファイルに保存
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['word', 'ipa', 'source', 'original_ipa'])
                writer.writeheader()
                writer.writerows(corrected_entries)
            
            print(f"Corrected words CSV saved to: {output_file}")
            print(f"Total entries processed: {len(corrected_entries)}")
            
        except Exception as e:
            print(f"Error processing words CSV: {e}")

def main():
    """
    メイン処理
    """
    print("Correct IPA Converter")
    print("=" * 50)
    
    converter = CorrectIPAConverter()
    
    # CMU辞書ファイルを処理
    cmu_input = "/Users/art0/development/usalingo_words_ipa/data/cmudict-0.7b-ipa.txt"
    cmu_output = "/Users/art0/development/usalingo_words_ipa/output/corrected_cmu_dict.csv"
    
    if Path(cmu_input).exists():
        converter.process_cmu_dict_file(cmu_input, cmu_output)
    else:
        print(f"CMU dictionary file not found: {cmu_input}")
    
    # words.csvファイルを処理
    words_input = "/Users/art0/development/usalingo_words_ipa/data/words.csv"
    words_output = "/Users/art0/development/usalingo_words_ipa/output/corrected_words_with_ipa.csv"
    
    if Path(words_input).exists():
        converter.process_words_csv(words_input, words_output)
    else:
        print(f"Words CSV file not found: {words_input}")

if __name__ == "__main__":
    main()
