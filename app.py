from flask import Flask, request, jsonify
from functions import do_login, fill_only

app = Flask(__name__)


@app.route("/auto-login", methods=["POST"])
def auto_login_route():
    """
    POST JSON:
    {
      "url": "https://example.com/login",
      "username": "myuser",
      "password": "mypass",
      "user_field_id": "username",
      "pass_field_id": "password",
      "login_button_selector": "button[type=submit]",
      "wait_time": 15,
      "headless": true
    }
    """
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
    return jsonify(res), (200 if res["ok"] else 500)


@app.route("/auto-fill", methods=["POST"])
def auto_fill_route():
    """
    POST JSON:
    {
      "url": "https://example.com/login",
      "username": "myuser",
      "password": "mypass",
      "user_field_id": "username",
      "pass_field_id": "password",
      "wait_time": 15,
      "headless": true
    }
    """
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
    return jsonify(res), (200 if res["ok"] else 500)


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)