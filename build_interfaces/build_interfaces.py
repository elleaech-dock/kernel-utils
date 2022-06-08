from subprocess import CompletedProcess
from os import chdir, getcwd
from abc import ABC, abstractmethod

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


class Busybox(ABC):
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


class CrossBusybox(Busybox):
    def __init__(self, build_automation: BuildAutomationTool, cross_compiler: str) -> None:
        super().__init__(build_automation)
        self._cross_compiler = cross_compiler
        self._arch: str = None