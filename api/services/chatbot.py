from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from api.core.config import get_settings
from api.services.clarity import ClarityClient


class ChatbotGateway:
    """Unified chatbot gateway with graceful fallback to Clarity."""

    def __init__(self, school_id: str):
        self.school_id = school_id
        self.settings = get_settings()

    def send_message(
        self,
        messages: List[Dict[str, str]],
        *,
        locale: str = "en",
        channel: str = "parent_app",
    ) -> Dict[str, Any]:
        if not messages:
            raise ValueError("At least one message is required.")

        if self._has_external_provider():
            try:
                external_response = self._call_external_provider(messages, locale=locale, channel=channel)
                if external_response:
                    return {
                        "source": "external_provider",
                        "response": external_response.get("message") or external_response.get("response"),
                        "raw": external_response,
                    }
            except Exception:
                # Fall back to Clarity if external provider fails.
                pass

        clarity_response = self._clarity_fallback(messages)
        return {
            "source": "clarity_fallback",
            "response": clarity_response["analysis"]["summary"],
            "raw": clarity_response,
        }

    def _has_external_provider(self) -> bool:
        return bool(self.settings.chatbot_api_base_url and self.settings.chatbot_api_key)

    def _call_external_provider(
        self,
        messages: List[Dict[str, str]],
        *,
        locale: str,
        channel: str,
    ) -> Optional[Dict[str, Any]]:
        client = httpx.Client(
            base_url=str(self.settings.chatbot_api_base_url),
            headers={
                "Authorization": f"Bearer {self.settings.chatbot_api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(20.0, read=30.0),
        )
        try:
            payload = {
                "school_id": self.school_id,
                "locale": locale,
                "channel": channel,
                "messages": messages,
            }
            response = client.post("/query", json=payload)
            response.raise_for_status()
            return response.json()
        finally:
            client.close()

    def _clarity_fallback(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        clarity = ClarityClient()
        try:
            conversation_text = self._render_conversation(messages)
            return clarity.analyze(
                directive=(
                    "You are the Parent Engagement Agent responding via in-app chat. Provide a concise, "
                    "empathetic answer to the final parent message. Conversation transcript:\n"
                    f"{conversation_text}"
                ),
                domain="education",
            )
        finally:
            clarity.close()

    def _render_conversation(self, messages: List[Dict[str, str]]) -> str:
        lines = []
        for message in messages:
            role = message.get("role", "user")
            role_label = "Parent" if role in {"user", "parent"} else "Assistant"
            lines.append(f"{role_label}: {message.get('content', '').strip()}")
        return "\n".join(lines)
