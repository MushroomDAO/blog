from pathlib import Path
import json
s='espica32-kiwisdr-wifi-radio-build-review'
cn='''ESPica32 是一台把远程 KiwiSDR 接收机装进实体旋钮操作体验里的 Wi-Fi 收音终端。日常收听可以脱离手机和电脑，但它仍需要网络，以及远方愿意共享接收通道的 KiwiSDR；真正接收无线电的天线和射频硬件在远端。

作者 Ivan（呼号 LU8MIL）在 Todo-SDR 分享了 Arduino 源码包、接线图和操作说明。本次查到的是作者网站的 RAR 下载，尚未找到可确认归属的 ESPica32 GitHub 仓库，也未在下载包里找到明确许可证。因此，准确的介绍是“源码可下载的 DIY 项目”，不能自行替它补上 MIT、GPL 或商业再分发授权。

作者页面标注 2026 年 11 月 1 日，RTL-SDR.com 报道日期是 11 月 5 日；媒体报道时间不等于代码首次公开时间。以下结合实际下载包阅读与本机辅助测试，拆开它的能力、材料清单和复现门槛。

## ESP32 究竟接收什么，为什么能听远方？

链路是：远方天线与 KiwiSDR 接收机 → 网络音频及控制协议 → 家中的 ESP32 → I2S 功放与扬声器。旋钮改变频率和模式时，ESP32 向服务器发调谐命令；服务器完成接收与解调，再把音频送回来。

这和播放一个固定互联网电台 URL 有区别：听众可以调频率、切换解调方式，探索远端天线所在地点能接收到的信号。也正因为如此，“全球”指可选择不同地区的接收站，并不表示每个台、每个时段都能听到；远端天线、传播条件、可用通道和站主访问限制都会影响结果。

源码 `state.cpp` 的模式表将屏幕上的 FM 映射为 `nbfm`，即窄带 FM。它不能据此被宣传成能直接收本地 88–108 MHz 宽带调频广播的 ESP32 射频收音机。换到远端站点，也不会改变本地板子的射频能力。

![小M用实体旋钮控制远方接收机，网络把音频送回扬声器](../../assets/images/SLUG-fig-01.png)

## 四块模块够吗？完整材料与接线

四块主要模块是 ESP32-WROOM-32 开发板、OLED 显示屏、带按键的编码器、MAX98357A I2S 功放。此外还需要一个扬声器、USB 供电及连线；面包板或焊接固定结构也应提前准备。“四样东西”适合作为主要模块概括，不是完整采购单。

| 模块 | 本次下载包中的配置与用途 |
|---|---|
| ESP32-WROOM-32 DevKit | 网络连接、协议处理、解码与控制 |
| SH1106 1.3 英寸 OLED | I2C 地址通常为 0x3C；外层代码默认屏型宏仍是 SSD1306，使用 SH1106 要改配置 |
| EC11 / KY-040 编码器 | A/B 两路旋转输入加按键，合用一个旋钮完成多个动作 |
| MAX98357A | 接收 I2S 音频并驱动扬声器 |
| 4–8 Ω 扬声器 | 单独的一件输出器件，不能漏买 |
| USB 电源、线材、安装材料 | 让整机获得稳定供电并可靠连接 |

外层 `config.h` 的信号脚为：OLED SDA→GPIO21、SCL→GPIO22；编码器 A→GPIO32、B→GPIO33、SW→GPIO27；I2S BCLK→GPIO18、LRC→GPIO19、DIN→GPIO23，共八个信号 GPIO。

供电按作者接线图分别处理：屏幕接 3V3，功放使用开发板 USB 供电对应的 VIN/5V，GND 共地。不同开发板对 VIN 的定义可能不同，接线前核对板卡丝印和说明；扬声器接功放的差分输出两端，不把其中一端当作 GND。

单旋钮是多功能操作器：旋转调整当前焦点，短按切换频率、音量和模式，双击跳到下一预设波段，长按切调谐步进，更长按显示 Web 地址。这里的“换台”主要是调频率或波段；服务器列表由 Web 面板选择，并不是无限电台目录已自动装进旋钮。

## 下载包里为什么有两套项目？如何开始复现？

本次 RAR 解压后，外层 `kiwi-radio-mini/` 里面还嵌套了一个同名目录。两套代码存在差异，外层有 `kiwiadpcm.h`、`audiobuf.h`、`debug.cpp` 等文件，内层缺少这些增强模块。复现时应认准这一层，先把外层项目单独复制到干净目录，避免误开旧版本。

作者 README 指定 Espressif Arduino ESP32 板卡包 2.0.17，并提示 3.x 不兼容；还需安装 U8g2，选择 ESP32 Dev Module 和 No OTA（2MB APP / 2MB SPIFFS）分区。这是作者给出的构建配方，本次没有实际编译完整固件，不能保证所有新旧板卡环境都能直接通过。

建议按以下顺序做：

1. 下载文末作者源码包，选对外层目录，确认 `.ino` 与项目目录同名。
2. 修改 OLED 类型、GPIO 与音频输出配置，核对接线。
3. 清空或替换 `DEFAULT_WIFI_SSID`、`DEFAULT_WIFI_PASS`。本次源码仍带开发者默认 Wi-Fi 配置，不能原样烧录后误以为必然直接进入配网热点，也不要把原值传播到自己的仓库。
4. 按 README 的板卡包和分区方案编译上传，串口监视器设为 115200。
5. 启动时按住编码器可进入配网；连接设备热点后，用浏览器打开 192.168.4.1，配置家庭 Wi-Fi 与可访问的 Kiwi 服务器。
6. 连通后再用屏幕、旋钮与扬声器独立操作；需要选服务器、诊断或改配置时，再打开 Web 面板。

所以“不用手机、不用电脑”说的是配置完成后的日常操作。下载、编译、烧录及首次浏览器配网仍需要相应设备，不能省略。

## ADPCM 为什么比一味扩大缓冲更关键？

外层代码把 Kiwi 音频采样率设为 12 kHz，PCM 为每样本 16 bit。理论音频净荷为 12,000×2=24,000 字节/秒；4 bit IMA ADPCM 则为 12,000÷2=6,000 字节/秒。这个四倍差别来自格式计算，未计入网络报头、重传和控制消息，也不是本次实测网速。

作者报告自己在德国连接阿根廷接收机时，约 260 ms 网络延迟下未压缩音频出现断续，改用 ADPCM 后改善。这个案例能说明压缩的工程价值，但不能推出所有 ESP32 或所有网络都存在同一个延迟门槛；实际瓶颈还与 TCP 窗口、接收循环和网络突发有关。

判断方法是区分平均到达速率不足与短时抖动。如果长期收进来的音频少于播放消耗，扩大缓冲只能延后断音，不能修复吞吐缺口。若平均速率足够、只是短暂卡顿，抖动缓冲才更有效。

代码的缓冲控制器提供 100–2000 ms 最低目标，断音后自动增加 300 ms，上限 2000 ms；稳定一段时间后逐步回落。另一个控制器通过偶尔重复或丢弃一个样本补偿两端时钟漂移。大缓冲换来稳定，也带来旋钮动作到声音变化的额外等待。

ADPCM 解码后仍回到 16 bit PCM 环形缓冲，所以“传输少四倍”不等于“本地音频缓冲占用也少四倍”。同样，输出侧 48 kHz 线性插值不会凭空恢复原来 12 kHz 音频没有的高频细节。

![小M先检查传输速率，再调节抖动缓冲，区分压缩与延迟的作用](../../assets/images/SLUG-fig-02.png)

## 本次实际验证了什么？

Mycelium Protocol 下载并记录了源码包哈希，读取外层实现，在 macOS 上用 Apple clang 编译其实际 ADPCM 与缓冲头文件，进行了两类主机辅助检查：

- 解码 4096 字节的固定随机输入，共 8192 个样本；调整输入半字节顺序后，与 Python 3.12 `audioop.adpcm2lin` 的结果逐样本一致。分块解码与一次性解码一致，重置后也能复现相同输出。
- 对缓冲初始目标、断音递增、2 秒封顶、关闭自动模式、稳定后回落，以及低水位重复/高水位丢弃样本等路径执行了 10 个断言，全部通过。

这些证据支持算法片段按预期工作，尚不能证明真实电路音质、供电稳定性、全部服务器协议兼容性或长时间无断音。本次没有 ESP32 实板、没有固件完整构建、没有连接公共 Kiwi 占用通道，也没有测量真实网络音频延迟。

源码包 SHA-256：`ff6035c799d0c7bdaae0c673df50544c2d790f98673586fe07becac21e3efd72`。网站文件可能更新；复现时保留自己的下载版本与哈希。

## 它离一台省心的成品还有哪些距离？

协议上，这版使用普通 `WiFiClient`，README 明确只支持 `ws://`；需要 TLS 的 `wss://` 端点不能默认可用。服务器满员、密码不对、连接被站主限制，都是正常可能遇到的情况，先用浏览器确认站点，再排查板端，通常更有效。

管理上，所读 `web.cpp` 的控制与配置路由未看到登录鉴权检查。使用家庭可信网络，不为这个面板做公网端口映射；默认配网密码也应改成自己的值。这是从具体代码得到的部署建议，不是对项目做过完整安全审计的结论。

功能上，作者页面把彩屏瀑布图、外壳和频率收藏列为后续方向，不能宣传成当前固件已完备支持。它真正有吸引力的地方是：把网络 SDR 的可调谐能力变成一个可摸到的旋钮，同时用压缩、缓冲和诊断应对微控制器的资源限制。

![小M按源码版本、接线、配网、声音的顺序验收，区分已测试与待实板验证](../../assets/images/SLUG-fig-03.png)

想把它当成一个周末学习项目，很合适；想要断网可用的应急短波机，或本地宽频射频接收器，就需要不同的接收硬件和设计。验收时先保证“声音稳定、控制有效、重启保留配置”，再考虑外壳与更多功能。

## 常见问题

### 必须有自己的 KiwiSDR 吗？

不一定，可以连接允许访问的公共服务器；接收范围与通道可用性由远端站点决定。自建接收机能增加控制权，但不是这个客户端的必需硬件。

### 有官方 GitHub 仓库吗？

本次从作者原文和 GitHub 精确项目名检索，找到的是作者网站的源码压缩包，未确认官方 ESPica32 GitHub 仓库。相关 `jks-prv/kiwiclient` 是 KiwiSDR Python 客户端及协议参考，不应冒充 ESPica32 自己的仓库。

### 能说已经实测“全球流畅收听”吗？

不能。本次只做源码核对、8192 样本参考解码比较和缓冲控制断言。跨国收听效果来自作者报告，实板、实际站点与长时间稳定性仍需复现者验证。

## 来源与进一步阅读

作者项目与下载入口：https://www.todo-sdr.com/espica32-cliente-kiwisdr/

作者源码包：https://www.todo-sdr.com/wp-content/uploads/2026/11/kiwi-radio-mini.rar

媒体报道：https://www.rtl-sdr.com/espica32-a-standalone-esp32-radio-for-tuning-any-kiwisdr-with-no-pc-or-phone/

相关协议与工具参考（不是 ESPica32 仓库）：https://github.com/jks-prv/kiwiclient

公共接收站目录：https://kiwisdr.com/public/

相关阅读：用 ESP32 LoRa 板接收 ADS-B 的条件与边界：https://blog.mushroom.cv/blog/esp32-adsb-receiver-analysis/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。
'''
en='''ESPica32 is a Wi-Fi audio and tuning terminal for remote KiwiSDR receivers, with a physical knob, OLED and speaker. Once configured, it can operate without a phone or PC at hand. It still depends on networking and a remote receiver: the antenna and RF reception happen at the KiwiSDR site.

Ivan, callsign LU8MIL, publishes the project on Todo-SDR. The primary page is dated November 1, 2026, while RTL-SDR.com covered it on November 5. Neither date alone establishes the first public code release. The verified distribution is a downloadable RAR source archive; this review did not locate an attributable official ESPica32 GitHub repository or an explicit license inside the archive. Downloadable source should not be assigned an invented MIT or GPL license.

## What does the ESP32 actually receive?

The chain is remote antenna and KiwiSDR → network audio/control → ESP32 → I2S amplifier and speaker. Turning the knob sends tuning commands to the receiver. That is more interactive than playing a fixed internet-radio URL, but coverage depends on the selected remote station, propagation, antenna and available receiver channels.

In the downloaded `state.cpp`, the displayed FM mode maps to `nbfm`, narrowband FM. It does not establish local reception of the 88–108 MHz wideband FM broadcast band. Selecting another server changes where reception occurs, not the ESP32 board's RF capabilities.

![LittleM controls a remote receiver with a local knob while audio travels back through the network](../../assets/images/SLUG-fig-01.png)

## Hardware and wiring: four modules are not the whole bill

The main modules are an ESP32-WROOM-32 DevKit, OLED, push-button rotary encoder and MAX98357A I2S amplifier. A separate speaker, USB power, wires and a mounting method are also needed.

| Part | Configuration in the downloaded outer project |
|---|---|
| ESP32-WROOM-32 DevKit | Networking, decoding, audio output and user controls |
| SH1106 1.3-inch OLED | Usually I2C 0x3C; change the OLED macro because the outer config defaults to SSD1306 |
| EC11 / KY-040 encoder | Two rotary inputs and a button |
| MAX98357A | I2S input and speaker amplification |
| 4–8 ohm speaker | A separate component beyond the four principal modules |
| USB supply and wiring | Required for a reliable physical build |

The outer configuration uses GPIO21/22 for OLED SDA/SCL, GPIO32/33 for encoder A/B, GPIO27 for its button, and GPIO18/19/23 for I2S BCLK/LRC/DIN. That is eight signal GPIOs.

The author's diagram powers the OLED from 3V3 and the amplifier from the USB-derived VIN/5V rail, with common ground. Verify the particular DevKit's VIN labeling before wiring. Connect the speaker across the amplifier's two differential output terminals; neither is a ground connection.

Rotating changes the focused control. A short click cycles frequency, volume and mode; double-click advances a band preset; longer presses change tuning steps or display the web address. Server selection lives in the web interface, rather than an automatically populated global-station directory on the knob.

## Which source directory should be built?

The RAR contains an outer `kiwi-radio-mini/` and a nested directory with the same name. They differ. The outer directory includes `kiwiadpcm.h`, `audiobuf.h` and diagnostics files missing from the nested version. Copy the outer project into a clean directory to avoid opening the older implementation accidentally.

Its README specifies Espressif's Arduino ESP32 package 2.0.17, warns about 3.x compatibility, and requires U8g2. It selects ESP32 Dev Module and the No OTA partition scheme with 2 MB application and 2 MB SPIFFS. This is an upstream build recipe, not a firmware build verified in this review.

Before flashing, set the OLED/audio/GPIO options and clear or replace `DEFAULT_WIFI_SSID` and `DEFAULT_WIFI_PASS`: the downloaded configuration contains developer fallback Wi-Fi settings. Do not republish their values. Those defaults also mean first boot need not immediately enter the setup hotspot as an oversimplified guide might suggest.

Hold the encoder during startup to enter setup, then use a browser at 192.168.4.1 to enter your network and Kiwi server. After configuration, listening uses the physical controls; the web panel remains useful for configuration and diagnostics. Initial downloading, flashing and browser setup still require appropriate external devices.

## Why does ADPCM matter more than a larger buffer?

The configuration uses a 12 kHz source rate. At 16-bit mono, PCM audio payload is 24,000 bytes/s; at four bits per sample, IMA ADPCM payload is 6,000 bytes/s. These are format calculations, excluding packet overhead and retransmissions, not measured network throughput.

The author reports improved Germany-to-Argentina listening after enabling ADPCM on a connection with roughly 260 ms delay. That is a reported example, not a universal ESP32 latency threshold. TCP windowing, receive-loop servicing and burst delivery also matter.

A jitter buffer helps when average delivery is adequate but packets arrive unevenly. If average delivery remains below playback consumption, a larger buffer merely postpones failure. The outer controller sets a 100–2000 ms minimum target, adds 300 ms after an underrun up to 2000 ms, then decreases gradually after stability. A separate controller occasionally repeats or removes one sample to counter clock drift.

Compression reduces transport payload, but the audio is decoded back into 16-bit PCM before entering the ring buffer. It therefore does not reduce that buffer's memory consumption fourfold. Likewise, 48 kHz output through linear interpolation does not recreate information missing from the original 12 kHz signal.

![LittleM checks sustained delivery before adjusting jitter buffering and its latency tradeoff](../../assets/images/SLUG-fig-02.png)

## What was actually tested?

Mycelium Protocol downloaded and hashed the archive, reviewed the outer implementation, and compiled its actual ADPCM and buffer headers on a macOS host with Apple clang.

For decoding, 4096 deterministic random input bytes produced 8192 samples. After adapting nibble order for Python 3.12's `audioop.adpcm2lin`, all samples matched the reference. Chunked and single-pass decoding matched, and resetting the decoder reproduced the output.

Ten assertions also passed for initial buffer targets, underrun increments, the two-second cap, manual mode, gradual decay, and low/high/middle buffer-level drift decisions. These checks establish behavior of selected algorithmic components. They do not establish circuit reliability, audio quality, full protocol compatibility or uninterrupted overseas playback.

No ESP32 board, full firmware build, live public receiver, RF listening session or end-to-end latency measurement was used. Archive SHA-256: `ff6035c799d0c7bdaae0c673df50544c2d790f98673586fe07becac21e3efd72`. Retain your own download hash because the website file may change.

## Practical limits and a useful acceptance order

This version uses plain `WiFiClient`; its README limits connections to `ws://`. Do not assume `wss://` endpoints work. Full channels, station passwords and operator restrictions can also prevent connections. First establish access in a browser, then diagnose the board.

The reviewed `web.cpp` registers control and configuration routes without an observed login check. Keep the panel on a trusted network, avoid public port forwarding, and replace the default setup password. This is a concrete deployment observation, not a comprehensive security audit.

The author's page lists a color waterfall, enclosure and frequency favorites as future directions. They should not be advertised as already delivered. The useful engineering lesson is combining a tactile interface with compression, buffering and diagnostics on a small device.

![LittleM checks source version, wiring, setup and audio, marking physical validation as still pending](../../assets/images/SLUG-fig-03.png)

A sensible acceptance sequence is stable sound, effective controls and configuration persistence across reboot, followed by enclosure work. For an offline emergency receiver or local wideband RF instrument, choose hardware designed for that purpose. ESPica32 is an interesting network-SDR learning build with different requirements.

## FAQ

### Is owning a KiwiSDR necessary?

No. Accessible public receivers can be used, subject to the operator's rules and free channels. Their location and antenna determine reception. A privately operated Kiwi gives more control but is not a required component of the client.

### Where is the official GitHub repository?

This review verified the author's website archive, not an official ESPica32 GitHub repository. The related `jks-prv/kiwiclient` repository provides Python clients and protocol reference material; it is a different project.

### Was worldwide smooth listening demonstrated here?

No. The evidence here is source inspection, an 8192-sample decoder comparison and buffer-control assertions. Cross-country listening comes from the author's report; physical hardware, actual server access and long-running stability need separate validation.

## Sources and related reading

Author and download entry: https://www.todo-sdr.com/espica32-cliente-kiwisdr/

Author's source archive: https://www.todo-sdr.com/wp-content/uploads/2026/11/kiwi-radio-mini.rar

Media report: https://www.rtl-sdr.com/espica32-a-standalone-esp32-radio-for-tuning-any-kiwisdr-with-no-pc-or-phone/

Related protocol/tools reference, not the ESPica32 repository: https://github.com/jks-prv/kiwiclient

Public receiver directory: https://kiwisdr.com/public/

Related ESP32 ADS-B analysis: https://blog.mushroom.cv/blog/esp32-adsb-receiver-analysis/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
'''
meta={'title':'ESPica32：把远方KiwiSDR装进ESP32旋钮收音机','titleEn':'ESPica32: A Knob-Controlled KiwiSDR Wi-Fi Radio','description':'ESPica32让ESP32通过Wi-Fi控制远方KiwiSDR并播放音频。本文核对作者源码包、OLED与功放接线、Arduino版本和ADPCM缓冲设计，解释四块模块之外的采购需求、嵌套旧代码和首次配网步骤，记录8192样本解码比较与缓冲断言结果，并区分作者跨国收听报告、本机辅助验证与仍待实板确认的能力。','descriptionEn':'Review ESPica32 hardware, source archive, ADPCM and buffering, with host decoder checks and clear limits on remote reception, setup and firmware validation.','wechatTitle':'ESPica32：ESP32旋钮收音机','wechatDigest':'通过Wi-Fi收听远方KiwiSDR，拆解接线、源码与ADPCM音频方案。','pubDate':'2026-11-08','updatedDate':'2026-11-08','category':'Tech-Experiment','tags':['ESPica32','ESP32','KiwiSDR','DIY硬件','网络收音机'],'heroImage':f'../../assets/images/{s}-banner.jpg'}
# Descriptions are checked explicitly before publication.
text='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False)for k,v in meta.items())+'\n---\n\n'+cn.replace('SLUG',s)+'\n<!--EN-->\n\n'+en.replace('SLUG',s)
Path('src/content/blog',s+'.md').write_text(text)
print({k:len(meta[k])for k in ['titleEn','description','descriptionEn','wechatTitle','wechatDigest']})
