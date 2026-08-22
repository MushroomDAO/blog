#!/usr/bin/env python3
"""
T1.3.2：段落级分片 + 双语拆分模块。

纯函数，不调用任何网络/Cloudflare API，可独立单元测试。产出的 chunk 列表交给
build-vectorize-index.py（或未来的增量索引 Worker）去 embedding + upsert。

分片规则（按 tasks.md T1.3.2 / spec.md 数据模型）：
- 只做正文段落级分片，不单独给代码块建 embedding——围栏代码块（```...```）整块从
  分片文本里剔除，不参与 token 计数，也不会单独成为一个 chunk（代码块前后的说明文字
  仍然正常参与分片）。
- 每篇文章的分片数硬上限 12-16（对应 architecture.md 的 chunk 数量预算），目标片段大小
  300-600 tokens，相邻片段 overlap 50-100 tokens；tokens 是近似计数（CJK 按字符数、
  非 CJK 按空格分词数），不是 bge-m3 真实分词器的精确 token 数，用于控制分片粒度已经足够。
- 双语文章（正文含 `<!--EN-->`）按分隔符拆成 zh/en 两段，分别独立分片，不混在一起；
  单语文章（无分隔符）只分片一次，语言由正文内容的 CJK 字符占比判定（不能假设"没有
  分隔符=中文"——T1.3.1 已经踩过这个坑，见 build-vectorize-index.py 的同名判定逻辑）。
- chunk_id：`sha256(article_id:language:chunk_type:content_hash)` 取前 48 位十六进制
  （沿用 T1.3.1 发现的 Vectorize v2 64 字节 id 上限对策）；chunk_type 放进哈希输入是
  T1.3.2 新加的一步——避免同一 (article_id, language) 下 article 级 chunk 和某个 paragraph
  chunk 恰好文本相同导致 id 碰撞（理论概率极低，但哈希入参多一个维度几乎零成本）。
"""

import hashlib
import math
import re

# CJK 统一表意文字 + 扩展 A + 中文标点/全角符号（review 指出：单独统计表意文字会让
# 标点密集的中文正文 token 数被低估——「」《》——等标点夹在表意文字之间时会被
# 非 CJK 分词路径当成一个词，跟真实分词粒度不符）
CJK_RE = re.compile(r"[一-鿿㐀-䶿　-〿＀-￯]")
# 修正（review 抓到的真实 bug）：原来固定按 3 个反引号匹配，遇到 CommonMark 合法的
# "用 4 个反引号包住内部含 3 个反引号示例" 的转义写法（本博客真实存在这种文章）会配对错乱，
# 非贪婪匹配吃掉/删掉中间的真实内容。改成用反向引用要求收尾围栏的反引号数量和开头一致
# （>=3 个都行，但首尾必须相等），且要求围栏各自独占一行，这是 CommonMark 的实际规则。
CODE_FENCE_RE = re.compile(r"^(`{3,})[^\n]*\n.*?^\1[ \t]*$", re.DOTALL | re.MULTILINE)
# 修正（review 抓到的真实 bug）：原来用子串匹配 "<!--EN-->" in text，导致正文里任何提到
# 这个分隔符字面量的地方（比如用反引号引用它来说明博客的双语约定）都会被误判成分隔符本身，
# 在错误位置把文章切开、大段中文内容被贴上 language=en 标签。真正的分隔符约定是独占一行，
# 要求匹配整行（允许行尾空白），不接受出现在句子/表格/代码引用里的字面提及。
EN_MARKER_RE = re.compile(r"^<!--EN-->[ \t]*$", re.MULTILINE)

MIN_CHUNK_TOKENS = 300
MAX_CHUNK_TOKENS = 600
OVERLAP_TOKENS = 75
MAX_CHUNKS_PER_LANGUAGE = 16


def detect_language(text):
    non_space = re.sub(r"\s", "", text)
    if not non_space:
        return "en"
    cjk_count = len(CJK_RE.findall(text))
    return "zh" if (cjk_count / len(non_space)) > 0.15 else "en"


def approx_token_count(text):
    """粗略 token 估算：CJK 按字符数（中文分词后单字大致对应一个子词单元），
    非 CJK 部分按空格切词计数。不追求跟 bge-m3 分词器的数字精确对齐，只用来控制
    分片目标大小的量级，这个精度足够。"""
    cjk_count = len(CJK_RE.findall(text))
    non_cjk = CJK_RE.sub(" ", text)
    word_count = len(non_cjk.split())
    return cjk_count + word_count


def strip_code_fences(text):
    return CODE_FENCE_RE.sub("", text)


HEADING_LINE_RE = re.compile(r"^#{1,6}\s+")


def is_heading_block(block):
    """按 split_into_blocks 的构造方式，heading 块恒为单行、且整块就是那一行 heading
    文本，判断时用同一个正则，保证跟切块逻辑的假设一致。"""
    return bool(HEADING_LINE_RE.match(block.strip()))


def split_into_blocks(text):
    """按空行分段；每个 heading 行（#/##/###...）单独成块，避免跟上一段落的正文
    粘在一起（分片时希望优先在 heading 边界断开）。"""
    text = strip_code_fences(text)
    raw_paragraphs = re.split(r"\n\s*\n", text.strip())
    blocks = []
    for para in raw_paragraphs:
        para = para.strip()
        if not para:
            continue
        lines = para.split("\n")
        buf = []
        for line in lines:
            if HEADING_LINE_RE.match(line):
                if buf:
                    blocks.append("\n".join(buf))
                    buf = []
                blocks.append(line)
            else:
                buf.append(line)
        if buf:
            blocks.append("\n".join(buf))
    return [b for b in blocks if b.strip()]


def group_blocks_into_chunks(blocks, min_tokens=MIN_CHUNK_TOKENS, max_tokens=MAX_CHUNK_TOKENS,
                              overlap_tokens=OVERLAP_TOKENS, max_chunks=MAX_CHUNKS_PER_LANGUAGE):
    if not blocks:
        return []

    total_tokens = sum(approx_token_count(b) for b in blocks)
    if total_tokens == 0:
        return []

    # 先按 max_tokens 估算需要多少片，如果超过硬上限，就把目标片段大小拉大，
    # 保证片数不超 max_chunks（片数上限是硬约束，token 区间是尽量满足的目标）。
    #
    # 关键修正（对抗式 review 抓到的真实 bug）：overlap 会让相邻 chunk 之间重复一部分
    # token，所以"gross token 产出"= total_tokens + (chunk数-1)*overlap_tokens，不是
    # 单纯的 total_tokens。原来的算法没算这笔重复账，导致 target_tokens 偏小、
    # chunk 边界比预期提前用完 max_chunks-1 个，剩余内容全部堆进最后一片（实测某些真实
    # 文章尾部 chunk 达到 1700+ token，是目标上限的近 3 倍）。这里把 overlap_tokens 加回
    # 每片的预算里，让"新内容"部分才真正对齐 [min_tokens, max_tokens] 区间。
    ideal_count = max(1, math.ceil(total_tokens / max_tokens))
    chunk_count_budget = min(max_chunks, ideal_count)
    target_tokens = max(min_tokens, math.ceil(total_tokens / chunk_count_budget) + overlap_tokens)

    chunks = []
    current = []
    current_tokens = 0

    for block in blocks:
        block_tokens = approx_token_count(block)
        would_exceed = current and (current_tokens + block_tokens > target_tokens)
        room_for_more_chunks = len(chunks) < max_chunks - 1
        # 修正（review 抓到的真实 bug）：如果 current 目前只有标题行、还没有任何正文，
        # 不能在这里断开——断开会把一个只含标题、没有正文的"空壳" chunk 单独 flush 出去，
        # 而这个标题接下来又会被 overlap 逻辑原样带到下一个 chunk 开头，变成标题重复出现
        # 两次、其中一次单独成一个几乎没用的 chunk。宁可让这个 chunk 稍微超一点预算，
        # 也要保证标题后面至少跟着一段真正的正文再断开。
        current_is_heading_only = current and all(is_heading_block(b) for b in current)
        if would_exceed and room_for_more_chunks and not current_is_heading_only:
            chunks.append(list(current))
            # overlap：从上一个 chunk 尾部往前取够 overlap_tokens 的 block，作为下一个 chunk 的开头。
            # 修正：如果最近一个 block 自己就已经比 overlap_tokens 大得多，把它整块搬去当
            # "overlap" 没有意义——只会让下一片一开始就严重超预算，且和上一片高度重复。
            # 这种情况下宁可不做 overlap，让下一片从下一个新 block 干净起步。
            overlap_blocks = []
            overlap_count = 0
            for b in reversed(current):
                if overlap_count >= overlap_tokens:
                    break
                b_tokens = approx_token_count(b)
                if not overlap_blocks and b_tokens > overlap_tokens * 2:
                    break
                overlap_blocks.insert(0, b)
                overlap_count += b_tokens
            current = overlap_blocks
            current_tokens = overlap_count
        current.append(block)
        current_tokens += block_tokens

    if current:
        chunks.append(current)

    # 保险：理论上不会触发（target_tokens 已经按 max_chunks 反推），但防止分片逻辑
    # 因为极端输入（比如单个 block 就超大）产出超过硬上限的片数
    while len(chunks) > max_chunks:
        tail = chunks.pop()
        chunks[-1] = chunks[-1] + tail

    return ["\n\n".join(c) for c in chunks]


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def make_chunk_id(article_id, language, chunk_type, chash):
    key = f"{article_id}:{language}:{chunk_type}:{chash}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:48]


def chunk_article(article_id, body_markdown):
    """输入：article_id + 正文 Markdown（含或不含 <!--EN--> 分隔符）。
    输出：list of {chunk_id, article_id, language, chunk_type, text, content_hash}，
    chunk_type 恒为 'paragraph'（article 级 chunk 是 T1.3.1 已经在做的，不在这个函数范围内）。
    """
    # 先剥离整篇正文里的围栏代码块，再判断/切分双语标记——修正 review 抓到的一个真实
    # 缺口：如果不先剥离，理论上示例代码里刚好含有字面量 "<!--EN-->" 字符串时，会在
    # 代码块中间切开双语，产出一段带着未闭合围栏残留、且语言硬编码错误的畸形 chunk。
    # 先剥离后：如果 "<!--EN-->" 恰好在代码块内部，剥离代码块时连同标记一起消失，
    # 这篇文章会被当成单语处理——比在代码块中间强行切开安全得多。
    cleaned_body = strip_code_fences(body_markdown)
    marker_match = EN_MARKER_RE.search(cleaned_body)
    if marker_match:
        zh_body = cleaned_body[: marker_match.start()]
        en_body = cleaned_body[marker_match.end():]
        sections = [("zh", zh_body), ("en", en_body)]
    else:
        lang = detect_language(cleaned_body)
        sections = [(lang, cleaned_body)]

    results = []
    for language, section_text in sections:
        blocks = split_into_blocks(section_text)
        chunk_texts = group_blocks_into_chunks(blocks)
        for chunk_text in chunk_texts:
            chash = content_hash(chunk_text)
            results.append({
                "chunk_id": make_chunk_id(article_id, language, "paragraph", chash),
                "article_id": article_id,
                "language": language,
                "chunk_type": "paragraph",
                "text": chunk_text,
                "content_hash": chash,
            })
    return results
