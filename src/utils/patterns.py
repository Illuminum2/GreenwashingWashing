import re


class Patterns:
    @staticmethod
    def compile(pattern: str, flags: re._FlagsType = 0) -> re.Pattern:
        if pattern != '': # Empty string matches everything
            return re.compile(pattern, flags)
        return re.compile(r"(?!)") # Pattern matches nothing


    @staticmethod
    def compile_patterns(patterns: list[str], flags: re._FlagsType = 0) -> re.Pattern:
        pattern = '|'.join("(?:%s)" % case for case in patterns) # Merge patterns into one
        
        return Patterns.compile(pattern, flags)

    # Case-insensitive, unicode
    @staticmethod
    def compile_patterns_iu(patterns: list[str]) -> re.Pattern:
        return Patterns.compile_patterns(patterns, re.I | re.U)
