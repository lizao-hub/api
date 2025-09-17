from flask import Flask, request, jsonify, send_file
import os
import csv
import pandas as pd


app = Flask(__name__)

# 配置上传设置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 限制

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """检查文件扩展名是否为CSV"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否有文件
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # 如果用户没有选择文件，浏览器可能会提交空文件名
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 验证文件扩展名
    if not allowed_file(file.filename):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    try:
        file = request.files['file']
        filename = file.filename
        temp_path = f"uploads/{filename}"
        file.save(temp_path)  # 保存到临时路径
        df = pd.read_csv(temp_path)  # 读取文件
        # 生成处理后的文件
        processed_df = df
        output_filename = f"processed_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        processed_df.to_csv(output_path, index=False)

        # 返回处理后的 CSV 文件
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='text/csv'
        )
        # return jsonify({
        #     "message": "successful",
        # }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)