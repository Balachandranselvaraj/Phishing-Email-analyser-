import os
from flask import Flask, jsonify, send_file
from flask_cors import CORS
from config import UPLOAD_DIR, REPORT_DIR, MAX_UPLOAD_SIZE
from storage.db import init_db, get_scan
from routes.analyze_routes import analyze_bp
from routes.history_routes import history_bp
from services.report_generator import generate_pdf_report


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    init_db()

    app.register_blueprint(analyze_bp, url_prefix="/api")
    app.register_blueprint(history_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Email Analyzer backend is running"})

    @app.get("/api/report/<int:scan_id>")
    def report(scan_id):
        result = get_scan(scan_id)
        if not result:
            return jsonify({"error": "Scan not found"}), 404
        path = generate_pdf_report(scan_id, result)
        return send_file(path, as_attachment=True, download_name=f"email_analysis_{scan_id}.pdf")

    @app.errorhandler(413)
    def too_large(_):
        return jsonify({"error": "File is too large. Maximum upload size is 8 MB."}), 413

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
