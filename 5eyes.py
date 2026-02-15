#!/usr/bin/env python3
"""
Jack Of All Trade.....
"""

import os
import sys
import json
import time
import hmac
import base64
import math
import secrets
import hashlib
import getpass
import platform
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Optional imports (hardened)
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    CRYPTO_AVAILABLE = True
except ImportError:
    print("Missing pycryptodome. Install with: pip install pycryptodome")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Missing requests. Install with: pip install requests")
    sys.exit(1)

try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

# Color support
try:
    from colorama import init as colorama_init, Fore, Style, Back
    colorama_init(autoreset=True)
except ImportError:
    class _C:
        RESET_ALL = ""
    Fore = Style = Back = _C()
    Fore.RED = Fore.GREEN = Fore.YELLOW = Fore.CYAN = Fore.MAGENTA = Fore.WHITE = Fore.BLUE = ""
    Style.RESET_ALL = Back.BLACK = ""

# ----------------------------------
# Secure Paths & config
# ----------------------------------
HOME = Path.home()
VAULT_DIR = HOME / ".secret_intel_vault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR = VAULT_DIR / "exports"
EXPORT_DIR.mkdir(exist_ok=True)
KEY_DIR = VAULT_DIR / "keys"
KEY_DIR.mkdir(exist_ok=True)
GIB_FILE = VAULT_DIR / "gib_mapping.json"
CFG_FILE = VAULT_DIR / "config.json"
LOG_FILE = VAULT_DIR / "operations.log"
INTEGRITY_DB = VAULT_DIR / "integrity_db.json"
QR_DIR = VAULT_DIR / "qr"
QR_DIR.mkdir(exist_ok=True)

# Enhanced gibberish mapping (with new symbols)
DEFAULT_GIB = {
    'A': 'Śx9', 'B': 'Øqa', 'C': '∆r7', 'D': 'm₽2', 'E': 'ẞt0',
    'F': 'k∂Z', 'G': '¥nq', 'H': 'Ƨ3v', 'I': 'æL8', 'J': 'zu†',
    'K': 'Ⱥ5b', 'L': 'Ϟc1', 'M': 'pßX', 'N': 'Tø4', 'O': 'ωhE',
    'P': 'sπ0', 'Q': '⚑d9', 'R': 'Jµ7', 'S': 'ϟAx', 'T': 'q⟠8',
    'U': 'Ẏp3', 'V': 'e𝕍r', 'W': 'χ2N', 'X': 'Ŧg6', 'Y': 'VζQ', 'Z': 'ρU5',
    '~': '§1z', '`': '¬2a', '!': '¡3b', '@': '¡4c', '#': '¡5d', '$': '¡6e',
    '%': '¡7f', '^': '¡8g', '&': '¡9h', '*': '¡0i', '(': '¡1j', ')': '¡2k',
    '_': '¡3l', '-': '¡4m', '+': '¡5n', '=': '¡6o', '<': '¡7p', '>': '¡8q',
    '.': '¡9r', ',': '¡0s', '?': '¡1t', '/': '¡2u', '|': '¡3v', '"': '¡4w',
    "'": '¡5x', ':': '¡6y', ';': '¡7z', '{': '¡8a', '}': '¡9b', '[': '¡0c', ']': '¡1d',
    '0': 'Ω0a', '1': 'Ω1b', '2': 'Ω2c', '3': 'Ω3d', '4': 'Ω4e',
    '5': 'Ω5f', '6': 'Ω6g', '7': 'Ω7h', '8': 'Ω8i', '9': 'Ω9j', ' ': 'Ξsp'
}

# Morse table (official + extended)
MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': '/',
    '~': '...-..-', '`': '.-..-.', '!': '-.-.--', '@': '.--.-.', '#': '-..-.',
    '$': '...-..-', '%': '.-..-.', '^': '-....-', '&': '.-...', '*': '-..-',
    '(': '-.--.', ')': '-.--.-', '_': '..--.-', '-': '-....-', '+': '.-.-.',
    '=': '-...-', '<': '-..-..', '>': '-..-.', '.': '.-.-.-', ',': '--..--',
    '?': '..--..', '/': '-..-.', '|': '-...-', '"': '.-..-.', "'": '.----.',
    ':': '---...', ';': '-.-.-.', '{': '-.--.', '}': '-.--.-', '[': '-.--.',
    ']': '-.--.-'
}
MORSE_R = {v: k for k, v in MORSE.items()}

# OSINT sites
USERNAME_SITES = {
    "GitHub": "https://github.com/{u}",
    "Reddit": "https://www.reddit.com/user/{u}",
    "X": "https://x.com/{u}",
    "Instagram": "https://www.instagram.com/{u}/",
    "Keybase": "https://keybase.io/{u}",
    "Medium": "https://medium.com/@{u}",
    "Telegram": "https://t.me/{u}",
    "Twitch": "https://www.twitch.tv/{u}",
    "Pinterest": "https://www.pinterest.com/{u}/",
    "YouTube": "https://www.youtube.com/@{u}",
    "LinkedIn": "https://www.linkedin.com/in/{u}/"
}

# ----------------------------------
# Secure utilities
# ----------------------------------
def now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def log(op: str, msg: str = "") -> None:
    if "password" in msg.lower() or "key" in msg.lower():
        msg = "REDACTED"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now()}] [{op}] {msg}\n")
    except Exception:
        pass

def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg: str = "Press Enter to continue...") -> None:
    try:
        input(Fore.CYAN + msg + Style.RESET_ALL)
    except EOFError:
        pass

def read_json(path: Path, default: Any = None) -> Any:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default

def write_json(path: Path, data: Any) -> None:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"JSON write error: {e}")

def secure_delete(path: Path) -> None:
    if path.exists():
        with open(path, 'r+b') as f:
            sz = path.stat().st_size
            for _ in range(3):
                f.seek(0)
                f.write(os.urandom(sz))
                f.flush()
                os.fsync(f.fileno())
        path.unlink()

def wipe_memory(data: Any) -> None:
    if hasattr(data, 'clear'):
        data.clear()
    else:
        data = None

def sha256(data: Any) -> str:
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

# ----------------------------------
# AES helpers (hardened)
# ----------------------------------
BLOCK_SIZE = AES.block_size

def pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len]) * pad_len

def unpad(data: bytes) -> bytes:
    if len(data) == 0:
        return b""
    pad_len = data[-1]
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding")
    return data[:-pad_len]

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = get_random_bytes(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200000, dklen=32)
    return key, salt

def aes_encrypt(data: bytes, password: str) -> bytes:
    key, salt = derive_key(password)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data))
    return b"ENCv3" + salt + iv + ct

def aes_decrypt(blob: bytes, password: str) -> bytes:
    if not blob.startswith(b"ENCv"):
        raise ValueError("Invalid encrypted blob format")
    salt = blob[5:21]
    iv = blob[21:37]
    ct = blob[37:]
    key, _ = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct))

def encrypt_file(file_path: str, key_path: str) -> None:
    with open(file_path, 'rb') as f:
        data = f.read()
    password = read_json(Path(key_path))['password']
    encrypted = aes_encrypt(data, password)
    out_path = file_path + '.enc'
    with open(out_path, 'wb') as f:
        f.write(encrypted)
    print(f"File encrypted: {out_path}")

def decrypt_file(file_path: str, key_path: str) -> None:
    with open(file_path, 'rb') as f:
        data = f.read()
    password = read_json(Path(key_path))['password']
    decrypted = aes_decrypt(data, password)
    if file_path.endswith('.enc'):
        out_path = file_path[:-4]
    else:
        out_path = file_path + '.dec'
    with open(out_path, 'wb') as f:
        f.write(decrypted)
    print(f"File decrypted: {out_path}")

# ----------------------------------
# Gibberish cipher (enhanced)
# ----------------------------------
def load_gib() -> Dict[str, str]:
    mapping = read_json(GIB_FILE)
    if not mapping:
        mapping = DEFAULT_GIB.copy()
        write_json(GIB_FILE, mapping)
    return mapping

def save_gib(mapping: Dict[str, str]) -> None:
    write_json(GIB_FILE, mapping)

def text_to_gib(text: str, mapping: Dict[str, str]) -> str:
    text = text.upper()
    tokens = []
    for ch in text:
        if ch in mapping:
            tokens.append(mapping[ch])
        else:
            tokens.append(ch)
    return ' '.join(tokens)

def gib_to_text(gib_str: str, mapping: Dict[str, str]) -> str:
    rev_map = {v: k for k, v in mapping.items()}
    tokens = gib_str.split()
    result = []
    for token in tokens:
        if token in rev_map:
            result.append(rev_map[token])
        else:
            result.append('?')
    return ''.join(result)

# ----------------------------------
# Morse (enhanced)
# ----------------------------------
def encode_morse(text: str) -> str:
    text = text.upper()
    words = []
    for word in text.split(' '):
        letters = [MORSE.get(c, '<?>') for c in word]
        words.append(' '.join(letters))
    return '   '.join(words)

def decode_morse(morse: str) -> str:
    words = morse.strip().split('   ')
    result = []
    for word in words:
        letters = [MORSE_R.get(symbol.strip(), '?') for symbol in word.split()]
        result.append(''.join(letters))
    return ' '.join(result)

# ----------------------------------
# Hashing & Integrity (enhanced)
# ----------------------------------
def hash_data(data: bytes, algo: str = 'sha256') -> str:
    algos = {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha256': hashlib.sha256(),
        'sha512': hashlib.sha512()
    }
    h = algos.get(algo.lower(), hashlib.sha256())
    h.update(data)
    return h.hexdigest()

def hash_file(path: str, algo: str = 'sha256') -> str:
    if algo.lower() == 'md5':
        h = hashlib.md5()
    elif algo.lower() == 'sha1':
        h = hashlib.sha1()
    elif algo.lower() == 'sha512':
        h = hashlib.sha512()
    else:
        h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def load_integrity_db() -> Dict[str, Any]:
    return read_json(INTEGRITY_DB, default={})

def index_folder(folder: str) -> int:
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(f'Folder not found: {folder}')
    db = load_integrity_db()
    added = 0
    for file_path in folder_path.rglob('*'):
        if file_path.is_file():
            file_hash = hash_file(str(file_path))
            db[str(file_path)] = {
                'hash': file_hash,
                'mtime': file_path.stat().st_mtime
            }
            added += 1
    write_json(INTEGRITY_DB, db)
    return added

def scan_folder_changes() -> list[tuple[str, str]]:
    db = load_integrity_db()
    alerts = []
    for file_path, meta in list(db.items()):
        path = Path(file_path)
        if not path.exists():
            alerts.append((file_path, 'DELETED'))
            continue
        new_hash = hash_file(file_path)
        if new_hash != meta['hash']:
            alerts.append((file_path, 'MODIFIED'))
    return alerts

# ----------------------------------
# Password tools (enhanced)
# ----------------------------------
def password_strength(password: str) -> Dict[str, Any]:
    charset_sizes = sum([
        26 if re.search(r'[a-z]', password) else 0,
        26 if re.search(r'[A-Z]', password) else 0,
        10 if re.search(r'[0-9]', password) else 0,
        32 if re.search(r'[^A-Za-z0-9]', password) else 0
    ])
    if charset_sizes == 0:
        return {'entropy': 0.0, 'score': 'EMPTY'}
    entropy = round(len(password) * math.log2(charset_sizes), 2)
    if len(password) < 6 or password.lower() in {'password', '123456', 'qwerty'}:
        score = 'VERY WEAK'
    elif entropy < 28:
        score = 'WEAK'
    elif entropy < 50:
        score = 'MODERATE'
    elif entropy < 80:
        score = 'STRONG'
    else:
        score = 'VERY STRONG'
    return {'entropy': entropy, 'score': score, 'length': len(password)}

def generate_password(length: int = 16, upper: bool = True, digits: bool = True, symbols: bool = True) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyz'
    if upper:
        chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if digits:
        chars += '0123456789'
    if symbols:
        chars += '@#$%^&*()_+-=[]{}|;:,.<>?'
    if length <= 0:
        length = 1
    return ''.join(secrets.choice(chars) for _ in range(length))

# ----------------------------------
# Encoding/Decoding tools
# ----------------------------------
def base64_encode(text: str) -> str:
    return base64.b64encode(text.encode('utf-8')).decode('ascii')

def base64_decode(text: str) -> str:
    try:
        return base64.b64decode(text.encode('ascii')).decode('utf-8', errors='replace')
    except Exception:
        return "Invalid Base64"

def rot13(text: str) -> str:
    trans = str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
    )
    return text.translate(trans)

def rot5(text: str) -> str:
    result = []
    for char in text:
        if char.isdigit():
            result.append(str((int(char) + 5) % 10))
        else:
            result.append(char)
    return ''.join(result)

def rot5_decode(text: str) -> str:
    result = []
    for char in text:
        if char.isdigit():
            result.append(str((int(char) - 5) % 10))
        else:
            result.append(char)
    return ''.join(result)

def rot47(text: str) -> str:
    result = []
    for char in text:
        ord_val = ord(char)
        if 33 <= ord_val <= 126:
            result.append(chr(33 + ((ord_val - 33 + 47) % 94)))
        else:
            result.append(char)
    return ''.join(result)

def caesar_encode(text: str, shift: int = 13) -> str:
    result = []
    shift = shift % 26
    for char in text:
        if char.isupper():
            result.append(chr((ord(char) - 65 + shift) % 26 + 65))
        elif char.islower():
            result.append(chr((ord(char) - 97 + shift) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)

def caesar_decode(text: str, shift: int = 13) -> str:
    result = []
    shift = shift % 26
    for char in text:
        if char.isupper():
            result.append(chr((ord(char) - 65 - shift) % 26 + 65))
        elif char.islower():
            result.append(chr((ord(char) - 97 - shift) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)

# Hex/Binary converters
def text_to_hex(text: str) -> str:
    return text.encode('utf-8').hex()

def hex_to_text(hex_str: str) -> str:
    try:
        return bytes.fromhex(hex_str).decode('utf-8', errors='replace')
    except Exception:
        return "Invalid hex"

def text_to_binary(text: str) -> str:
    return ' '.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binary_to_text(binary_str: str) -> str:
    try:
        binary = binary_str.replace(' ', '')
        bytes_data = bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
        return bytes_data.decode('utf-8', errors='replace')
    except Exception:
        return "Invalid binary"

# File decoding
def decode_file(file_path: str, decode_func) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return decode_func(content)
    except Exception as e:
        return f"Error reading file: {e}"

# ----------------------------------
# Timestamp converter
# ----------------------------------
def timestamp_to_datetime(ts: str) -> str:
    try:
        dt = datetime.utcfromtimestamp(float(ts))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "Invalid timestamp"

def datetime_to_timestamp(dt_str: str) -> str:
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            return str(int(dt.timestamp()))
        except Exception:
            continue
    return "Invalid date format"

# HTTP Header formatter
def format_http_headers(raw_headers: str) -> str:
    cleaned = re.sub(r'\\n|\r', '\n', raw_headers)
    lines = re.split(r'\n(?=[A-Z][a-z]+:)', cleaned)
    return '\n'.join(line.strip() for line in lines if line.strip())

# Device fingerprint
def device_fingerprint() -> str:
    info = f"{platform.node()}|{platform.system()}|{platform.processor()}|{platform.machine()}"
    return sha256(info.encode())

# TOTP/HOTP
def hotp(key: bytes, counter: int, digits: int = 6) -> str:
    msg = counter.to_bytes(8, 'big')
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0f
    code = int.from_bytes(h[offset:offset+4], 'big') & 0x7fffffff
    return str(code % (10**digits)).zfill(digits)

def totp(key: bytes, time_step: int = 30, digits: int = 6) -> str:
    counter = int(time.time() // time_step)
    return hotp(key, counter, digits)

def base32_to_bytes(secret: str) -> bytes:
    secret = secret.replace(' ', '').upper()
    padding = '=' * ((8 - len(secret) % 8) % 8)
    return base64.b32decode(secret + padding)

# OSINT username checker
def check_username(username: str, timeout: int = 5) -> Dict[str, Optional[str]]:
    headers = {'User-Agent': 'Mozilla/5.0 (SecretIntel/5.1)'}
    results: Dict[str, Optional[str]] = {}
    for platform_name, url_template in USERNAME_SITES.items():
        url = url_template.format(u=username)
        try:
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            status = response.status_code
            if status == 200:
                results[platform_name] = url
                continue
            if status == 404:
                results[platform_name] = None
                continue
            response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            if response.status_code == 200:
                results[platform_name] = url
            else:
                results[platform_name] = None
        except Exception:
            results[platform_name] = None
    return results

# QR Code generator
def generate_qr(data: str, filename: Optional[str] = None) -> str:
    if not QR_AVAILABLE:
        raise RuntimeError("QR libraries not available (install qrcode[pil])")
    if not filename:
        timestamp = int(time.time())
        filename = f"qr_{timestamp}.png"
    qr_path = QR_DIR / filename
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)
    return str(qr_path)

# AI-powered keyword extraction (basic)
def extract_keywords(text: str) -> list:
    words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return sorted(freq.keys(), key=lambda x: freq[x], reverse=True)[:10]

# Metadata extractor (simple)
def extract_metadata(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError("File not found")
    stat = p.stat()
    meta = {
        "path": str(p),
        "size_bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "sha256": hash_file(str(p), "sha256"),
        "md5": hash_file(str(p), "md5")
    }
    return meta

# ----------------------------------
# Master password: set once, then login forever
# ----------------------------------
def setup_master_password() -> str:
    """
    Hardened master password logic:
    - Password is set ONLY ONCE
    - Later runs ONLY ask for login
    - Panic mode does NOT remove password
    """

    config = read_json(CFG_FILE, default={})

    # ------------------------------
    # FIRST TIME SETUP
    # ------------------------------
    if not config.get("initialized", False):
        print(Fore.YELLOW + "🔐 First-time setup: Create master password" + Style.RESET_ALL)

        while True:
            pwd1 = getpass.getpass("Set master password (min 8 chars): ")
            pwd2 = getpass.getpass("Confirm master password: ")

            if pwd1 != pwd2:
                print(Fore.RED + "❌ Passwords do not match" + Style.RESET_ALL)
                continue

            if len(pwd1) < 8:
                print(Fore.RED + "❌ Password too short" + Style.RESET_ALL)
                continue

            config = {
                "master_hash": sha256(pwd1),
                "initialized": True,
                "created_at": datetime.utcnow().isoformat()
            }

            write_json(CFG_FILE, config)
            log("AUTH_SETUP", "Master password initialized")

            print(Fore.GREEN + "✓ Master password set successfully!" + Style.RESET_ALL)
            return pwd1

    # ------------------------------
    # LOGIN MODE
    # ------------------------------
    print(Fore.CYAN + "🔐 Enter master password" + Style.RESET_ALL)

    for attempt in range(3):
        pwd = getpass.getpass("Password: ")
        if secrets.compare_digest(sha256(pwd), config.get("master_hash", "")):
            log("AUTH_SUCCESS", "Master login OK")
            return pwd
        else:
            print(Fore.RED + "❌ Incorrect password" + Style.RESET_ALL)

    log("AUTH_LOCKOUT", "3 failed attempts")
    print(Fore.RED + "Too many failed attempts. Exiting." + Style.RESET_ALL)
    sys.exit(1)

    # New user: first and ONLY time we set a master password here
    print(Fore.YELLOW + "No master password set. Create one now." + Style.RESET_ALL)
    while True:
        pwd1 = getpass.getpass("Set new master password: ")
        pwd2 = getpass.getpass("Confirm new master password: ")

        if pwd1 != pwd2:
            print(Fore.RED + "❌ Passwords do not match" + Style.RESET_ALL)
            continue

        if len(pwd1) < 8:
            print(Fore.RED + "❌ Password too short (min 8 chars)" + Style.RESET_ALL)
            continue

        config['master_hash'] = sha256(pwd1)
        write_json(CFG_FILE, config)
        log("AUTH_SETUP", "New master password created")
        print(Fore.GREEN + "✓ Master password set successfully!" + Style.RESET_ALL)
        return pwd1

# ----------------------------------
# CLI Modules
# ----------------------------------
def banner() -> None:
    clear_screen()
    print(Fore.CYAN + "="*80 + Style.RESET_ALL)
    print(Fore.CYAN + " " * 25 + "SECRET INTELLIGENCE TOOL v5.1" + " " * 25 + Style.RESET_ALL)
    print(Fore.CYAN + " " * 30 + "Advanced for Intelligence Prep" + " " * 30 + Style.RESET_ALL)
    print(Fore.CYAN + " " * 35 + "Developed by: cyph3r (RG)" + " " * 35 + Style.RESET_ALL)
    print(Fore.CYAN + "="*80 + Style.RESET_ALL)
    print(Fore.YELLOW + f"[!] Device ID: {device_fingerprint()[:16]}..." + Style.RESET_ALL)
    print()

def main_menu() -> None:
    print(Fore.GREEN + "[1]" + Style.RESET_ALL + "  Gibberish Cipher (Encode/Decode)")
    print(Fore.GREEN + "[2]" + Style.RESET_ALL + "  Morse Code (Encode/Decode)")
    print(Fore.GREEN + "[3]" + Style.RESET_ALL + "  AES-256 Vault")
    print(Fore.GREEN + "[4]" + Style.RESET_ALL + "  Hashing & File Integrity")
    print(Fore.GREEN + "[5]" + Style.RESET_ALL + "  Encodings (Base64/ROT)")
    print(Fore.GREEN + "[6]" + Style.RESET_ALL + "  QR Codes & OTP")
    print(Fore.GREEN + "[7]" + Style.RESET_ALL + "  Password Generator")
    print(Fore.GREEN + "[8]" + Style.RESET_ALL + "  Metadata Extractor")
    print(Fore.GREEN + "[9]" + Style.RESET_ALL + "  OSINT Username Check")
    print(Fore.GREEN + "[10]" + Style.RESET_ALL + " File Monitor")
    print(Fore.GREEN + "[11]" + Style.RESET_ALL + " Hex/Binary Convert")
    print(Fore.GREEN + "[12]" + Style.RESET_ALL + " Timestamp Converter")
    print(Fore.GREEN + "[13]" + Style.RESET_ALL + " HTTP Headers")
    print(Fore.GREEN + "[14]" + Style.RESET_ALL + " Decode Base64/ROT/Hex/Binary/Caesar")
    print(Fore.GREEN + "[15]" + Style.RESET_ALL + " Encrypt File")
    print(Fore.GREEN + "[16]" + Style.RESET_ALL + " Decrypt File")
    print(Fore.GREEN + "[17]" + Style.RESET_ALL + " AI Keyword Extractor")
    print(Fore.RED + " [s]" + Style.RESET_ALL + " Stealth Mode")
    print(Fore.RED + " [p]" + Style.RESET_ALL + " Panic (Ctrl+C)")
    print(Fore.GREEN + " [h]" + Style.RESET_ALL + " Help  " + Fore.GREEN + "[q]" + Style.RESET_ALL + " Quit")

# ----------------------------------
# Stealth mode (forgiving)
# ----------------------------------
def stealth_calculator() -> bool:
    clear_screen()
    print(Fore.WHITE + Back.BLUE + "SimpleCalc v5.1 - Educational Tool" + Style.RESET_ALL)
    print("Type :unlock opensesame to access full features")
    while True:
        try:
            cmd = input("calc> ").strip()

            if cmd.lower().strip() in {":unlock opensesame", "unlock opensesame", "unlock"}:
                print(Fore.GREEN + "Access granted!" + Style.RESET_ALL)
                return True

            elif cmd.lower() in ("exit", "quit", "q"):
                return False

            elif cmd:
                if re.fullmatch(r"[0-9+\-*/(). ]+", cmd):
                    try:
                        result = eval(cmd, {"__builtins__": {}})
                        print(result)
                    except Exception:
                        print("Invalid expression")
                else:
                    print("Invalid expression")
        except (KeyboardInterrupt, EOFError):
            return False

# ----------------------------------
# Panic
# ----------------------------------
def panic_exit():
    """
    Emergency panic exit:
    - Clears logs and volatile files
    - Preserves master password
    - Exits safely
    """
    try:
        clear_screen()
        print("SYSTEM MAINTENANCE MODE")
        print("Clearing operational traces...")

        log("PANIC", "Emergency panic triggered")

        # ❌ DO NOT delete CFG_FILE
        for file in [LOG_FILE, GIB_FILE, INTEGRITY_DB]:
            try:
                if file.exists():
                    secure_delete(file)
            except Exception:
                pass

    finally:
        # Safe, clean termination
        raise SystemExit(0)


# ----------------------------------
# Main execution
# ----------------------------------
def main() -> None:
    mapping = load_gib()
    master_pwd = setup_master_password()
    print(Fore.GREEN + "✓ Initialization complete!" + Style.RESET_ALL)
    log("STARTUP", f"Session started on {device_fingerprint()}")

    while True:
        try:
            banner()
            main_menu()
            choice = input(Fore.WHITE + "\nSelect > " + Style.RESET_ALL).strip().lower()

            if choice == 'q':
                print(Fore.GREEN + "Secure exit. Session logged." + Style.RESET_ALL)
                log("SHUTDOWN", "Normal exit")
                break

            elif choice == 'h':
                clear_screen()
                print("HELP - SECRET INTELLIGENCE TOOL v5.1\n")
                print("1  Gibberish Cipher:")
                print("   - Encode: Plain text -> custom gibberish tokens.")
                print("   - Decode: Gibberish tokens -> plain text.\n")
                print("2  Morse Code:")
                print("   - Encode: Text -> Morse code (with / between words).")
                print("   - Decode: Morse code -> text.\n")
                print("3  AES-256 Vault:")
                print("   - Encrypt text to a Base64 blob using AES-256.")
                print("   - Decrypt a Base64 blob back to plaintext.\n")
                print("4  Hashing & File Integrity:")
                print("   - Hash file: md5/sha1/sha256/sha512.")
                print("   - Index folder: store hashes for all files.")
                print("   - Scan changes: detect modified/deleted files.\n")
                print("5  Encodings (Base64/ROT):")
                print("   - Show Base64, ROT13, ROT5, ROT47 for given text.\n")
                print("6  QR Codes & OTP:")
                print("   - Generate QR code PNG for any text.")
                print("   - Generate TOTP from Base32 secret.\n")
                print("7  Password Generator:")
                print("   - Create random strong password and show entropy.\n")
                print("8  Metadata Extractor:")
                print("   - Show size, timestamps, hashes of a file.\n")
                print("9  OSINT Username Check:")
                print("   - Check major platforms for a username and show URLs if found.\n")
                print("10 File Monitor:")
                print("   - Index folder and quickly detect changes later.\n")
                print("13 Hex/Binary Convert:")
                print("   - Text -> Hex + binary representation.\n")
                print("14 Timestamp Converter:")
                print("   - Timestamp -> human datetime.")
                print("   - Datetime -> Unix timestamp.\n")
                print("15 HTTP Headers:")
                print("   - Clean and format raw HTTP headers for readability.\n")
                print("16 Decode Center:")
                print("   - Decode Base64, ROT13, ROT5, ROT47, Caesar, Hex, Binary.\n")
                print("17 Encrypt File:")
                print("   - AES-256-CBC encrypt a file (.enc output) using a named key.\n")
                print("18 Decrypt File:")
                print("   - Decrypt a previously encrypted .enc file using the same key name.\n")
                print("19 AI Keyword Extractor:")
                print("   - Extract top keywords from a block of text by frequency.\n")
                print("[p] Panic:")
                print("   - Emergency exit that attempts to securely wipe config/log traces.\n")
                print("[s] Stealth Mode:")
                print("   - Switches to a simple educational-looking interface.\n")
                pause()

            elif choice == 's':
                if stealth_calculator():
                    continue

            elif choice == 'p':
                panic_exit()

            elif choice == '1':
                print("1. Encode to Gibberish")
                print("2. Decode from Gibberish")
                sub = input("Choose > ").strip()
                if sub == '1':
                    text = input("Enter text: ")
                    result = text_to_gib(text, mapping)
                    print("Gibberish:", result)
                elif sub == '2':
                    text = input("Enter gibberish text: ")
                    result = gib_to_text(text, mapping)
                    print("Plain:", result)
                else:
                    print("Invalid choice")
                pause()

            elif choice == '2':
                print("1. Encode to Morse")
                print("2. Decode from Morse")
                sub = input("Choose > ").strip()
                if sub == '1':
                    text = input("Enter text: ")
                    result = encode_morse(text)
                    print("Morse:", result)
                elif sub == '2':
                    text = input("Enter Morse: ")
                    result = decode_morse(text)
                    print("Plain:", result)
                else:
                    print("Invalid choice")
                pause()

            elif choice == '3':
                print("1. Encrypt text")
                print("2. Decrypt text")
                sub = input("Choose > ").strip()
                if sub == '1':
                    data_str = input("Enter data to encrypt: ")
                    data = data_str.encode('utf-8')
                    password = getpass.getpass("Enter password: ")
                    if not data:
                        print("No data entered, nothing to encrypt.")
                    else:
                        encrypted = aes_encrypt(data, password)
                        print("Encrypted (Base64):", base64.b64encode(encrypted).decode('ascii'))
                elif sub == '2':
                    b64 = input("Enter Base64 encrypted blob: ")
                    password = getpass.getpass("Enter password: ")
                    try:
                        blob = base64.b64decode(b64.encode('ascii'))
                        decrypted = aes_decrypt(blob, password)
                        print("Decrypted:", decrypted.decode('utf-8', errors='replace'))
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Invalid choice")
                pause()

            elif choice == '4':
                print("1. Hash file")
                print("2. Index folder")
                print("3. Scan indexed changes")
                sub = input("Choose > ").strip()
                if sub == '1':
                    path = input("Enter file path to hash: ")
                    algo = input("Enter hashing algo (md5, sha1, sha256, sha512): ")
                    try:
                        h = hash_file(path, algo)
                        print(f"Hash ({algo}): {h}")
                    except Exception as e:
                        print(f"Error: {e}")
                elif sub == '2':
                    folder = input("Enter folder path to index: ")
                    try:
                        added = index_folder(folder)
                        print(f"Indexed {added} files.")
                    except Exception as e:
                        print(f"Error: {e}")
                elif sub == '3':
                    changes = scan_folder_changes()
                    if not changes:
                        print("No changes detected.")
                    else:
                        for file, status in changes:
                            print(f"{file}: {status}")
                else:
                    print("Invalid choice")
                pause()

            elif choice == '5':
                text = input("Enter text: ")
                print("Base64:", base64_encode(text))
                print("ROT13:", rot13(text))
                print("ROT5:", rot5(text))
                print("ROT47:", rot47(text))
                pause()

            elif choice == '6':
                print("1. Generate QR from text")
                print("2. Generate TOTP from Base32 secret")
                sub = input("Choose > ").strip()
                if sub == '1':
                    data = input("Enter data for QR: ").strip()
                    if not data:
                        print("No data, QR not generated.")
                    else:
                        try:
                            path = generate_qr(data)
                            print(f"QR saved at: {path}")
                        except Exception as e:
                            print(f"Error: {e}")
                elif sub == '2':
                    secret = input("Enter Base32 secret: ")
                    try:
                        key = base32_to_bytes(secret)
                        code = totp(key)
                        print("Current TOTP:", code)
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Invalid choice")
                pause()

            elif choice == '7':
                try:
                    length = int(input("Password length: "))
                except ValueError:
                    length = 16
                pwd = generate_password(length)
                info = password_strength(pwd)
                print("Generated password:", pwd)
                print(f"Entropy: {info['entropy']} bits, Strength: {info['score']}")
                pause()

            elif choice == '8':
                path = input("Enter file path: ")
                try:
                    meta = extract_metadata(path)
                    print(json.dumps(meta, indent=2))
                except Exception as e:
                    print(f"Error: {e}")
                pause()

            elif choice == '9':
                username = input("Enter username: ")
                results = check_username(username)
                for platform_name, url in results.items():
                    if url:
                        print(f"{platform_name}: Found -> {url}")
                    else:
                        print(f"{platform_name}: Not found / Error")
                pause()

            elif choice == '10':
                folder = input("Enter folder path to monitor/index: ")
                try:
                    added = index_folder(folder)
                    print(f"Indexed {added} files.")
                    changes = scan_folder_changes()
                    if changes:
                        print("Detected changes:")
                        for file, status in changes:
                            print(f"{file}: {status}")
                    else:
                        print("No changes detected.")
                except Exception as e:
                    print(f"Error: {e}")
                pause()

            elif choice == '13':
                text = input("Enter text: ")
                print("Hex:", text_to_hex(text))
                print("Binary:", text_to_binary(text))
                pause()

            elif choice == '14':
                print("1. Timestamp -> Datetime")
                print("2. Datetime -> Timestamp")
                sub = input("Choose > ").strip()
                if sub == '1':
                    ts = input("Enter timestamp: ")
                    print("Datetime:", timestamp_to_datetime(ts))
                elif sub == '2':
                    dt = input("Enter datetime (YYYY-MM-DD [HH:MM[:SS]]): ")
                    print("Timestamp:", datetime_to_timestamp(dt))
                else:
                    print("Invalid choice")
                pause()

            elif choice == '15':
                headers = input("Enter raw headers: ")
                print("Formatted:\n", format_http_headers(headers))
                pause()

            elif choice == '16':
                print("Select decode type:")
                print("1. Base64")
                print("2. ROT13")
                print("3. ROT5")
                print("4. ROT47")
                print("5. Caesar")
                print("6. Hex")
                print("7. Binary")
                sub_choice = input("Choose > ").strip()
                text = input("Enter text to decode: ")
                if sub_choice == '1':
                    result = base64_decode(text)
                elif sub_choice == '2':
                    result = rot13(text)
                elif sub_choice == '3':
                    result = rot5_decode(text)
                elif sub_choice == '4':
                    result = rot47(text)
                elif sub_choice == '5':
                    try:
                        shift = int(input("Enter shift: "))
                    except ValueError:
                        shift = 13
                    result = caesar_decode(text, shift)
                elif sub_choice == '6':
                    result = hex_to_text(text)
                elif sub_choice == '7':
                    result = binary_to_text(text)
                else:
                    result = "Invalid choice"
                print("Decoded:", result)
                pause()

            elif choice == '17':
                file_path = input("Enter file path to encrypt: ")
                key_name = input("Enter key name: ")
                key_path = KEY_DIR / f"{key_name}.json"
                password = getpass.getpass("Enter password for key: ")
                write_json(key_path, {'password': password})
                try:
                    encrypt_file(file_path, key_path)
                except Exception as e:
                    print(f"Error: {e}")
                pause()

            elif choice == '18':
                file_path = input("Enter encrypted file path (.enc): ")
                key_name = input("Enter key name: ")
                key_path = KEY_DIR / f"{key_name}.json"
                try:
                    decrypt_file(file_path, key_path)
                except Exception as e:
                    print(f"Error: {e}")
                pause()

            elif choice == '19':
                text = input("Enter text for keyword extraction: ")
                keywords = extract_keywords(text)
                print("Top keywords:", ', '.join(keywords))
                pause()

            else:
                print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)
                pause()

        except KeyboardInterrupt:
            print("\n" + Fore.RED + "PANIC triggered!" + Style.RESET_ALL)
            panic_exit()
        except Exception as e:
            log("CRASH", str(e))
            print(Fore.RED + f"Fatal error: {e}" + Style.RESET_ALL)
            sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        panic_exit()
    except Exception as e:
        log("CRASH", str(e))
        print(Fore.RED + f"Fatal error: {e}" + Style.RESET_ALL)
        sys.exit(1)
