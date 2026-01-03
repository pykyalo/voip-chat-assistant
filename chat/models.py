from django.db import models


class Document(models.Model):
    """Stores uploaded PDF documents for context"""

    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="documents/")
    extracted_text = models.TextField(blank=True)

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    """Stores conversation history"""

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
