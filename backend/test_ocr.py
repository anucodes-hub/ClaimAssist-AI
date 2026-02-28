from ocr_service import extract_text_from_pdf

text = extract_text_from_pdf("test.pdf")

print("Extracted Text:")
print(text)