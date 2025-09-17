#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英単語リストにIPA発音記号を自動生成するスクリプト
phonemizerライブラリを使用してIPA変換を実行
"""

import pandas as pd
from phonemizer import phonemize
import logging
import time
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ipa(word, backend='espeak', language='en-us'):
    """
    単語のIPA発音記号を取得する関数
    
    Args:
        word (str): 変換する単語
        backend (str): 使用するバックエンド ('espeak', 'festival', 'segments')
        language (str): 言語設定
    
    Returns:
        str: IPA発音記号
    """
    try:
        # 単語を小文字に変換
        word_lower = word.lower().strip()
        
        # 空の単語や無効な文字をスキップ
        if not word_lower or word_lower in ['', 'nan', 'none'] or word_lower.isspace():
            return ''
        
        # 直接espeakコマンドを使用してIPA変換
        import subprocess
        import os
        
        espeak_path = '/opt/homebrew/bin/espeak'
        if os.path.exists(espeak_path):
            # espeakコマンドでIPA変換を実行
            cmd = [espeak_path, '-x', '-q', word_lower]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                ipa = result.stdout.strip()
                # espeakの出力をクリーンアップ
                ipa = ipa.replace(' ', '').replace('\n', '')
                return ipa
            else:
                logger.warning(f"espeakコマンドが失敗: {result.stderr}")
                return ''
        else:
            logger.warning("espeakが見つかりません")
            return ''
    
    except subprocess.TimeoutExpired:
        logger.warning(f"単語 '{word}' の変換がタイムアウトしました")
        return ''
    except Exception as e:
        logger.warning(f"単語 '{word}' の変換に失敗: {e}")
        return ''

def process_words_batch(words, batch_size=100):
    """
    単語をバッチ処理でIPA変換する関数
    
    Args:
        words (list): 変換する単語のリスト
        batch_size (int): バッチサイズ
    
    Returns:
        list: IPA発音記号のリスト
    """
    ipa_results = []
    total_words = len(words)
    
    logger.info(f"合計 {total_words} 語の処理を開始します...")
    
    for i in range(0, total_words, batch_size):
        batch = words[i:i + batch_size]
        batch_start_time = time.time()
        
        logger.info(f"バッチ {i//batch_size + 1}/{(total_words-1)//batch_size + 1} を処理中... ({len(batch)} 語)")
        
        batch_ipa = []
        for word in batch:
            ipa = get_ipa(word)
            batch_ipa.append(ipa)
        
        ipa_results.extend(batch_ipa)
        
        batch_time = time.time() - batch_start_time
        logger.info(f"バッチ完了: {batch_time:.2f}秒")
        
        # 進捗表示
        processed = min(i + batch_size, total_words)
        progress = (processed / total_words) * 100
        logger.info(f"進捗: {processed}/{total_words} ({progress:.1f}%)")
    
    return ipa_results

def main():
    """メイン処理"""
    start_time = time.time()
    
    # 入力ファイルの確認
    input_file = Path('../data/words.csv')
    if not input_file.exists():
        logger.error(f"入力ファイル '{input_file}' が見つかりません")
        return
    
    # CSVファイルを読み込み
    logger.info("CSVファイルを読み込み中...")
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        logger.info(f"CSVファイル読み込み完了: {len(df)} 行")
    except Exception as e:
        logger.error(f"CSVファイルの読み込みに失敗: {e}")
        return
    
    # 単語列を確認
    word_column = 'word'
    if word_column not in df.columns:
        logger.error(f"列 '{word_column}' が見つかりません。利用可能な列: {list(df.columns)}")
        return
    
    # 既存のphonetic_symbol列があるかチェック
    if 'phonetic_symbol' in df.columns:
        logger.info("既存のphonetic_symbol列を確認中...")
        existing_ipa = df['phonetic_symbol'].fillna('').astype(str)
        empty_mask = (existing_ipa == '') | (existing_ipa == 'nan')
        empty_count = empty_mask.sum()
        logger.info(f"空のphonetic_symbol: {empty_count} 語")
        
        if empty_count == 0:
            logger.info("すべての単語に既にIPAが設定されています")
            return
    else:
        logger.info("新しいphonetic_symbol列を作成します")
        empty_mask = pd.Series([True] * len(df))
    
    # 空の単語をスキップ
    words_to_process = df[empty_mask][word_column].dropna().tolist()
    # 空文字列や空白のみの単語も除外
    words_to_process = [word for word in words_to_process if word and str(word).strip() and not str(word).strip().isspace() and str(word).strip() != '']
    
    # 空の単語の行をDataFrameからも除外
    df = df[df[word_column].notna() & (df[word_column].str.strip() != '') & (df[word_column].str.strip() != ',')]
    logger.info(f"処理対象: {len(words_to_process)} 語")
    
    if len(words_to_process) == 0:
        logger.info("処理対象の単語がありません")
        return
    
    # IPA変換を実行
    logger.info("IPA変換を開始します...")
    ipa_results = process_words_batch(words_to_process)
    
    # 結果をDataFrameに追加
    if 'phonetic_symbol' not in df.columns:
        df['phonetic_symbol'] = ''
    
    # 空のphonetic_symbolに結果を設定
    # インデックスを正しく対応させる
    empty_indices = df[empty_mask].index
    for i, idx in enumerate(empty_indices):
        if i < len(ipa_results):
            df.loc[idx, 'phonetic_symbol'] = ipa_results[i]
    
    # 結果を保存
    output_file = Path('words_with_ipa.csv')
    logger.info(f"結果を '{output_file}' に保存中...")
    
    try:
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"保存完了: {output_file}")
    except Exception as e:
        logger.error(f"ファイルの保存に失敗: {e}")
        return
    
    # 統計情報を表示
    total_time = time.time() - start_time
    processed_count = len(words_to_process)
    avg_time_per_word = total_time / processed_count if processed_count > 0 else 0
    
    logger.info("=" * 50)
    logger.info("処理完了!")
    logger.info(f"処理時間: {total_time:.2f} 秒")
    logger.info(f"処理単語数: {processed_count} 語")
    logger.info(f"平均処理時間: {avg_time_per_word:.3f} 秒/語")
    logger.info(f"出力ファイル: {output_file}")
    logger.info("=" * 50)
    
    # サンプル結果を表示
    logger.info("\nサンプル結果:")
    sample_df = df[df['phonetic_symbol'] != ''].head(10)
    for _, row in sample_df.iterrows():
        logger.info(f"{row[word_column]:<20} -> {row['phonetic_symbol']}")

if __name__ == "__main__":
    main()

