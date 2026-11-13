"""Self-contained ctypes bindings for Windows IMM32 input method state.

This widget must not modify YASB's core win32 modules, so the declarations it
needs on top of what ``core.utils.win32`` already provides (IMM32 functions,
GetGUIThreadInfo, SendMessageTimeoutW and the IME constants) live here. A
private user32 handle is used so none of these declarations can interfere
with the ones registered by YASB itself.
"""

import ctypes
from ctypes import POINTER, WinDLL, byref
from ctypes.wintypes import BOOL, DWORD, HANDLE, HWND, LONG, LPARAM, UINT, WPARAM, c_size_t

# IME message and conversion mode constants
WM_IME_CONTROL = 0x0283
IMC_GETCONVERSIONMODE = 0x0001
IMC_GETSENTENCEMODE = 0x0003
IMC_GETOPENSTATUS = 0x0005
IME_CMODE_NATIVE = 0x0001
IME_CMODE_KATAKANA = 0x0002
IME_CMODE_FULLSHAPE = 0x0008
IME_CMODE_ROMAN = 0x0010
IME_CMODE_CHARCODE = 0x0020
IME_CMODE_HANJACONVERT = 0x0040
IME_CMODE_SOFTKBD = 0x0080
IME_CMODE_NOCONVERSION = 0x0100
IME_CMODE_EUDC = 0x0200
IME_CMODE_SYMBOL = 0x0400
IME_CMODE_FIXED = 0x0800
SMTO_ABORTIFHUNG = 0x0002

# Timeout for WM_IME_CONTROL queries against the default IME window
IME_TIMEOUT_MS = 30

# ---------------------------------------------------------------------------
# imm32 (Input Method Manager)
# ---------------------------------------------------------------------------
imm32 = WinDLL("imm32", use_last_error=True)

imm32.ImmGetDefaultIMEWnd.argtypes = [HWND]
imm32.ImmGetDefaultIMEWnd.restype = HWND

imm32.ImmGetContext.argtypes = [HWND]
imm32.ImmGetContext.restype = HANDLE

imm32.ImmReleaseContext.argtypes = [HWND, HANDLE]
imm32.ImmReleaseContext.restype = BOOL

imm32.ImmGetOpenStatus.argtypes = [HANDLE]
imm32.ImmGetOpenStatus.restype = BOOL

imm32.ImmGetConversionStatus.argtypes = [HANDLE, POINTER(DWORD), POINTER(DWORD)]
imm32.ImmGetConversionStatus.restype = BOOL

# ---------------------------------------------------------------------------
# user32 additions (private handle, separate from the one in core bindings)
# ---------------------------------------------------------------------------


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", LONG),
        ("top", LONG),
        ("right", LONG),
        ("bottom", LONG),
    ]


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("flags", DWORD),
        ("hwndActive", HWND),
        ("hwndFocus", HWND),
        ("hwndCapture", HWND),
        ("hwndMenuOwner", HWND),
        ("hwndMoveSize", HWND),
        ("hwndCaret", HWND),
        ("rcCaret", RECT),
    ]


_user32 = WinDLL("user32", use_last_error=True)

_user32.GetGUIThreadInfo.argtypes = [DWORD, POINTER(GUITHREADINFO)]
_user32.GetGUIThreadInfo.restype = BOOL

# lpdwResult must be POINTER(c_size_t); a c_ulong reference is rejected by
# ctypes on 64-bit Windows.
_user32.SendMessageTimeoutW.argtypes = [HWND, UINT, WPARAM, LPARAM, UINT, UINT, POINTER(c_size_t)]
_user32.SendMessageTimeoutW.restype = LPARAM


def get_focused_hwnd(thread_id: int) -> int | None:
    """Return the focused (or active) window handle of the given thread."""
    if not thread_id:
        return None

    gui_thread_info = GUITHREADINFO()
    gui_thread_info.cbSize = ctypes.sizeof(GUITHREADINFO)
    if _user32.GetGUIThreadInfo(thread_id, byref(gui_thread_info)):
        return gui_thread_info.hwndFocus or gui_thread_info.hwndActive or None
    return None


def send_ime_control(ime_hwnd: int, command: int) -> int | None:
    """Send WM_IME_CONTROL and return its result, or None when it fails."""
    result = c_size_t()
    sent = _user32.SendMessageTimeoutW(
        ime_hwnd,
        WM_IME_CONTROL,
        command,
        0,
        SMTO_ABORTIFHUNG,
        IME_TIMEOUT_MS,
        byref(result),
    )
    return result.value if sent else None
