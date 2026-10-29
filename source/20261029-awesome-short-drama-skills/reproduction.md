# Reproduction notes
Pinned upstream: https://github.com/UnderleveledBuilder/awesome-short-drama-skills/tree/4c3ba567a35325bd9041858d56116fc4ebbcdc43
Use Python3.11+; local checks used Python3.12.14. Read scripts before running.
Run from an isolated clone checked out at that commit:
```
python3.12 scripts/build.py --validate
python3.12 scripts/build.py --check
python3.12 evals/verify.py 001-open-brief
python3.12 evals/verify.py 002-topic
```
No --write flag was used. Verification reconstructs existing prompts and statistics; it does not call generation/judging models or rerun contestant skills. Installing the finder and generating a video were not part of this pass.
Agent-reach could not run: skill and executable unavailable. Jina Reader returned403. GitHub connector, isolated clone and official site/data.json succeeded. Broken user URL restored using all path segments. Official social image downloaded to the requested media directory; it is text-dominated and displays stale82+14counts. CatalogueandliveJSON agree99=83+16.
