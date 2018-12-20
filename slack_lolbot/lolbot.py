# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import time

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-502761537154-507493624130-RaCypj9SuSAXW6MyR9hWZBXd"
slack_client_id = "502761537154.507489582978"
slack_client_secret = "0ddac4c9871a348260ed98f7930add1d"
slack_verification = "QNcuMRrBw2DVB0QewKmUXvEY"
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    result = []

    text = re.sub(r'<@\S+> ', '', text)


    ########################################## 완결 웹툰 ####################################################
    # if "완결 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/finish.nhn?page=1&sort=HIT"
    #     sourceCode = urllib.request.urlopen(url).read()
    #     soup = BeautifulSoup(sourceCode, "html.parser")
    #
    #     complete_webtoons = []
    #
    #     for webtoon in soup.find_all("span", class_="toon_name"):
    #         complete_webtoons.append(webtoon.get_text())
    #
    #     result = ["조회순가 높은 순서로 보여드리겠습니다.\n"]
    #     for i in range(10):
    #         result.append(str(i+1)+"위 "+complete_webtoons[i])
    ##########################################################################################################


    ########################################### 요일별 웹툰##################################################
    # if "월요일 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=mon"
    # elif "화요일 웹툰" in text:
    #     url = "https://m.comic.naver    .com/webtoon/weekday.nhn?week=tue"
    # elif "수요일 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=wed"
    # elif "목요일 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=thu"
    # elif "금요일 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=fri"
    # elif "토요일 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=sat"
    # elif "일요일 웹툰" in text:
    #     url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=sun"
    # else:
    #     return u"유효하지 않은 주소"
    #
    # sourceCode = urllib.request.urlopen(url).read()
    # # URL 주소에 있는 HTML 코드를 soup에 저장합니다.
    # soup = BeautifulSoup(sourceCode, "html.parser")
    #
    # keyword_list = []
    # title_list = []
    # name_list = []
    #
    # for keyword in soup.find_all("span", class_="txt_score"):
    #     keyword_list.append(keyword.get_text())
    # for title in soup.find_all("span", class_="toon_name"):
    #     title_list.append(title.get_text())
    # for title in soup.find_all("p", class_="sub_info"):
    #     name_list.append(title.get_text())
    #
    # result = []
    #
    # for i in range(len(keyword_list)):
    #     result.append(title_list[i] + " " + keyword_list[i] + " " + name_list[i])
    # ####################################################################################################

    return u'\n'.join(result)

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords,
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
#https://afd3a7ae.ngrok.io