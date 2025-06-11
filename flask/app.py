from quart import Quart, jsonify
from routing import reservation_bp


app = Quart(__name__)
app.register_blueprint(reservation_bp)


@app.route("/sts")
def hello():
    print("Flask + Cassandra is running!")
    return "Flask + Cassandra is asdasdarunning!"


@app.route("/add_res", methods=["POST"])
def add_reservation():
    print("Received request to add reservation")
    print("Received request to add reservation")
    return jsonify({"message": "This endpoint is not implemented yet"}), 501


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=True)
