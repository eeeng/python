from browser import document, window, html
import json
import random
import string
import time


STORAGE_KEY = "meetpick_5500_data_v1"

current_room_id = None
current_room_data = None


def get_el(element_id):
    return document[element_id]


def load_data():
    saved = window.localStorage.getItem(STORAGE_KEY)

    if not saved:
        return {
            "rooms": {},
            "participants": {}
        }

    try:
        data = json.loads(saved)

        if "rooms" not in data or "participants" not in data:
            raise ValueError

        return data
    except Exception:
        return {
            "rooms": {},
            "participants": {}
        }


def save_data(data):
    window.localStorage.setItem(STORAGE_KEY, json.dumps(data, ensure_ascii=False))


def create_room_id():
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(6))


def create_room(title):
    data = load_data()
    room_id = create_room_id()

    while room_id in data["rooms"]:
        room_id = create_room_id()

    data["rooms"][room_id] = {
        "title": title,
        "created_at": time.strftime("%Y-%m-%d %H:%M")
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


def parse_schedule_input(schedule_text):
    raw_inputs = schedule_text.split()

    if len(raw_inputs) == 0:
        raise ValueError("일정을 하나 이상 입력해야 합니다.")

    if len(raw_inputs) % 2 != 0:
        raise ValueError("날짜와 시간이 쌍으로 입력되지 않았습니다.")

    schedules = []

    for i in range(0, len(raw_inputs), 2):
        day = raw_inputs[i]
        time_text = raw_inputs[i + 1]

        if not time_text.endswith("시"):
            raise ValueError("시간은 13시, 14시처럼 '시'를 붙여 입력해야 합니다.")

        try:
            hour = int(time_text.replace("시", ""))
        except Exception:
            raise ValueError("시간 형식이 올바르지 않습니다. 예: 13시")

        if hour < 0 or hour > 24:
            raise ValueError("시간은 0시부터 24시 사이로 입력해야 합니다.")

        schedules.append(f"{day} {hour}시")

    return schedules


def add_participant_to_room(room_id, name, schedule_text):
    data = load_data()

    if room_id not in data["rooms"]:
        raise ValueError("존재하지 않는 방입니다.")

    if not name:
        raise ValueError("이름을 공백으로 입력할 수 없습니다.")

    if name in data["participants"][room_id]:
        raise ValueError(f"'{name}'님은 이미 일정을 입력했습니다.")

    schedules = parse_schedule_input(schedule_text)
    data["participants"][room_id][name] = schedules
    save_data(data)

    return schedules


def delete_participant_from_room(room_id, name):
    data = load_data()

    if room_id in data["participants"]:
        if name in data["participants"][room_id]:
            del data["participants"][room_id][name]
            save_data(data)


def get_total_schedule_count(participants):
    total = 0

    for schedules in participants.values():
        total += len(schedules)

    return total


def build_room_response(room_id):
    room = get_room(room_id)

    if room is None:
        raise ValueError("존재하지 않는 방입니다.")

    participants = get_participants(room_id)

    return {
        "room_id": room_id,
        "room": room,
        "participants": participants,
        "participant_count": len(participants),
        "total_schedule_count": get_total_schedule_count(participants)
    }


def analyze_schedule(room_id):
    participants = get_participants(room_id)

    if not participants:
        return {
            "success": False,
            "message": "참여한 사용자가 없어 계산할 수 없습니다.",
            "common_days": [],
            "results": []
        }

    user_day_sets = []

    for name, schedules in participants.items():
        day_set = set()

        for item in schedules:
            day = item.split()[0]
            day_set.add(day)

        user_day_sets.append(day_set)

    common_days = user_day_sets[0]

    for day_set in user_day_sets[1:]:
        common_days = common_days.intersection(day_set)

    if not common_days:
        return {
            "success": False,
            "message": "모두 겹치는 날짜가 없어서 약속 잡기가 불가능합니다.",
            "common_days": [],
            "results": []
        }

    results = []

    for best_day in sorted(common_days):
        collected_times = []

        for name, schedules in participants.items():
            for item in schedules:
                if item.startswith(best_day):
                    time_text = item.split()[1]
                    hour = int(time_text.replace("시", ""))
                    collected_times.append(hour)

        average_time = sum(collected_times) / len(collected_times)
        recommended_time = int(average_time + 0.5)

        results.append({
            "day": best_day,
            "times": collected_times,
            "average_time": round(average_time, 1),
            "recommended_time": recommended_time,
            "recommended_text": f"{best_day} {recommended_time}시"
        })

    return {
        "success": True,
        "message": f"모든 참여자 {len(participants)}명이 공통으로 가능한 날짜를 찾았습니다.",
        "common_days": sorted(list(common_days)),
        "results": results
    }


def show_screen(name):
    screens = ["home", "room", "add", "participants", "result"]

    for screen in screens:
        get_el(f"screen-{screen}").classList.remove("active")

    get_el(f"screen-{name}").classList.add("active")


def set_message(element_id, text, kind=""):
    message = get_el(element_id)
    message.textContent = text
    message.className = f"form-message {kind}"


def show_toast(text):
    toast = get_el("toast")
    toast.textContent = text
    toast.classList.add("show")

    def hide_toast():
        toast.classList.remove("show")

    window.setTimeout(hide_toast, 1800)


def render_room(data):
    room = data["room"]

    get_el("roomNameText").textContent = room["title"]
    get_el("roomIdText").textContent = f"방 ID: {data['room_id']}"
    get_el("roomCreatedText").textContent = f"생성 시간: {room['created_at']}"
    get_el("participantCount").textContent = str(data["participant_count"])
    get_el("slotCount").textContent = str(data["total_schedule_count"])
    get_el("shareLink").value = f"{window.location.origin}{window.location.pathname}#room={data['room_id']}"


def create_room_click(event):
    global current_room_id
    global current_room_data

    title = get_el("roomTitle").value.strip()
    set_message("homeMessage", "")

    if not title:
        set_message("homeMessage", "약속 이름을 입력해 주세요.", "error")
        get_el("roomTitle").focus()
        return

    room_id = create_room(title)
    data = build_room_response(room_id)

    current_room_id = room_id
    current_room_data = data

    window.location.hash = f"room={room_id}"

    get_el("roomTitle").value = ""
    render_room(data)
    show_screen("room")
    show_toast("방이 만들어졌습니다.")


def add_participant_click(event):
    global current_room_data

    if current_room_id is None:
        go_home()
        return

    name = get_el("participantName").value.strip()
    schedule_text = get_el("scheduleInput").value.strip()

    set_message("formMessage", "")

    try:
        add_participant_to_room(current_room_id, name, schedule_text)
        current_room_data = build_room_response(current_room_id)

        get_el("participantName").value = ""
        get_el("scheduleInput").value = ""

        set_message("formMessage", f"{name}님의 일정이 저장되었습니다.", "success")
        render_room(current_room_data)
        show_toast("일정이 저장되었습니다.")

        def move_room():
            show_screen("room")

        window.setTimeout(move_room, 450)

    except Exception as error:
        set_message("formMessage", str(error), "error")


def render_participants_screen(event=None):
    if current_room_data is None:
        go_home()
        return

    participants = current_room_data["participants"]
    list_box = get_el("participantsList")
    list_box.clear()

    if len(participants) == 0:
        card = html.ARTICLE(Class="card empty-card")
        card <= html.DIV("🕒", Class="emoji")
        card <= html.H2("아직 등록된 참여자가 없습니다.")
        card <= html.P("참여자 일정을 먼저 등록해 주세요.", Class="muted")

        button = html.BUTTON("일정 등록하러 가기", Class="primary-btn")
        button.bind("click", lambda event: show_screen("add"))
        card <= button

        list_box <= card
    else:
        for name, schedules in participants.items():
            card = html.ARTICLE(Class="card participant-card")
            head = html.DIV(Class="participant-head")
            head <= html.H2(name)

            delete_button = html.BUTTON("삭제", Class="delete-btn")
            delete_button.bind("click", make_delete_handler(name))
            head <= delete_button

            card <= head

            chips = html.DIV(Class="chips")
            for schedule in schedules:
                chips <= html.SPAN(schedule)

            card <= chips
            list_box <= card

    show_screen("participants")


def make_delete_handler(name):
    def handler(event):
        global current_room_data

        if window.confirm(f"{name}님의 일정을 삭제할까요?"):
            delete_participant_from_room(current_room_id, name)
            current_room_data = build_room_response(current_room_id)
            render_room(current_room_data)
            render_participants_screen()
            show_toast("삭제되었습니다.")

    return handler


def render_result_screen(event=None):
    if current_room_id is None:
        go_home()
        return

    result_box = get_el("resultBox")
    result_box.clear()

    analysis = analyze_schedule(current_room_id)

    if not analysis["success"]:
        result_box <= html.DIV(analysis["message"], Class="result-message error-box")

        button = html.BUTTON("일정 더 등록하기", Class="primary-btn")
        button.bind("click", lambda event: show_screen("add"))
        result_box <= button
    else:
        result_box <= html.DIV(analysis["message"], Class="result-message success-box")

        common_box = html.DIV(Class="common-days")
        common_box <= html.STRONG("공통 가능 날짜")
        common_box <= html.P(", ".join(analysis["common_days"]))
        result_box <= common_box

        result_list = html.DIV(Class="result-list")

        for item in analysis["results"]:
            card = html.ARTICLE(Class="result-item")
            card <= html.SPAN("추천 날짜")
            card <= html.H2(item["day"])
            card <= html.P("해당 날짜에 나온 시간 목록: ") + html.STRONG(str(item["times"]))
            card <= html.P("시간 평균: ") + html.STRONG(f"{item['average_time']}시")
            card <= html.P("추천 약속 시간: ") + html.STRONG(item["recommended_text"])
            result_list <= card

        result_box <= result_list

    show_screen("result")


def reset_all(event=None):
    global current_room_id
    global current_room_data

    if window.confirm("저장된 방과 참여자 정보를 모두 초기화할까요?"):
        save_data({
            "rooms": {},
            "participants": {}
        })

        current_room_id = None
        current_room_data = None
        window.location.hash = ""
        show_screen("home")
        show_toast("초기화되었습니다.")


def copy_link(event=None):
    link = get_el("shareLink").value

    try:
        window.navigator.clipboard.writeText(link)
        show_toast("공유 링크가 복사되었습니다.")
    except Exception:
        show_toast("링크를 직접 선택해서 복사해 주세요.")


def go_home(event=None):
    global current_room_id
    global current_room_data

    current_room_id = None
    current_room_data = None
    window.location.hash = ""
    show_screen("home")


def boot(event=None):
    global current_room_id
    global current_room_data

    get_el("statusText").textContent = "준비 완료"
    get_el("statusText").style.color = "#16a34a"

    hash_value = window.location.hash.replace("#", "")

    if hash_value.startswith("room="):
        room_id = hash_value.replace("room=", "")

        try:
            data = build_room_response(room_id)
            current_room_id = room_id
            current_room_data = data
            render_room(data)
            show_screen("room")
            return
        except Exception:
            window.location.hash = ""
            show_toast("방 정보를 찾을 수 없습니다.")

    show_screen("home")


get_el("createRoomBtn").bind("click", create_room_click)
get_el("saveParticipantBtn").bind("click", add_participant_click)
get_el("goParticipantsBtn").bind("click", render_participants_screen)
get_el("goResultBtn").bind("click", render_result_screen)
get_el("resetBtn").bind("click", reset_all)
get_el("copyBtn").bind("click", copy_link)

get_el("goHomeTop").bind("click", go_home)
get_el("homeBtn").bind("click", go_home)
get_el("goAddBtn").bind("click", lambda event: show_screen("add"))
get_el("backFromAddBtn").bind("click", lambda event: show_screen("room"))
get_el("backFromParticipantsBtn").bind("click", lambda event: show_screen("room"))
get_el("backFromResultBtn").bind("click", lambda event: show_screen("room"))

window.bind("hashchange", boot)

boot()
