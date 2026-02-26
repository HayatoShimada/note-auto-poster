import os
import google.generativeai as genai
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, api_key: str):
        """
        Gemini APIを用いたコンテンツ生成器
        
        Args:
            api_key: Gemini API キー
        """
        if not api_key:
            logger.warning("Gemini API key is not set. Dummy content will be generated.")
            self.api_key = None
            return
            
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Gemini 2.5 Flash を使用
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_article(self, theme: str, instructions: str) -> Tuple[str, str]:
        """
        指定されたテーマと指示に基づいて記事のタイトルと本文（Markdown）を生成する
        
        Args:
            theme: 記事のテーマ (例: "今週の古着トレンド予報・注目キーワード")
            instructions: 詳細な指示やトーン＆マナー
            
        Returns:
            Tuple[str, str]: (タイトル, Markdown形式の本文)
        """
        if not self.api_key:
            return f"【テスト】{theme}", f"# テスト記事\n\nテーマ: {theme}\n\nこれはGemini APIキーが設定されていない場合のダミーテキストです。"

        prompt = f"""
あなたはプロの古着・ファッションライターです。
以下のテーマと指示に基づいて、note向けの魅力的な記事を作成してください。
出力は「記事のタイトル」と「Markdown形式の本文」のみとし、JSON形式で返してください。

【テーマ】
{theme}

【詳細指示】
{instructions}
- 読者が読んでワクワクするような魅力的なタイトルにしてください。
- 記事の構成は見出し(##, ###)を使って見やすくしてください。
- トーン＆マナーは「親しみやすく、かつ専門的」なハイブリッドでお願いします。
- 他の曜日の内容とかぶらないような独自性を持たせてください。

【出力フォーマット】（必ずこのJSON構造に従うこと）
{{
  "title": "ここに記事のタイトルを含める",
  "content": "ここにMarkdown形式の本文を含める"
}}
"""
        
        try:
            # プロンプト内で強力にJSON出力を要求しているため、単に generate_content を呼ぶ
            response = self.model.generate_content(prompt)
            
            # JSON部分を確実に抽出するクリーンアップ処理
            result_text = response.text.strip()
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].strip()
                
            import json
            # JSON パースエラー(Invalid control character)を避けるために strict=False を指定
            data = json.loads(result_text, strict=False)
            
            title = data.get('title', f"無題: {theme}")
            content = data.get('content', "コンテンツの生成に失敗しました。")
            
            return title, content
            
        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return f"【エラー】{theme}", f"記事の生成中にエラーが発生しました。\n\nException: {e}"
