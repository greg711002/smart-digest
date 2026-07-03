"""AI summarizer module with configurable providers."""
import os
import random
from typing import Optional

import httpx

# Predefined tags for categorization
PRESET_TAGS = [
    "Финансы", "IT", "Дизайн", "Маркетинг", "Наука", 
    "Политика", "Культура", "Спорт", "Бизнес", "Технологии",
    "Медицина", "Образование", "Путешествия", "Еда", "Автомобили"
]

# Keywords for automatic tagging
TAG_KEYWORDS = {
    "Финансы": ["финансы", "деньги", "банк", "инвестиции", "акции", "рубль", "доллар", "экономика", "финтех"],
    "IT": ["it", "software", "programming", "developer", "код", "программирование", "github", "технологии"],
    "Дизайн": ["дизайн", "ui", "ux", "interface", "figma", "graphic", "вёрстка"],
    "Маркетинг": ["маркетинг", "marketing", "реклама", "seo", "smm", "бренд", "контент"],
    "Наука": ["наука", "исследование", "учёные", "открытие", "NASA", "космос"],
    "Политика": ["политика", "government", "election", "парламент", "президент"],
    "Культура": ["культура", "искусство", "кино", "музыка", "театр", "книга"],
    "Спорт": ["спорт", "football", "футбол", "хоккей", "олимпиада", "матч"],
    "Бизнес": ["бизнес", "startup", "предпринимательство", "компания", "рынок"],
    "Технологии": ["технологии", "ai", "ml", "machine learning", "нейросеть", "робот"],
    "Медицина": ["медицина", "здоровье", "врач", "лечение", "болезнь", "医院"],
    "Образование": ["образование", "университет", "школа", "курсы", "обучение"],
    "Путешествия": ["путешествия", "travel", "туризм", "отпуск", "страна", "город"],
    "Еда": ["еда", "food", "рецепт", "кухня", "ресторан", "готовить"],
    "Автомобили": ["автомобиль", "машина", "tesla", "bmw", "авто", "транспорт"]
}


def _extract_keywords(text: str) -> list[str]:
    """Extract keywords from text for tagging."""
    text_lower = text.lower()
    found_tags = []
    
    for tag, keywords in TAG_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_tags.append(tag)
                break
    
    # Return unique tags, limited to 5
    return list(set(found_tags))[:5]


class MockSummarizer:
    """Mock summarizer for development/demo purposes."""
    
    async def summarize(self, title: str, content: str) -> tuple[str, list[str]]:
        """Generate a mock summary and tags."""
        # Clean content
        clean_content = content[:2000] if content else ""
        
        # Generate mock summary
        sentences = clean_content.split('.')
        summary_parts = []
        for s in sentences[:3]:
            s = s.strip()
            if s and len(s) > 20:
                summary_parts.append(s.capitalize() + '.')
        
        if not summary_parts:
            summary_parts = [f"Статья о {title[:50]}... подробности доступны по ссылке."]
        
        summary = " ".join(summary_parts[:2])
        
        # Auto-tag based on content
        tags = _extract_keywords(title + " " + clean_content)
        
        # If no tags found, add random ones
        if not tags:
            tags = random.sample(PRESET_TAGS, min(2, len(PRESET_TAGS)))
        
        return summary, tags


class OpenAISummarizer:
    """OpenAI-powered summarizer."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    async def summarize(self, title: str, content: str) -> tuple[str, list[str]]:
        """Generate summary using OpenAI."""
        prompt = f"""Прочитай следующую статью и создай краткое резюме (1-3 предложения) на русском языке.
Также определи 2-5 тегов из списка: {', '.join(PRESET_TAGS)}.
Верни результат в формате JSON: {{"summary": "...", "tags": ["tag1", "tag2"]}}

Заголовок: {title}
Содержимое: {content[:3000]}"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            result = response.json()
            
            import json as json_lib
            content_response = result["choices"][0]["message"]["content"]
            
            # Try to parse JSON response
            try:
                data = json_lib.loads(content_response)
                return data.get("summary", ""), data.get("tags", [])
            except:
                # Fallback: return raw text
                return content_response[:500], _extract_keywords(content)


class AnthropicSummarizer:
    """Anthropic Claude-powered summarizer."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    async def summarize(self, title: str, content: str) -> tuple[str, list[str]]:
        """Generate summary using Anthropic Claude."""
        prompt = f"""Прочитай статью и создай краткое резюме (1-3 предложения) на русском языке.
Определи теги из списка: {', '.join(PRESET_TAGS)}.
Верни в формате JSON: {{"summary": "...", "tags": ["tag1", "tag2"]}}

Заголовок: {title}
Содержимое: {content[:3000]}"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            result = response.json()
            
            import json as json_lib
            content_response = result["content"][0]["text"]
            
            try:
                data = json_lib.loads(content_response)
                return data.get("summary", ""), data.get("tags", [])
            except:
                return content_response[:500], _extract_keywords(content)


def get_summarizer():
    """Get the configured summarizer based on environment."""
    provider = os.getenv("AI_PROVIDER", "mock").lower()
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            return OpenAISummarizer(api_key)
    
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if api_key:
            return AnthropicSummarizer(api_key)
    
    # Default to mock
    return MockSummarizer()


# Global summarizer instance
_summarizer = None

def get_summarizer_instance():
    """Get or create the global summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = get_summarizer()
    return _summarizer
