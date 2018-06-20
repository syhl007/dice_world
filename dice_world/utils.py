import re


class WordFilter:

    @staticmethod
    def handle(text):
        return text


class DiceFilter:

    @staticmethod
    def handle(text):
        dice = re.compile(r'^\.([1-9][0-9]*)?d([1-9][0-9]*)(\s)*(.+)?$')
        return dice.match(text)