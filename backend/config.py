import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
DB_PATH = os.path.join(BASE_DIR, "storage", "scans.db")
MAX_UPLOAD_SIZE = 8 * 1024 * 1024  # 8 MB
ALLOWED_EMAIL_EXTENSIONS = {".eml", ".txt"}
ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".docm", ".xls", ".xlsx", ".xlsm",
    ".zip", ".rar", ".7z", ".js", ".vbs", ".ps1", ".exe", ".bat",
    ".cmd", ".scr", ".html", ".htm", ".txt", ".png", ".jpg", ".jpeg"
}
