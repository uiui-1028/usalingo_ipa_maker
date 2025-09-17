#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPA出力テストスクリプト
フィードバックに基づいてphonemizerのIPA出力を確認
"""

from phonemizer import phonemize
import os

def test_ipa_output():
    """IPA出力をテストする関数"""
    test_words = ["absorption", "read", "wind", "sample", "abortion"]
    
    print("=== IPA出力テスト ===")
    print(f"テスト単語: {test_words}")
    print()
    
    # espeak-ngのパスを設定
    espeak_path = "/opt/homebrew/bin/espeak-ng"
    if os.path.exists(espeak_path):
        os.environ['PHONEMIZER_ESPEAK_PATH'] = espeak_path
        print(f"espeak-ngパスを設定: {espeak_path}")
    else:
        print("espeak-ngが見つかりません")
        return False
    
    try:
        # espeakバックエンドでIPA変換を実行
        result = phonemize(test_words, 
                          language='en-us', 
                          backend='espeak', 
                          strip=True, 
                          with_stress=True)
        
        print("結果:")
        for word, ipa in zip(test_words, result):
            print(f"{word:<15} -> {ipa}")
        
        print()
        print("期待される結果例:")
        print("absorption      -> əbˈzɔːpʃən")
        print("read            -> riːd")
        print("wind            -> wɪnd")
        print("sample          -> ˈsæmpl")
        print("abortion        -> əˈbɔːrʃən")
        
        return True
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    test_ipa_output()
