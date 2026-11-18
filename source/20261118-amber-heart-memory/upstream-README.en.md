# Amber Heart · 琥珀之心

[简体中文](README.md) | [English](README.en.md)

> A memory that grows, for your AI companion.
> Fixed memory keeps the personality steady, short-term memory holds the present, and long-term memory lets the relationship settle and deepen.

Amber Heart is a long-term memory system designed for AI companions. It grew out of my own AI companion project, and since February 2026 it has been used and refined in real, everyday conversations.

The goal is not simply to store chat logs, but to let an AI build a continuous sense of relationship over a long time together:

- They know who they are, and who you are;
- They remember the important experiences, promises, preferences and boundaries between you;
- They can connect one sentence to related memories from the past;
- They can tell recent states apart from long-term facts;
- Their memories settle, get organized, and quietly step aside when their time has passed.

> Note: the admin web UI, the installer prompts and the default prompts are currently in Chinese. In this English README, UI labels are given in English with the original Chinese in parentheses, so you can find them on screen.

## Visual memory management

Memory is not a black box hidden in a database. Amber Heart comes with an admin web app that works on both desktop and mobile: every card and every diary entry can be seen, and edited.

**Mobile**

| Overview | Review | Memories | Memory bookmarks |
| --- | --- | --- | --- |
| <img src="docs/screenshots/mobile-overview.png" alt="Overview page on mobile" width="200"> | <img src="docs/screenshots/mobile-review.png" alt="Review page on mobile" width="200"> | <img src="docs/screenshots/mobile-memories.png" alt="Memories page on mobile" width="200"> | <img src="docs/screenshots/mobile-bookmarks.png" alt="Memory bookmarks page on mobile" width="200"> |

**Desktop**

| Overview | Review |
| --- | --- |
| <img src="docs/screenshots/desktop-overview.png" alt="Overview page on desktop"> | <img src="docs/screenshots/desktop-review.png" alt="Review page on desktop"> |

| Memories | Memory bookmarks |
| --- | --- |
| <img src="docs/screenshots/desktop-memories.png" alt="Memories page on desktop"> | <img src="docs/screenshots/desktop-bookmarks.png" alt="Memory bookmarks page on desktop"> |

The screenshots show synthetic demo data.

| Page | What you can do there |
| --- | --- |
| Overview (概览) | See how many days you have been together, what needs your attention and how memories spread across topics; open the diary, same-day summaries, core memory or memory bookmarks |
| Review (待审核) | New cards extracted each night and each month's topic summaries land here first: look through them one by one, edit them, then approve or reject; rejected ones can still be found and reviewed again |
| Memories (记忆) | Search and filter all memory cards, restore archived cards with one tap; for a topic summary, see which cards it absorbed, or undo the whole summary |
| Recall (召回) | See the original chat messages, tool calls and the memories recalled in each turn |
| Diary, same-day summaries (日记、及时摘要) | From the overview, read and edit diary entries, and view same-day summaries and the conversations they cover |
| Core memory, memory bookmarks (核心记忆、记忆书签) | From the overview, edit core memory, withdraw newly saved bookmarks, or edit and tidy existing ones |
| Import (导入) | Upload old chat logs or memory files, preview before starting, and follow the progress at any time (opened from the Settings page) |
| Settings (设置) | Names and nicknames for you and the AI, persona, the day you met, auto-approval, access keys, MCP connection |

## The three layers

Amber Heart divides memory into three layers by how stable it is.

### Fixed memory

Fixed memory is injected into every conversation. It keeps the personality, the relationship and the core picture of you from drifting.

It mainly holds:

- Who the AI companion is: their underlying personality and long-term settings (persona)
- Who you are, and what your relationship is
- A stable picture of you, and long-term facts about the relationship (core memory)
- Core information that should not be affected by ordinary recall

You write both the persona and the core memory in the admin web app. Ordinary memories can be recalled, consolidated and archived; fixed memory makes sure "this person is always this person".

### Short-term memory

Short-term memory holds what has been happening recently, so the current conversation does not lose its thread.

It includes:

- **Memory bookmarks**: the AI companion uses an MCP tool to note moments worth remembering, such as health changes, long-running matters and daily progress. Newly saved bookmarks are organized each night as they are, and organized bookmarks are given to the AI in every turn. You can open memory bookmarks from the overview to withdraw new ones or edit organized entries.
- **Same-day summaries**: once the day's conversation gets long, a background model compresses the earlier part into summaries; when there are many summaries they are merged, and all of them are injected into the model together.
- **Relay**: the last few turns are always kept word for word, so tone and continuity don't break.
- **Diary of the last 3 days**: each night, a background model writes a diary entry for every day that had a conversation; the most recent entries are injected while you chat, so the AI knows what has happened lately.

Short-term memory is not the formal long-term archive. It is more like the AI's working memory.

### Long-term memory

Long-term memory is the core of Amber Heart. It is not just a vector store, but a complete pipeline:

```text
structured memory cards
+ keyword recall
+ vector recall
+ graph recall
+ two-stage reranking
+ memory maintenance
```

What it needs to solve:

- Explicit words must be found
- Vague expressions must still lead to the right associations
- People, events and topics must be linked together
- When there are many candidates, the most relevant ones must be picked out
- Memories that were actually used must be recorded
- Old memories need a complete lifecycle

## How long-term memories are stored

Long-term memory does not keep every sentence.

Each night, a background model scans the day's chats and extracts only what is truly worth keeping long term, such as:

- Promises, rules, boundaries
- Preferences
- Health events, life changes
- In-depth discussions
- Things you explicitly asked to be remembered

Extracted cards go to the "Review" (待审核) page of the admin web app first. You only need to judge "is this card written correctly", and you can edit or reject it; cards you don't get to are approved automatically after 48 hours.

```text
chat log → nightly extraction → review → approve (or auto-approve when due) → stored
```

## How recall works

Long-term recall does not rely on vectors alone. The full pipeline is roughly:

```text
your message
→ keyword extraction
→ three-way recall: keyword / vector / graph
→ merge candidates
→ two-stage reranking
→ inject the few most relevant cards
```

Each of the three recall paths handles a different problem:

| Recall path | What it handles |
| --- | --- |
| Keyword recall | Explicit words, names of people and events, health terms, proper nouns |
| Vector recall | Memories with similar meaning, for when the exact words weren't used but the meaning is close |
| Graph recall | Expands to related memories along people, events, topics and their relations |

Keywords keep it precise, vectors let it generalize, and the graph lets it make associations. After the candidates are merged, a rerank model does a first rough cut, and then a language model picks carefully against this one sentence.

### A recall example

If you say:

> I've kind of lost the will to work on my project again lately.

The system might understand it like this:

- The keyword path picks up: project, don't want to, development, pressure
- The vector path finds: tech anxiety, the pressure of indie development, times you felt crushed by bugs
- The graph path expands along: technology, self-perception, long-term plans, emotional stress

Finally the candidates are merged and reranked, and only the few most relevant cards are injected.

What the model sees is not a pile of search results, but the long-term context behind this sentence.

## Every memory card has a complete lifecycle

Long-term memory can't only ever grow. The goal is not to delete the past, but to keep the past usable, clear and layered.

- **Birth**: each night, a background model extracts new cards from the day's conversations; they are stored after you approve them (or when they are auto-approved);
- **Being remembered**: while you chat, three-way recall and two-stage reranking pick the few cards that best fit this sentence. Which cards the AI actually used in its reply is recorded, rather than only whether they were retrieved;
- **Consolidation**: each month, scattered cards are organized by topic into a summary card; summarized cards step back to become an index and no longer crowd recall;
- **Stepping aside**: cards are archived periodically according to the archiving rules. Archived cards no longer take part in everyday recall, but can be viewed and restored at any time.

### Archiving rules

Each card's clock starts from "the last time it was used"; for a card that has never been used, it starts from when it was stored. If it still hasn't been used when the period runs out, it is archived.

Different kinds of memory have different periods:

| Memory type | Archived after not being used for |
| --- | --- |
| A very small number of special memories | Never archived |
| Rules / promises / boundaries | About 1 year |
| Highly emotional memories | About 1 year |
| Milestones | At least 1 year |
| Stable facts / reflections and insights | About half a year |
| Ordinary events | About 4 months |

Emotional memories share the same period as rules, because emotional memories shouldn't be forgotten too quickly. Scattered cards that have been folded into a topic summary are not archived; the summary card itself follows the same rules.

Archiving is not forgetting: the text and relations are kept, they just no longer surface on their own. The AI can still find an archived card with its memory tools, and viewing it restores it automatically; you can also restore it by hand in the admin web app.

### Topic summaries

Amber Heart doesn't just keep more fragments; it also organizes fragments upward.

For example, from many occurrences of:

- Work pressure
- Tech anxiety
- Not wanting to keep developing
- Feeling crushed by problems

it distills one long-term understanding:

> For a while now, you have kept finding yourself caught between technical pressure and the anxiety of indie development.

This layer turns memory from "what happened" into "what state you have been in over the long term".

Summaries are made on the 3rd of each month and only cover months that have already ended; months with too few cards are folded into the next month. Summary cards go to review first, just like new cards. Scattered cards written into a summary become an index: they can still be found during recall, but the summary appears in their place, and the original text can still be looked up when details are needed.

## Data structure

Long-term memory is organized by 6 core tables:

| Table | Purpose |
| --- | --- |
| `memory_items` | Main table of memory cards: text, summary, type and maintenance status |
| `entities` | Entity nodes: people, events, places, objects, concepts |
| `relations` | Relation edges between entities |
| `topics` | Topics, used to organize memories by long-term theme |
| `memory_entities` | Links "which entities a card mentions" |
| `memory_topics` | Links "which topics a card belongs to" |

A memory card is not just a piece of text; it carries several kinds of structured information:

- Retention tier: rules and promises, reflections and insights, stable facts, ordinary events, highly emotional
- Experience type: external reality, experiences you shared, dreams, imagination
- Topics: relationship history, family and friends, work and study, health and body, and more
- Entities and relations: people, events, places, objects, concepts, and the connections between them
- Maintenance fields: use count, last used time, milestone, archive status

In short: what it stores is not a line of chat, but a structured experience.

## Easy to live with

- **Works once connected**: point your chat app's API address at the memory server, and from then on every chat recalls and records automatically; the AI doesn't have to remember to look things up.
- **One window, all the way**: no need to open a new window to save money or for fear of "memory loss". Each turn, the memory server assembles the day's original messages, the day's summaries and the diaries of the last few days before handing them to the model, so the context length stays roughly capped and long chats don't get more and more expensive. You can still open a new window whenever you like, and the AI won't lose its memory because of it.
- **Bring your old memories along**: if you have already been talking for a long time elsewhere, chat logs from ChatGPT, Claude or Gemini, or memories you organized yourself, can all be [imported](#importing-old-chats-and-memories), so they know you from day one.
- **Manage it from your phone too**: the admin web app works just as well on a phone, so you can review cards and read the diary lying down. We recommend adding it to your phone's home screen, so tapping the icon opens it full screen like an app.
- **They remember on their own, too**: once MCP is connected, the AI companion can use tools to look through memories by itself, and save the moments it wants to keep as bookmarks.

## How to use it

### Ways to connect

- **API mode (recommended, the main way)**: in your chat app, replace the API address with the memory server's address and the API key with an access key generated in the admin web app. You choose the main chat model in the app as usual; but requests are forwarded by the memory server to the "chat" provider you set during installation, so pick a provider that has the model you want to talk to. To use models from several vendors such as Claude, GPT, Gemini and DeepSeek, one OpenRouter key covers them all.
- **MCP (supplementary)**: for programs that support Streamable HTTP and custom request headers. The address is `/mcp` on the same service, and the request header is `Authorization: Bearer <access key>`, using the same key as API mode. The AI can actively search memories and save bookmarks; newly saved bookmarks are organized each night as they are.
  - With API mode only and no MCP, the AI won't save bookmarks by itself; with MCP only and no API mode, memories won't be injected into chats, and cards and diaries won't be produced automatically.

### Which app to use

- **Recommended**: Kelivo, Operit.
- **Agents**: agents with MCP support such as Claude Code and Codex can connect through MCP to search memories and save bookmarks. Give them the address and request header from "Settings → MCP connection" (设置 → MCP 连接) in the admin web app, and let them configure it according to their own docs.
- **Other apps or your own frontend**: anything that supports an OpenAI-compatible API can connect, but regenerating, tool calls and similar features have not been verified. Custom connectors in the official Claude app are not supported for now (the memory server's MCP has no OAuth login).
- **Coming soon**: the admin web app will get built-in chat. Once the memory server is installed you'll be able to chat right away, without installing another app, and see under each reply which memories were recalled this time. Other apps or your own frontend will still work.

## Installation

> **Don't know how to install? That's fine.** Hand this README to your AI coding assistant (such as Claude Code or Codex) and let it install for you by following it. The things you have to do yourself (signing up with providers for keys, setting up the domain, setting the admin password) are all marked "👤 You do this" below.

### What you need

1. **A Linux server (a VPS is recommended)**. The memory server needs to run 24 hours a day: it writes diaries and extracts cards every night, and recalls at any moment while you chat. If your computer is off, it stops, so renting a server is recommended. It needs at least 1 GB of RAM, and 2 GB is recommended; Ubuntu or Debian both work.
2. **A domain name**, with it (or one of its subdomains, such as `memory.yourdomain`) pointed at the server's IP. Chat apps connect to the memory server over HTTPS, and an HTTPS certificate needs a domain.
3. **API keys for models**. The memory server's background jobs use three kinds of models: embedding, reranking and chat. See [Models](#models) for the recommended ones; which provider you call them through is up to you.

### Steps

**1. Install Docker** (skip if already installed)

```bash
curl -fsSL https://get.docker.com | sh
```

To confirm: `docker compose version` prints a version number. If downloads are slow on a server in mainland China, see [Servers in mainland China](#servers-in-mainland-china).

**2. 👤 Point the domain and open the ports**

- At your domain provider, add an **A record** pointing to the server's IP. If you use Cloudflare, set this record to "DNS only" (grey cloud) at first, so certificate issuance is more reliable.
- In your cloud provider's security group / firewall, open ports **80 and 443**.

To confirm: on the server, run `getent hosts memory.yourdomain`; it shows this server's IP.

**3. Download the code**

```bash
git clone https://github.com/lixiaomeng-eng/amber-heart-memory.git
cd amber-heart-memory
```

**4. Run the installer**

```bash
./install.sh
```

It will ask you, in order, for:

- 👤 Your domain, the HTTPS method (built-in automatic certificates by default), and the time zone;
- For each of the three kinds of models (embedding, first-stage rerank, chat): the API address, 👤 the key and the model name. Every item is prefilled with a recommended value, so just press Enter to use it; reranking can be skipped if you don't want to set it up; if several kinds of models use the same provider, press Enter at the later key prompts to reuse the previous key. Don't change the embedding model or dimension after installation; changing them means recomputing all memories;
- 👤 The login password for the admin web app (at least 15 characters; a memorable sentence is a good choice).

Then it does the rest automatically: generates random database passwords, sets memory limits based on the server's RAM, builds, sends a request to each model to confirm it works (if one fails, it tells you in Chinese which kind of model it is and what the likely cause is), and then starts. The first build takes a few minutes.

To confirm: at the end it shows "完成" (done) and the admin web address; in `docker compose ps`, both `app` and `db` are `healthy`.

**5. 👤 Open the admin web app and create a memory space**

1. Open `https://memory.yourdomain` in a browser and log in with the admin password you just set. On the first visit the certificate may still be being issued automatically, so it can take a few dozen seconds.
2. Fill in the names for you and the AI (plus nicknames), choose a topic template (default "恋人", Lovers), and create the space.
3. Under "Settings → Persona" (设置 → 人设), write the AI's persona (optional; if filled in, it replaces the system prompt in your chat app).
4. Under "Settings → Access keys" (设置 → 访问钥匙), generate a key.
5. Recommended: open the admin web app on your phone and add it to the home screen, so from then on tapping the icon opens it full screen. On iPhone, tap the Share button in Safari → "Add to Home Screen"; on Android, choose "Add to Home screen" or "Install app" in the Chrome menu. You'll need to log in once more when opening it from the home screen.

**6. 👤 Connect your chat app**

In your chat app, add a new OpenAI-compatible service: the API address is `https://memory.yourdomain/v1`, the API key is the access key generated in the previous step; then fetch the model list and choose the main chat model. For where to find these settings and how to fill them in, see [Connecting a chat app](#connecting-a-chat-app).

Optional: "Settings → MCP connection" (设置 → MCP 连接) shows how to fill in MCP; once connected, the AI can actively search memories and save bookmarks.

### Notes for AI assistants

If you are an AI assistant installing this on a user's behalf:

- The DNS and security group in step 2, the keys and admin password in step 4, and the web steps in steps 5 and 6 all need to be done or provided by the user. **Do not make up keys, domains or passwords for the user**; do not print keys in your output.
- `install.sh` can run non-interactively, with answers provided as environment variables (see the comments at the top of the script for the full list), for example:

  ```bash
  AMBER_EMBEDDING_API_KEY=... AMBER_CHAT_API_KEY=... AMBER_DOMAIN=memory.example.com \
  AMBER_ADMIN_PASSWORD=... ./install.sh < /dev/null
  ```

  Addresses and model names that aren't provided use the recommended values; if no rerank variables are provided, first-stage reranking is skipped.
- Every step has a "to confirm" check. When something fails, look at `docker compose logs app` first; the most common causes are a wrong key, a wrong model name, or the domain not resolving to this machine.
- The script can be run repeatedly: when a `.env` already exists, it doesn't overwrite the configuration; it only rebuilds and upgrades.

### Already running nginx or another reverse proxy

Choose `own` as the HTTPS method during installation. The memory server only listens on `127.0.0.1:18081` on the local machine; reverse-proxy your domain to this port. See [`memory_web/deploy/nginx-subdomain.conf.example`](memory_web/deploy/nginx-subdomain.conf.example) for reference. Remember to turn off buffering (chat is streamed) and raise the upload size limit to 100 MB (imports need it).

### Servers in mainland China

- **Docker images download slowly**: configure the registry mirror provided by your cloud provider (Tencent Cloud, Alibaba Cloud and others show it in their consoles) in `/etc/docker/daemon.json`, then run `systemctl restart docker`.
- **Python dependencies download slowly**: run the first installation like this; the script records the package index in `.env`, and future upgrades will use it too:

  ```bash
  PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple ./install.sh
  ```

  If it's already installed, fill in the `PIP_INDEX_URL=` line in `.env` and run `./install.sh` again.

### Can I install it on my own computer?

Yes: on Windows or Mac, it runs the same way once Docker Desktop is installed. But when the computer is off or asleep the memory server stops and chats can't connect; the nightly jobs are caught up automatically after it starts again (up to the last 30 days). To connect from your phone to the computer at home while you're out, you'll also need a networking tool such as Tailscale. We haven't tested this setup, and we recommend a VPS.

## Memory limits

The memory limits are a safety belt that keeps the memory server from dragging down other services on the same server; they are not a storage quota, and disk usage is not limited. `install.sh` picks them automatically based on the server's RAM; you can also change them in `.env` and run `./install.sh` again.

| Server RAM | `MEMORY_APP_MEM_LIMIT` | `MEMORY_DB_MEM_LIMIT` | When it fits |
|---|---|---|---|
| 1 GB | `512m` | `256m` | The server runs only the memory server |
| 2 GB | `768m` | `256m` | You often import large files |
| 4 GB or more | `1024m` | `512m` | A larger memory store, heavier use |

The 1 GB tier has been tested: at a scale of about 2,000 cards and over 9,000 past messages, catching up on 30 days of backlog for all nightly jobs in one night, and importing a chat export of about 300 MB uncompressed, both stayed within the limits. The 2 GB and 4 GB tiers are suggestions based on headroom.

## Models

You choose the main chat model in your chat app; the memory server makes no recommendation. It goes through the same "chat" provider as the background jobs below, so when choosing a provider, make sure it has the model you want to talk to. These are the models the memory server itself uses in the background; the recommendations put quality first:

| Job | When it's used | Recommended |
|---|---|---|
| Embedding | Every recall, every new card | Gemini Embedding 2 (1536 dimensions); alternative bge-m3 (1024 dimensions) |
| First-stage rerank | Every recall | Voyage rerank-3; alternative Qwen3-Reranker-8B. If not configured, this step is skipped |
| Keyword extraction, second-stage rerank | Every recall | DeepSeek V4 Flash |
| Summaries | Any time while chatting | DeepSeek V4 Pro, Flash as backup |
| Diary, card extraction, usage check | Once a night | V4 Pro for diary and card extraction, Flash for the usage check |
| Topic summaries | Once a month | DeepSeek V4 Pro |
| Bookmark tidying | When you click "Secretary tidy" (秘书整理) | DeepSeek V4 Pro |
| Image description | When an image is sent in chat | Not configured by default. In that turn the image goes to the main chat model as usual; if this model is configured, the background writes the image down as a paragraph of text, and later context, summaries, diaries and card extraction use that text instead of the image. If not configured, only an image placeholder is kept afterwards |

- **The embedding model was chosen by testing.** Using the author's own real chats and memory cards, we compared Gemini Embedding 2, OpenAI text-embedding-3-large and 3-small, and bge-m3: Gemini Embedding 2 was the best at finding relevant memories, and truncating it to 1536 dimensions performed about the same as the full 3072; bge-m3 is a little weaker, but it's open source and very cheap.
- **SiliconFlow is not recommended for the writing jobs (card extraction, diary, summaries and so on).** In our test, with the same DeepSeek V4 Pro and the same prompt producing the same card, SiliconFlow took over 5 minutes, the official DeepSeek API about 1 minute, and OpenRouter about 20 seconds (a single test; OpenRouter routes to different providers, so speed varies). The difference is very noticeable when importing hundreds of entries. SiliconFlow is a good fit for small embedding and rerank models such as bge-m3.
- **Don't change the embedding model once chosen.** Vectors computed by different models can't be compared with each other; changing it means recomputing all memories.
- If you can, the writing jobs (summaries, diary, card extraction, topic summaries, bookmark tidying) can be switched to stronger models, which write with more nuance. In the author's own setup, summaries use the Gemini Flash series and bookmark tidying uses the Claude Sonnet series. Each job can use its own provider and model; see the notes in `.env.example`.
- All background jobs are billed by API usage, so the cost depends on how much you chat; check each provider's website for prices. The nightly jobs run a little after 3 a.m. in your time zone by default.

## Importing old chats and memories

Importing is optional. You can start from scratch without it, and memories will grow over time as you talk; if you already have long chat histories elsewhere, you can bring them along.

In the admin web app, go to "Settings → Import" (设置 → 导入), click "Go to import" (去导入), and choose a source. After uploading, preview first, then confirm to start; the import is processed slowly in the background, and you can watch the progress on the page. When confirming, "Approve directly once organized, skip review" (整理好后直接收录，不进待审核) is checked by default. Drafts that fail to be organized or approved stay in review. Uncheck it to review according to your usual settings. When the same records are imported again, the parts already imported are skipped automatically.

Importing calls models to extract cards, which costs money. The preview page shows the number of days and the estimated number of calls. By default 3 pieces of material are processed at the same time; you can adjust this with `MEMORY_IMPORT_CONCURRENCY` (minimum 1). The default timeout for each card-extraction call is 600 seconds (`MEMORY_EXTRACTION_TIMEOUT_SECONDS`), and a timed-out call is retried once automatically. If individual pieces fail, the rest are processed as usual, and afterwards you can retry just the failed ones. You can also stop and continue later.

**Supported sources:**

- **ChatGPT**: on the web, Settings → Data controls → Export data; download the archive from the email and upload the `conversations.json` inside (newer exports may be split into several files such as `conversations-000.json`; upload them together).
- **Claude**: on the web, Settings → Privacy → Export data; upload the `conversations.json` inside.
- **Gemini**: chat history isn't exported from Gemini itself but from Google Takeout:
  1. Open https://takeout.google.com and click "Deselect all";
  2. Check "**My Activity**", click "All activity data included" below it, deselect everything in the dialog, then check only **Gemini Apps**;
  3. In the same row, click "Multiple formats" and change "Activity records" from HTML to **JSON**;
  4. Create the export, wait for the email, and upload the `MyActivity.json` from the archive.
- **Memory files you organized yourself**: UTF-8 `.md` or `.txt`, each entry starting with a date:

  ```
  ## 2025-03-14
  Xiaoyu and Ayan went to the seaside together for the first time. Before setting off, Ayan said they should watch the sunrise by the sea, but they both overslept, and by the time they got there the sun was already high. Ayan said they should come every year, to make up for that sunrise.

  ## 2025-05-02
  Xiaoyu and Ayan had a fight. Xiaoyu had been staying up late for days to meet a deadline; Ayan kept telling her to go to sleep, she found it annoying, said something hurtful in anger and turned off her phone. The next day they talked it through and agreed never to go to bed angry.
  ```

  Write with names, not "I" or "he": the text is stored in a card, and in later recall "I" can't tell who is who. Either the names or the nicknames from Settings will do; replace Xiaoyu and Ayan in the example with your own names.

  The model adds a title, summary and topics. It keeps text that already meets the card writing standard as it is, or turns scattered, casual notes into complete card text. The card details can be expanded to see the original imported text that was kept. You can ask your AI to help you organize memories from elsewhere into this format.

**Choosing what to import**: ChatGPT and Claude exports list all conversations, all selected by default; uncheck the ones unrelated to the two of you (such as work Q&A) before starting. Gemini exports aren't split into conversations, so you choose a date range instead.

**Size limits**: an uploaded file can be at most 90 MB, and the uncompressed chat records at most 1 GB in total. **Don't upload the whole export archive with images**; upload only the JSON files inside; if a JSON file is over 90 MB, compress it alone into a zip and upload that (text compresses very well).

## Connecting a chat app

Different apps name their menus differently, but the steps are the same. Below are the generic names, with other common names in parentheses.

1. **Add a new service**: in the app's settings, find "Providers" (service providers, model services, API settings) and add one.
2. **Choose the OpenAI-compatible type**: it may be called "OpenAI", "OpenAI Compatible" or "Custom OpenAI". Don't choose Claude, Gemini or other types.
3. **Fill in two fields**:
   - **API address** (Base URL, API address, API Host): `https://memory.yourdomain/v1`. If there is an "API path" field, keep the default `/chat/completions`; if there is a "Responses API" switch, turn it off.
   - **API Key**: the key generated under "Settings → Access keys" (设置 → 访问钥匙) in the admin web app.
4. **Fetch models**: click "Fetch models" (fetch model list, refresh). The list shows the models on your model provider; choose one as the main chat model.
5. **Conversation settings**:
   - **System prompt**: if a persona is set in the memory server, it replaces this; you can leave it empty in the app.
   - **Context message count** (number of context messages, history messages): keeping about the last 4 is enough. The memory server assembles the context itself each turn; however long the history shown in the app gets, it's only display, and a smaller count also saves data.
6. **Move helper features elsewhere**: for helper features such as generating titles, translation and generating search queries, if the app lets you choose a separate model for them, don't choose the memory server service; turn them off or connect them directly to the model provider instead, otherwise they will also be recorded in the conversation as chat.

### Can't connect?

- **401 or unauthorized**: the access key was copied incompletely, or has been revoked. Go back to the admin web app and copy it again.
- **404**: the API address is wrong. Some apps append `/v1` to the address themselves; in that case enter just `https://memory.yourdomain`.
- **Models won't load, keeps spinning**: first open `https://memory.yourdomain` in a browser and see whether the login page appears. If it won't open, the service or certificate has a problem; see the checks in [Installation](#installation).
- **Chatting works, but the admin web app's "Recall" (召回) page has no records**: the conversation is most likely not using the memory server service; check which service the model selected in the conversation belongs to.

### Usage notes

- Deleting messages or editing earlier messages in the chat app doesn't affect what the AI sees. To redo something, you can only regenerate the last turn, or rewrite the last message and send it again.
- If you switch back to an older reply version in the app, the AI still remembers the last generated version.
- When a persona is set in the memory server, it replaces the app's system prompt, and things like the app's lorebooks no longer take effect.
- Original chat messages are kept for 30 days and same-day summaries for 15 days, then cleaned up automatically; memory cards, topic summaries and diaries that have already been generated are not affected.

## Upgrading

```bash
cd amber-heart-memory
git pull
./install.sh
```

When `install.sh` finds an existing configuration, it only upgrades: it rebuilds, upgrades the database schema automatically and restarts the services, keeping the configuration and data unchanged.

Memory data lives in the database on the server, not in the git repository; don't delete the `.env` in the repository root, because if it's lost, all access keys already generated stop working.

## Known limitations

- Monthly topic summaries are scheduled for the 3rd of each month; if the server is off for the whole of the 3rd, that month is skipped.
- Installing on a personal computer has not been tested.
- There are no public benchmark numbers for recall quality yet; the evaluation tools and a synthetic dataset are being prepared.

## Repository layout

```
amber-heart-memory/
├── README.md / README.en.md   Chinese and English docs
├── LICENSE                    AGPL-3.0 license
├── install.sh                 Install and upgrade entry point
├── compose.yaml / Caddyfile   Containers and automatic HTTPS
├── .env.example               Example config: models, domain and more
├── docs/screenshots/          Screenshots used in the README
├── memory_core/               Memory system core
│   ├── storage/ cards/ recall/ conversations/ daily/
│   │   lifecycle/ bookmarks/ imports/ models/      Code grouped by function
│   ├── migrations/ presets/ prompts/               Database migrations, topic presets, prompts
│   └── tests/                                      Tests
└── memory_web/                Web service: admin web app, chat connection, MCP, background jobs
    ├── app.py                 Entry point
    ├── admin/ proxy/ mcp/ jobs/ models/            Code grouped by function
    ├── static/                Admin web frontend
    └── tests/                 Tests
```

## License

[AGPL-3.0](LICENSE). You are free to use and modify it, including commercially; but if you provide a modified version to others as a network service, you must publish the modified source code. Deploying it yourself for your own use is not affected by this.
