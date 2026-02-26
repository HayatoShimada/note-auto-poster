import os
import markdown
import logging
from note_api import NoteAPIClient
from llm_generator import ContentGenerator
from content_manager import ContentManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path='.env.local')
    except ImportError:
        pass

    # 必須環境変数の取得
    note_cookies = os.environ.get("NOTE_COOKIES")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not note_cookies:
        logger.error("NOTE_COOKIES が設定されていません。")
        return
        
    if not gemini_api_key:
        logger.warning("GEMINI_API_KEY が設定されていません。ダミー記事でテストします。")

    logger.info("自動投稿プロセスを開始します。")

    # 初期化
    note_client = NoteAPIClient(cookies=note_cookies)
    content_generator = ContentGenerator(api_key=gemini_api_key)
    content_manager = ContentManager()

    # テーマと指示の取得
    todays_info = content_manager.get_todays_theme()
    theme = todays_info['theme']
    instructions = todays_info['instructions']
    
    logger.info(f"本日のテーマ: {theme}")

    # 記事生成 (Gemini API)
    logger.info("Gemini APIで記事を生成中...")
    title, md_content = content_generator.generate_article(theme, instructions)
    
    # ハルシネーション対策の免責事項を末尾に追加
    footer = "\n\n---\n*※この記事はLLM（AI）によって自動生成された下書きです。内容は投稿者が確認した後に公開されています。*\n"
    md_content += footer

    # noteの仕様に合わせてシンプルなHTMLにするため、拡張は基本設定
    html_content = markdown.markdown(md_content, extensions=['tables', 'nl2br', 'fenced_code', 'sane_lists'])

    # note API を用いて下書き保存
    logger.info("note非公式APIで下書き保存中...")
    article_id, article_key = note_client.create_article(title=title, html_content=html_content)

    if article_id:
        logger.info(f"自動投稿（下書き作成）が完了しました。 https://note.com/notes/{article_id}")
    else:
        logger.error("自動投稿（下書き作成）に失敗しました。")


if __name__ == "__main__":
    main()
