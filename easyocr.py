import easyocr

def extract_text_from_image(image_path, languages=['en', 'ru']):
    # Инициализируем EasyOCR
    reader = easyocr.Reader(languages)

    # Распознаём текст
    results = reader.readtext(image_path)

    # Извлекаем и возвращаем только текст
    extracted_text = '\n'.join([text for _, text, _ in results])
    return extracted_text
