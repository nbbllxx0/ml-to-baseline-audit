"""Pin the current process to the performance cores at high priority (Windows, hybrid Intel CPUs).

    from tools.pin import pin_from_env
    cpu_pinning = pin_from_env()        # acts only when PIN_PCORES=1; returns what was applied, for the run config

Why: on the i5-14600KF (6 performance + 8 efficiency cores), Windows placed launch-bound GPU processes on efficiency
cores at times, doubling OAT inference time (plan/BASELINE_PREREG.md §9, CPU placement row). Pinning every timed
process the same way removes that source of variation. Performance cores are found with GetSystemCpuSetInformation
(highest EfficiencyClass), not assumed. Threads started later inherit the process affinity. Standard library only.
"""
import ctypes
import os
from ctypes import wintypes

HIGH_PRIORITY_CLASS = 0x00000080


class _CpuSet(ctypes.Structure):
    _fields_ = [("Id", wintypes.DWORD), ("Group", wintypes.WORD), ("LogicalProcessorIndex", ctypes.c_ubyte),
                ("CoreIndex", ctypes.c_ubyte), ("LastLevelCacheIndex", ctypes.c_ubyte),
                ("NumaNodeIndex", ctypes.c_ubyte), ("EfficiencyClass", ctypes.c_ubyte), ("AllFlags", ctypes.c_ubyte),
                ("Reserved", wintypes.DWORD), ("AllocationTag", ctypes.c_ulonglong)]


class _Info(ctypes.Structure):
    _fields_ = [("Size", wintypes.DWORD), ("Type", wintypes.DWORD), ("CpuSet", _CpuSet)]


def performance_core_mask():
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    n = wintypes.ULONG(0)
    k32.GetSystemCpuSetInformation(None, 0, ctypes.byref(n), None, 0)
    buf = (ctypes.c_ubyte * n.value)()
    if not k32.GetSystemCpuSetInformation(buf, n, ctypes.byref(n), None, 0):
        raise OSError(ctypes.get_last_error(), "GetSystemCpuSetInformation failed")
    sets, off = [], 0
    while off < n.value:
        info = _Info.from_buffer(buf, off)
        sets.append((info.CpuSet.LogicalProcessorIndex, info.CpuSet.EfficiencyClass))
        off += info.Size
    top = max(e for _, e in sets)
    return sum(1 << lp for lp, e in sets if e == top)


def pin_from_env():
    if os.environ.get("PIN_PCORES") != "1":
        return {"pinned": False}
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
    k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    mask = performance_core_mask()
    h = k32.GetCurrentProcess()
    if not k32.SetProcessAffinityMask(h, mask):
        raise OSError(ctypes.get_last_error(), "SetProcessAffinityMask failed")
    if not k32.SetPriorityClass(h, HIGH_PRIORITY_CLASS):
        raise OSError(ctypes.get_last_error(), "SetPriorityClass failed")
    return {"pinned": True, "affinity_mask": hex(mask), "priority": "HIGH_PRIORITY_CLASS"}
