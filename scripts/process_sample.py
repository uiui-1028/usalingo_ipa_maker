# process_sample.py
# sample.txt用のIPA正規化パイプライン
# 使い方: python3 process_sample.py

import os, sys, shutil, subprocess
import pandas as pd
import regex as re
from phonemizer import phonemize

# ---- 設定ファイル名 ----
INPUT_TXT = "../data/sample.txt"              # タブ区切りの単語\tIPAファイル
MAPPING_TSV = "../config/mapping_updated.tsv"   # 置換表: pattern \t ipa_replacement
OUTPUT_CSV = "../output/words_with_ipa_final.csv"
REVIEW_CSV = "../output/ipa_review.csv"

# ---- ユーティリティ ----
def read_mapping(path):
    """ mapping.tsv を読み込み、(compiled_regex, replacement) のリストを返す """
    rules = []
    if not os.path.exists(path):
        print("警告: mapping.tsv が見つかりません。置換ルールはスキップされます。")
        return rules
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # タブ区切りで分割
            parts = line.split('\t', 1)
            if len(parts) != 2:
                print(f"警告: 行 {line_num} の形式が正しくありません: {line}")
                continue
                
            pattern, replacement = parts
            try:
                cre = re.compile(pattern)
                rules.append((cre, replacement))
                print(f"ルール追加: {pattern} -> {replacement}")
            except Exception as e:
                print(f"mapping rule compile error (行 {line_num}): {pattern} -> {e}", file=sys.stderr)
    
    print(f"合計 {len(rules)} 個の置換ルールを読み込みました")
    return rules

def apply_mapping(text, rules):
    """ ルールを順に適用（最初にマッチしたら置換） """
    s = text
    changes = []
    for i, (cre, replacement) in enumerate(rules):
        if cre.search(s):
            old_s = s
            s = cre.sub(replacement, s)
            if old_s != s:
                changes.append(f"ルール{i+1}: {cre.pattern} -> {replacement}")
    return s, changes

def has_espeak():
    for b in ("espeak-ng","espeak"):
        p = shutil.which(b)
        if p:
            return p
    return None

# ---- メイン処理 ----
def main():
    if not os.path.exists(INPUT_TXT):
        print(f"入力ファイル {INPUT_TXT} が見つかりません。", file=sys.stderr)
        return

    rules = read_mapping(MAPPING_TSV)
    espeak_path = has_espeak()
    espeak_ok = bool(espeak_path)
    if espeak_ok:
        print("espeak-ng found at:", espeak_path)
    else:
        print("espeak-ng not found: phonemizer IPA 変換は動作しない可能性があります。")

    results = []
    review_items = []
    
    with open(INPUT_TXT, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            # タブ区切りで分割
            parts = line.split('\t', 1)
            if len(parts) != 2:
                print(f"警告: 行 {line_num} の形式が正しくありません: {line}")
                continue
                
            word, original_ipa = parts
            
            # 置換ルールを適用
            if rules:
                normalized_ipa, changes = apply_mapping(original_ipa, rules)
                if changes:
                    print(f"単語 '{word}': {len(changes)} 個の変更")
                    for change in changes:
                        print(f"  - {change}")
            else:
                normalized_ipa = original_ipa
                changes = []
            
            # __NO_IPA__をerrorに置換
            if normalized_ipa == "__NO_IPA__":
                normalized_ipa = "error"
                changes.append("__NO_IPA__ -> error")
            
            # 結果を記録
            result = {
                "word": word,
                "original_ipa": original_ipa,
                "normalized_ipa": normalized_ipa,
                "changes_count": len(changes),
                "changes_detail": "; ".join(changes) if changes else ""
            }
            results.append(result)
            
            # レビュー対象の判定
            if (normalized_ipa != original_ipa or 
                "__NO_IPA__" in normalized_ipa or
                "#TOKEN" in normalized_ipa or
                "__EMPTY__" in normalized_ipa):
                review_items.append(result)

    # 結果をCSVに保存
    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    
    # レビュー用CSVを保存
    if review_items:
        review_df = pd.DataFrame(review_items)
        review_df.to_csv(REVIEW_CSV, index=False, encoding='utf-8')
        print(f"レビュー対象: {len(review_items)} 件 -> {REVIEW_CSV}")
    else:
        print("レビュー対象の項目はありませんでした")
    
    print(f"完了: {OUTPUT_CSV}")
    print(f"総処理件数: {len(results)} 件")
    print(f"変更があった件数: {len([r for r in results if r['changes_count'] > 0])} 件")

if __name__ == "__main__":
    main()
