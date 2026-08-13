import re


class Patterns:
    @staticmethod
    def _compile_patterns(patterns: list[str], flags: re._FlagsType) -> re.Pattern:
        pattern = '|'.join("(?:%s)" % case for case in patterns) # Merge patterns into one
        
        if pattern != '': # Empty string matches everything
            return re.compile(pattern, flags)
        return re.compile(r"(?!)") # Pattern matches nothing

    # Case-insensitive, unicode
    @staticmethod
    def compile_patterns_iu(patterns: list[str]) -> re.Pattern:
        return Patterns._compile_patterns(patterns, re.I | re.U)
