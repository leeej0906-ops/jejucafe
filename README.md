# ☕ 제주도 카페 분석 & 지도 시각화

Streamlit · Folium · Pandas · MarkerCluster 로 만든 제주도 카페 분석/지도 앱입니다.

- **마우스 오버** → 법정동명 툴팁 표시
- **마커 클릭** → 상호명 + 도로명주소 팝업 표시 (클릭 시 툴팁은 사라짐)
- 시군구/법정동/상호명 필터, 시군구·법정동별 카페 수 차트

## 📁 파일 구성

| 파일 | 설명 |
|------|------|
| `app.py` | Streamlit 메인 앱 |
| `제주상권 .csv` | 원본 데이터 (cp949 인코딩, 파일명에 공백 포함) |
| `requirements.txt` | Python 의존 패키지 |
| `.streamlit/config.toml` | 테마 및 서버 설정 |
| `.gitignore` | Git 제외 목록 |

## 💻 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 http://localhost:8501 접속.

## 🚀 Streamlit Community Cloud 배포

1. 이 폴더 전체를 **GitHub 저장소**에 올립니다.
   - `제주상권 .csv`(약 21MB)도 반드시 함께 커밋합니다. (GitHub 파일 제한 100MB 이내라 OK)
2. https://share.streamlit.io 에 GitHub 계정으로 로그인합니다.
3. **New app → 저장소 / 브랜치 / `app.py`** 선택.
4. **Advanced settings → Python version: 3.12** 로 지정하는 것을 권장합니다.
5. **Deploy** 클릭.

### 배포 시 주의사항
- CSV 파일명에 **공백**이 있습니다(`제주상권 .csv`). 파일명을 바꾸면 `app.py`의 `CSV_PATH`도 함께 수정해야 합니다.
- 데이터가 인코딩 `cp949`(EUC-KR)이므로 `app.py`에서 `encoding="cp949"`로 읽습니다. 파일을 UTF-8로 재저장하지 마세요(또는 재저장했다면 인코딩 값도 변경).
