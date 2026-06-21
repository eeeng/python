from flask import Flask, render_template, request, jsonify
from pathlib import Path
from datetime import datetime
import json
import uuid


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"

app = Flask(__name__)


def load_data():
    if not DATA_FILE.exists():
        return {
            "rooms": {},
            "participants": {}
        }

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def make_room_id():
    return str(uuid.uuid4())[:6]


def create_room(title):
    data = load_data()
    room_id = make_room_id()

    while room_id in data["rooms"]:
        room_id = make_room_id()

    data["rooms"][room_id] = {
        "title": title,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    data["participants"][room_id] = {}
    save_data(data)

    return room_id


def get_room(room_id):
    data = load_data()
    return data["rooms"].get(room_id)


def get_participants(room_id):
    data = load_data()
    return data["participants"].get(room_id, {})


def parse_schedule(schedule_text):
    words = schedule_text.split()

    if len(words) == 0:
        raise ValueError("가능한 일정을 입력해 주세요.")

    if len(words) % 2 != 0:
        raise ValueError("날짜와 시간을 한 쌍으로 입력해 주세요.")

    schedules = []

    for i in range(0, len(words), 2):
        date = words[i]
        time_text = words[i + 1]

        if not time_text.endswith("시"):
            raise ValueError("시간은 13시, 14시처럼 입력해 주세요.")

        try:
            hour = int(time_text.replace("시", ""))
        except ValueError:
            raise ValueError("시간 형식이 올바르지 않습니다.")

        if hour < 0 or hour > 24:
            raise ValueError("시간은 0시부터 24시 사이로 입력해 주세요.")

        schedules.append(f"{date} {hour}시")

    return schedules


def add_participant(room_id, name, schedule_text):
    data = load_data()

    if room_id not in data["rooms"]:
        raise ValueError("존재하지 않는 방입니다.")

    if not name:
        raise ValueError("이름을 입력해 주세요.")

    if name in data["participants"][room_id]:
        raise ValueError(f"{name}님은 이미 등록되어 있습니다.")

    schedules = parse_schedule(schedule_text)
    data["participants"][room_id][name] = schedules
    save_data(data)


def delete_participant(room_id, name):
    data = load_data()

    if room_id in data["participants"]:
        if name in data["participants"][room_id]:
            del data["participants"][room_id][name]
            save_data(data)


def count_schedules(participants):
    total = 0

    for schedules in participants.values():
        total += len(schedules)

    return total


def get_room_data(room_id):
    room = get_room(room_id)

    if room is None:
        raise ValueError("방을 찾을 수 없습니다.")

    participants = get_participants(room_id)

    return {
        "room_id": room_id,
        "room": room,
        "participants": participants,
        "participant_count": len(participants),
        "schedule_count": count_schedules(participants)
    }


def analyze_room(room_id):
    participants = get_participants(room_id)

    if not participants:
        return {
            "success": False,
            "message": "아직 등록된 참여자가 없습니다.",
            "common_days": [],
            "results": []
        }

    day_sets = []

    for schedules in participants.values():
        days = set()

        for schedule in schedules:
            day = schedule.split()[0]
            days.add(day)

        day_sets.append(days)

    common_days = day_sets[0]

    for days in day_sets[1:]:
        common_days = common_days.intersection(days)

    if not common_days:
        return {
            "success": False,
            "message": "모두 가능한 공통 날짜가 없습니다.",
            "common_days": [],
            "results": []
        }

    results = []

    for day in sorted(common_days):
        hours = []

        for schedules in participants.values():
            for schedule in schedules:
                if schedule.startswith(day):
                    hour_text = schedule.split()[1]
                    hour = int(hour_text.replace("시", ""))
                    hours.append(hour)

        average = sum(hours) / len(hours)
        recommended = round(average)

        results.append({
            "day": day,
            "hours": hours,
            "average": round(average, 1),
            "recommended": recommended,
            "text": f"{day} {recommended}시"
        })

    return {
        "success": True,
        "message": "가능한 시간을 찾았습니다.",
        "common_days": sorted(list(common_days)),
        "results": results
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/rooms", methods=["POST"])
def api_create_room():
    body = request.get_json(silent=True) or {}
    title = body.get("title", "").strip()

    if not title:
        return jsonify({
            "success": False,
            "message": "약속 이름을 입력해 주세요."
        }), 400

    room_id = create_room(title)

    return jsonify({
        "success": True,
        "data": get_room_data(room_id)
    })


@app.route("/api/rooms/<room_id>", methods=["GET"])
def api_get_room(room_id):
    try:
        room_data = get_room_data(room_id)
    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    return jsonify({
        "success": True,
        "data": room_data
    })


@app.route("/api/rooms/<room_id>/participants", methods=["POST"])
def api_add_participant(room_id):
    body = request.get_json(silent=True) or {}

    name = body.get("name", "").strip()
    schedule_text = body.get("schedule_text", "").strip()

    try:
        add_participant(room_id, name, schedule_text)
        room_data = get_room_data(room_id)
    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    return jsonify({
        "success": True,
        "message": "일정이 저장되었습니다.",
        "data": room_data
    })


@app.route("/api/rooms/<room_id>/participants/<name>", methods=["DELETE"])
def api_delete_participant(room_id, name):
    delete_participant(room_id, name)

    try:
        room_data = get_room_data(room_id)
    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    return jsonify({
        "success": True,
        "data": room_data
    })


@app.route("/api/rooms/<room_id>/result", methods=["GET"])
def api_result(room_id):
    if get_room(room_id) is None:
        return jsonify({
            "success": False,
            "message": "방을 찾을 수 없습니다."
        }), 404

    return jsonify({
        "success": True,
        "data": analyze_room(room_id)
    })


@app.route("/api/reset", methods=["POST"])
def api_reset():
    save_data({
        "rooms": {},
        "participants": {}
    })

    return jsonify({
        "success": True
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5500, debug=True)
