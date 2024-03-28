import ctypes
from ctypes import wintypes
from consts import *

kernel32 = ctypes.windll.kernel32

def find_pattern(process, pattern):
    memory = process.read_bytes(process.base_address, process.process_base.SizeOfImage)
    results = []
    pattern_len = len(pattern)
    for i in range(len(memory) - pattern_len):
        if memory[i:i+pattern_len] == pattern:
            results.append(process.base_address + i)
    return results

def GetProcId(processName):
    procId = None
    hSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

    if hSnap != INVALID_HANDLE_VALUE:
        procEntry = PROCESSENTRY32()
        procEntry.dwSize = ctypes.sizeof(PROCESSENTRY32)

        if kernel32.Process32First(hSnap, ctypes.byref(procEntry)):
            while True:
                if procEntry.szExeFile.decode("utf-8") == processName:
                    procId = int(procEntry.th32ProcessID)
                    break
                if not kernel32.Process32Next(hSnap, ctypes.byref(procEntry)):
                    break

    kernel32.CloseHandle(hSnap)
    return procId

def GetModuleBaseAddress(pid, moduleName):
    baseAddress = None
    hSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)

    if hSnap != INVALID_HANDLE_VALUE:
        modEntry = MODULEENTRY32()
        modEntry.dwSize = ctypes.sizeof(MODULEENTRY32)

        if kernel32.Module32First(hSnap, ctypes.byref(modEntry)):
            while True:
                if modEntry.szModule.decode("utf-8") == moduleName:
                    baseAddress = int(hex(ctypes.addressof(modEntry.modBaseAddr.contents)), 16)
                    break
                if not kernel32.Module32Next(hSnap, ctypes.byref(modEntry)):
                    break

    kernel32.CloseHandle(hSnap)
    return baseAddress

def FindDMAAddy(hProc, base, offsets, arch=64):
    size = 8 if arch == 64 else 4
    address = ctypes.c_uint64(base)

    for offset in offsets:
        kernel32.ReadProcessMemory(hProc, address, ctypes.byref(address), size, 0)
        address = ctypes.c_uint64(address.value + offset)

    return address.value

def patchBytes(handle, src, destination, size):
    src = bytes.fromhex(src)
    size = ctypes.c_size_t(size)
    destination = ctypes.c_ulonglong(destination)
    oldProtect = wintypes.DWORD()

    kernel32.VirtualProtectEx(handle, destination, size, PAGE_EXECUTE_READWRITE, ctypes.byref(oldProtect))
    kernel32.WriteProcessMemory(handle, destination, src, size, None)
    kernel32.VirtualProtectEx(handle, destination, size, oldProtect, ctypes.byref(oldProtect))

def nopBytes(handle, destination, size):
    hexString = "90" * size
    patchBytes(handle, hexString, destination, size)
