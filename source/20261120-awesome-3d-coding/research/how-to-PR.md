# How to open a pull request

Contributions to **Awesome-3D-Coding** can be as small as fixing a link or adding a missing paper. A good entry tells readers what 3D program or editable structure a project creates, evaluates, or lets someone change.

## Choose a table

Search the [README](README.md) for the project name and paper link first. If the work is already listed, update its row. For a new entry, choose the subsection where a reader would look for its main contribution.

| Section | What to describe |
| --- | --- |
| Benchmarks | What the model must produce or edit, and what the evaluator actually checks. |
| Datasets | The scale and counting unit, such as programs or instruction–script pairs, and what one sample contains. |
| Methods and Representations | The input, the resulting program or representation, and what the method contributes. |
| Modeling Systems | The runtime and how the system builds or revises a model. For interactive work, say what a designer can inspect or edit. |
| Evaluation Metrics | The property being measured and the implementation or protocol used to measure it. |
| Tools and Related Collections | What the tool helps someone do or which research area the collection covers. |

## Add or update the row

Copy a neighboring row so the columns match. Write the description in English and link to primary sources, such as the paper, authors’ code, dataset, or project page.

Use a linked **YYYY-MM** in the **Release date** column. For a paper, use its first arXiv submission or the publisher’s online publication date. For a dataset or code-only project, link to a dated release or upload of the resource. Put the venue and year in **Publication** when that column is present. Insert the row in descending month order within its table, after existing entries from the same month.

For example, the Frontier3DBench row belongs in **Benchmarks → Interactive Worlds**. Its description covers both the executable deliverables and the behavior that the benchmark evaluates.

```markdown
| **Frontier3DBench** | [2026-11](https://arxiv.org/abs/2611.09017v1) | arXiv 2026 | Build Blender objects and scenes and runnable Unreal Engine worlds. Across 145 tasks, evaluation checks rendered appearance, project structure, and runtime behavior. | [Paper](https://arxiv.org/abs/2611.09017) · [Code](https://github.com/Einsia/Frontier3D) · [Dataset](https://huggingface.co/datasets/Einsia/Frontier3DBench) · [Leaderboard](https://lab.einsia.ai/frontier3dbench/) |
```

## Submit on GitHub

1. Fork the repository, create a branch in your fork, and edit the README.
2. Use GitHub’s Markdown preview to check the row and open the links you added.
3. Commit the edit and open a pull request against the main branch of [jweihe/Awesome-3D-Coding](https://github.com/jweihe/Awesome-3D-Coding/pulls). Give it a descriptive title such as **Add Frontier3DBench to Interactive Worlds**. In the description, link the primary source and briefly explain the addition or correction.

If this is your own work, you’re welcome to say so in the pull request.
