import csv
from io import StringIO
import os
import uuid
import logging
from datetime import datetime
from flask import Flask, Response, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from docx_parser import parse_docx      
from parse import generate_html          
from pdf_generator import generate_pdf   


app = Flask(__name__)
app.secret_key = 'dev-key-12345'  

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'docx'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vacancies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  



SMTP_CONFIG = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'user': 'mamayv99@gmail.com',  
    'password': 'hmie lqne svug kxna'  
}

MANAGER_EMAIL = 'kovaleria0307@gmail.com'  
BASE_URL = 'http://localhost:5002'     



db = SQLAlchemy(app)

class Vacancy(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    salary = db.Column(db.String(50))
    employment_type = db.Column(db.String(50))
    requirements = db.Column(db.Text)
    benefits = db.Column(db.Text)
    contact_email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Vacancy {self.title}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.String(36), db.ForeignKey('vacancy.id'))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='new')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vacancy = db.relationship('Vacancy', backref='applications')



def send_email_with_pdf(subject, body, to_emails, pdf_path, from_email, smtp_config, job_id, base_url=None):
    """Отправка email с PDF и кнопками действий"""
    try:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication
        import smtplib

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        
        html = f"""
        <html>
            <body>
                <p>{body}</p>
                <p>Действия:</p>
                <div>
                    <a href="{base_url}/approve/{job_id}" 
                       style="background: #4CAF50; color: white; padding: 10px; text-decoration: none; margin-right: 10px;">
                       ✓ Одобрить
                    </a>
                    <a href="{base_url}/reject/{job_id}" 
                       style="background: #f44336; color: white; padding: 10px; text-decoration: none;">
                       ✗ Отклонить
                    </a>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))
        
        
        with open(pdf_path, 'rb') as f:
            part = MIMEApplication(f.read(), _subtype="pdf")
            part.add_header('Content-Disposition', 'attachment', filename='vacancy.pdf')
            msg.attach(part)
      
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['user'], smtp_config['password'])
            server.send_message(msg)
            
        return True
    except Exception as e:
        logging.error(f"Ошибка отправки email: {str(e)}")
        return False



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не найден', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('Не выбран файл', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Недопустимый формат файла. Только .docx', 'error')
            return redirect(request.url)
        
        try:
            
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            file.save(temp_path)
            
            data = parse_docx(temp_path)
            if not data.get('название вакансии'):
                flash('Не найдено название вакансии', 'error')
                return redirect(request.url)
            
            html_content = generate_html(data)
            pdf_filename = f"vacancy_{uuid.uuid4()}.pdf"
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            generate_pdf(html_content, pdf_path)
            
            job_id = str(uuid.uuid4())
            new_vacancy = Vacancy(
                id=job_id,
                title=data.get('название вакансии'),
                company=data.get('компания'),
                location=data.get('локация'),
                description=data.get('описание'),
                salary=data.get('зарплатная вилка'),
                employment_type=data.get('вид занятости'),
                requirements='\n'.join(data.get('требования', [])),
                benefits='\n'.join(data.get('преимущества', [])),
                contact_email=data.get('контактный email'),
                status='pending'
            )
            db.session.add(new_vacancy)
            db.session.commit()
            
            email_sent = send_email_with_pdf(
                subject=f"Новая вакансия: {data['название вакансии']}",
                body=f"Требуется проверка вакансии от {data.get('компания', '')}",
                to_emails=[MANAGER_EMAIL],
                pdf_path=pdf_path,
                from_email=SMTP_CONFIG['user'],
                smtp_config=SMTP_CONFIG,
                job_id=job_id,
                base_url=BASE_URL
            )
            
            if not email_sent:
                raise Exception("Не удалось отправить email подтверждения")
            
            flash('Вакансия успешно отправлена на утверждение', 'success')
            return redirect(url_for('success', job_title=data['название вакансии']))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Ошибка обработки: {str(e)}")
            flash(f'Ошибка обработки: {str(e)}', 'error')
            return redirect(request.url)
        finally:
            
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            if 'pdf_path' in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    return render_template('upload.html')



@app.route('/approve/<job_id>', methods=['GET', 'POST'])
def approve_vacancy(job_id):
    vacancy = Vacancy.query.get(job_id)
    if vacancy:
        vacancy.status = 'approved'
        vacancy.published_at = datetime.utcnow()
        db.session.commit()
        flash('Вакансия одобрена', 'success')
        return render_template('approve_success.html', vacancy=vacancy)
    return redirect(url_for('pending_vacancies'))



@app.route('/reject/<job_id>', methods=['GET', 'POST'])
def reject_vacancy(job_id):
    vacancy = Vacancy.query.get(job_id)
    if vacancy:
        db.session.delete(vacancy)
        db.session.commit()
        flash('Вакансия отклонена', 'success')
        return render_template('reject_success.html', vacancy=vacancy)
    return redirect(url_for('pending_vacancies'))



@app.route('/apply/<job_id>', methods=['POST'])
def apply_for_job(job_id):
    vacancy = Vacancy.query.get(job_id)
    if not vacancy:
        flash('Вакансия не найдена', 'error')
        return redirect(url_for('show_vacancies'))

    try:
        application = Application(
            vacancy_id=job_id,
            name=request.form.get('name'),
            email=request.form.get('email'),
            message=request.form.get('message')
        )
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('application_sent'))
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при отправке отклика', 'error')
        return redirect(url_for('show_vacancies'))
    
    

@app.route('/delete_vacancy/<job_id>', methods=['POST'])
def delete_vacancy(job_id):
    if request.method == 'POST':
        vacancy = Vacancy.query.get(job_id)
        if not vacancy:
            flash('Вакансия не найдена', 'error')
            return redirect(url_for('show_vacancies'))
        
        db.session.delete(vacancy)
        db.session.commit()
        flash('Вакансия успешно удалена', 'success')
    
    return redirect(url_for('show_vacancies'))



@app.route('/vacancies')
def show_vacancies():
    vacancies = Vacancy.query.filter_by(status='approved').order_by(Vacancy.published_at.desc()).all()
    return render_template('vacancies.html', vacancies=vacancies, is_hr=False)



@app.route('/administrationhr/vacancies')
def hr_vacancies():
    vacancies = Vacancy.query.filter_by(status='approved').order_by(Vacancy.published_at.desc()).all()
    return render_template('vacancies.html', vacancies=vacancies, is_hr=True)



@app.route('/administrationhr/pending')
def pending_vacancies():
    vacancies = Vacancy.query.filter_by(status='pending').order_by(Vacancy.created_at.desc()).all()
    return render_template('vacancies.html', vacancies=vacancies, is_pending=True)



@app.route('/success')
def success():
    job_title = request.args.get('job_title', 'Вакансия')
    return render_template('success.html', job_title=job_title)



@app.route('/application-sent')
def application_sent():
    return render_template('application_sent.html')



@app.route('/administrationhr')
def administrationhr():
    new_apps_count = Application.query.filter_by(status='new').count()
    return render_template('administrationhr.html', new_apps_count=new_apps_count)



@app.route('/administrationhr/applications')
def hr_applications():
    applications = Application.query.order_by(Application.created_at.desc()).all()
    return render_template('hr_applications.html', applications=applications)



@app.route('/administrationhr/applications/<status>')
def hr_applications_filtered(status):
    apps = Application.query.filter_by(status=status).all()
    return render_template('hr_applications.html', applications=apps)



@app.route('/export_applications')
def export_applications():
    apps = Application.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Вакансия', 'Имя', 'Email', 'Дата', 'Статус'])
    for app in apps:
        writer.writerow([app.vacancy.title, app.name, app.email, 
                       app.created_at.strftime('%Y-%m-%d'), app.status])
    return Response(output.getvalue(), mimetype="text/csv",
                   headers={"Content-disposition": "attachment; filename=applications.csv"})



@app.route('/update_application/<int:app_id>', methods=['POST'])
def update_application(app_id):
    application = Application.query.get(app_id)
    if application:
        application.status = request.form.get('status')
        db.session.commit()
        flash('Статус заявки обновлен', 'success')
    return redirect(url_for('hr_applications'))



@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Страница не найдена'), 404



@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message='Внутренняя ошибка сервера'), 500



def init_db():
    with app.app_context():
        db.create_all()



if __name__ == '__main__':

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        db.create_all()  
        
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='app.log'
    )
    
    app.run(debug=True, host='0.0.0.0', port=5002)
    
  