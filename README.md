# MeetPick

Flask로 실행하는 일정 조율 웹사이트입니다.

## 실행 방법

터미널에서 아래 명령어를 입력합니다.

```bash
python app.py
```

브라우저에서 아래 주소로 접속합니다.

```txt
http://127.0.0.1:5500
```

## 주의

VS Code Live Server도 5500번 포트를 사용할 수 있습니다.  
이 프로젝트를 실행할 때는 Live Server를 꺼두는 것이 좋습니다.

## 파일 구조

```txt
meetpick_flask_5500_final/
├── app.py
├── data.json
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## 기능

- 일정 조율 방 생성
- 참여자 일정 저장
- 참여자 삭제
- 참여 현황 확인
- 공통 날짜 계산
- 평균 시간 계산
- 추천 시간 출력
