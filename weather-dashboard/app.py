import streamlit as st
import pandas as pd
from dataclasses import dataclass

# 클래스 선언
@dataclass
class Weather:
    date: str
    weather_am: str
    weather_pm: str
    temperature_am: float
    temperature_pm: float
    rainchance_am: float
    rainchance_pm: float

    def as_dict(self):
        return {
            "날짜": self.date,
            "날씨(오전)": self.weather_am,
            "날씨(오후)": self.weather_pm,
            "기온(오전)": self.temperature_am,
            "기온(오후)": self.temperature_pm,
            "강수확률(오전)%": self.rainchance_am,
            "강수확률(오후)%": self.rainchance_pm,
            "평균기온": self.avg_temp(),
            "평균강수확률(%)": self.avg_rainchance(),
        }
    
    def avg_temp(self):
        return (self.temperature_am+self.temperature_pm)/2
    
    def avg_rainchance(self):
        return (self.rainchance_am+self.rainchance_pm)/2
    
    def compare_temp(self, anotherday: "Weather"):
        return (self.avg_temp()-anotherday.avg_temp())

# 데이터 로드 함수
def load_weather_data(excel_file):

    df_raw = pd.read_excel(excel_file)
    day_cols = df_raw.columns[1:]

    weather_list = []
    records_for_table = []

    for col in day_cols:
        weather_am = df_raw.iloc[0][col]  # 날씨(오전)
        weather_pm = df_raw.iloc[1][col]  # 날씨(오후)
        temp_am = df_raw.iloc[2][col] # 기온(오전)
        temp_pm = df_raw.iloc[3][col] # 기온(오후)
        rain_am = df_raw.iloc[4][col] # 강수확률(오전)
        rain_pm = df_raw.iloc[5][col] # 강수확률(오후)

        w = Weather(
            date=str(col),
            weather_am=str(weather_am),
            weather_pm=str(weather_pm),
            temperature_am=temp_am,
            temperature_pm=temp_pm,
            rainchance_am=rain_am,
            rainchance_pm=rain_pm,
        )
        weather_list.append(w)
        records_for_table.append(w.as_dict())

    df_w_list = pd.DataFrame(records_for_table)

    return weather_list, df_w_list

# 홈페이지 구성
st.title("날씨 홈페이지")
st.write("---")

# 날씨 엑셀 파일 업로드
uploaded_file = st.file_uploader(
    "날씨 엑셀 파일을 업로드하세요 (.xlsx)",
    type="xlsx"
)

if uploaded_file is None:
    st.info("None")
else:
    # 자료 수집
    weather_list, df_w_list = load_weather_data(uploaded_file)
    weather_by_date = {w.date: w for w in weather_list} # 날짜별로 정리
    date_options = list(weather_by_date.keys()) # 날짜들 모음

    st.subheader("전체 자료")
    st.dataframe(df_w_list, use_container_width=True)
    st.write("---")

    # 날짜별 상세 보기
    st.subheader("날짜별 상세 보기")
    
    selected_date = st.selectbox("어느 날짜를 볼까요?", date_options, index=0)

    w_sel = weather_by_date[selected_date]

    st.markdown(f"*** {selected_date} 상세")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**오전**")
        st.write(f"- 날씨: {w_sel.weather_am}")
        st.write(f"- 기온: {w_sel.temperature_am} °C")
        st.write(f"- 강수확률: {w_sel.rainchance_am} %")

    with col2:
        st.markdown("**오후**")
        st.write(f"- 날씨: {w_sel.weather_pm}")
        st.write(f"- 기온: {w_sel.temperature_pm} °C")
        st.write(f"- 강수확률: {w_sel.rainchance_pm} %")

    with col3:
        st.markdown("**하루 평균**")
        avg_t = w_sel.avg_temp()
        avg_r = w_sel.avg_rainchance()
        st.write(f"- 평균 기온: {avg_t} °C")
        st.write(f"- 평균 강수확률: {avg_r} %")

    st.write("---")

    # 두 날짜 평균 기온 비교
    st.subheader("두 날짜 평균 기온 비교")

    colA, colB = st.columns(2)

    date_a = colA.selectbox("날짜 A", date_options, index=0)
    date_b = colB.selectbox("날짜 B", date_options, index=1)

    w_a = weather_by_date[date_a]
    w_b = weather_by_date[date_b]

    diff = w_a.compare_temp(w_b)  # A 평균기온 - B 평균기온

    avg_a = w_a.avg_temp()
    avg_b = w_b.avg_temp()

    st.markdown("**결과**")
    st.write(f"A({date_a}) 평균 기온: {avg_a} °C")
    st.write(f"B({date_b}) 평균 기온: {avg_b} °C")

    if diff > 0:
        msg = f"{date_a} 가 {date_b} 보다 평균 {diff:.1f} °C 더 따뜻합니다."
    elif diff < 0:
        msg = f"{date_a} 가 {date_b} 보다 평균 {abs(diff):.1f} °C 더 선선합니다."
    else:
        msg = f"{date_a} 와 {date_b} 의 평균 기온은 동일합니다."

    st.success(
        f"평균 기온 차이 (A - B): {diff:.1f} °C\n\n{msg}"
    )
