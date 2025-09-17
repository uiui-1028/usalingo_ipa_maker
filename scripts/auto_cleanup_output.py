#!/usr/bin/env python3
"""
outputディレクトリを自動で整理するスクリプト
最終的な成果物のみを残し、中間ファイルを削除
"""

import os
import shutil
from pathlib import Path

def auto_cleanup_output_directory():
    """
    outputディレクトリを自動で整理する
    """
    output_dir = Path("output")
    
    if not output_dir.exists():
        print("Output directory not found")
        return
    
    # 保持するファイル（最終的な成果物）
    keep_files = {
        "final_corrected_words_with_ipa.csv",  # 最終的なIPAデータセット
        "corrected_cmu_dict.csv"  # CMU辞書の修正版（参考用）
    }
    
    # 削除するファイル
    files_to_remove = []
    
    for file_path in output_dir.iterdir():
        if file_path.is_file():
            if file_path.name not in keep_files:
                files_to_remove.append(file_path)
    
    print("Files to be removed:")
    for file_path in files_to_remove:
        print(f"  - {file_path.name}")
    
    print(f"\nFiles to be kept:")
    for file_name in keep_files:
        file_path = output_dir / file_name
        if file_path.exists():
            print(f"  - {file_name}")
        else:
            print(f"  - {file_name} (not found)")
    
    # ファイルを削除
    removed_count = 0
    for file_path in files_to_remove:
        try:
            file_path.unlink()
            print(f"Removed: {file_path.name}")
            removed_count += 1
        except Exception as e:
            print(f"Error removing {file_path.name}: {e}")
    
    print(f"\nCleanup completed!")
    print(f"Files removed: {removed_count}")
    print(f"Files kept: {len(keep_files)}")

def create_readme():
    """
    outputディレクトリのREADMEを作成
    """
    readme_content = """# Output Directory

This directory contains the final output files from the IPA processing pipeline.

## Files

- `final_corrected_words_with_ipa.csv` - Final IPA dataset with standardized IPA notation
  - Contains 7,321 words with IPA transcriptions
  - 99.8% from CMU dictionary, 0.2% generated
  - 100% coverage with standardized IPA format
  
- `corrected_cmu_dict.csv` - Corrected CMU dictionary (reference)
  - Contains the original CMU dictionary with IPA corrections
  - Used as reference for the main dataset

## Data Format

The main dataset (`final_corrected_words_with_ipa.csv`) contains:
- `word`: The English word
- `ipa`: IPA transcription in standardized format
- `source`: Data source (cmu_dict or generated)

## IPA Standardization

The IPA data has been standardized according to:
- /ɝ/ → /ɜːr/ conversion for American English
- /ɹ/ → /r/ unification
- Proper stress marking with ˈ and ˌ
- Consistent long vowel notation with ː
"""
    
    readme_path = Path("output/README.md")
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"Created README: {readme_path}")
    except Exception as e:
        print(f"Error creating README: {e}")

def main():
    """
    メイン処理
    """
    print("Output Directory Auto Cleanup")
    print("=" * 50)
    
    # 現在の状況を表示
    output_dir = Path("output")
    if output_dir.exists():
        files = list(output_dir.iterdir())
        print(f"Current files in output directory: {len(files)}")
        for file_path in files:
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  {file_path.name} ({size:,} bytes)")
    
    # クリーンアップを実行
    auto_cleanup_output_directory()
    
    # READMEを作成
    create_readme()
    
    # 最終的な状況を表示
    print("\nFinal output directory contents:")
    if output_dir.exists():
        files = list(output_dir.iterdir())
        for file_path in files:
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  {file_path.name} ({size:,} bytes)")
    
    print("\nOutput directory cleanup completed!")

if __name__ == "__main__":
    main()
