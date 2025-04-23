from weasyprint import HTML, CSS
import os

def generate_pdf(html_content, output_path="vacancy.pdf"):
    try:
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
                @top-center {
                    content: "Вакансия";
                }
                @bottom-right {
                    content: "Страница " counter(page);
                }
            }
        ''')
        

        HTML(
            string=html_content,
            base_url=os.getcwd()
        ).write_pdf(
            output_path,
            stylesheets=[css]
        )
        
        
        if os.path.getsize(output_path) < 1024:
            raise ValueError("PDF файл слишком мал")
            
        return output_path
    except Exception as e:
        print(f"Ошибка генерации PDF: {str(e)}")
        raise