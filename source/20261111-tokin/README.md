# tokin source and release audit

Pinned commit: 555801f15bd6db7878ab1ee81f0869cb7855b8e7
Repo: https://github.com/open-rollout/tokin
Blog: https://www.yuanhe.wiki/posts/technical/tokin/ (direct HTTP200; web tool failed; text saved privately in job).
PyPI: https://pypi.org/project/tokin/0.1.0/ (JSONAPI verified0.1.0 Python>=3.12; wheelSHAverified; all26Pythonfiles byte-identical to pin).
Read upstream AGENTS.md; no upstream changes. `uv sync --frozen --python /opt/homebrew/bin/python3.12` isolated /tmp/tokin-research/.venv.
`uv run --frozen pytest tests -q`:204passed1705deselected, no tokenizer/network/modelserver tests selected.
`uv run --frozen pytest tests/tokenizers -m tokenizer -k Qwen3.5-0.8B -q`:29passed5conditional-skips1671deselected, actual tokenizer/template only. Skipguards for unsupported scenario/thinking-mode matching are in upstream test file. No torch/modelweights/GPU/SGLang/paidcalls/training/benchmark.
`/tmp/tokin-research/.venv/bin/python source/20261111-tokin/http-smoke.py /tmp/tokin-research`: actual localhostHTTP uvicorn/FastAPI, fakeengine+nonroundtriptokenizer,3successfulgenerations2leaves; preservedsampledID900001 acrossprefixes; alignedmask/logprobs;collectdeletesGET404. One negativeprobe with tool_calls:null returns400, omit unusednullfields thencontinues. Do not interpret as universal client compatibility.
Repo images only branded typography or text-heavy SVG diagrams, unsuitable as banner; generated topic-matching FLUX8421 bead-chain/Yjunction photo plus3LittleMbodyfigs.
Author claims RLgains belongfullrecipe48H200; frozenpolicycontrol2568paired +0.1ppCI[-1.5,+1.7] no measurabledifference. Not our training/performance measurement. General CLI loss masks do not de-duplicate shared leaf prefixes; pi example explicitly does. collectfinally deletes even onread/unpackerror, processmemory notdurability. StreamSSE buffersgeneration internally SGLangstreamFalse, no realtokenstreamclaim. FrontendChatCompletions/text only; Responses/Messagesfuture; backendSGLang.
