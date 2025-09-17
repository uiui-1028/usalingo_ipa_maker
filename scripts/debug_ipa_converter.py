#!/usr/bin/env python3
"""
IPA変換のデバッグ用スクリプト
"""

import re

def test_arpabet_conversion():
    """
    Arpabet変換をテストする
    """
    # テストケース
    test_cases = [
        "ˈsæmpəl",
        "əˈbɔrʃən", 
        "ˌækˌsɛlɝˈeɪʃən",
        "ˈeɪkɝ"
    ]
    
    # 音素マッピング
    vowel_mapping = {
        'AA': 'ɑ', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔ', 'AW': 'aʊ', 'AY': 'aɪ',
        'EH': 'ɛ', 'ER': 'ɜːr', 'EY': 'eɪ', 'IH': 'ɪ', 'IY': 'iː',
        'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'uː'
    }
    
    consonant_mapping = {
        'P': 'p', 'B': 'b', 'T': 't', 'D': 'd', 'K': 'k', 'G': 'ɡ',
        'CH': 'tʃ', 'JH': 'dʒ', 'F': 'f', 'V': 'v', 'TH': 'θ', 'DH': 'ð',
        'S': 's', 'Z': 'z', 'SH': 'ʃ', 'ZH': 'ʒ', 'HH': 'h',
        'M': 'm', 'N': 'n', 'NG': 'ŋ', 'L': 'l', 'R': 'r', 'W': 'w', 'Y': 'j'
    }
    
    print("Testing Arpabet conversion...")
    
    for test_case in test_cases:
        print(f"\nInput: {test_case}")
        
        # 強勢記号を抽出
        stress_marks = re.findall(r'[ˈˌ]', test_case)
        text = re.sub(r'[ˈˌ]', '', test_case)
        print(f"After stress removal: {text}")
        
        # 音素を分割（大文字の連続を音素として認識）
        phonemes = []
        current_phoneme = ""
        
        for char in text:
            if char.isupper():
                current_phoneme += char
            elif char.isdigit():
                if current_phoneme:
                    phonemes.append((current_phoneme, char))
                    current_phoneme = ""
            elif char in [' ', ',', '/']:
                if current_phoneme:
                    phonemes.append((current_phoneme, '0'))
                    current_phoneme = ""
            else:
                if current_phoneme:
                    phonemes.append((current_phoneme, '0'))
                    current_phoneme = ""
        
        if current_phoneme:
            phonemes.append((current_phoneme, '0'))
        
        print(f"Phonemes found: {phonemes}")
        
        # 音素をIPAに変換
        ipa_phonemes = []
        for phoneme, stress in phonemes:
            if phoneme in vowel_mapping:
                ipa_phoneme = vowel_mapping[phoneme]
                if stress == '1':
                    ipa_phoneme = 'ˈ' + ipa_phoneme
                elif stress == '2':
                    ipa_phoneme = 'ˌ' + ipa_phoneme
                ipa_phonemes.append(ipa_phoneme)
                print(f"  {phoneme} -> {ipa_phoneme}")
            elif phoneme in consonant_mapping:
                ipa_phoneme = consonant_mapping[phoneme]
                ipa_phonemes.append(ipa_phoneme)
                print(f"  {phoneme} -> {ipa_phoneme}")
            else:
                print(f"  {phoneme} -> NOT FOUND")
        
        result = ''.join(ipa_phonemes)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_arpabet_conversion()
