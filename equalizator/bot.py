import os
import logging
import requests
import shutil

from typing import List, Callable
from pathlib import Path


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return Path(local_filename)


class Cfg:
    api_url: str
    token: str

    @classmethod
    def configure(cls, api_url: str, token: str):
        cls.api_url = api_url
        cls.token = token

    @classmethod
    def method_url(cls, method):
        return f"{cls.api_url}bot{cls.token}/{method}"


class Handler:
    hook: Callable


class Pooling(Handler):
    def handle_update(self, data):
        pass

    def run(self):
        import time

        update_id = 0
        while True:
            time.sleep(0.2)

            resp = requests.get(Cfg.method_url("getUpdates"), params={"offset": update_id})
            if resp.status_code != 200:
                continue

            for update in resp.json().get("result"):
                update_id = update["update_id"]
                self.handle_update(update)

            update_id += 1


class TgBot:
    def __init__(self, method=Pooling(), logger=logging.getLogger()):
        self._logg = logger
        self._handlers = []
        self._method = method
        method.handle_update = self.route

    def handle(self, fn):
        self._handlers.append(fn)
        return fn

    def route(self, update):
        for fn in self._handlers:
            fn(update)

    def getMe(self) -> requests.Response:
        return requests.get(Cfg.method_url("getMe"))

    def sendMessage(self, chat, text):
        return requests.post(Cfg.method_url("sendMessage"), dict(chat_id=chat, text=text))
    
    def sendFile(self, chat, file:str):
        with open(file, "rb") as img:
            return requests.post(
                Cfg.method_url("sendDocument"),
                data={'chat_id': chat},
                files={'document': ("image.png", img)})

    def getFile(self, file_id):
        resp = requests.get(Cfg.method_url("getFile"), dict(file_id=file_id))
        if resp.status_code != 200:
            raise Exception(resp.text)
        
        json = resp.json()
        path = json['result']['file_path']
        return download_file(f"https://api.telegram.org/file/bot{Cfg.token}/{path}")


    def run(self):
        self._method.run()