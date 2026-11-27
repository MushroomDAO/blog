"""Chinese front end for qora-voca-zh: text -> POLYGLOT phoneme tokens + tone feature.

Design (mirrors src/tiny_voca/text.py of upstream tiny-voca):
* Inventory = the 35 real phones of lyonlu13/wav2vec2-large-zh-singing-phoneme-ctc
  (POLYGLOT set, AISHELL-3 trained) + specials + CJK punctuation. One token =
  one recogniser label, so forced alignment works unchanged.
* The parallel "stress" feature carries the syllable TONE (0 neutral, 1..4).
  It goes on the vowel tokens of the syllable; model.stress Embedding is
  resized 3 -> 6 in the zh fork.
* pypinyin (phrase dictionary + tone-sandhi) is the pronunciation source.
  Polyphone errors beyond the dictionary are a known v1 limitation (g2pW later).
* Same token conventions as upstream: <bos> ... <eos>, <sp> between words,
  punctuation tokens may carry pauses and last zero frames.
"""
from dataclasses import dataclass
import hashlib
import json
import re
import unicodedata

FRONTEND_VERSION = 2
FRONTEND_NAME = "zh-pypinyin-polyglot"

PAD, BOS, EOS, SP, UNK = "<pad>", "<bos>", "<eos>", "<sp>", "<unk>"
SPECIALS = (PAD, BOS, EOS, SP, UNK)
PUNCTUATION = ("，", "。", "？", "！", "；", "：", "、", "…", "—", "“", "”", "（", "）")
# POLYGLOT real phones (vocab.json of the zh CTC recogniser, minus specials).
PHONES = ("p", "t", "k", "b", "d", "g", "ch", "jh", "ts", "dz",
          "f", "s", "sh", "zh", "h", "x", "m", "n", "ng", "l", "r",
          "w", "y", "a", "o", "e", "i", "u", "ü", "ae", "ir")
# 'x' is not in the 39-token vocab; see INITIAL_MAP: x -> hy (the palatal slot).
PHONES = tuple(p for p in PHONES if p != "x") + ("hy",)
# w/y are English-only glides in POLYGLOT; Mandarin zero-initial syllables
# start with i/u/ü directly, so drop them from the usable inventory.
# ae/hy carry no Mandarin training signal in this checkpoint (README note +
# greedy-decode verification), and the v2 maps never emit them: drop too.
PHONES = tuple(p for p in PHONES if p not in ("w", "y", "ae", "hy"))
SYMBOLS = SPECIALS + PUNCTUATION + PHONES
SYMBOL_TO_ID = {s: i for i, s in enumerate(SYMBOLS)}
PHONE_SET = frozenset(PHONES)
PHONE_IDS = frozenset(SYMBOL_TO_ID[p] for p in PHONES) | {SYMBOL_TO_ID[UNK]}
VOWEL_SET = frozenset(("a", "o", "e", "i", "u", "ü", "ir"))
# Unvoiced phones for the alignment QC voiced-share checks.
VOICELESS = frozenset(("p", "t", "k", "f", "s", "sh", "zh", "h", "ch", "ts"))
TONE_LEVELS = 6  # stress embedding size: 0 neutral + tones 1..4 (+1 spare)

# Empirically verified against the checkpoint's greedy decodes on AISHELL-style
# Mandarin (the README's POLYGLOT table is aspirational; several labels carry no
# Mandarin training signal). Observed mapping:
#   z(资)->dz  c(次)->ts  x(写)->sh  ai->a+i  eng->a+ng  ian->i+a+n
# ae / hy / ü-as-jqx are NOT emitted by this checkpoint for Mandarin.
INITIAL_MAP = {
    "b": ("b",), "p": ("p",), "m": ("m",), "f": ("f",),
    "d": ("d",), "t": ("t",), "n": ("n",), "l": ("l",),
    "g": ("g",), "k": ("k",), "h": ("h",),
    "j": ("jh",), "q": ("ch",), "x": ("sh",),
    "zh": ("zh",), "ch": ("ch",), "sh": ("sh",), "r": ("r",),
    "z": ("dz",), "c": ("ts",), "s": ("s",),
    "y": ("y",), "w": ("w",),
}
# pypinyin final (after y/w/jq/x normalisation) -> POLYGLOT vowel sequence.
# v2: ai->a+i, eng->a+ng, ian->i+a+n (verified against checkpoint decodes).
FINAL_MAP = {
    "a": ("a",), "o": ("o",), "e": ("e",), "i": ("i",), "u": ("u",), "v": ("ü",),
    "ai": ("a", "i"), "ei": ("e", "i"), "ao": ("a", "o"), "ou": ("o", "u"),
    "an": ("a", "n"), "en": ("e", "n"), "ang": ("a", "ng"), "eng": ("a", "ng"),
    "ong": ("o", "ng"), "er": ("ir",),
    "ia": ("i", "a"), "ie": ("i", "e"), "iao": ("i", "a", "o"), "iu": ("i", "u"),
    "ian": ("i", "a", "n"), "in": ("i", "n"), "iang": ("i", "a", "ng"),
    "ing": ("i", "ng"), "iong": ("i", "o", "ng"),
    "ua": ("u", "a"), "uo": ("u", "o"), "uai": ("u", "a", "i"), "ui": ("u", "e", "i"),
    "uan": ("u", "a", "n"), "un": ("u", "e", "n"), "uang": ("u", "a", "ng"),
    "ueng": ("u", "a", "ng"),
    "ve": ("ü", "e"), "van": ("ü", "a", "n"), "vn": ("ü", "n"),
    # pypinyin quirk: 'yo' (哟/唷) splits as y + o
    "io": ("i", "o"),
    # standalone syllables written with y/w by pypinyin TONE3 style
    "i": ("i",), "u": ("u",), "v": ("ü",),
}
# Whole-syllable overrides for y/w spellings pypinyin emits (style=TONE3 keeps
# the initial separate, but zero-initial syllables come as 'yi', 'wu', 'yu'...).
ZERO_INITIAL = {
    "yi": ("i",), "ya": ("i", "a"), "ye": ("i", "e"), "yao": ("i", "a", "o"),
    "you": ("i", "o", "u"), "yan": ("i", "a", "n"), "yin": ("i", "n"),
    "yang": ("i", "a", "ng"), "ying": ("i", "ng"), "yong": ("i", "o", "ng"),
    "yo": ("i", "o"),
    "wu": ("u",), "wa": ("u", "a"), "wo": ("u", "o"), "wai": ("u", "a", "i"),
    "wei": ("u", "e", "i"), "wan": ("u", "a", "n"), "wen": ("u", "e", "n"),
    "wang": ("u", "a", "ng"), "weng": ("u", "a", "ng"),
    "yu": ("ü",), "yue": ("ü", "e"), "yuan": ("ü", "a", "n"), "yun": ("ü", "n"),
    "a": ("a",), "o": ("o",), "e": ("e"), "ai": ("a", "i"), "ei": ("e", "i"),
    "ao": ("a", "o"), "ou": ("o", "u"), "an": ("a", "n"), "en": ("e", "n"),
    "ang": ("a", "ng"), "eng": ("a", "ng"), "er": ("ir",),
    # standalone nasal syllables (嗯/唔/呣...)
    "n": ("n",), "ng": ("ng",), "m": ("m",), "hng": ("h", "ng"), "hm": ("h", "m"),
    "ê": ("e",),
    }

_PUNCT_TRANSLATE = str.maketrans({
    ",": "，", ".": "。", "?": "？", "!": "！", ";": "；", ":": "：",
    "(": "（", ")": "）", '"': "”", "'": "”", "…": "…", "—": "—",
    "“": "“", "”": "”", "‘": "“", "’": "”",
})
_PUNCT_CHARS = frozenset(PUNCTUATION)
_CJK = re.compile(r"[\u4e00-\u9fff]")


class NothingToPronounce(ValueError):
    pass


@dataclass(frozen=True)
class Phonemized:
    symbols: tuple
    ids: tuple
    stress: tuple   # tone per token (0 for non-vowels/specials)
    unknown: tuple

    def __len__(self):
        return len(self.ids)


def frontend():
    return FRONTEND_NAME


def frontend_identity():
    return {"frontend_version": FRONTEND_VERSION, "phonemizer": "pypinyin",
            "symbols": list(SYMBOLS), "initial_map": {k: list(v) for k, v in sorted(INITIAL_MAP.items())},
            "final_map": {k: list(v) for k, v in sorted(FINAL_MAP.items())},
            "zero_initial": {k: list(v) for k, v in sorted(ZERO_INITIAL.items())}}


def frontend_runtime():
    import pypinyin
    return {"pypinyin_version": pypinyin.__version__}


def frontend_fingerprint():
    return hashlib.sha256(json.dumps(frontend_identity(), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def normalize_text(text):
    text = unicodedata.normalize("NFKC", text).translate(_PUNCT_TRANSLATE)
    text = re.sub(r"\.{3,}|。{3,}", "…", text)
    return re.sub(r"\s+", " ", text).strip()


def chunks(text):
    """Yield (is_punctuation, piece); CJK runs and latin/digit runs are pieces."""
    start, mode = 0, None
    for i, ch in enumerate(text):
        if ch in _PUNCT_CHARS:
            if text[start:i].strip():
                yield False, text[start:i].strip()
            yield True, ch
            start, mode = i + 1, None
            continue
        kind = "cjk" if _CJK.match(ch) else ("space" if ch.isspace() else "other")
        if mode is not None and kind != mode and kind != "space" and mode != "space":
            if text[start:i].strip():
                yield False, text[start:i].strip()
            start = i
        if kind != "space":
            mode = kind
    if text[start:].strip():
        yield False, text[start:].strip()


def _split_syllable(pinyin):
    """'zhong1' -> ('zh', 'ong', 1). pypinyin TONE3 output."""
    m = re.fullmatch(r"([a-zü]+?)([0-5])", pinyin)
    if not m:
        return None
    body, tone = m.group(1), int(m.group(2))
    tone = 0 if tone == 5 else tone
    for ini in ("zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n", "l",
                "g", "k", "h", "j", "q", "x", "r", "z", "c", "s", "y", "w"):
        if body.startswith(ini):
            return ini, body[len(ini):], tone
    return "", body, tone


def syllable_phones(pinyin):
    """One TONE3 pinyin syllable -> (phone tuple, tone). Raises KeyError if unmapped."""
    parts = _split_syllable(pinyin)
    if parts is None:
        raise KeyError(pinyin)
    ini, fin, tone = parts
    if ini in ("y", "w", ""):
        whole = ini + fin
        if whole in ZERO_INITIAL:
            return ZERO_INITIAL[whole], tone
        # j/q/x + ü-family finals: pypinyin writes u after j/q/x/y
        if ini in ("j", "q", "x") and fin.startswith("u"):
            fin = "v" + fin[1:]
    if ini in ("j", "q", "x") and fin.startswith("u"):
        fin = "v" + fin[1:]  # ju/qu/xu 的 u 实为 ü，走 v- 系映射
    if ini in ("y", "w"):
        ini = ""  # 其余 y/w 音节按零声母处理，滑音并入韵母首元音
    phones = INITIAL_MAP.get(ini, ())
    if fin not in FINAL_MAP:
        raise KeyError(pinyin)
    return phones + FINAL_MAP[fin], tone


def _piece_words(piece):
    """CJK piece -> list of syllable lists (jieba words); latin piece -> letters spoken."""
    from pypinyin import lazy_pinyin, Style
    import jieba
    if _CJK.search(piece):
        words = []
        for word in jieba.cut(piece):
            if not word.strip():
                continue
            if _CJK.search(word):
                pys = lazy_pinyin(word, style=Style.TONE3, neutral_tone_with_five=True, errors="ignore")
                syls = [p for p in pys if re.fullmatch(r"[a-zü]+[0-5]", p)]
                if syls:
                    words.append(syls)
            elif word.strip():
                words.append(list(word.strip()))
        return words
    # pure latin/digits: keep as one "word" of letter names is out of scope v1;
    # drop (corpus is Chinese sentences; digits get normalised upstream).
    return []


def tokenize(pieces):
    symbols, stress, unknown = [BOS], [0], []
    for punctuation, value in pieces:
        if punctuation:
            if symbols[-1] != value:
                symbols.append(value)
                stress.append(0)
            continue
        for word in value:
            if symbols[-1] in PHONE_SET or symbols[-1] == UNK:
                symbols.append(SP)
                stress.append(0)
            for syl in word:
                try:
                    phones, tone = syllable_phones(syl)
                except KeyError:
                    unknown.append(syl)
                    symbols.append(UNK)
                    stress.append(0)
                    continue
                for ph in phones:
                    symbols.append(ph)
                    stress.append(tone if ph in VOWEL_SET else 0)
    symbols.append(EOS)
    stress.append(0)
    if not any(s in PHONE_SET or s == UNK for s in symbols):
        raise NothingToPronounce("the text has nothing to pronounce")
    return Phonemized(tuple(symbols), tuple(SYMBOL_TO_ID[s] for s in symbols), tuple(stress), tuple(unknown))


def phonemize(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must not be empty")
    pieces = []
    for punctuation, piece in chunks(normalize_text(text)):
        if punctuation:
            pieces.append((True, piece))
        else:
            words = _piece_words(piece)
            if words:
                pieces.append((False, words))
    return tokenize(pieces)


def is_phone(token_ids):
    return [int(i) in PHONE_IDS for i in token_ids]
