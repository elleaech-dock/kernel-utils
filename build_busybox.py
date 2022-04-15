from subprocess import run
from os import chdir, getcwd
from abc import ABC, abstractmethod
from sys import exit

import argparse


def parse_cli_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "arch",
        type=str,
        help="Busybox's target architecture",
    )

    args = parser.parse_args()
    return args


class BoxBuilder(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._command = "make"
        self.__basedir = f"{getcwd()}"
        self._initrd = f"{self.__basedir}/initrd"
        self.__busybox_dir = f"{self.__basedir}/deps/busybox"

    @abstractmethod
    def build(self, procs: int) -> None:
        raise NotImplementedError

    def _goto_busybox_folder(self) -> None:
        chdir(self.__busybox_dir)

    def _dump_log(self) -> str:
        return f"2>&1 | tee -a {self.__basedir}/log"


class CrossBoxBuilder(BoxBuilder):
    def __init__(self, cross_compiler: str) -> None:
        super().__init__()
        self._cross_compiler = cross_compiler
        self._arch: str = None


class ARMBoxBuilder(CrossBoxBuilder):
    def __init__(self, compiler: str) -> None:
        super().__init__(compiler)
        self._arch = "arm"

    def build(self, procs: int) -> None:
        self._goto_busybox_folder()

        run(
            f"{self._command} -j{str(procs)} \
               ARCH={self._arch} CROSS_COMPILE={self._cross_compiler} {self._dump_log()}",
            shell=True,
            check=True,
        )
        run(
            f"{self._command} \
               CONFIG_PREFIX={self._initrd} \
               ARCH={self._arch} CROSS_COMPILE={self._cross_compiler} \
               install {self._dump_log()}",
            shell=True,
            check=True,
        )


class X86_64BoxBuilder(BoxBuilder):
    def __init__(self) -> None:
        super().__init__()

    def build(self, procs: int) -> None:
        self._goto_busybox_folder()

        run(
            f"{self._command} -j{str(procs)} {self._dump_log()}",
            shell=True,
            check=True,
        )
        run(
            f"{self._command} CONFIG_PREFIX={self._initrd} install {self._dump_log()}",
            shell=True,
            check=True,
        )


if __name__ == "__main__":
    args: argparse.ArgumentParser = parse_cli_args()

    if args.arch == "x86_64":
        make = X86_64BoxBuilder()
        make.build(2)

    elif args.arch == "arm":
        make = ARMBoxBuilder("arm-linux-gnueabi-")
        make.build(2)

    exit(0)
