import requests
from bs4 import BeautifulSoup
from utils import UTILITIES, TYPE_MAPS
import json


class WebScraper:
    def __init__(self, utilities=None):
        """Initializes the WebScraper class to scrape for a given list of utilities.

        :param utilities: (list) a list of utilities to scrape for. Defaults to list from utils.py.
        """
        if utilities is None:
            utilities = UTILITIES

        self.utilities = utilities
        self.descs = {}
        self.data = {}

    def extract_utilities(self):
        """Extracts all of the utility information from the man pages"""
        self.insert_syntax('find', 'find options Folder Regex')
        self.insert_syntax('tar', 'tar options File File')
        self.insert_syntax('file', 'file options File')
        self.insert_syntax('hostname', 'hostname options')

        for utility in self.utilities:
            utility_url = f'https://man7.org/linux/man-pages/man1/{utility}.1.html'
            r = requests.get(utility_url)
            if r.status_code == 200:
                print(utility)
                soup = BeautifulSoup(r.text)
                desc = soup.find_all('pre')[2].text

                syntax = WebScraper._generate_syntax(utility, desc.split('\n')[1].strip())
                if not syntax:
                    print(f"syntax not found for {utility}")
                elif utility not in self.descs:
                    self.descs[utility] = syntax
                pre_len = len(soup.find_all('pre'))
                options = "\n".join([soup.find_all('pre')[i].text for i in range(3, pre_len)])
                stripped_options = [line.strip() for line in options.split('\n')]
                flag_lines = list(filter(lambda x: x and x[0] == "-", stripped_options))

                d = set(flag for flag in flag_lines)

                self._clean_and_insert_flags(utility, d)
            else:
                print(f"No web page found for {utility}")

    def _clean_and_insert_flags(self, utility, lines):
        """Cleans and inserts the flags for a given utility into the data structure.

        :param utility: The utility to insert flags for.
        :param lines: The lines of html scraped from the man pages.
        """
        self.data[utility] = {}
        for flag_line in lines:
            flag_line = WebScraper._remove_punctuation(flag_line)
            flag, arg = WebScraper._get_flag(flag_line), None
            if "[" in flag_line and "]" in flag_line:
                arg = WebScraper._get_inner_brackets(flag_line)
            elif "=" in flag_line:
                arg = WebScraper._get_equal_arg(flag_line)
            elif len(flag_line.split(" ")) == 2 and "-" not in flag_line[1]:
                arg = flag_line[1]
            self.data[utility][flag] = arg

    @staticmethod
    def _generate_syntax(utility, syntax):
        """Generates valid syntax expression for given web scraped syntax.

        :param utility: (str) the utility to generate syntax for.
        :param syntax: (str) the syntax scraped from the website.
        :return (str) the cleaned syntax expression.
        """

        if 'option' not in syntax.lower():
            return None

        # clean scraped html syntax string
        s = syntax.replace('...', '')
        s = WebScraper._remove_brackets(WebScraper._remove_punctuation(s)).lower()

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
        """Saves scraped data to provided file paths.

        :param syntax_path: (str) the filepath to save the json with syntax.
        :param map_path: (str) the file path to save the json with the utility, flag, arg mappings.
        """
        if not self.data or not self.descs:
            raise Exception("Mapping and syntax uninitialized")

        with open(syntax_path, 'w') as fp:
            json.dump(self.descs, fp)

        with open(map_path, 'w') as fp:
            json.dump(self.data, fp)

    def insert_syntax(self, utility, syntax):
        """Manual insertion of syntax expression for given utility.

        Useful for syntax that was not scraped correctly from man pages.

        :param utility: (str) the utility to insert syntax for.
        :param syntax: (str) the syntax expression to insert.
        """
        self.descs[utility] = syntax

    def insert_flag(self, utility, flag, arg):
        """Manual insertion of a flag, arg mapping for a given utility

        Useful for flag, arg mappings that were not scraped correctly from man pages.

        :param utility: (str) the utility to insert the mapping for.
        :param flag: (str) the flag to insert.
        :param arg: (str) or (None) the argument that maps to the provided flag. None if there
            is no argument.
        """
        self.data[utility][flag] = arg

    def unprocessed_utilities(self):
        ret = []
        for utility in self.utilities:
            if utility not in self.descs:
                ret.append(utility)

        return ret

    @staticmethod
    def _get_inner_brackets(s):
        open_idx = s.index("[") + 1
        closed_idx = s.index("]")
        a = s[open_idx: closed_idx]
        a = a.replace("=", "")
        return a

    @staticmethod
    def _get_equal_arg(s):
        return WebScraper._remove_punctuation(s.split("=")[1])

    @staticmethod
    def _remove_punctuation(s):
        punctuation = set(_ for _ in ",.()")
        return "".join([x if x not in punctuation else "" for x in s])

    @staticmethod
    def _remove_brackets(s):
        brackets = {"[", "]"}
        return "".join([x if x not in brackets else "" for x in s])

    @staticmethod
    def _get_flag(line):
        punctuation = set(p for p in "[].,()=[]")
        for val in punctuation:
            line = line.replace(val, " ")
        flag = line.split(" ")[0]
        return flag

    @staticmethod
    def non_conforming_flags(data, types):
        """Finds all of the flags that were scraped that were not given mappings"""
        nc_list = []
        for ut in data:
            for flag in data[ut]:
                if data[ut][flag] and data[ut][flag] not in types:
                    nc_list.append(":".join([ut, flag, data[ut][flag]]))
        return nc_list

    @staticmethod
    def convert_flag_types(data, mapping):
        for ut in data:
            for flag in data[ut]:
                if data[ut][flag]:
                    for t in mapping:
                        for substr in mapping[t]:
                            if substr in data[ut][flag].lower():
                                data[ut][flag] = t
