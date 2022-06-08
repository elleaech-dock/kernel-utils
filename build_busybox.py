from subprocess import CompletedProcess, run
from os import chdir, getcwd
from abc import ABC, abstractmethod
from sys import exit

import argparse


def _parse_cli_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "arch",
        type=str,
        help="Busybox's target architecture",
    )

    args = parser.parse_args()
    return args


class BuildAutomationTool(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._command = ""
        self._log_dir = f"{getcwd()}/log"

    @abstractmethod
    def build(self, procs: int, arch: str="", cross_compiler: str="") -> CompletedProcess:
        raise NotImplementedError

    @abstractmethod
    def install(self, config_prefix: str, arch: str="", cross_compiler: str=""):
        raise NotImplementedError

    def dump_log(self) -> str:
        return f"2>&1 | tee -a {self._log_dir}"


class BusyboxBuilder(ABC):
    def __init__(self, build_automation: BuildAutomationTool) -> None:
        super().__init__()
        self._compiler = build_automation
        base_dir = f"{getcwd()}"
        self._initrd = f"{base_dir}/initrd"
        self.__busybox_dir = f"{base_dir}/deps/busybox"

    @abstractmethod
    def build(self, procs: int) -> None:
        raise NotImplementedError

    def goto_busybox_folder(self) -> None:
        chdir(self.__busybox_dir)


class CrossBoxBuilder(BusyboxBuilder):
    def __init__(self, build_automation: BuildAutomationTool, cross_compiler: str) -> None:
        super().__init__(build_automation)
        self._cross_compiler = cross_compiler
        self._arch: str = None


class Make(BuildAutomationTool):
    def __init__(self) -> None:
        super().__init__()
        self._command = "make"

    def build(self, procs: int, arch: str="", cross_compiler: str="") -> CompletedProcess:
        return run(
                f"{self._command} -j{str(procs)} \
                ARCH={arch} CROSS_COMPILE={cross_compiler} {self.dump_log()}",
                shell=True,
                check=True,
            )

    def install(self, config_prefix: str, arch: str="", cross_compiler: str=""):
        return run(
                f"{self._command} \
                CONFIG_PREFIX={config_prefix} \
                ARCH={arch} CROSS_COMPILE={cross_compiler} \
                install {self.dump_log()}",
                shell=True,
                check=True,
            )


class ARMBoxBuilder(CrossBoxBuilder):
    def __init__(self, build_automation: BuildAutomationTool, cross_compiler: str) -> None:
        super().__init__(build_automation, cross_compiler)
        self._arch = "arm"

    def build(self, procs: int) -> None:
        self.goto_busybox_folder()
        self._compiler.build(procs, arch = self._arch, cross_compiler = self._cross_compiler)
        self._compiler.install(self._initrd, arch = self._arch, cross_compiler = self._cross_compiler)


class X86_64BoxBuilder(BusyboxBuilder):
    def __init__(self, build_automation: BuildAutomationTool) -> None:
        super().__init__(build_automation)

    def build(self, procs: int) -> None:
        self.goto_busybox_folder()
        self._compiler.build(procs)
        self._compiler.install(self._initrd)


if __name__ == "__main__":
    args: argparse.ArgumentParser = _parse_cli_args()

    make: BuildAutomationTool = Make()

    if args.arch == "x86_64":
        make = X86_64BoxBuilder(make)
        make.build(2)

    elif args.arch == "arm":
        make = ARMBoxBuilder(make, "arm-linux-gnueabi-")
        make.build(2)

    exit(0)
