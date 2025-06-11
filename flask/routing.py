from quart import Blueprint, request, jsonify, render_template
from utils import session
import asyncio

reservation_bp = Blueprint("reservation", __name__)


@reservation_bp.route("/book", methods=["POST"])
async def post_route():
    data = await request.get_json()
    seat_id = data.get("seat_id")
    user = data.get("user")

    if not seat_id or not user:
        return jsonify({"error": "seat_id and user are required"}), 400

    if not isinstance(seat_id, int) or not isinstance(user, str):
        return (
            jsonify({"error": "seat_id must be an integer and user must be a string"}),
            400,
        )

    # convert seat_id to int
    seat_id = int(seat_id)

    if seat_id < 0 and seat_id > 1000:
        return jsonify({"error": "seat_id must be between 0 and 1000"}), 400

    def insert_reservation():
        future = session.execute_async(
            "INSERT INTO reservation (seat_id, user) VALUES (%s, %s) IF NOT EXISTS",
            (seat_id, user),
        )
        return future.result()

    try:
        result = await asyncio.to_thread(insert_reservation)
        if result.was_applied:
            return jsonify({"message": "Reservation added successfully"}), 201
        else:
            return jsonify({"error": "Reservation already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservation_bp.route("/book", methods=["PUT"])
async def update_reservation():
    data = await request.get_json()
    seat_id = data.get("seat_id")
    user = data.get("user")

    if not seat_id or not user:
        return jsonify({"error": "seat_id and user are required"}), 400

    if not isinstance(seat_id, int) or not isinstance(user, str):
        return (
            jsonify({"error": "seat_id must be an integer and user must be a string"}),
            400,
        )

    # convert seat_id to int
    seat_id = int(seat_id)

    if seat_id < 0 or seat_id > 108:
        return jsonify({"error": "seat_id must be between 0 and 108"}), 400

    def update_reservation_async():
        future = session.execute_async(
            "UPDATE reservation SET user = %s WHERE seat_id = %s IF EXISTS",
            (user, seat_id),
        )
        return future.result()

    try:
        result = await asyncio.to_thread(update_reservation_async)
        if result.was_applied:
            return jsonify({"message": "Reservation updated successfully"}), 201
        else:
            return jsonify({"error": "Reservation does not exist"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservation_bp.route("/", methods=["GET"])
async def get_all_reservations():
    seats = []
    for i in range(1, 109):
        seats.append(i)

    def fetch_reservations():
        future = session.execute_async("SELECT * FROM reservation")
        return future.result()

    try:
        result = await asyncio.to_thread(fetch_reservations)
        reservations = []
        selected_seats = []
        for row in result:
            reservations.append({"seat_id": row.seat_id, "user": row.user})
            selected_seats.append(row.seat_id)
        return await render_template(
            "cinema_seating.html",
            seats=seats,
            selected_seats=selected_seats,
            reservations=reservations,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reservation_bp.route("/cancel", methods=["POST"])
async def cancel_reservation():
    data = await request.get_json()
    seat_id_tab = data.get("seat_id_tab")
    print(seat_id_tab)
    if not seat_id_tab:
        return jsonify({"error": "seat_id_tav is required"}), 400

    if not isinstance(seat_id_tab, list):
        print("seat_id_tab is a list")
        return (
            jsonify({"error": "seat_id_tab must be a list"}),
            400,
        )
    if len(seat_id_tab) < 1:
        return jsonify({"error": "seat_id_tab size must be greater than 0"}), 400

    for seat_id in seat_id_tab:
        if not isinstance(seat_id, int):
            return (
                jsonify(
                    {"error": "seat_id must be an integer and user must be a string"}
                ),
                400,
            )
        if seat_id < 0 or seat_id > 108:
            return jsonify({"error": "seat_id must be between 0 and 108"}), 400

    def cancel_reservation_async():
        results = []
        for seat_id in seat_id_tab:
            query = "DELETE FROM reservation WHERE seat_id = %s IF EXISTS"
            future = session.execute_async(query, (seat_id,))
            results.append(future.result())
        return results

    try:
        result = await asyncio.to_thread(cancel_reservation_async)
        for res in result:
            if not res.was_applied:
                return jsonify({"error": "One or more reservations do not exist"}), 404

        return jsonify({"message": "Reservation cancelled successfully"}), 200
    except Exception as e:
        print("Error in cancel_reservation:", str(e))
        return jsonify({"error": str(e)}), 500
