---
name: LR2021 ESP32 ADS-B receiver analysis
description: W12 out-of-band aircraft receiver, filter modification, decoding and measured-claim boundaries
type: project
---
# W12 LR2021 ADS-B
Date: 2026-11-03
Slug: lr2021-esp32-adsb-receiver-analysis
Hackaday original: https://hackaday.com/2026/11/01/building-an-ads-b-receiver-for-less-than-you-think/
Hackaday author: Zoe Skyforest. Builder: thefatmoop.
Source: https://github.com/thefatmoop/esp32s3-lr2021-adsb-receiver
Commit: ab0f225b78ec2622b2cbe64f8601136c66a4aa29
Firmware GPL-3.0-or-later, release docs v1.0.1, upstream credits ADSBee/LakeShark/lr2021-sdr/TheClams.
Core facts: Real local 1090MHz reception/decoding, not cloud display and not LoRa modulation. W12 ESP32-S3 + LR2021 specifically; SX1262 boards not interchangeable. Hardware Manchester, software CRC/CPR/aircraft table, local web/TCP Beast. 1090MHz outside published LR2021 receive bands; PLL/software accepted frequency range does not prove RF specification. LF U12 SAW902-928MHz bypass required for author's better range; HF unmodified possible but worse in author's tests. 150NM=277.8km author-reported indoor915MHz antenna modified LF, not independent RF measurement/guarantee. Under50USD from Hackaday not current complete BOM quote.
Limits: 978UAT/surface positions not supplied, software timestamps not precision MLAT, map prediction not new reception, offline map USA not global, GNSS optional for receiver position not airborne globalCPR decoding.
Actual verification: six upstream native test groups executed successfully with C11 cc, Python and Node. Synthetic decoder/correction/wifi/stream/webserialization/browser polling only; no board/flash/RF/range/sensitivity/full firmware build tested.
Dedup: only bot raw KB, no existing article or M2 receipt; remote blocked40164 IP223.204.71.95. Blog proceeds, actual M2 once after publication, pause if fail.
Blog: pending.
WeChat: pending.

Source review: main/radio.c config1090000000Hz/2Mchip/s, hardware Manchester14byte output; main/adsb.c DF17/DF18 and payload-only limited correction, fresh clean trust, CPR. main/live.js bounded extrapolation. No independent RF measurement. Native test results recorded from actual execution; six groups passed once; script reruns upstream checks.
Cover uses genuine author hardware photograph, not synthetic dashboard or assembly illustration. Text on enclosure/OLED is real photographed marking; allowed warning for adopted image.
