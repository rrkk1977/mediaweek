import streamlit as st
import pandas as pd
import os
import re

# 엑셀 데이터 불러오기 (GitHub 업로드 파일 사용)
file_path = "mediaweek.xlsx"
df = pd.read_excel(file_path)

# 날짜 형식을 'YYYY-MM-DD'로 변환하여 시간 제거
df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

# 구글 드라이브 링크 변환 함수
def convert_drive_link(url):
    match = re.search(r'd/([a-zA-Z0-9_-]+)/view', str(url))
    if match:
        return f"https://drive.google.com/uc?id={match.group(1)}"
    return url

df['Image URL'] = df['Image URL'].apply(convert_drive_link)

# 이미지 경로 수정 (GitHub에 업로드된 이미지 사용)
GITHUB_REPO_URL = "https://raw.githubusercontent.com/rrkk1977/mediaweek/main/image/"
def get_image_url(filename):
    if pd.notna(filename) and isinstance(filename, str):
        return GITHUB_REPO_URL + filename
    return None

df['Image URL'] = df['file'].apply(get_image_url)

# 페이지 레이아웃 설정
st.set_page_config(layout="centered")

# 페이지 제목 및 폰트 적용
st.title("📊 미디어 동향 보고")

# ─────────────────────────────────────────────
# Session state 초기화
# ─────────────────────────────────────────────
if 'search_active' not in st.session_state:
    st.session_state.search_active = False
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1
if 'search_input' not in st.session_state:
    st.session_state.search_input = ""

# ─────────────────────────────────────────────
# 주차 선택 및 페이지 필터 (NaN 제거)
# ─────────────────────────────────────────────
week_options = df['Date'].dropna().drop_duplicates().sort_values(ascending=False).tolist()
selected_week = st.selectbox("주차 선택", week_options, key="selected_week")

filtered_df = df[df['Date'] == selected_week]
max_page = len(filtered_df) if not filtered_df.empty else 1

default_page = st.session_state.page_number if st.session_state.page_number <= max_page else 1
page_number = st.number_input("페이지", min_value=1, max_value=max_page, value=default_page, step=1)
st.session_state.page_number = page_number

# ─────────────────────────────────────────────
# 검색 영역: 토글 버튼 (검색 ↔ 검색 해제)
# ─────────────────────────────────────────────
st.session_state.search_input = st.text_input("검색어 입력", value=st.session_state.search_input)
search_button_label = "검색 해제" if st.session_state.search_active else "검색"
if st.button(search_button_label):
    if st.session_state.search_active:
        st.session_state.search_active = False
        st.session_state.search_query = ""
        st.session_state.page_number = 1
        st.session_state.search_input = ""
    else:
        if st.session_state.search_input.strip():
            st.session_state.search_active = True
            st.session_state.search_query = st.session_state.search_input.strip()
        else:
            st.info("검색어를 입력해주세요.")

# ─────────────────────────────────────────────
# 콘텐츠 출력
# ─────────────────────────────────────────────
if st.session_state.search_active:
    search_results = df[
        df['Title'].str.contains(st.session_state.search_query, case=False, na=False) |
        df['Contents'].str.contains(st.session_state.search_query, case=False, na=False)
    ]
    st.markdown("### 검색 결과")
    if search_results.empty:
        st.info("검색 결과가 없습니다.")
    else:
        for idx, row in search_results.iterrows():
            st.markdown(
                f"""
                <div style='border: 2px solid #ddd; padding: 20px; margin: 20px auto; border-radius: 10px;'>
                    <h4 style='text-align: center;'>{row['Media']}</h4>
                    <h6 style='text-align: center; font-size:0.8em; color:gray;'>[{row['Date']}]</h6>
                    <h3>{row['Title']}</h3>
                    <p>{row['Contents']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if pd.notna(row['Image URL']):
                st.image(row['Image URL'], caption=row['Title'], use_column_width=True)
else:
    if filtered_df.empty:
        st.warning("선택한 주차에 해당하는 데이터가 없습니다.")
    else:
        selected_row = filtered_df.iloc[st.session_state.page_number - 1]
        st.markdown(
            f"""
            <div style='border: 2px solid #ddd; padding: 20px; margin: 20px auto; border-radius: 10px;'>
                <h4 style='text-align: center;'>{selected_row['Media']}</h4>
                <h6 style='text-align: center; font-size:0.8em; color:gray;'>[{selected_row['Date']}]</h6>
                <h3>{selected_row['Title']}</h3>
                <p>{selected_row['Contents']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if pd.notna(selected_row['Image URL']):
            st.image(selected_row['Image URL'], caption=selected_row['Title'], use_column_width=True)

        st.write(f"페이지 {st.session_state.page_number} / {max_page}")
