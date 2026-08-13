import asyncio
import csv
from abc import ABC, abstractmethod
from typing import Literal, Self

from pipeline import Pipeline

from sites import Page

from config import PRINT_MODE, CSV_PATH


class Printer(ABC):
    @staticmethod
    def get(mode: Literal['console', 'csv'] = PRINT_MODE) -> Printer:
        if mode == "csv":
            return CsvPrinter()
        return ConsolePrinter()


    @abstractmethod
    async def print_page(self, page: Page) -> None:
        pass


    @staticmethod
    async def run(in_q: asyncio.Queue, mode: Literal['console', 'csv'] = PRINT_MODE) -> None:
        async with Printer.get(mode) as printer:
            async with asyncio.TaskGroup() as tg:
                async for page in Pipeline.queue_drain(in_q):
                    tg.create_task(printer.print_page(page))


    async def __aenter__(self) -> Self:
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass



class ConsolePrinter(Printer):
    async def print_page(self, page: Page) -> None: # Technically just synchronous
        if page.matches:
            print(f"Page '{page.url}': ", end="")
            print (*page.matches, sep=", ")



class CsvPrinter(Printer):
    def __init__(self, path: str = CSV_PATH) -> None:
        self._path = path
        self._file = None
        self._writer = None


    async def print_page(self, page: Page) -> None:
        if page.matches or page.error and not page.url.is_XML:
            self._writer.writerow([page.url, ", ".join(page.matches), page.error])


    async def __aenter__(self) -> Self:
        self._file = open(self._path, 'w', newline='', encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(["url", "matches", "error"])

        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._file.close()
