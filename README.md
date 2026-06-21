# MeetPick

`app.py` 없이 실행하는 버전입니다.  
VS Code Live Server로 `index.html`을 열면 바로 실행됩니다.

## 실행 방법

1. VS Code에서 이 폴더를 엽니다.
2. `index.html`을 우클릭합니다.
3. `Open with Live Server`를 누릅니다.
4. 주소가 아래처럼 뜨면 정상입니다.

```txt
http://127.0.0.1:5500/index.html
```

또는

```txt
http://127.0.0.1:5500
```

## 파일 구조

```txt
meetpick_5500_index_python_logic/
├── index.html
├── style.css
├── logic.py
└── README.md
```

## 역할

- `index.html`: 화면 구조
- `style.css`: 디자인
- `logic.py`: 방 생성, 참여자 저장, 평균 계산, 공통 날짜 계산

## 참고

브라우저에서 Python을 실행하기 위해 Brython을 사용합니다.  
처음 실행할 때 인터넷 연결이 필요할 수 있습니다.
