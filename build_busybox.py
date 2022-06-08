from subprocess import CompletedProcess, run
from .build_interfaces import BuildAutomationTool, Busybox, CrossBusybox
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


class ARMBoxBuilder(CrossBusybox):
    def __init__(self, build_automation: BuildAutomationTool, cross_compiler: str) -> None:
        super().__init__(build_automation, cross_compiler)
        self._arch = "arm"

    def build(self, procs: int) -> None:
        self.goto_busybox_folder()
        self._compiler.build(procs, arch = self._arch, cross_compiler = self._cross_compiler)
        self._compiler.install(self._initrd, arch = self._arch, cross_compiler = self._cross_compiler)


class X86_64BoxBuilder(Busybox):
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
