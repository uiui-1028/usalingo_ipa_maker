#!/usr/bin/env python3
"""
最終的なIPAデータセットの検証とクリーンアップ
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple

def validate_ipa_format(ipa: str) -> bool:
    """
    IPA形式を検証する
    """
    if not ipa:
        return False
    
    # 基本的なチェック：空でなく、適切な長さがある
    if len(ipa.strip()) < 2:
        return False
    
    # 明らかに無効な文字が含まれていないかチェック
    invalid_chars = ['<', '>', '&', '"', "'", '(', ')', '[', ']', '{', '}']
    if any(char in ipa for char in invalid_chars):
        return False
    
    # 基本的なIPA記号が含まれているかチェック
    ipa_indicators = ['ˈ', 'ˌ', 'ə', 'ɪ', 'ɛ', 'æ', 'ɑ', 'ɔ', 'ʊ', 'ʌ', '/', 'ː']
    if not any(indicator in ipa for indicator in ipa_indicators):
        # 英数字のみの場合は長さで判断
        if len(ipa) < 3:
            return False
    
    return True

def clean_ipa(ipa: str) -> str:
    """
    IPA文字列をクリーンアップする
    """
    if not ipa:
        return ""
    
    # 不要な文字を除去
    cleaned = re.sub(r'[\[\]{}]', '', ipa)
    
    # 複数のスペースを単一のスペースに
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # 前後の空白を除去
    cleaned = cleaned.strip()
    
    return cleaned

def validate_dataset(input_file: str, output_file: str):
    """
    データセットを検証してクリーンアップする
    """
    print(f"Validating dataset: {input_file}")
    
    valid_entries = []
    invalid_entries = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                word = row.get('word', '').strip()
                ipa = row.get('ipa', '').strip()
                source = row.get('source', '').strip()
                
                # IPAをクリーンアップ
                cleaned_ipa = clean_ipa(ipa)
                
                # 検証
                if validate_ipa_format(cleaned_ipa):
                    valid_entries.append({
                        'word': word,
                        'ipa': cleaned_ipa,
                        'source': source
                    })
                else:
                    invalid_entries.append({
                        'word': word,
                        'ipa': cleaned_ipa,
                        'source': source,
                        'reason': 'Invalid IPA format'
                    })
        
        # 有効なエントリを保存
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['word', 'ipa', 'source'])
            writer.writeheader()
            writer.writerows(valid_entries)
        
        print(f"Validated dataset saved to: {output_file}")
        print(f"Valid entries: {len(valid_entries)}")
        print(f"Invalid entries: {len(invalid_entries)}")
        
        # 無効なエントリを表示
        if invalid_entries:
            print("\nInvalid entries:")
            for entry in invalid_entries[:10]:  # 最初の10件のみ表示
                print(f"  {entry['word']}: {entry['ipa']} ({entry['reason']})")
        
        return len(valid_entries), len(invalid_entries)
        
    except Exception as e:
        print(f"Error validating dataset: {e}")
        return 0, 0

def main():
    """
    メイン処理
    """
    print("Final IPA Dataset Validation")
    print("=" * 50)
    
    input_file = "enhanced_words_with_ipa.csv"
    output_file = "final_words_with_ipa.csv"
    
    if not Path(input_file).exists():
        print(f"Input file {input_file} not found")
        return
    
    valid_count, invalid_count = validate_dataset(input_file, output_file)
    
    if valid_count > 0:
        print(f"\nValidation completed successfully!")
        print(f"Coverage: {valid_count/(valid_count + invalid_count)*100:.1f}%")
    else:
        print("Validation failed!")

if __name__ == "__main__":
    main()
