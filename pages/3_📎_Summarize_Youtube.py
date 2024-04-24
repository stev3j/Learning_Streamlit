# 유튜브 동영상을 요약하고 번역하는 웹 앱

import streamlit as st
from openai import OpenAI
import os
import tiktoken
import textwrap
import deepl

# 유튜브 동영상 정보와 자막을 가져오기 위한 모듈

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from pathlib import Path
import my_data

# OpenAI 라이브러리를 이용해 텍스트를 요약하는 함수
def summarize_text(user_text, lang="en"):  # lang 인자에 영어를 기본적으로 지정
    # API 키 설정
    client = OpenAI(api_key=my_data.api_key)

    # 대화 메시지 정의
    if lang == "en":
        messages = [
            {"role": "system", "content": "You are a helpful assistant in the summary."},
            {"role": "user", "content": f"Summarize the following. \n {user_text}"}
        ]
    elif lang == "ko":
        messages = [
            {"role": "system", "content": "You are a helpful assistant in the summary."},
            {"role": "user", "content": f"다음의 내용을 한국어로 요약해 주세요 \n {user_text}"}
            #             {"role": "user", "content": f"Summarize the following in Korea. \n {user_text}"}
        ]

    # Chat Completions API 호출
    response = client.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",  # 사용할 모델 선택
        messages=messages,  # 전달할 메시지 지정
        max_tokens=2000,  # 응답 최대 토큰 수 지정
        temperature=0.3,  # 완성의 다양성을 조절하는 온도 설정
        n=1  # 생성할 완성의 개수 지정
    )
    summary = response.choices[0].message.content
    return summary


# 요약 리스트를 최종적으로 요약하는 함수
def summarize_text_final(text_list, lang='en'):
    # 리스트를 연결해 하나의 요약 문자열로 통합
    joined_summary = " ".join(text_list)

    enc = tiktoken.encoding_for_model("gpt-4-turbo-2024-04-09")
    token_num = len(enc.encode(joined_summary))  # 텍스트 문자열의 토큰 개수 구하기

    req_max_token = 2000  # 응답을 고려해 설정한 최대 요청 토큰
    final_summary = ""  # 빈 문자열로 초기화
    if token_num < req_max_token:  # 설정한 토큰보다 작을 때만 실행 가능
        # 하나로 통합한 요약문을 다시 요약
        final_summary = summarize_text(joined_summary, lang)

    return token_num, final_summary


# OpenAI 라이브러리를 이용해 영어를 한국어로 번역하는 함수
def traslate_english_to_korean_using_openAI(text):
    # API 키 설정
    client = OpenAI(api_key=my_data.api_key)

    # 대화 메시지 정의
    user_content = f"Translate the following English sentences into Korean.\n {text}"
    messages = [{"role": "user", "content": user_content}]

    # Chat Completions API 호출
    response = client.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",  # 사용할 모델 선택
        messages=messages,  # 전달할 메시지 지정
        max_tokens=2000,  # 응답 최대 토큰 수 지정
        temperature=0.3,  # 완성의 다양성을 조절하는 온도 설정
        n=1  # 생성할 완성의 개수 지정
    )

    assistant_reply = response.choices[0].message.content  # 첫 번째 응답 결과 가져오기

    return assistant_reply


# DeepL 라이브러리를 이용해 텍스트를 한국어로 번역하는 함수
def traslate_english_to_korean_using_deepL(text):
    auth_key = '7e7111d0-bfd5-4b02-83d7-425ebbfd5589'  # Deepl 인증 키
    translator = deepl.Translator(auth_key)  # translator 객체를 생성

    result = translator.translate_text(text, target_lang="KO")  # 번역 결과 객체를 result 변수에 할당

    return result.text


# 유튜브 비디오 정보를 가져오는 함수
def get_youtube_video_info(video_url):
    ydl_opts = {  # 다양한 옵션 지정
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(video_url, download=False)  # 비디오 정보 추출
        video_id = video_info['id']  # 비디오 정보에서 비디오 ID 추출
        title = video_info['title']  # 비디오 정보에서 제목 추출
        upload_date = video_info['upload_date']  # 비디오 정보에서 업로드 날짜 추출
        channel = video_info['channel']  # 비디오 정보에서 채널 이름 추출
        duration = video_info['duration_string']

    return video_id, title, upload_date, channel, duration


# 유튜브 비디오 URL에서 비디오 ID를 추출하는 함수
def get_video_id(video_url):
    video_id = video_url.split('v=')[1][:11]

    return video_id


# 유튜브 동영상 자막을 직접 가져오는 함수
def get_transcript_from_youtube(video_url, lang='en'):
    # 비디오 URL에서 비디오 ID 추출
    video_id = get_video_id(video_url)

    # 자막 리스트 가져오기
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    #     print(f"- 유튜브 비디오 ID: {video_id}")
    #     for transcript in transcript_list:
    #         print(f"- [자막 언어] {transcript.language}, [자막 언어 코드] {transcript.language_code}")

    # 자막 가져오기 (lang)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])

    text_formatter = TextFormatter()  # Text 형식으로 출력 지정
    text_formatted = text_formatter.format_transcript(transcript)

    return text_formatted


# 텍스트의 토큰 수를 계산하는 함수(모델: "gpt-3.5-turbo")
def calc_token_num(text, model="gpt-4-turbo-2024-04-09"):
    enc = tiktoken.encoding_for_model(model)
    encoded_list = enc.encode(text)  # 텍스트 인코딩해 인코딩 리스트 생성
    token_num = len(encoded_list)  # 인코딩 리스트의 길이로 토큰 개수 계산

    return token_num


# 토큰에 따라 텍스트를 나눠 분할하는 함수
def divide_text(text, token_num):
    req_max_token = 2000  # 응답을 고려해 설정한 최대 요청 토큰

    divide_num = int(token_num / req_max_token) + 1  # 나눌 계수를 계산
    divide_char_num = int(len(text) / divide_num)  # 나눌 문자 개수
    divide_width = divide_char_num + 20  # wrap() 함수로 텍스트 나눌 때 여유분 고려해 20 더함

    divided_text_list = textwrap.wrap(text, width=divide_width)

    return divide_num, divided_text_list


# 유튜브 동영상을 요약하는 함수
def summarize_youtube_video(video_url, selected_lang, trans_method):
    if selected_lang == '영어':
        lang = 'en'
    else:
        lang = 'ko'

        # 유튜브 동영상 플레이
    st.video(video_url, format='video/mp4')  # st.video(video_url) 도 동일

    # 유튜브 동영상 제목 가져오기
    _, yt_title, _, _, yt_duration = get_youtube_video_info(video_url)
    st.write(f"[제목] {yt_title}, [길이(분:초)] {yt_duration}")  # 제목 및 상영 시간출력

    # 유튜브 동영상 자막 가져오기
    yt_transcript = get_transcript_from_youtube(video_url, lang)

    # 자막 텍스트의 토큰 수 계산
    token_num = calc_token_num(yt_transcript)

    # 자막 텍스트를 분할해 리스트 생성
    div_num, divided_yt_transcripts = divide_text(yt_transcript, token_num)

    st.write("유튜브 동영상 내용 요약 중입니다. 잠시만 기다려 주세요.")

    # 분할 자막의 요약 생성
    summaries = []
    for divided_yt_transcript in divided_yt_transcripts:
        summary = summarize_text(divided_yt_transcript, lang)  # 텍스트 요약
        summaries.append(summary)

    # 분할 자막의 요약을 다시 요약     
    _, final_summary = summarize_text_final(summaries, lang)

    if selected_lang == '영어':
        shorten_num = 200
    else:
        shorten_num = 120

    shorten_final_summary = textwrap.shorten(final_summary, shorten_num, placeholder=' [..이하 생략..]')
    st.write("- 자막 요약(축약):", shorten_final_summary)  # 최종 요약문 출력 (축약)
    # st.write("- 자막 요약:", final_summary) # 최종 요약문 출력

    if selected_lang == '영어':
        if trans_method == 'OpenAI':
            trans_result = my_text_sum.traslate_english_to_korean_using_openAI(final_summary)
        elif trans_method == 'DeepL':
            trans_result = my_text_sum.traslate_english_to_korean_using_deepL(final_summary)

        shorten_trans_result = textwrap.shorten(trans_result, 120, placeholder=' [..이하 생략..]')
        st.write("- 한국어 요약(축약):", shorten_trans_result)  # 한국어 번역문 출력 (축약)
        # st.write("- 한국어 요약:", trans_result) # 한국어 번역문 출력


# ------------------- 콜백 함수 --------------------
def button_callback():
    st.session_state['input'] = ""


# ------------- 사이드바 화면 구성 --------------------------
st.title("요약 설정 ")
url_text = st.text_input("유튜브 동영상 URL을 입력하세요.", key="input")

clicked_for_clear = st.button('URL 입력 내용 지우기', on_click=button_callback)

yt_lang = st.radio('유튜브 동영상 언어 선택', ['한국어', '영어'], index=1, horizontal=True)

if yt_lang == '영어':
    trans_method = st.radio('번역 방법 선택', ['OpenAI', 'DeepL'], index=1, horizontal=True)
else:
    trans_method = ""

clicked_for_sum = st.button('동영상 내용 요약')

# ------------- 메인 화면 구성 --------------------------     
st.title("유튜브 동영상 요약")

# 텍스트 입력이 있으면 수행
if url_text and clicked_for_sum:
    yt_video_url = url_text.strip()
    summarize_youtube_video(yt_video_url, yt_lang, trans_method)
