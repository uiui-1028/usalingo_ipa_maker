# analyze_updated_results.py
# 更新されたマッピングでの結果を詳細分析

import pandas as pd
import re
from collections import Counter

def analyze_updated_results():
    # CSVファイルを読み込み
    try:
        df = pd.read_csv('words_with_ipa_final.csv', encoding='utf-8')
        print(f"=== 更新されたマッピングでの処理結果 ===")
        print(f"総処理件数: {len(df)} 件")
        print(f"変更があった件数: {len(df[df['changes_count'] > 0])} 件")
        print(f"変更なしの件数: {len(df[df['changes_count'] == 0])} 件")
        
        # 変更回数の分布
        print("\n=== 変更回数の分布 ===")
        change_counts = df['changes_count'].value_counts().sort_index()
        for count, freq in change_counts.items():
            print(f"{count}回の変更: {freq} 件")
        
        # ルール別の適用回数
        print("\n=== ルール別適用回数 ===")
        rule_counts = {}
        for changes_detail in df['changes_detail']:
            if pd.isna(changes_detail) or changes_detail == '':
                continue
            rules = changes_detail.split('; ')
            for rule in rules:
                if 'ルール' in rule:
                    rule_num = re.search(r'ルール(\d+)', rule)
                    if rule_num:
                        rule_id = rule_num.group(1)
                        rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
        
        for rule_id in sorted(rule_counts.keys(), key=int):
            print(f"ルール{rule_id}: {rule_counts[rule_id]} 回適用")
        
        # 新しいルールの効果を確認
        print("\n=== 新しいルールの効果 ===")
        
        # r-vowel正規化の例
        r_changes = df[df['changes_detail'].str.contains('ルール13', na=False)]
        if len(r_changes) > 0:
            print(f"\n--- r-vowel正規化 (ルール13) の例 ({len(r_changes)}件) ---")
            for _, row in r_changes.head(5).iterrows():
                print(f"単語: {row['word']}")
                print(f"  元のIPA: {row['original_ipa']}")
                print(f"  正規化後: {row['normalized_ipa']}")
        
        # ストレス記号分割の例
        stress_changes = df[df['changes_detail'].str.contains('ルール5', na=False)]
        if len(stress_changes) > 0:
            print(f"\n--- ストレス記号分割 (ルール5) の例 ({len(stress_changes)}件) ---")
            for _, row in stress_changes.head(5).iterrows():
                print(f"単語: {row['word']}")
                print(f"  元のIPA: {row['original_ipa']}")
                print(f"  正規化後: {row['normalized_ipa']}")
        
        # カンマ区切り正規化の例
        comma_changes = df[df['changes_detail'].str.contains('ルール1|ルール2', na=False)]
        if len(comma_changes) > 0:
            print(f"\n--- カンマ区切り正規化の例 ({len(comma_changes)}件) ---")
            for _, row in comma_changes.head(5).iterrows():
                print(f"単語: {row['word']}")
                print(f"  元のIPA: {row['original_ipa']}")
                print(f"  正規化後: {row['normalized_ipa']}")
        
        # 怪しい表記の自動抽出
        print("\n=== 怪しい表記の自動抽出 ===")
        suspicious_patterns = []
        
        for _, row in df.iterrows():
            ipa = row['normalized_ipa']
            if pd.isna(ipa) or ipa == '':
                continue
                
            # 数字が残っているパターン
            if re.search(r'\b[0-9]+\b', ipa):
                suspicious_patterns.append(f"数字残存: {row['word']} -> {ipa}")
            
            # 大文字が残っているパターン
            if re.search(r'[A-Z]', ipa):
                suspicious_patterns.append(f"大文字残存: {row['word']} -> {ipa}")
            
            # 特殊記号が残っているパターン
            if re.search(r'[#@&$%]', ipa):
                suspicious_patterns.append(f"特殊記号残存: {row['word']} -> {ipa}")
            
            # 連続する同じ文字
            if re.search(r'(.)\1{2,}', ipa):
                suspicious_patterns.append(f"連続文字: {row['word']} -> {ipa}")
        
        if suspicious_patterns:
            print(f"怪しい表記を {len(suspicious_patterns)} 件発見:")
            for pattern in suspicious_patterns[:10]:  # 最初の10件を表示
                print(f"  - {pattern}")
            if len(suspicious_patterns) > 10:
                print(f"  ... 他 {len(suspicious_patterns) - 10} 件")
        else:
            print("怪しい表記は見つかりませんでした")
        
        # ルール追加候補の生成
        print("\n=== ルール追加候補の生成 ===")
        
        # 頻出パターンの分析
        all_ipa = ' '.join(df['normalized_ipa'].dropna().astype(str))
        
        # 数字パターン
        digit_patterns = re.findall(r'\b[0-9]+\b', all_ipa)
        if digit_patterns:
            digit_counter = Counter(digit_patterns)
            print(f"数字パターン: {dict(digit_counter.most_common(5))}")
        
        # 大文字パターン
        upper_patterns = re.findall(r'[A-Z]+', all_ipa)
        if upper_patterns:
            upper_counter = Counter(upper_patterns)
            print(f"大文字パターン: {dict(upper_counter.most_common(5))}")
        
        # 特殊記号パターン
        special_patterns = re.findall(r'[#@&$%]+', all_ipa)
        if special_patterns:
            special_counter = Counter(special_patterns)
            print(f"特殊記号パターン: {dict(special_counter.most_common(5))}")
        
        # エラー件数の確認
        error_count = len(df[df['normalized_ipa'] == 'error'])
        print(f"\n=== エラー件数 ===")
        print(f"error表記: {error_count} 件")
        
        if error_count > 0:
            print("エラー例:")
            error_examples = df[df['normalized_ipa'] == 'error'].head(5)
            for _, row in error_examples.iterrows():
                print(f"  - {row['word']}: {row['original_ipa']}")
        
        # レビュー対象の詳細
        review_df = pd.read_csv('ipa_review.csv', encoding='utf-8')
        print(f"\n=== レビュー対象の詳細 ===")
        print(f"レビュー対象件数: {len(review_df)} 件")
        
        if len(review_df) > 0:
            print("レビュー対象の例:")
            for _, row in review_df.head(10).iterrows():
                print(f"  - {row['word']}: {row['original_ipa']} -> {row['normalized_ipa']}")
            
    except Exception as e:
        print(f"エラー: {e}")
        print("ファイルの読み込みに失敗しました。")

if __name__ == "__main__":
    analyze_updated_results()
