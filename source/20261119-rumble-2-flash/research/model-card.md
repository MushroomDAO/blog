---
license: apache-2.0
language:
- af
- ar
- bn
- bs
- ca
- ceb
- cs
- da
- de
- el
- en
- es
- eu
- fa
- fi
- fil
- fr
- hi
- hr
- hu
- id
- is
- it
- ja
- ko
- lt
- lv
- mk
- ms
- mt
- nb
- nl
- pl
- pt
- ro
- ru
- sq
- sr
- sv
- th
- tr
- uk
- vi
- yue
- zh
pipeline_tag: automatic-speech-recognition
library_name: transformers
tags:
- qwen3-asr
- vllm
---

# Rumble-2-Flash

![Parameters](https://img.shields.io/badge/Parameters-0.5B-D6F366)
![Languages](https://img.shields.io/badge/Languages-45-D5CDFB)
[![License](https://img.shields.io/badge/License-Apache_2.0-FFC3A1)](LICENSE)

Speech recognition model with native Hugging Face Transformers and vLLM support.

## Usage (Transformers)

```bash
uv pip install torch transformers accelerate
```

```python
from transformers import AutoProcessor, AutoModelForMultimodalLM

model_id = "Reson8/Rumble-2-Flash"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForMultimodalLM.from_pretrained(model_id, device_map="auto")

inputs = processor.apply_transcription_request(
    audio="https://hf.co/datasets/hf-internal-testing/dummy-audio-samples/resolve/main/bcn_weather.mp3",
    language="English",  # omit to detect automatically
).to(model.device, dtype=model.dtype)

output = model.generate(**inputs, max_new_tokens=512)
generated = output[:, inputs["input_ids"].shape[-1]:]
print(processor.decode(generated, return_format="transcription_only")[0])  # return_format="parsed" if detecting language
```

`audio` accepts a local path, a URL, a NumPy array, or a list of these.

## Usage (vLLM)

```bash
uv pip install "vllm[audio]" openai
vllm serve Reson8/Rumble-2-Flash --max-model-len 4096
```

```python
import base64
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
audio = base64.b64encode(open("audio.wav", "rb").read()).decode()

response = client.chat.completions.create(
    model="Reson8/Rumble-2-Flash",
    messages=[{
        "role": "user",
        "content": [{
            "type": "audio_url",
            "audio_url": {"url": f"data:audio/wav;base64,{audio}"},
        }],
    }],
    temperature=0,
    extra_body={"chat_template_kwargs": {"language": "English"}},
)
print(response.choices[0].message.content)
```

## Transcription options

Pass these options through vLLM's `chat_template_kwargs`, or directly to
`processor.apply_chat_template` in Transformers.

| Option | Default | Effect |
|---|---|---|
| `language` | unset | Forces the language using its English name, such as `"Dutch"` or `"English"`. If unset, output starts with `language <Name><asr_text>`. |
| `digits` | `true` | Numbers as digits; `false` writes them as words. |
| `filler` | `false` | `true` keeps fillers such as "um" and "uh". |
| `verbatim` | `true` | `false` collapses repeated words. |

## License

Licensed under the [Apache License 2.0](LICENSE).

## Open ASR Leaderboard results

Evaluated on the [Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard?version=1.16.1) (release 18-11-2026, v1.16.1), run on an H200 with vLLM. Compare against other open models on the multilingual tracks with [this view](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard?languages=Reson8%2FRumble-2-Flash&proprietary=false) (API models hidden).

### English track

Average WER on the leaderboard: **6.60** (RTFx 6338), over the 7 public splits plus the aggregated Private (scripted) and Private (conversational) scores.

| Split | WER (%) | RTFx |
|---|---|---|
| AMI | 9.24 | 4245 |
| Earnings22 | 6.45 | 4811 |
| GigaSpeech | 7.56 | 5978 |
| SPGISpeech | 3.08 | 7308 |
| URGENT24 | 10.25 | 3314 |
| Voice Arena Monsoon | 3.56 | 3760 |
| VoxPopuli | 2.43 | 4222 |
| Private (scripted) | 3.71 | |
| Private (conversational) | 13.14 | |

### Multilingual track

WER (%) per language and dataset; Chinese is CER. The last column is the leaderboard's average for the language.

| Language | FLEURS | Common Voice | MLS | Voice Arena Monsoon | AISHELL-1 | Average |
|---|---|---|---|---|---|---|
| German | 4.77 | 6.28 |  |  |  | **5.52** |
| Spanish | 2.82 | 4.33 | 4.04 |  |  | **3.73** |
| French | 5.95 | 10.01 | 5.66 |  |  | **7.21** |
| Italian | 2.53 | 4.84 | 7.90 |  |  | **5.09** |
| Dutch | 6.05 | 4.92 | 9.38 |  |  | **6.78** |
| Portuguese | 5.31 |  | 7.61 |  |  | **6.46** |
| Hindi |  |  |  | 14.11 |  | **14.11** |
| Chinese (CER) | 5.82 |  |  |  | 7.31 | **6.56** |
