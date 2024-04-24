# PDF 문서를 요약하는 웹 앱

import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader
import tiktoken
import textwrap

# 텍스트 요약을 위한 모듈
from openai import OpenAI
import os
import deepl
import tiktoken
# import my_data

# OpenAI 라이브러리를 이용해 텍스트를 요약하는 함수
def summarize_text(user_text, lang="en"):  # lang 인자에 영어를 기본적으로 지정
    # API 키 설정
    client = OpenAI(api_key=api_key)

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
    client = OpenAI(api_key=api_key)

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
    auth_key = ''  # Deepl 인증 키
    translator = deepl.Translator(auth_key)  # translator 객체를 생성

    result = translator.translate_text(text, target_lang="KO")  # 번역 결과 객체를 result 변수에 할당

    return result.text



# PDF 파일을 요약하는 함수
def summarize_PDF_file(pdf_file, lang, trans_checked):
    if (pdf_file is not None):
        st.write("PDF 문서를 요약 중입니다. 잠시만 기다려 주세요.")
        reader = PdfReader(pdf_file)  # PDF 문서 읽기

        text_summaries = []

        for page in reader.pages:
            page_text = page.extract_text()  # 페이지의 텍스트 추출
            text_summary = my_text_sum.summarize_text(page_text, lang)
            text_summaries.append(text_summary)

        token_num, final_summary = my_text_sum.summarize_text_final(text_summaries, lang)

        if final_summary != "":
            shorten_final_summary = textwrap.shorten(final_summary,
                                                     250,
                                                     placeholder=' [..이하 생략..]')

            st.write("- 최종 요약(축약):", shorten_final_summary)  # 최종 요약문 출력 (축약)
            # st.write("- 최종 요약:", shorten_final_summary) # 최종 요약문 출력

            if trans_checked:
                trans_result = my_text_sum.traslate_english_to_korean_using_openAI(final_summary)
                shorten_trans_result = textwrap.shorten(trans_result,
                                                        200,
                                                        placeholder=' [..이하 생략..]')
                st.write("- 한국어 요약(축약):", shorten_trans_result)  # 한국어 번역문 출력 (축약)
                # st.write("- 한국어 요약:", trans_result) # 한국어 번역문 출력
        else:
            st.write("- 통합한 요약문의 토큰 수가 커서 요약할 수 없습니다.")


# ------------- 메인 화면 구성 --------------------------
st.title("PDF 문서를 요약하는 웹 앱")

uploaded_file = st.file_uploader("PDF 파일을 업로드하세요.", type='pdf')

radio_selected_lang = st.radio('PDF 문서 언어', ['한국어', '영어'], index=1, horizontal=True)

if radio_selected_lang == '영어':
    lang_code = 'en'
    checked = st.checkbox('한국어 번역 추가')  # 체크박스 생성
else:
    lang_code = 'ko'
    checked = False  # 체크박스 불필요

clicked = st.button('PDF 문서 요약')

if clicked:
    summarize_PDF_file(uploaded_file, lang_code, checked)  # PDF 파일 요약 수행
