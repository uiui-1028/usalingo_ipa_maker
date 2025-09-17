# USALingo Words IPA Project

英語単語にIPA（国際音声記号）を付与するプロジェクトです。

## 📁 プロジェクト構造

```
usalingo_words_ipa/
├── 📁 data/                    # データファイル
│   ├── cmudict-0.7b-ipa.txt   # CMU辞書データ
│   ├── words.csv              # 元の単語リスト
│   ├── sample.txt             # サンプルデータ
│   └── wiktextract_output.json.tmp
├── 📁 scripts/                # メインスクリプト
│   ├── generate_ipa.py        # 基本的なIPA生成
│   ├── enhanced_ipa_processor.py  # 拡張IPA処理
│   ├── normalize_ipa_pipeline.py  # IPA正規化
│   ├── process_sample.py      # サンプル処理
│   └── test_ipa.py           # テストスクリプト
├── 📁 processors/             # 外部API処理
│   ├── wiktextract_ipa_extractor.py
│   ├── wiktextract_local_processor.py
│   └── wiktionary_api_processor.py
├── 📁 analysis/               # 分析・検証
│   ├── analyze_updated_results.py
│   └── final_validation.py
├── 📁 config/                 # 設定ファイル
│   └── mapping_updated.tsv
├── 📁 output/                 # 出力ファイル
│   ├── words_with_ipa_final.csv
│   ├── final_words_with_ipa.csv
│   ├── enhanced_words_with_ipa.csv
│   ├── wiktionary_api_results.csv
│   └── wiktionary_ipa_results.csv
└── 📁 docs/                   # ドキュメント
    └── go                     # 作業手順書
```

## 🚀 使用方法

### 基本的なIPA生成
```bash
cd scripts
python3 generate_ipa.py
```

### 拡張IPA処理
```bash
cd scripts
python3 enhanced_ipa_processor.py
```

### サンプル処理
```bash
cd scripts
python3 process_sample.py
```

### テスト実行
```bash
cd scripts
python3 test_ipa.py
```

## 📊 データファイル

- **words.csv**: 処理対象の単語リスト（7,324語）
- **cmudict-0.7b-ipa.txt**: CMU Pronouncing DictionaryのIPA版
- **sample.txt**: テスト用サンプルデータ（500語）

## 🔧 設定ファイル

- **mapping_updated.tsv**: IPA正規化ルール（81ルール）

## 📈 出力ファイル

- **final_words_with_ipa.csv**: 最終的なIPA付き単語リスト（7,322語）
- **enhanced_words_with_ipa.csv**: 拡張処理結果
- **wiktionary_*.csv**: Wiktionary API処理結果

## 🛠️ 外部API処理

- **Wiktionary API**: オンライン辞書からIPAデータを取得
- **Wiktextract**: ローカルWiktionaryデータからIPAを抽出

## 📝 注意事項

- スクリプトは各フォルダ内から実行してください
- パス参照は相対パスで設定されています
- espeak-ngのインストールが必要です（macOS: `brew install espeak-ng`）

## 🔍 分析・検証

- **final_validation.py**: 最終データの検証とクリーンアップ
- **analyze_updated_results.py**: 結果の分析とレポート生成
