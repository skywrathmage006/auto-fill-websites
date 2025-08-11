from flask import Flask, request, jsonify
from functions import do_login, fill_only

app = Flask(__name__)


@app.route("/auto-login", methods=["POST"])
def auto_login_route():
    """Full login flow — fills and clicks submit."""
    data = request.get_json(silent=True) or {}
    required = ["url", "username", "password", "user_field_id", "pass_field_id", "login_button_selector"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    res = do_login(
        url=data["url"],
        username=data["username"],
        password=data["password"],
        user_field_id=data["user_field_id"],
        pass_field_id=data["pass_field_id"],
        login_button_selector=data["login_button_selector"],
        wait_time=int(data.get("wait_time", 15)),
        headless=bool(data.get("headless", True)),
    )
    status = 200 if res.get("ok") else 500
    return jsonify(res), status


@app.route("/auto-fill", methods=["POST"])
def auto_fill_route():
    """Only open URL and fill in credentials — no login click."""
    data = request.get_json(silent=True) or {}
    required = ["url", "username", "password", "user_field_id", "pass_field_id"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"ok": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    res = fill_only(
        url=data["url"],
        username=data["username"],
        password=data["password"],
        user_field_id=data["user_field_id"],
        pass_field_id=data["pass_field_id"],
        wait_time=int(data.get("wait_time", 15)),
        headless=bool(data.get("headless", True)),
    )
    status = 200 if res.get("ok") else 500
    return jsonify(res), status


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
