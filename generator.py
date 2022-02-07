from utils import UTILITIES, ARG_TYPES
import collections
import json
import random
import subprocess


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
        """Generates commands for a given utility or list of utilities.

        :param utility: (str) or (lst) of (str) of the utility(s) to generate commands for.
        :param max_commands: (int) the maximum number of commands to generate.

        :returns a (list) of (str) of generated commands.
        """
        if type(utility) == list:
            ret = []
            for ut in utility:
                ret.extend(self.generate_commands(ut))
        else:
            ops = self._generate_options(utility)
            ret = []
            syntax = self.syntax[utility]
            if "Invalid" in syntax:
                return ret
            for option_combo in ops:
                ret.append(syntax.replace("[Options]", option_combo))

        if not max_commands or max_commands > len(ret):
            return ret
        return random.sample(ret, max_commands)

    def generate_all_commands(self, save_path=None):
        """Generates the maximum number of commands for every utility.

        :param save_path: (optional str) the path to a file to save the commands to.
        :returns (list) of (str) the commands generated.
        """
        ret = []
        for ut in self.utilities:
            if ut in self.syntax and ut in self.mappings:
                ret.extend(self.generate_commands(ut))

        if save_path:
            with open(save_path, 'w') as fp:
                fp.write("\n".join(ret))

        return ret

    def generate_scaled_commands(self, training_path='data/original_training.txt', save_path=None):
        """Generates commands scaled to distribution of training data.

        :param training_path: (str) the path to the training commands.
        :param save_path: (optional str) the path to a file to save the commands to.
        :returns (list) of (str) the commands generated.
        """
        print(f"Generating commands to match distribution of {training_path}")
        with open(training_path) as fp:
            cmds = fp.read().split('\n')
            ut_list = [cmd.split(' ')[0] for cmd in cmds]
            ut_count = collections.Counter(ut_list)

        multiplier = None
        for ut, count in ut_count.most_common(20):
            if ut in UTILITIES:
                multiplier = len(self.generate_commands(ut)) // ut_count[ut]
                break

        if not multiplier:
            print("Training data utilities not supported by generator")
            return

        generated_cmds = []
        for ut, count in ut_count.most_common(20):
            if ut not in self.syntax:
                print(f"No support for {ut} utility, not included in the dataset")
            else:
                cmds_to_add = self.generate_commands(ut, ut_count[ut] * multiplier)
                if ut_count[ut] * multiplier > len(cmds_to_add):
                    print(f"Unable to generate enough commands for {ut}, generated "
                          f"{len(cmds_to_add)}/{multiplier * ut_count[ut]}")
                else:
                    print(f"Successfully generated {len(cmds_to_add)} commands for {ut}")

                generated_cmds.extend(cmds_to_add)

        if save_path:
            with open(save_path, 'w') as fp:
                fp.write("\n".join(generated_cmds))

        return generated_cmds

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


def replace(rep_path, in_path, out_path='replaced_cmds.txt', reverse=False):
    """Replaces particular words within a list of commands according to a given mapping.

    This function can be used to turn a list of generic commands to actual executable commands,
    or vice versa.

    :param rep_path: (str) the path to a json file with the word mappings.
    :param in_path: (str) the path to a text file with all of the commands to be converted.
    :param out_path: (str) the path to the new file to save all of the converted commands to.
    :param reverse: (bool) whether to reverse the direction of the replacement (i.e. replacing
        executable commands with generic commands).

    Replacement json must be in the format
    {
    '[File]': 'temp.txt',
    '[Folder]': '/abc'
    }

    and would convert
    'find Folder -regex File' -->   'find /abc -regex temp.text'
    """

    with open(in_path, 'r') as fp:
        cmds = fp.read()

    with open(rep_path, 'r') as fp:
        reps = json.load(fp)

    if reverse:
        reps = {value: key for (key, value) in reps.items()}

    for (key, value) in reps.items():
        cmds = cmds.replace(key, value)

    with open(out_path, 'w') as fp:
        fp.write(cmds)


def validate_commands(file_path, out_path=None, sudo=False):
    """Validates a list of commands and returns only the valid commands.

    Takes in a text file of bash commands and runs them on the command line. All of those
    with non zero exit statuses are returned.

    ****NOTE****
    Only run in an isolated environment. These commands will be run and will alter the state of
    the environment.
    ****----****

    :param file_path: (str) a file path to a text file of commands.
    :param out_path: (optional str) a file path to save the validated commands to.
    :param sudo: (bool) whether to run the commands as a root user.
    :returns: (list) of (str) commands that came back with a zero exit status.
    """
    with open(file_path, 'r') as f:
        cmds = f.read().split('\n')
    ret = []

    for count, cmd in enumerate(cmds):
        valid = True
        if sudo:
            cmd = " ".join(["sudo", cmd])
        try:
            # run the command
            subprocess.check_output(cmd, shell=True)
        except BaseException as e:
            valid = False
            print(e)

        if valid:
            print("SUCCESS")
            ret.append(cmd)

        print(f"processed {count}/{len(cmds)} commands")

    if out_path:
        with open(out_path, 'w') as fp:
            fp.write("\n".join(ret))
    return ret
