import waitress
from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置上传目录
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 存储 task_id 和文件路径的映射
task_map = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    try:
        # 生成唯一任务 ID
        task_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(upload_path)

        # 读取并处理数据
        df = pd.read_csv(upload_path)
        processed_df = df

        # 保存处理后的文件
        processed_filename = f"processed_{original_filename}"
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
        processed_df.to_csv(processed_path, index=False)

        # 存储 task_id 和文件路径的映射
        task_map[task_id] = processed_path

        return jsonify({
            "task_id": task_id,
            "message": "File uploaded and processed successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    file_path = task_map.get(task_id)
    if not file_path:
        return jsonify({"error": "Task not found"}), 404

    if not os.path.exists(file_path):
        return jsonify({"error": "Processed file not found"}), 404

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path),
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    # waitress.run(app)
    # waitress.run(app, host='172.22.132.3', port=8080)