#!/usr/bin/env python3
"""
最終的なIPAデータセットを作成するスクリプト
標準化されたIPAデータから最終的な形式のファイルを生成
"""

import csv
from pathlib import Path
from typing import List, Dict

def create_final_dataset(input_file: str, output_file: str):
    """
    最終的なIPAデータセットを作成する
    """
    print(f"Creating final dataset from {input_file}...")
    
    final_data = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                word = row.get('word', '').strip()
                standardized_ipa = row.get('standardized_ipa', '').strip()
                source = row.get('source', '').strip()
                
                # 最終的なデータ形式
                final_data.append({
                    'word': word,
                    'ipa': standardized_ipa,
                    'source': source
                })
        
        # 結果を保存
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['word', 'ipa', 'source'])
            writer.writeheader()
            writer.writerows(final_data)
        
        print(f"Final dataset saved to {output_file}")
        
    except Exception as e:
        print(f"Error creating final dataset: {e}")

def print_final_statistics(output_file: str):
    """
    最終データセットの統計を表示する
    """
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            total_words = 0
            cmu_words = 0
            generated_words = 0
            words_with_ipa = 0
            words_without_ipa = 0
            
            for row in reader:
                total_words += 1
                source = row.get('source', '')
                ipa = row.get('ipa', '').strip()
                
                if source == 'cmu_dict':
                    cmu_words += 1
                elif source == 'generated':
                    generated_words += 1
                
                if ipa:
                    words_with_ipa += 1
                else:
                    words_without_ipa += 1
            
            print(f"\nFinal Dataset Statistics:")
            print(f"Total words: {total_words}")
            print(f"Words from CMU dictionary: {cmu_words} ({cmu_words/total_words*100:.1f}%)")
            print(f"Words with generated IPA: {generated_words} ({generated_words/total_words*100:.1f}%)")
            print(f"Words with IPA: {words_with_ipa} ({words_with_ipa/total_words*100:.1f}%)")
            print(f"Words without IPA: {words_without_ipa} ({words_without_ipa/total_words*100:.1f}%)")
            
    except Exception as e:
        print(f"Error calculating statistics: {e}")

def main():
    """
    メイン処理
    """
    print("Final Dataset Creator")
    print("=" * 50)
    
    # ファイルパス
    input_file = "output/standardized_words_with_ipa.csv"
    output_file = "output/final_corrected_words_with_ipa.csv"
    
    # 入力ファイルの存在確認
    if not Path(input_file).exists():
        print(f"Input file {input_file} not found")
        return
    
    # 最終データセットを作成
    create_final_dataset(input_file, output_file)
    
    # 統計を表示
    print_final_statistics(output_file)
    
    print(f"\nFinal dataset creation completed!")
    print(f"Output: {output_file}")

if __name__ == "__main__":
    main()
