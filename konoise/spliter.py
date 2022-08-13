import os.path
import re
import json
from typing import List
from dataclasses import field
from itertools import compress, islice
from .utils import load_json

REPL = {")": "\)", "}": "\}"}
ENDS = {".", "!", "?", "’", ' '}
EXEC = {"고", "라", "”", '면', '하'}


def find_all_indices(text:str, target:str):
    return [e.start() for e in re.finditer(target, text)]


class JoinSplit:
    def split(self, text: str) -> List[str]:
        raise ValueError

    def join(self, texts: List[str]) -> str:
        raise ValueError


class NoSplit(JoinSplit):
    def split(self, text: str) -> List[str]:
        return [text]

    def join(self, texts: List[str]) -> str:
        raise "".join(texts)


class SentenceSplit(JoinSplit):
    def __init__(self):
        self.endwords: dict = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/endwords.json"))
        self.endwords = {k: v for k, v in self.endwords.items() if k in ["다", "까", "임", "함", "요"]}

    def _sub_split(self, text: str) -> List[str]:
        def search(dictionary, chars, i=0):
            if i < len(chars):
                if chars[i] in dictionary:
                    if chars[i] == " ":
                        return True
                    return search(dictionary[chars[i]], chars, i+1)
                elif 2 < i:
                    return True
            return False

        reverse_text = text[::-1]
        maps = [search(self.endwords, reverse_text[i:]) for i in range(len(reverse_text))]

        ids = [0]+[len(reverse_text)-i for i in compress(range(len(reverse_text)), maps)][::-1]+[len(reverse_text)+1]

        is_changed = True
        while is_changed:
            new = [min(i+1, len(text)) if (text[min(i+1, len(text)-1)] in ENDS) else i for i in ids]
            if ids == new:
                is_changed = False
            ids = new
        ids = [i for i in ids if text[min(i, len(text)-1)] not in EXEC]
        ids = [i+1 if text[min(max(0, i), len(text)-1)] == " " else i for i in ids]
        return [text[ids[i]:ids[i+1]] for i in range(len(ids)-1)]

    def split(self, text: str) -> List[str]:
        text = re.split("(?<=[가-힣ㄱ-ㅎ][가-힣ㄱ-ㅎ\)][\.\?\!\n\^]) ?(?=[^\"\'’”\.\)])", text)
        text = [sub for line in compress(text, text) for sub in self._sub_split(line) if sub]
        output = ['']
        in_bracket = False
        for t in text:
            if "(" in t and all(e not in t for e in [":(", ";(", ":)"]):
                in_bracket = True
            if t.strip().endswith(("다고", "하고", "이고")):
                in_bracket = True
            if len(t) == 1 or in_bracket:
                if ")" in t:
                    in_bracket = False
                    sp = t.split(")")
                    output[-1] += ")".join(sp[:-1])+")"
                    output.append(sp[-1])
                else:
                    output[-1] += t
            else:
                output.append(t)
        if not output[0]:
            del output[0]
        return output

    def join(self, texts: List[str]) -> str:
        return " ".join(texts)


class ParagraphSplit(JoinSplit):
    def split(self, text: str) -> List[str]:
        return text.split("\n\n")

    def join(self, texts: List[str]) -> str:
        raise "\n\n".join(texts)