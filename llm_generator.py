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
- 【重要】Google検索ツールを使用して、最新の動向やトレンド情報、具体的なブランド動向などを踏まえた説得力のある最新の内容にしてください。
- 【重要】noteAPIの仕様で外部画像タグ(`<img>`)が削除されてしまうため、**Markdownの画像構文(`![alt](URL)`)は絶対に使わないでください**。
  代わりに、読者や投稿者が後から手動で画像を挿入しやすいように、以下のような**テキストリンク付きの引用ブロック**として画像URLを複数箇所に配置してください。
  例: 
  > 📷 **画像挿入推奨**: `vintage fashion`
  > [参考用フリー素材(Unsplash)](https://source.unsplash.com/featured/?vintage,fashion)

【出力フォーマット】
以下の形式で出力してください。タイトル（1行のみ）の後に `---BODY---` という区切り文字を入れ、その後にMarkdown形式の本文を書いてください。

<title>
---BODY---
<content>
"""
        
        try:
            # Google Search Grounding を使用
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "tools": [{"google_search": {}}],
                },
            )
            
            text = response.text.strip()
            
            # ---BODY--- で分割してタイトルと本文を取得
            parts = text.split("---BODY---", 1)
            if len(parts) == 2:
                title = parts[0].strip()
                content = parts[1].strip()
            else:
                # 区切り文字がない場合のフォールバック（最初の行をタイトルとみなす）
                lines = text.split('\n', 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""
                
            # 不要なマークダウンコードブロックのバッククォートなどをクリーンアップ
            title = title.replace('#', '').strip()
            if content.startswith('```markdown'):
                content = content[11:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            return title, content
            
        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return f"【エラー】{theme}", f"記事の生成中にエラーが発生しました。\n\nException: {e}"
