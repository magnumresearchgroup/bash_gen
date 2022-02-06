UTILITIES = [
    "find",
    "xargs",
    "grep",
    "rm",
    "echo",
    "ls",
    "sort",
    "chmod",
    "wc",
    "cat",
    "cut",
    "head",
    "mv",
    "chown",
    "cp",
    "mkdir",
    "tr",
    "tail",
    "dirname",
    "tar",
    "uniq",
    "ln",
    "split",
    "tee",
    "date",
    "pwd",
    "ssh",
    "diff",
    "du",
    "file",
    "rename",
    "md5sum",
    "comm",
    "mktemp",
    "df",
    "rev",
    "rmdir",
    "od",
    "hostname",
]


ARG_TYPES = [

    '[Pattern]',  # ex. '*.txt'
    '[Formatted String]',  # ex. '%m:%u:%g:%p\0'
    '[Separator]',  # ex. '|'

    "[Directory]",  # /

    "[File]",  # ex. temp.txt
    "[File2]",  # second file in command
    "[File Type]",  # one of b, c, d, p, f, l, s, D
    "[Filesystem Type]",  # one of ufs, 4.2, 4.3, nfs, tmp, mfs, S51K, S52K

    '[Permission]',  # ex. 744
    '[Mode]',

    '[Small Number]',  # ex. 1
    '[Medium Number]',  # ex. 20
    '[Large Number]',  # ex. 800

    '[Action]',  # ex read, skip, recurse

    '[Command]'

]


TYPE_MAPS = {
    '[Pattern]': {'pattern', 'patterns', 'glob'},
    '[Separator]': {'delim', 'sep', 'str'},
    '[Formatted String]': {'format', 'lfmt', 'fmt'},
    "[Directory]": {'directory', 'dest', 'dir'},
    "[File]": {'file', 'file1', 'source'},
    "[File2]": {'file2'},  # for commands with multiple file arguments
    "[File Type]": {'c'},
    "[Filesystem Type]": {'type'},
    '[Permission]': {'permission'},
    '[Mode]': {'mode'},
    '[Small Number]': {'depth', 'levels', 'level', 'n', 'num', 'max-lines', 'max-args',
                       'max-procs', 'size', 'quantity', 'pid', 'uid', 'gid'},
    '[Medium Number]': {'number'},
    '[Large Number]': {'port', 'bytes'},
    '[Action]': {'max-chars'},
    '[Command]': {'command'}
}

MANUAL_SYNTAX_INSERTS = {
    'find': 'find [Directory] [Options]',
    'tar': 'tar [Options] [File] [File2]',
    'file': 'file [Options] [File]',
    'hostname': 'hostname [Options]',
}

POST_PIPE = {
    'xargs',
    'grep',
    'wc',
    'awk',
    'sort',
    'head',
    'sed',
    'tee',
}
