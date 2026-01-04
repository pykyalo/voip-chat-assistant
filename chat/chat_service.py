import anthropic
from django.conf import settings
from .models import Document, ChatMessage


class VOIPChatService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
        )
        self.model = "claude-sonnet-4-20250514"

    def build_context_from_documents(self) -> str:
        """Retrieve all uploaded documents as context"""
        documents = Document.objects.all()

        if not documents.exists():
            return "No documents uploaded yet."

        context_parts = []

        for doc in documents:
            context_parts.append(
                f"=== {doc.title} ===\n{doc.extracted_text[:8000]}"  # Limit per doc
            )

        return "\n\n".join(context_parts)

    def build_conversation_history(self):
        """Get recent chat messages for context"""
        messages = ChatMessage.objects.order_by("-created_at")[:20]
        messages = list(reversed(messages))

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def send_message(self, user_message: str) -> str:
        """
        Send message to Claude with document context.
        Returns assistant's response.
        """

        # Save user message
        ChatMessage.objects.create(role="user", content=user_message)

        # Build system prompt with document context
        document_context = self.build_context_from_documents()
        system_prompt = f"""
        You are a VOIP and SIP protocol expert assitant.

        You have access to the following documentation:
        {document_context}

        Use this documentation to provide accurate, detailed answers about VoIP, SIP, FreeSWITCH, and related telecommunications topics. When answering:
            - Reference specific sections from the docs when relevant
            - Provide practical examples
            - Explain technical concepts clearly
            - If the answer isn't in the docs, say so and provide general knowledge
        """

        # Get conversation history
        conversation_history = self.build_conversation_history()

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=conversation_history,
            max_tokens=1000,
        )

        # Extract assistant's response
        assistant_response = response.content[0].text

        # Save assistant's response
        ChatMessage.objects.create(role="assistant", content=assistant_response)

        return assistant_response
