import re


def compile_patterns(patterns: list[str]) -> re.Pattern:
    pattern = '|'.join("(?:%s)" % case for case in patterns) # Merge patterns into one

    if pattern != '': # Empty string matches everything
        return re.compile(pattern, re.I | re.U)
    return re.compile(r"(?!)") # Pattern matches nothing