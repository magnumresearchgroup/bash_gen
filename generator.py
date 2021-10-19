from utils import UTILITIES, ARG_TYPES
import json
import random


def valid_arg(flag):
    """Determines whether a flag argument scraped flag is in the predefined flag types"""
    return flag in ARG_TYPES or not flag


class Generator:
    def __init__(self, syntax_path='syntax.json', map_path='utility_map.json', utilities=None):
        """Initializes the Generator class.

        :param syntax_path: (str) A file path to retrieve syntax structure.
        :param map_path: (str) A file path to retrieve utility, flag, arg mappings.
        :param utilities: (list) of (str) a list of utilities to generate.
        """
        with open(syntax_path) as fp:
            self.syntax = json.load(fp)

        with open(map_path) as fp:
            self.mappings = json.load(fp)

        if utilities is None:
            utilities = UTILITIES

        self.utilities = list(filter(lambda x: x in self.syntax and x in self.mappings, utilities))

    def get_utilities(self):
        """Gets a list of all of the utilities supported by the generator, ordered by usage"""
        return self.utilities

    def generate_commands(self, utility, max_commands=None):
        """Generates commands for a given utility

        :param utility: (str) the utility to generate commands for.
        :param max_commands: (int) the maximum number of commands to generate.

        :returns a (list) of (str) of generated commands.
        """
        ops = self._generate_options(utility)
        ret = []
        syntax = self.syntax[utility]
        if "Invalid" in syntax:
            return ret
        for option_combo in ops:
            ret.append(syntax.replace("option", option_combo))

        if not max_commands or max_commands > len(ret):
            return ret
        return random.sample(ret, max_commands)

    def generate_all_commands(self):
        """Generates the maximum number of commands for every utility."""
        ret = []
        for ut in self.utilities:
            if ut in self.syntax and ut in self.mappings:
                ret.extend(self.generate_commands(ut))
        return ret

    def _generate_options(self, utility):
        """Generates options combinations for a particular utility.

        :param utility: (str) the utility to generate combinations for
        :return: (list) of (str) of options combinations for the given utility.
        """
        flag_map = self.mappings[utility]

        ret = []
        keys = list(flag_map.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                for k in range(j + 1, len(keys)):
                    if all(valid_arg(flag_map[x]) for x in [keys[i], keys[j], keys[k]]):
                        f1 = " ".join([keys[i], flag_map[keys[i]]]) if flag_map[keys[i]] else keys[
                            i]
                        f2 = " ".join([keys[j], flag_map[keys[j]]]) if flag_map[keys[j]] else keys[
                            j]
                        f3 = " ".join([keys[k], flag_map[keys[k]]]) if flag_map[keys[k]] else keys[
                            k]
                        ret.append(f1)
                        ret.append(" ".join([f1, f2]))
                        ret.append(" ".join([f1, f2, f3]))
        return list(set(ret))


def replace(rep_path, in_path, out_path='replaced_cmds.txt'):
    """Replaces generated command placeholder arguments with executable arguments

    :param rep_path: the path to a json file
    :param in_path:
    :param out_path:

    Replacement json must be in the format
    {
    'File': 'temp.txt',
    'Folder': '/abc'
    }
    """

    with open(in_path, 'r') as fp:
        cmds = fp.read().split('\n')

    with open(rep_path, 'r') as fp:
        reps = json.load(fp)

    for i in range(len(cmds)):
        for arg_type in reps:
            if arg_type in cmds[i]:
                cmds[i] = cmds[i].replace(arg_type, reps[arg_type])

    with open(out_path, 'w') as fp:
        for line in cmds:
            fp.write(line + '\n')
