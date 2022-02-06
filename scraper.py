import requests
from bs4 import BeautifulSoup
from utils import UTILITIES, TYPE_MAPS, ARG_TYPES, MANUAL_SYNTAX_INSERTS
import json
from pprint import pprint


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
        self.relevant_flags = {}

    def load_relevant_flags(self, path='original_training.txt'):
        """Saves all of the flags included in the original training set to the class instance.

        This method takes note of all of the flags used in the training data to help limit the
        use of rare and unnecessary flags in the bash generator.

        :param path: (str) the file path for the original training data.
        """

        with open(path) as fp:
            self.relevant_flags = set(fp.read().replace('\n', ' ').split(' '))

    def is_relevant(self, flag):
        """Returns whether or not a flag is relevant enough to be incorporated in bash generation.

        This includes all flags scraped except those that both have a double hyphen ("--") and
        are not included in the original training data.

        :param flag: (str) the flag to determine relevancy for.

        :returns: (bool) whether or bot the flag is deemed relevant.
        """
        return False if "--" in flag and flag not in self.relevant_flags else True

    def display_structures(self):
        pprint(self.descs)
        pprint(self.data)

    def extract_utilities(self):
        """Extracts all of the utility information from the man pages."""

        print(f"Scraping the internet for {len(self.utilities)} utilities, this may take some "
              f"time ...")

        # lists to keep track of utilities with unknown man pages or syntax structures
        no_page_uts, no_syntax_uts = [], []
        successful_searches = []

        for utility in self.utilities:
            utility_url = f'https://man7.org/linux/man-pages/man1/{utility}.1.html'
            r = requests.get(utility_url)

            # search different man pages for utility description if needed
            if r.status_code != 200:
                utility_url = f'https://man7.org/linux/man-pages/man1/{utility}.2.html'
                r = requests.get(utility_url)

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, features='lxml')
                desc = soup.find_all('pre')[2].text

                syntax = WebScraper._generate_syntax(utility, desc.split('\n')[1].strip())
                if not syntax:
                    if utility in MANUAL_SYNTAX_INSERTS:
                        # manually insert syntax structure for given utility
                        self.descs[utility] = MANUAL_SYNTAX_INSERTS[utility]
                        successful_searches.append(utility)
                    else:
                        no_syntax_uts.append(utility)
                elif utility:
                    self.descs[utility] = syntax
                    successful_searches.append(utility)

                # build options
                pre_len = len(soup.find_all('pre'))
                options = "\n".join([soup.find_all('pre')[i].text for i in range(3, pre_len)])
                stripped_options = [line.strip() for line in options.split('\n')]
                flag_lines = list(filter(lambda x: x and x[0] == "-", stripped_options))

                d = set(flag for flag in flag_lines)

                self._clean_and_insert_flags(utility, d)
            else:
                no_page_uts.append(utility)

        self.convert_flag_types()
        self.data['find -L'] = self.data['find']  # specific behavior for find command

        print(f"Successfully scraped for {len(successful_searches)} utilities")
        print(f"{len(no_page_uts)} utilities with no found man page: {no_page_uts}")
        print(f"{len(no_syntax_uts)} utilities without syntax structures: {no_syntax_uts}")

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
            elif len(flag_line.split(" ")) == 2 and "-" not in flag_line.split(" ")[1]:
                arg = flag_line.split(" ")[1]
            if flag not in self.data[utility] or not self.data[utility][flag] and self.is_relevant(
                    flag):
                self.data[utility][flag] = arg

    @staticmethod
    def _generate_syntax(utility, syntax):
        """Generates valid syntax expression for given web scraped syntax.

        :param utility: (str) the utility to generate syntax for.
        :param syntax: (str) the syntax scraped from the website.
        :returns (str) the cleaned syntax expression.
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
                cleaned.append("[Options]")
            elif val and val[0] != "-":
                s = ""
                for data_type in TYPE_MAPS:
                    for match in TYPE_MAPS[data_type]:
                        if match == val:
                            s = data_type
                if s:
                    if s == '[File]' and s in cleaned:
                        cleaned.append('[File2]')
                    else:
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
        """Manual insertion of a flag, arg mapping for a given utility.

        Useful for flag, arg mappings that were not scraped correctly from man pages.

        :param utility: (str) the utility to insert the mapping for.
        :param flag: (str) the flag to insert.
        :param arg: (str) or (None) the argument that maps to the provided flag. None if there
            is no argument.
        """
        self.data[utility][flag] = arg

    def unprocessed_utilities(self):
        """Discovering which utilities were not found when scraping.

        :returns a list of utilities with no assigned mapping.
        """
        ret = []
        for utility in self.utilities:
            if utility not in self.descs:
                ret.append(utility)

        return ret

    @staticmethod
    def _get_inner_brackets(s):
        """Helper method to parse for value within brackets.

        :param s: (str) a string with opening and closing brackets.
        :returns (str) a string containing only the characters in between the brackets.
        """
        open_idx = s.index("[") + 1
        closed_idx = s.index("]")
        a = s[open_idx: closed_idx]
        a = a.replace("=", "")
        return a

    @staticmethod
    def _get_equal_arg(s):
        """Helper method to parse for value after equal sign.

        :param s: (str) a string with an equal sign.
        :returns (str) a string with only the character proceeding the equal sign.
        """
        return WebScraper._remove_punctuation(s.split("=")[1])

    @staticmethod
    def _remove_punctuation(s):
        """Helper method to remove specific punctuation from a string.

        :param s: (str) any string.
        :returns (str) a string without commas, parenthesis, and periods.
        """
        punctuation = set(_ for _ in ",.()")
        return "".join([x if x not in punctuation else "" for x in s])

    @staticmethod
    def _remove_brackets(s):
        """Helper method to remove brackets from a string.

        :param s: (str) any string.
        :returns (str) the same string without any brackets.
        """
        brackets = {"[", "]"}
        return "".join([x if x not in brackets else "" for x in s])

    @staticmethod
    def _get_flag(line):
        """Helper method to find a flag within a line from the man pages.

        :param line: (str) a scraped line from the man pages containing a flag definition.
            Example: input "-e PATTERNS" which returns "-e".
        :returns (str) the flag itself.
        """
        punctuation = set(p for p in "[].,()=[]")
        for val in punctuation:
            line = line.replace(val, " ")
        flag = line.split(" ")[0]
        return flag

    def non_conforming_flags(self, types=None):
        """Finds all of the flags that were scraped that were not given mappings.

        :param types: (list) of (str) valid argument types. Defaults to the list in utils.py.
        :returns: (list) of (str) showing which utility, flag, argument type combinations do not
            conform to the type mappings.
        """
        if types is None:
            types = ARG_TYPES

        nc_list = []
        for ut in self.data:
            for flag in self.data[ut]:
                if self.data[ut][flag] and self.data[ut][flag] not in types:
                    nc_list.append(":".join([ut, flag, self.data[ut][flag]]))
        return nc_list

    def convert_flag_types(self, mapping=None):
        """Converts the flag types to those match those in a specific mapping

        Different models and datasets use different words to differentiate argument types (i.e.
        files, directories, numbers). This method looks for key words within the scraped argument
        types to infer the argument types based on those scraped.

        :param mapping: (dict) a mapping of argument types to strings that may appear in the man
            pages that are synonymous with the argument type.
        """

        if mapping is None:
            mapping = TYPE_MAPS

        for ut in self.data:
            for flag in self.data[ut]:
                if self.data[ut][flag]:
                    arg_type = self.data[ut][flag]
                    if arg_type == 'n' or 'size' in flag:
                        self.data[ut][flag] = 'Number'
                    elif 'file' in flag:
                        self.data[ut][flag] = 'File'
                    else:
                        for t in mapping:
                            for substr in mapping[t]:
                                if substr in self.data[ut][flag].lower():
                                    self.data[ut][flag] = t
