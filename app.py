import re
import smtplib
import dns.resolver
import pandas as pd
import os
from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import uuid
from datetime import datetime
import threading

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Results')
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
tasks = {}

def generate_output_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f'Validated_emails_{timestamp}.csv'

class EmailValidator:
    def __init__(self):
        self.email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def is_valid_format(self, email):
        return re.match(self.email_regex, email) is not None
    
    def get_mx_record(self, domain):
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return str(mx_records[0].exchange)
        except:
            return None
    
    def check_smtp_connection(self, mx_server, email):
        try:
            server = smtplib.SMTP(timeout=20)
            server.connect(mx_server, 25)
            server.helo()
            server.mail('test@example.com')
            code, message = server.rcpt(email)
            server.quit()
            return "Valid" if code == 250 else "Invalid"
        except:
            return "Unknown"
    
    def validate_single_email(self, email):
        if not self.is_valid_format(email):
            return "Invalid Email Format"
        domain = email.split('@')[1]
        mx_server = self.get_mx_record(domain)
        if not mx_server:
            return "Unknown"
        return self.check_smtp_connection(mx_server, email)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_bulk_emails(file_path, task_id):
    validator = EmailValidator()
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, header=None)
        else:
            df = pd.read_excel(file_path, header=None)
    except Exception as e:
        tasks[task_id] = {'status': 'error', 'message': f"Error reading file: {str(e)}"}
        return
    
    if len(df.columns) == 0:
        tasks[task_id] = {'status': 'error', 'message': "File has no columns"}
        return
    
    emails = df[0].tolist()
    results = []
    total = len(emails)
    
    for i, email in enumerate(emails):
        try:
            if not email or pd.isna(email) or str(email).strip() == '':
                result = "Empty"
            else:
                email_str = str(email).strip()
                result = validator.validate_single_email(email_str)
            results.append((email, result))
            tasks[task_id]['progress'] = round((i+1) / total * 100, 1)
            tasks[task_id]['current'] = i+1
            tasks[task_id]['total'] = total
            tasks[task_id]['email'] = email_str
        except:
            results.append((email, "Error"))
    
    result_df = pd.DataFrame(results, columns=['Emails', 'Validation Results'])
    output_filename = generate_output_filename()
    output_path = os.path.join(app.config['RESULTS_FOLDER'], output_filename)
    try:
        result_df.to_csv(output_path, index=False)
        tasks[task_id].update({'status': 'completed', 'result_path': output_path, 'filename': output_filename})
    except Exception as e:
        tasks[task_id] = {'status': 'error', 'message': f"Error saving results: {str(e)}"}

def cleanup_old_tasks():
    current_time = datetime.now().timestamp()
    to_remove = []
    for task_id, task in tasks.items():
        if 'timestamp' in task and current_time - task['timestamp'] > 3600:
            to_remove.append(task_id)
    for task_id in to_remove:
        del tasks[task_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate_single_email():
    data = request.get_json()
    email = data.get('email', '').strip()
    if not email:
        return jsonify({'error': 'Email address is required'}), 400
    validator = EmailValidator()
    smtp_check = validator.validate_single_email(email)
    return jsonify({'email': email, 'smtp_check': smtp_check})

@app.route('/bulk-validate', methods=['POST'])
def bulk_validate():
    cleanup_old_tasks()
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload CSV or Excel files only.'}), 400
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    filename = f"upload_{timestamp}.{file_extension}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'running', 'progress': 0, 'timestamp': datetime.now().timestamp()}
    threading.Thread(target=process_bulk_emails, args=(file_path, task_id)).start()
    return jsonify({'task_id': task_id})

@app.route('/progress/<task_id>')
def get_progress(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    task = tasks[task_id]
    if task['status'] == 'completed':
        return jsonify({'status': 'completed', 'download_url': f'/download/{task["filename"]}', 'filename': task['filename']})
    elif task['status'] == 'error':
        return jsonify({'status': 'error', 'message': task['message']})
    else:
        return jsonify({'status': 'running', 'progress': task['progress'], 'current': task.get('current', 0), 'total': task.get('total', 0), 'email': task.get('email', '')})

@app.route('/download/<filename>')
def download_file(filename):
    if not filename.startswith('Validated_emails_') or not filename.endswith('.csv'):
        return jsonify({'error': 'Invalid filename'}), 404
    file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)