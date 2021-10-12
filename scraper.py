import requests
from bs4 import BeautifulSoup
from utils import UTILITIES, ARG_TYPES, TYPE_MAPS
import json


class WebScraper:
    def __init__(self):
        self.descs = {}
        self.data = {}

    def clean_and_insert_flags(self, utility, lines):
        """CLeans and inserts the flags for a given utility into the data structure

        :param utility:
        :param lines:
        :return:
        """
        self.data[utility] = {}
        for flag_line in lines:
            flag_line = remove_punctuation(flag_line)
            flag, arg = get_flag(flag_line), None
            if "[" in flag_line and "]" in flag_line:
                arg = get_inner_brackets(flag_line)
            elif "=" in flag_line:
                arg = get_equal_arg(flag_line)
            self.data[utility][flag] = arg

    def extract_utilities(self, utilities=None):
        if utilities is None:
            utilities = UTILITIES

        for utility in utilities:
            utility_url = f'https://man7.org/linux/man-pages/man1/{utility}.1.html'
            r = requests.get(utility_url)
            soup = BeautifulSoup(r.text)
            desc = soup.find_all('pre')[2].text

            self.descs[utility] = desc.split('\n')[1].strip()
            pre_len = len(soup.find_all('pre'))
            options = "\n".join([soup.find_all('pre')[i].text for i in range(3, pre_len)])
            stripped_options = [line.strip() for line in options.split('\n')]
            flag_lines = list(filter(lambda x: x and x[0] == "-", stripped_options))

            d = set(flag for flag in flag_lines)

            self.clean_and_insert_flags(utility, d)

    def generate_syntax(self, utility):
        syntax = self.descs[utility]

        if 'option' not in syntax.lower():
            return f"Invalid syntax for utility {utility}, {syntax}"

        s = syntax.replace('...', '')
        s = remove_punctuation(s)
        s = remove_brackets(s)
        s = s.lower()

        sp = s.split(" ")
        cleaned = []
        for val in sp:
            if val == utility:
                cleaned.append(val)
            elif "option" in val:
                cleaned.append("option")
            elif val and val[0] != "-":
                s = ""
                for data_type in TYPE_MAPS:
                    for match in TYPE_MAPS[data_type]:
                        if match in val:
                            s = data_type
                cleaned.append(s)

        return " ".join(cleaned)

    def save_json(self, syntax_path='syntax.json', map_path='utility_map.json'):
        """Saves scraped data """
        if not self.data or not self.descs:
            raise Exception("Mapping and syntax uninitialized")

        with open(syntax_path, 'w') as fp:
            json.dump(self.descs, fp)

        with open(map_path, 'w') as fp:
            json.dump(self.data, fp)


def get_inner_brackets(s):
    open_idx = s.index("[") + 1
    closed_idx = s.index("]")
    a = s[open_idx: closed_idx]
    a = a.replace("=", "")
    return a


def get_equal_arg(s):
    return remove_punctuation(s.split("=")[1])


def remove_punctuation(s):
    punctuation = set(_ for _ in ",.()")
    return "".join([x if x not in punctuation else "" for x in s])


def remove_brackets(s):
    brackets = {"[", "]"}
    return "".join([x if x not in brackets else "" for x in s])


def get_flag(line):
    punctuation = set(p for p in "[].,()=[]")
    for val in punctuation:
        line = line.replace(val, " ")
    flag = line.split(" ")[0]
    return flag


def non_conforming_flags(data, types):
    l = []
    for ut in data:
        for flag in data[ut]:
            if data[ut][flag] and data[ut][flag] not in types:
                l.append(":".join([ut, flag, data[ut][flag]]))
    return l


def convert_flag_types(data, mapping):
    for ut in data:
        for flag in data[ut]:
            if data[ut][flag]:
                for t in mapping:
                    for substr in mapping[t]:
                        if substr in data[ut][flag].lower():
                            data[ut][flag] = t
