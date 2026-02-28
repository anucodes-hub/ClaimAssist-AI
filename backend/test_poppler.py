from pdf2image import convert_from_path

pages = convert_from_path("test.pdf", dpi=300)

for i, page in enumerate(pages):
    page.save(f"page_{i+1}.png", "PNG")

print("PDF converted and saved successfully!")