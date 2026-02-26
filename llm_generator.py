import os
from google import genai
from pydantic import BaseModel, Field
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# 出力形式を定義する Pydantic モデル
class ArticleDraft(BaseModel):
    title: str = Field(description="note向けの魅力的な記事のタイトル")
    content: str = Field(description="Markdown形式の記事本文")

class ContentGenerator:
    def __init__(self, api_key: str):
        """
        Gemini APIを用いたコンテンツ生成器
        
        Args:
            api_key: Gemini API キー
        """
        if not api_key:
            logger.warning("Gemini API key is not set. Dummy content will be generated.")
            self.client = None
            return
            
        # SDK v1.0.0以降の新しいクライアント初期化
        self.client = genai.Client(api_key=api_key)
        # Gemini 2.5 Flash を使用
        self.model_name = 'gemini-2.5-flash'

    def generate_article(self, theme: str, instructions: str) -> Tuple[str, str]:
        """
        指定されたテーマと指示に基づいて記事のタイトルと本文（Markdown）を生成する
        
        Args:
            theme: 記事のテーマ (例: "今週の古着トレンド予報・注目キーワード")
            instructions: 詳細な指示やトーン＆マナー
            
        Returns:
            Tuple[str, str]: (タイトル, Markdown形式の本文)
        """
        if not self.client:
            return f"【テスト】{theme}", f"# テスト記事\n\nテーマ: {theme}\n\nこれはGemini APIキーが設定されていない場合のダミーテキストです。"

        prompt = f"""
あなたはプロの古着・ファッションライターです。
以下のテーマと指示に基づいて、note向けの魅力的な記事を作成してください。

【テーマ】
{theme}

【詳細指示】
{instructions}
- 読者が読んでワクワクするような魅力的なタイトルにしてください。
- 記事の構成は見出し(##, ###)を使って見やすくしてください。
- トーン＆マナーは「親しみやすく、かつ専門的」なハイブリッドでお願いします。
- 過去の内容とかぶらないような独自性を持たせてください。
"""
        
        try:
            # 最新の Structured Outputs の仕組みを使ってリクエスト
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": ArticleDraft.model_json_schema(),
                },
            )
            
            # レスポンス文字列を Pydantic モデルでバリデーションしつつパース
            article_draft = ArticleDraft.model_validate_json(response.text)
            
            return article_draft.title, article_draft.content
            
        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return f"【エラー】{theme}", f"記事の生成中にエラーが発生しました。\n\nException: {e}"
