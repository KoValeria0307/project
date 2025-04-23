from docx import Document

def parse_docx(file_path):
    doc = Document(file_path)
    data = {}
    current_key = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        if not text or '---' in text:
            continue
        
        # Определяем возможные ключи
        possible_keys = {
            'название вакансии': 'название вакансии',
            'компания': 'компания',
            'локация': 'локация',
            'вид занятости': 'вид занятости',
            'стаж работы': 'стаж работы',
            'описание': 'описание',
            'обязанности': 'обязанности',
            'требования': 'требования',
            'зарплатная вилка': 'зарплатная вилка',
            'преимущества': 'преимущества',
            'контактный email': 'контактный email',
            'срок подачи': 'срок подачи',
            'испытательный срок': 'испытательный срок'
        }
        
        # Проверяем, является ли текст ключом
        found_key = None
        for possible_key in possible_keys:
            if text.lower() == possible_key.lower():
                found_key = possible_keys[possible_key]
                break
                
        if found_key:
            current_key = found_key
            data[current_key] = ""  # Инициализируем пустую строку
        elif current_key:
            # Добавляем текст к текущему ключу
            if data[current_key]:
                data[current_key] += "\n" + text
            else:
                data[current_key] = text
    
    # Обрабатываем списковые поля
    list_fields = ['обязанности', 'требования', 'преимущества']
    for field in list_fields:
        if field in data:
            # Разбиваем по строкам и убираем пустые элементы
            items = [item.strip() for item in data[field].split('\n') if item.strip()]
            data[field] = items
    
    return data