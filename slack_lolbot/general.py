# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-502761537154-506888988689-b7E6bbYgy6Zyj9qhAczX0B3s"  # slack bot User OAuth Acess Token, slack App -permissions
# slack App- basic information
slack_client_id = '502761537154.506886203489'
slack_client_secret = '5aeb8d80bb6d2fa0803f580640f8cec8'
slack_verification = '7VjlCtOHvwz0A9rH1HbBm2Ec'
sc = SlackClient(slack_token)

def recommend_webtoon(url):
    sourceCode = urllib.request.urlopen(url).read()
    # URL 주소에 있는 HTML 코드를 soup에 저장합니다.
    soup = BeautifulSoup(sourceCode, "html.parser")
    # print(soup)
    # result_t1=soup.find_all("strong",class_="point")
    # print (result_t1)

    score_list = []
    title_list = []
    name_list = []

    for score in soup.find_all("span", class_="txt_score"):
        score_list.append(score.get_text())
    for title in soup.find_all("span", class_="toon_name"):
        title_list.append(title.get_text())
    for name in soup.find_all("p", class_="sub_info"):
        name_list.append(name.get_text())

    score_title_name = []

    for i in range(len(score_list)):
        score_title_name.append((score_list[i], title_list[i], name_list[i]) )

    score_title_name_sorted = sorted(score_title_name, key=lambda a: a[0], reverse=True)

    result = []

    for i in range(10):
        result.append(score_title_name_sorted[i][0] + " " + score_title_name_sorted[i][1] + " " + score_title_name_sorted[i][2])

    return result
# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):

    text = re.sub(r'<@\S+> ', '', text)
    # URL 데이터를 가져올 사이트 url 입력

    if "요일" in text:
        if "추천" in text :
            if "월요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=mon"
                result = recommend_webtoon(url)
            elif "화요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=tue"
                result = recommend_webtoon(url)
            elif "수요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=wed"
                result = recommend_webtoon(url)
            elif "목요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=thu"
                result = recommend_webtoon(url)
            elif "금요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=fri"
                result = recommend_webtoon(url)
            elif "토요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=sat"
                result = recommend_webtoon(url)
            elif "일요일" in text:
                url = "https://m.comic.naver.com/webtoon/weekday.nhn?week=sun"
                result = recommend_webtoon(url)
            else:
                return u"유효하지 않은 주소"
    elif "완결" in text:
        pass
    else :
        return "유효하지 않은 명령어입니다."

    return u'\n'.join(result)

def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
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
# http://9dadb86b.ngrok.io/listening