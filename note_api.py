import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

class NoteAPIClient:
    def __init__(self, cookies: str):
        """
        noteの非公式APIクライアント
        
        Args:
            cookies: セッションCookie文字列 (ex: 'note_session=xxx; ...')
        """
        self.cookies = {}
        # Simple cookie parsing
        if '=' not in cookies:
            # ユーザーが "note_session=XXX" の形式ではなく値だけを設定した場合のフォールバック
            self.cookies['note_session'] = cookies.strip()
        else:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    k, v = cookie.strip().split('=', 1)
                    self.cookies[k] = v
                
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

    def _request(self, method, url, **kwargs):
        # サーバー負荷への配慮でAPIコール間にsleepを入れる
        time.sleep(1)
        
        headers = kwargs.pop('headers', {})
        headers.update(self.base_headers)
        
        try:
            response = requests.request(
                method, 
                url, 
                cookies=self.cookies, 
                headers=headers, 
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Body: {e.response.text}")
            return None

    def create_article(self, title: str, html_content: str):
        """
        新しい記事を作成（下書き保存）
        """
        url = 'https://note.com/api/v1/text_notes'
        headers = {'Content-Type': 'application/json'}
        data = {
            'body': html_content,
            'name': title,
            'template_key': None,
        }
        
        result = self._request('POST', url, headers=headers, json=data)
        
        logger.error(f"create_article raw response: {json.dumps(result, ensure_ascii=False)}")
        
        if result and 'data' in result:
            article_id = result['data'].get('id')
            article_key = result['data'].get('key')
            logger.info(f"記事作成成功！ ID: {article_id}")
            return article_id, article_key
            
        logger.error(f"create_article failed. API response was not as expected: {result}")
        return None, None

    def update_article(self, article_id: str, title: str, html_content: str):
        """
        既存の下書き記事を更新
        """
        url = f'https://note.com/api/v1/text_notes/{article_id}'
        headers = {'Content-Type': 'application/json'}
        data = {
            'body': html_content,
            'name': title,
            'template_key': None,
        }
        
        result = self._request('PUT', url, headers=headers, json=data)
        if result and 'data' in result:
            logger.info(f"記事更新成功！ ID: {article_id}")
            return True
        return False

    def upload_image(self, image_path: str):
        """
        画像をアップロード
        """
        url = 'https://note.com/api/v1/upload_image'
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                result = self._request('POST', url, files=files)
                
                if result and 'data' in result:
                    image_key = result['data'].get('key')
                    image_url = result['data'].get('url')
                    logger.info(f"画像アップロード成功！ KEY: {image_key}")
                    return image_key, image_url
        except FileNotFoundError:
            logger.error(f"Image not found: {image_path}")
            
        return None, None
