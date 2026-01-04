from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Document, ChatMessage
from .chat_service import VOIPChatService
from .utils import extract_text_from_pdf


def index(request):
    """Main chat interface"""
    documents = Document.objects.all()
    chat_messages = ChatMessage.objects.all()

    return render(
        request,
        "chat/index.html",
        {
            "documents": documents,
            "chat_messages": chat_messages,
        },
    )


@require_http_methods(["POST"])
def upload_document(request):
    """Handle PDF upload"""
    if "document" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES["document"]
    title = request.POST.get("title", file.name)

    # Create document record
    doc = Document.objects.create(title=title, file=file)

    # Extract text
    doc.extracted_text = extract_text_from_pdf(doc.file.path)
    doc.save()

    return redirect("index")


@require_http_methods(["POST"])
def send_message(request):
    """Send message to Claude"""
    user_message = request.POST.get("message", "").strip()

    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # Send message to Claude
    chat_service = VOIPChatService()
    assistant_response = chat_service.send_message(user_message)

    return JsonResponse(
        {"user_message": user_message, "assistant_response": assistant_response}
    )


def clear_chat(request):
    """Clear conversation history"""
    if request.method == "POST":
        ChatMessage.objects.all().delete()
    return redirect("index")
