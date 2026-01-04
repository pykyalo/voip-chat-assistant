from django.core.management.base import BaseCommand
from chat.models import Document
from chat.utils import extract_text_from_pdf
import os


class Command(BaseCommand):
    help = "Re-extract text from PDF documents"

    def handle(self, *args, **options):
        documents = Document.objects.all()

        for doc in documents:
            if doc.file and os.path.exists(doc.file.path):
                self.stdout.write(f"Processing: {doc.title}")

                # Check if file is actually a PDF
                try:
                    with open(doc.file.path, "rb") as f:
                        header = f.read(5)
                        if header != b"%PDF-":
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Skipping {doc.title} - not a valid PDF file"
                                )
                            )
                            continue
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error reading {doc.title}: {e}")
                    )
                    continue

                # Extract text
                extracted_text = extract_text_from_pdf(doc.file.path)

                if extracted_text.startswith("Error:"):
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to extract {doc.title}: {extracted_text}"
                        )
                    )
                else:
                    doc.extracted_text = extracted_text
                    doc.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully extracted {len(extracted_text)} chars from {doc.title}"
                        )
                    )
            else:
                self.stdout.write(self.style.ERROR(f"File not found for {doc.title}"))
