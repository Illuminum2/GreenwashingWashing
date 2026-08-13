import asyncio
import re

from utils.pipeline import Pipeline

from data.sites import Page
from utils.patterns import Patterns

from utils.config import Config


class Matcher:
    _match_prog = Patterns.compile_patterns_iu(Config.get("match.patterns"))
    _match_exclusion_prog = Patterns.compile_patterns_iu(Config.get("match.exclusion_patterns"))
    _letter_strip_prog = Patterns.compile(Config.get("match.letter_strip_pattern", r"(?!-)[\W\d_]"), re.U)

    @staticmethod
    def match_content(content: str) -> list[str]:
        if not Config.get("match.patterns"):
            raise ValueError('Empty match patterns list provided')

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
