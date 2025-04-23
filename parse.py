from jinja2 import Template

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Вакансия: {{ job_title }}</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px;
            line-height: 1.6;
        }
        h1 { 
            color: #2c3e50; 
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .section { 
            margin-bottom: 15px;
            page-break-inside: avoid;
        }
        .section-title {
            font-weight: bold;
            color: #3498db;
            display: block;
            margin-bottom: 5px;
        }
        ul, ol {
            margin-top: 5px;
            padding-left: 20px;
        }
        .salary {
            font-weight: bold;
            color: #27ae60;
        }
    </style>
</head>
<body>
    <h1>{{ job_title }}</h1>
    
    <div class="section">
        <span class="section-title">Компания:</span>
        {{ company }}
    </div>
    
    <div class="section">
        <span class="section-title">Локация:</span>
        {{ location }}
    </div>
    
    <div class="section">
        <span class="section-title">Вид занятости:</span>
        {{ employment_type }}
    </div>
    
    <div class="section">
        <span class="section-title">Требуемый опыт:</span>
        {{ experience }}
    </div>
    
    <div class="section">
        <span class="section-title">Описание:</span>
        {{ description }}
    </div>
    
    <div class="section">
        <span class="section-title">Обязанности:</span>
        <ul>
            {% for item in responsibilities %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <span class="section-title">Требования:</span>
        <ul>
            {% for item in requirements %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <span class="section-title">Зарплата:</span>
        <span class="salary">{{ salary }}</span>
    </div>
    
    <div class="section">
        <span class="section-title">Преимущества:</span>
        <ul>
            {% for item in benefits %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <span class="section-title">Контактный email:</span>
        {{ contact_email }}
    </div>
    
    <div class="section">
        <span class="section-title">Срок подачи:</span>
        {{ deadline }}
    </div>
    
    <div class="section">
        <span class="section-title">Испытательный срок:</span>
        {{ probation }}
    </div>
</body>
</html>
"""


def generate_html(data):
    mapping = {
        'название вакансии': 'job_title',
        'компания': 'company',
        'локация': 'location',
        'вид занятости': 'employment_type',
        'стаж работы': 'experience',
        'описание': 'description',
        'обязанности': 'responsibilities',
        'требования': 'requirements',
        'зарплатная вилка': 'salary',
        'преимущества': 'benefits',
        'контактный email': 'contact_email',
        'срок подачи': 'deadline',
        'испытательный срок': 'probation'
    }
    
    standardized_data = {}
    for ru_key, en_key in mapping.items():
        if ru_key in data:
            standardized_data[en_key] = data[ru_key]
    
    template = Template(HTML_TEMPLATE)
    return template.render(standardized_data)