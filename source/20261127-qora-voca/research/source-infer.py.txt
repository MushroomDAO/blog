import argparse
import os
from pathlib import Path
import re
import torch
from .config import CHECKPOINT_FORMAT, Config
from .model import TinyVoca, UtteranceTooLong
from .text import FRONTEND_VARIABLE, FRONTENDS, NothingToPronounce, frontend_fingerprint, phonemize, set_frontend

# The loudest sample of the audio that ``speak_text`` and the command return.
PEAK = 0.99
# Said when no sentence of a text could be read.
CHINESE_ONLY = "qora-voca-zh 只朗读中文。这段文本没有可朗读的中文内容，未生成音频文件。"
ENGLISH_ONLY = CHINESE_ONLY  # kept under the upstream name for callers
_SPACE = re.compile("[\\s" + chr(0xFEFF) + "]+")    # JavaScript's \s, which the demo uses, takes U+FEFF too
_SENTENCE_END = re.compile(r"(?<=[。！？…])")
_NOT_AN_END = re.compile(r"(?:\b(?:mr|mrs|ms|dr|prof|sr|jr|st|vs|etc|no|inc|ltd|co|e\.g|i\.e|a\.m|p\.m)|\b[A-Z])\.$",
                         re.IGNORECASE | re.ASCII)
_CLAUSE_END = re.compile(r"(?<=[，；：、—])")
_TEXT_END = re.compile("[\\s" + chr(0xFEFF) + "]+$")
_CLOSING = "\"'”’)]»"                               # these may stand after the last mark: She said "go!"


def load_model(path, device="cpu", check_frontend=True):
    """``check_frontend=False`` lets a checkpoint speak tokens of the other
    front end (same inventory, slightly different conventions): for listening
    tests of the new phonemizer before the model is retrained on it."""
    state = torch.load(path, map_location="cpu", weights_only=True)
    if state.get("format_version") != CHECKPOINT_FORMAT:
        raise ValueError("unsupported checkpoint format: byte-token checkpoints (format 2-3) cannot be used with this code")
    if check_frontend and state["frontend"]["fingerprint"] != frontend_fingerprint():
        raise ValueError("checkpoint was trained with a different phoneme inventory/front end")
    model = TinyVoca(Config.from_dict(state["config"]))
    model.load_state_dict(state["model"], strict=True)
    return model.to(device).eval()


def match_frontend(path):
    """Select the front end the checkpoint was trained with."""
    wanted = torch.load(path, map_location="cpu", weights_only=True)["frontend"]["fingerprint"]
    for name in FRONTENDS:
        set_frontend(name)
        try:
            if frontend_fingerprint() == wanted:
                return name
        except ImportError:
            continue
    set_frontend(FRONTENDS[0])
    return None


def sentences(text):
    """The sentences of ``text``, without a break after a title or an initial
    or inside a number. The browser demo splits the same way
    (``web/public/worker.js``); keep the two alike."""
    parts, current = [], ""
    for piece in _SENTENCE_END.split(_SPACE.sub(" ", text).strip()):
        current = f"{current} {piece}" if current else piece
        if not _NOT_AN_END.search(current):
            parts.append(current)
            current = ""
    if current:
        parts.append(current)
    return [part for part in parts if any(char.isalnum() for char in part)]


def finished(text):
    """``text`` with a full stop added when it ends without a mark. Before a
    final mark the voice lengthens the last syllable and lets the sound fall;
    without one the audio breaks off. A face or another sign after the last
    word is no mark ("see you :)"), a comma or a colon is one. The browser
    demo does the same (``web/public/worker.js``); keep the two alike."""
    body = _TEXT_END.sub("", text)
    if not body:
        return text
    marked = body.rstrip(_CLOSING)[-1:] in tuple("。！？…，；：、.!?…,;:")
    return text if marked else body + "。"


def shorter(text):
    """``text`` in smaller pieces: cut after commas and the like if it has
    any, else in two between words. ``[]`` for a single word."""
    pieces = [p for p in _CLAUSE_END.split(text) if p]
    if len(pieces) > 1:
        return pieces
    if len(text) < 2:
        return []
    half = (len(text) + 1) // 2
    return [text[:half], text[half:]]


def limit_peak(wave, peak=PEAK):
    """``wave`` scaled down as a whole when its loudest sample is above
    ``peak``; quieter audio is returned as it is. The model sometimes peaks
    above 1.0, and that clips when the audio is saved as 16-bit samples."""
    loudest = float(wave.abs().max()) if wave.numel() else 0.0
    return wave * (peak / loudest) if loudest > peak else wave


def _voice(model, phones, voice, speed, pitch_shift, seed, pitch_range):
    """Phonemes -> (float waveform tensor, details): one call of the model."""
    device = next(model.parameters()).device
    tokens = torch.tensor([phones.ids], device=device)
    stress = torch.tensor([phones.stress], device=device)
    speaker = torch.tensor([model.config.speakers.index(voice)], device=device)
    audio, lengths, details = model.synthesize(tokens, stress, torch.tensor([len(phones)], device=device), speaker, speed, pitch_shift, seed, pitch_range)
    if not torch.isfinite(audio).all():
        raise RuntimeError("model produced non-finite audio")
    return audio[0, :int(lengths[0])].cpu(), details


def speak(model, text, voice, speed=1.0, pitch_shift=0.0, seed=0, pitch_range=1.0):
    """One utterance: text -> (float waveform tensor, phonemized text, details).
    Same front end as training. The audio is the model's output as it is and
    can peak above 1.0 (see ``limit_peak``). ``speak_text`` reads text of any
    length."""
    phones = phonemize(text)
    if len(phones) > model.config.max_tokens:
        raise ValueError("text is too long for one utterance; speak_text splits it into sentences")
    wave, details = _voice(model, phones, voice, speed, pitch_shift, seed, pitch_range)
    return wave, phones, details


def speak_text(model, text, voice, speed=1.0, pitch_shift=0.0, seed=0, pitch_range=1.0, peak=PEAK):
    """Text of any length -> (float waveform tensor, phonemized utterances).

    The text is read sentence by sentence and the audio is joined. A text that
    ends without a mark gets a full stop (``finished``). A sentence
    too long for one call of the model (``max_tokens`` phonemes or
    ``max_frames`` frames) is cut after commas, then between words. A sentence
    with nothing to pronounce (another script, a face, signs only) is skipped;
    when no sentence could be read, ``NothingToPronounce`` says so. The audio
    is scaled down as a whole when it peaks above ``peak``, so that it can be
    saved as 16-bit samples without clipping; ``peak=None`` returns the
    model's output as it is."""
    limit = model.config.max_tokens - 12
    waves, spoken = [], []

    def read(piece):
        try:
            phones = phonemize(piece)
        except NothingToPronounce:
            return
        if len(phones) <= limit:
            try:
                wave, _ = _voice(model, phones, voice, speed, pitch_shift, seed + len(waves), pitch_range)
            except UtteranceTooLong:
                pass
            else:
                waves.append(wave)
                spoken.append(phones)
                return
        pieces = shorter(piece)
        if not pieces:
            raise ValueError(f"one word is too long to speak: {piece[:40]!r}")
        for part in pieces:
            read(part)

    for sentence in sentences(finished(text)):
        read(sentence)
    if not waves:
        raise NothingToPronounce(f"nothing in the text could be read: {ENGLISH_ONLY}")
    wave = torch.cat(waves)
    return (wave if peak is None else limit_peak(wave, peak)), spoken


def main():
    parser = argparse.ArgumentParser(description="Generate speech from a trained tiny-voca inference checkpoint")
    parser.add_argument("--checkpoint", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Text of any length; it is read sentence by sentence")
    source.add_argument("--text-file", type=Path, help="Read the text from a file (UTF-8)")
    parser.add_argument("--voice", default=None, help="speaker name (default: first in checkpoint)")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--speed", type=float, default=1)
    parser.add_argument("--pitch-shift", type=float, default=0, help="Added to log F0 (0.058 is about one semitone)")
    parser.add_argument("--pitch-range", type=float, default=1, help="Scale pitch movement around the utterance mean (1 = as predicted)")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--frontend", choices=FRONTENDS, help="Phonemizer (default: TINY_VOCA_FRONTEND, else the one the checkpoint was trained with)")
    parser.add_argument("--allow-frontend-mismatch", action="store_true",
                        help="Speak although the checkpoint was trained on the other front end's tokens")
    args = parser.parse_args()
    import soundfile as sf
    if args.frontend:
        set_frontend(args.frontend)
    elif FRONTEND_VARIABLE not in os.environ:
        match_frontend(args.checkpoint)
    model = load_model(args.checkpoint, args.device, check_frontend=not args.allow_frontend_mismatch)
    args.voice = args.voice or model.config.speakers[0]
    text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
    try:
        raw, spoken = speak_text(model, text, args.voice, args.speed, args.pitch_shift, pitch_range=args.pitch_range, peak=None)
    except NothingToPronounce:
        parser.exit(1, f"{CHINESE_ONLY}\n")
    wave = limit_peak(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Float samples, never above PEAK: a later conversion to 16-bit does not clip.
    sf.write(args.output, wave.numpy(), model.config.sample_rate, subtype="FLOAT")
    for phones in spoken:
        print(" ".join(phones.symbols))
    loudest = float(raw.abs().max())
    scaled = f", scaled down to {PEAK}" if wave is not raw else ""
    print(f"Saved {len(wave)/model.config.sample_rate:.2f}s in {len(spoken)} utterance{'s' if len(spoken) != 1 else ''}; peak={loudest:.4f}{scaled}")


if __name__ == "__main__":
    main()
