from flask import Blueprint, jsonify
from storage.db import list_scans, get_scan

history_bp = Blueprint("history", __name__)


@history_bp.get("/history")
def history():
    return jsonify({"items": list_scans()})


@history_bp.get("/history/<int:scan_id>")
def scan_detail(scan_id):
    result = get_scan(scan_id)
    if not result:
        return jsonify({"error": "Scan not found"}), 404
    result["scan_id"] = scan_id
    return jsonify(result)
