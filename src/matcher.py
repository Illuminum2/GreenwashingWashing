import asyncio
import re

from pipeline import Pipeline

from sites import Page

from config import MATCH_PATTERNS, MATCH_EXCLUSION_PATTERNS


class Matcher:
    @staticmethod
    def _compile_patterns(patterns: list[str]) -> re.Pattern:
        pattern = '|'.join('(?:%s)' % case for case in patterns) # Merge patterns into one

        if pattern != '': # Empty string matches everything
            return re.compile(pattern, re.I | re.U)
        return re.compile('?!')


    @staticmethod
    def match_content(content: str, match_patterns: list[str] = MATCH_PATTERNS, anti_match_patterns: list[str] = MATCH_EXCLUSION_PATTERNS) -> list[str]:
        if not match_patterns:
            raise ValueError('Empty list of match patterns provided')

        match_prog = Matcher._compile_patterns(match_patterns)
        match_exclusion_prog = Matcher._compile_patterns(anti_match_patterns)

        matches = []

        for word in content.split():
            if match_prog.search(word) and not match_exclusion_prog.search(word):
                matches.append(word)

        return matches


    @staticmethod
    async def match_page(page: Page, out_q: asyncio.Queue) -> None:
        if page.content:
            page.matches = await asyncio.get_running_loop().run_in_executor(None, Matcher.match_content, page.content)

        await out_q.put(page)


    @staticmethod
    async def match_queue(in_q: asyncio.Queue, out_q: asyncio.Queue) -> None:
        try:
            async with asyncio.TaskGroup() as tg:
                async for page in Pipeline.queue_drain(in_q):
                    tg.create_task(Matcher.match_page(page, out_q))
        finally:
            out_q.shutdown()
