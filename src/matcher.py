import asyncio
import re

from pipeline import Pipeline

from sites import Page
from patterns import Patterns

from config import LETTER_STRIP_PATTERN, MATCH_PATTERNS, MATCH_EXCLUSION_PATTERNS


class Matcher:
    _match_prog = Patterns.compile_patterns_iu(MATCH_PATTERNS)
    _match_exclusion_prog = Patterns.compile_patterns_iu(MATCH_EXCLUSION_PATTERNS)
    _letter_strip_prog = Patterns.compile(LETTER_STRIP_PATTERN, re.U)

    @staticmethod
    def match_content(content: str) -> list[str]:
        if not MATCH_PATTERNS:
            raise ValueError('Empty list of match patterns provided')

        matches = []

        for word in content.split():
            word = Matcher._letter_strip_prog.sub('', word)
            if Matcher._match_prog.search(word) and not Matcher._match_exclusion_prog.search(word):
                matches.append(word)

        return matches


    @staticmethod
    async def match_page(page: Page, out_q: asyncio.Queue) -> None:
        if page.content:
            page.matches = await asyncio.get_running_loop().run_in_executor(None, Matcher.match_content, page.content)

        await out_q.put(page)


    @staticmethod
    async def run(in_q: asyncio.Queue, out_q: asyncio.Queue) -> None:
        try:
            async with asyncio.TaskGroup() as tg:
                async for page in Pipeline.queue_drain(in_q):
                    tg.create_task(Matcher.match_page(page, out_q))
        finally:
            out_q.shutdown()
