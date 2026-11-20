<h1 align="center"><img src="assets/cover.png" width="100%" alt="Awesome 3D Coding — a procedural lamp shown as a wireframe and a shaded model"></h1>

Papers, benchmarks, and datasets on generating 3D content as editable code, from Blender scenes and parametric CAD parts to interactive Three.js worlds. The collection also covers interfaces for editing the structure of generated models.

<p align="left">
  <a href="#3d-coding-benchmarks"><img src="assets/nav-benchmarks.svg" alt="Benchmarks" height="30"></a>
  <a href="#datasets-for-3d-code"><img src="assets/nav-datasets.svg" alt="Datasets" height="30"></a>
  <a href="#models-for-3d-code-generation"><img src="assets/nav-models.svg" alt="Methods" height="30"></a>
  <a href="#3d-modeling-agents"><img src="assets/nav-agents.svg" alt="Systems" height="30"></a>
  <a href="#evaluation-metrics"><img src="assets/nav-metrics.svg" alt="Metrics" height="30"></a>
</p>

<details open>
<summary><strong>🧭 Browse the full collection</strong></summary>

- [Benchmarks](#3d-coding-benchmarks)
  - [Asset Creation and Editing](#asset-creation-and-editing)
  - [Parametric CAD and Assembly](#parametric-cad-and-assembly)
  - [Interactive Worlds](#interactive-worlds)
- [Datasets](#datasets-for-3d-code)
  - [Assets and Scenes](#assets-and-scenes)
  - [CAD Programs](#cad-programs)
- [Methods and Representations](#models-for-3d-code-generation)
  - [Text to CAD](#text-to-cad)
  - [Shape to Code](#shape-to-code)
  - [Images and Drawings to Code](#images-and-drawings-to-code)
  - [Shape Program Synthesis](#shape-program-synthesis)
- [Modeling Systems](#3d-modeling-agents)
  - [Objects and Articulation](#objects-and-articulation)
  - [Scene Layout and Generation](#scene-layout-and-generation)
  - [Editing and Reconstruction](#editing-and-reconstruction)
- [Evaluation Metrics](#evaluation-metrics)
- [Tools](#development-tools)
- [Related Collections](#related-collections)
- [Contributing](#contributing)
- [Citation](#citation)

</details>

<a name="3d-coding-benchmarks"></a>

## 📏 Benchmarks

*Release date* links to the source for each month. Research papers use the first arXiv submission or the publisher’s online date. Code-only projects and datasets use a documented release or data upload.

Compare a Blender asset against reference views, test a CAD solid against its design brief, or trigger a browser interaction and inspect how the scene responds.

### Asset Creation and Editing

| Benchmark | Release date | Publication | Task and evaluation | Resources |
| --- | --- | --- | --- | --- |
| **BlenderWorld** | [2026-10](https://arxiv.org/abs/2610.23986v1) | arXiv 2026 | Deliver editable Blender projects for 223 creation briefs. Multi-view renders are scored against task-specific criteria and for overall visual quality. | [Paper](https://arxiv.org/abs/2610.23986) · [Code](https://github.com/QwenLM/BlenderWorld) · [Gallery](https://blenderworld.github.io/) |
| **3DCodeEdit** | [2026-10](https://arxiv.org/abs/2610.38231v1) | arXiv 2026 | Edit 108 Blender programs in response to 2,592 instructions. A verifier compares six matched views against a checklist of requested changes and features to preserve. | [Paper](https://arxiv.org/abs/2610.38231) · [Code](https://github.com/BinjieW/3DCodeEdit) · [Dataset](https://huggingface.co/datasets/BinjieW/3DCodeEdit) |
| **3DHarnessBench** | [2026-09](https://arxiv.org/abs/2609.06535v1) | arXiv 2026 | Recover an object as Blender Python under four access settings, from a single reference view to active inspection of the target in Blender. | [Paper](https://arxiv.org/abs/2609.06535) · [Project](https://3dharnessbench.com/) |
| **SceneActBench** | [2026-07](https://arxiv.org/abs/2607.22393v1) | arXiv 2026 | Act on multi-object scenes from images or video frames. Five tasks yield 520 cases from 210 source instances, scored against hidden geometry. | [Paper](https://arxiv.org/abs/2607.22393) · [Code](https://github.com/Feinaldo2/SceneActBench) |
| **4DBuildBench** | [2026-07](https://arxiv.org/abs/2607.01766v1) | arXiv 2026 | Generate 50 dynamic Blender scenes from text. Evaluation combines visual judgments with checks on simulation state to test whether the requested motion occurs. | [Paper](https://arxiv.org/abs/2607.01766) · [Project](https://dynsimworlds.github.io/) |
| **Code3DBench** | [2026-06](https://github.com/VladimirGl/Code3DBench/commit/02cb9299d0a39f02470da18314411d3a6cceaf8d) | 2026 release | Write Three.js object-building code from a single reference render. A fixed browser scaffold renders the result across 1,012 low-poly objects. | [Code](https://github.com/VladimirGl/Code3DBench) |
| **3DCodeBench** | [2026-05](https://arxiv.org/abs/2606.01057v1) | NeurIPS 2026 | Write Blender Python from text or reference views across 212 asset categories. Scorers check execution, mesh geometry, and rendered appearance. | [Paper](https://arxiv.org/abs/2606.01057) · [Code](https://github.com/gaoypeng/3dcodebench) · [Leaderboard](https://www.3dcodebench.com/) |
| **BlenderBench (VIGA)** | [2026-01](https://arxiv.org/abs/2601.11109v1) | arXiv 2026 | Follow multi-step visual editing tasks in Blender Python across three difficulty levels. | [Paper](https://arxiv.org/abs/2601.11109) · [Dataset](https://huggingface.co/datasets/DietCoke4671/blenderbench) |
| **IR3D-Bench** | [2025-06](https://arxiv.org/abs/2506.23329v1) | NeurIPS 2025 | Recreate a scene from an image with programming and rendering tools. Score object geometry, relative placement, and appearance. | [Paper](https://arxiv.org/abs/2506.23329) · [Code](https://github.com/LiuHengyu321/IR3D-Bench) |
| **BlenderGym** | [2025-04](https://arxiv.org/abs/2504.01786v1) | CVPR 2025 | Edit a starting Blender scene to match a target. Its 245 scenes cover geometry, lighting, materials, blend shapes, and placement. | [Paper](https://openaccess.thecvf.com/content/CVPR2025/html/Gu_BlenderGym_Benchmarking_Foundational_Model_Systems_for_Graphics_Editing_CVPR_2025_paper.html) · [Code](https://github.com/richard-guyunqi/BlenderGym-Open) · [Leaderboard](https://blendergym.github.io/) |
| **CADBench (BlenderLLM)** | [2024-12](https://arxiv.org/abs/2412.14203v1) | arXiv 2024 | Generate Blender scripts for 500 simulated requests and 200 requests from online forums. A judge scores each result against criteria specific to the request. | [Paper](https://arxiv.org/abs/2412.14203) · [Dataset](https://huggingface.co/datasets/FreedomIntelligence/CADBench) · [Code](https://github.com/FreedomIntelligence/BlenderLLM) |

<a name="cad-and-interactive-worlds"></a>

### Parametric CAD and Assembly

| Benchmark | Release date | Publication | Task and evaluation | Resources |
| --- | --- | --- | --- | --- |
| **Parametric CAD Bench v3** | [2026-11](https://arxiv.org/abs/2611.02659v1) | arXiv 2026 | Create or edit native FreeCAD parts across 100 tasks, including 40 engineering drawings. A verifier scores geometry and compliance with the design specification. | [Paper](https://arxiv.org/abs/2611.02659) · [Benchmark](https://cadbench.ai/) · [Verifier](https://github.com/gNucleus-AI/freecad-validator) |
| **P3D-Bench** | [2026-06](https://arxiv.org/abs/2606.11152v1) | arXiv 2026 | Generate parts or assemblies from text or images. The evaluation uses 100 cases from each of three task families and checks dimensions, topology, and part structure. | [Paper](https://arxiv.org/abs/2606.11152) · [Code](https://github.com/SpatiaOS/P3D-Bench) · [Dataset](https://huggingface.co/datasets/SpatiaOS/P3D-Bench) |
| **CADTestBench** | [2026-05](https://arxiv.org/abs/2605.07807v1) | NeurIPS 2026 | Build a part from a written specification. Executable tests query the resulting solid for the geometric and topological properties requested in the prompt. | [Paper](https://arxiv.org/abs/2605.07807) · [Code](https://github.com/dimitrismallis/CADTestBench) · [Examples](https://dimitrismallis.github.io/cadtests/) |
| **BenchCAD** | [2026-05](https://arxiv.org/abs/2605.10865v1) | arXiv 2026 | Read, generate, or edit industrial CadQuery programs across 106 part families. Image-to-code and code-edit tasks compare the resulting solid with a target. | [Paper](https://arxiv.org/abs/2605.10865) · [Code](https://github.com/BenchCAD/BenchCAD-main) |
| **CADBench** | [2026-05](https://arxiv.org/abs/2605.10873v1) | arXiv 2026 | Recover editable CAD from meshes or rendered views. Its 18,000 evaluation samples test geometric fidelity, executability, and program compactness. | [Paper](https://arxiv.org/abs/2605.10873) · [Code](https://github.com/anniedoris/CADBench) · [Dataset](https://huggingface.co/datasets/DeCoDELab/CADBench) |
| **Text2CAD-Bench** | [2026-05](https://arxiv.org/abs/2605.18430v1) | arXiv 2026 | Generate a part from either a geometric description or procedural instructions. The 600 curated examples span four complexity levels. | [Paper](https://arxiv.org/abs/2605.18430) |
| **CADGenBench** | [2026-05](https://github.com/huggingface/cadgenbench/commit/4ad74878fc2e3f524fef85ac65a1d990a4d59699) | 2026 release | Build a part from a drawing or edit a supplied STEP file. The scoring engine compares submitted solids with held-out reference geometry, and the baseline generates CAD code. | [Code](https://github.com/huggingface/cadgenbench) · [Leaderboard](https://huggingface.co/spaces/HuggingAI4Engineering/CADGenBench) |

### Interactive Worlds

| Benchmark | Release date | Publication | Task and evaluation | Resources |
| --- | --- | --- | --- | --- |
| **Frontier3DBench** | [2026-11](https://arxiv.org/abs/2611.09017v1) | arXiv 2026 | Build Blender objects and scenes and runnable Unreal Engine worlds. Across 145 tasks, evaluation checks rendered appearance, project structure, and runtime behavior. | [Paper](https://arxiv.org/abs/2611.09017) · [Code](https://github.com/Einsia/Frontier3D) · [Dataset](https://huggingface.co/datasets/Einsia/Frontier3DBench) · [Leaderboard](https://lab.einsia.ai/frontier3dbench/) |
| **WorldBench** | [2026-10](https://arxiv.org/abs/2610.10622v1) | arXiv 2026 | Use one detailed voxel-island brief to test an open-ended Three.js world. The judge inspects source, navigates between biomes, and advances the in-world clock. | [Paper](https://arxiv.org/abs/2610.10622) |
| **WorldCoder-Bench** | [2026-06](https://arxiv.org/abs/2606.01869v1) | arXiv 2026 | Build an interactive Three.js world. StateProbe triggers actions in a browser and checks resulting state transitions. | [Paper](https://arxiv.org/abs/2606.01869) · [Code](https://github.com/shuolucs/WorldCoder-Bench) |
| **VoxelCodeBench** | [2026-04](https://arxiv.org/abs/2604.02580v1) | arXiv 2026 | Execute generated voxel-manipulation code in Unreal Engine. Tasks cover symbol interpretation, geometric construction, and artistic composition. | [Paper](https://arxiv.org/abs/2604.02580) |

<a name="datasets-for-3d-code"></a>

## 🗂️ Datasets

<a name="procedural-assets-and-scene-programs"></a>

### Assets and Scenes

| Dataset | Release date | Reported scale | What a sample contains | Resources |
| --- | --- | --- | --- | --- |
| **3DCodeVerse-2M** | [2026-10](https://github.com/gaoypeng/3dcodeverse/blob/2aab24df3cba8e434df0b071a0c0b5f7cc269211/README.md) | 2,028,286 caption–program pairs in the merged text split | One caption paired with code. The same program can have several captions. The corpus spans Blender Python, CadQuery, OpenSCAD, Three.js, GLSL, and URDF. | [Dataset and schema](https://huggingface.co/datasets/3dcodeverse/3dcodeverse-2m) |
| **3DCodeData** | [2026-05](https://github.com/gaoypeng/3dcodebench/blob/00e1e4d9bb0f44eab7ba57139e0858504e536fef/README.md) | 12,720 asset instances from 212 procedural generators | One parameterized Blender asset with scripts, captions, four rendered views, and textured and geometry-only mesh exports. | [Dataset](https://huggingface.co/datasets/YipengGao/3DCode) |
| **BlenderRAG** | [2026-05](https://huggingface.co/datasets/MaxRondelli/BlenderRAG/commit/87879daf1b7e6b9b802ec7b3e7879397494c7da9) | 500 objects in 50 categories | A Blender Python script, its rendered image, and a text description. Indoor and outdoor subsets each contain 250 objects. | [Dataset](https://huggingface.co/datasets/MaxRondelli/BlenderRAG) · [Paper](https://arxiv.org/abs/2605.00632) |
| **MeshCoder object corpus** | [2025-11](https://github.com/InternRobotics/MeshCoder/blob/8d27cde8076b56b78b82d133f670cafe2a95a8b3/README.md) | 1 million object–code pairs in the study (100K released) | An Infinigen-derived object paired with a Blender program organized by semantic part. The paper separately describes synthetic part-level training pairs. | [Paper](https://arxiv.org/abs/2508.14879) · [Code](https://github.com/InternRobotics/MeshCoder) |
| **VLMaterial** | [2025-02](https://github.com/mit-gfx/VLMaterial/blob/5193dadfdd3d2e9e08f8ad8d970bc7538b2ee3f0/README.md) | 1,640 seed materials, over 550,000 after augmentation | A procedural Blender material encoded as Python and paired with a render. The authors vary both shader graph structure and node parameters. | [Code](https://github.com/mit-gfx/VLMaterial) · [Paper](https://arxiv.org/abs/2501.18623) |
| **BlendNet** | [2024-12](https://huggingface.co/datasets/FreedomIntelligence/BlendNet/commit/c30addb1b074a47e53f18a4f845781276dbc6aaa) | 12K instruction–script pairs | A modeling instruction paired with Blender Python. Human annotators labeled 2K examples and GPT-4o labeled the other 10K. | [Dataset](https://huggingface.co/datasets/FreedomIntelligence/BlendNet) · [Paper](https://arxiv.org/abs/2412.14203) |
| **ShapeAssembly programs** | [2020-09](https://github.com/rkjones4/ShapeAssembly/blob/3e2152e2c629818fa03223a1dc219518b54b5dd7/README.md) | 3 released furniture categories | A PartNet-derived chair, table, or storage design encoded as a hierarchy of cuboids and attachment operations. The release includes parsed programs and their interpreter. | [Code](https://github.com/rkjones4/ShapeAssembly) · [Paper](https://arxiv.org/abs/2009.08026) |

<a name="parametric-cad-programs"></a>

### CAD Programs

| Dataset | Release date | Reported scale | What a sample contains | Resources |
| --- | --- | --- | --- | --- |
| **CodeCAD v2** | [2026-08](https://gitlab.lrz.de/ai-ad/codecad/-/tree/master#changelog) | 76,047 models in v2 | A human-written OpenSCAD file with a rendered thumbnail, license metadata, and a description of how to construct the part. | [Dataset](https://gitlab.lrz.de/ai-ad/codecad/-/tree/master) · [Paper](https://doi.org/10.1145/3770855.3817592) |
| **CADFS** | [2026-05](https://huggingface.co/datasets/VladPyatov/CADFS/commit/961a17cca7a637916d45f590e1412df459af0001) | 382,609 models in the deduplicated subset | A FeatureScript construction history with text annotations. Model IDs connect the programs to multiview renders and reference geometry. | [Dataset](https://huggingface.co/datasets/VladPyatov/CADFS) · [Paper](https://arxiv.org/abs/2605.01925) |
| **Zero-to-CAD 1M** | [2026-04](https://huggingface.co/datasets/ADSKAILab/Zero-To-CAD-1m/commit/b2fb49752edccc7ebf02e0c6278ffa4cf47704ef) | 1 million construction sequences | A synthetic CadQuery program with its operation list and exported STEP geometry. Programs come from an agent interacting with a CAD execution environment. | [Dataset](https://huggingface.co/datasets/ADSKAILab/Zero-To-CAD-1m) · [Paper](https://arxiv.org/abs/2604.24479) |
| **Ortho2CAD drawings** | [2026-03](https://huggingface.co/datasets/AdityaJoglekar/Ortho2CAD_Orthographic_Drawings/commit/98a564cc5afab5b597f34d6a4d1d916c40ec135c) | Over 1 million drawings generated in the study | Orthographic projections rendered from STEP geometry, including hidden lines. The released DeepCAD and Fusion 360 subsets provide drawings and training annotations. | [Code](https://github.com/AdityaJoglekar/Ortho2CAD) · [Paper](https://arxiv.org/abs/2607.08891) |
| **CAD-Coder training data (Guan et al.)** | [2026-01](https://huggingface.co/datasets/gudo7208/CAD-Coder/commit/484e3e675533b5ced3e20afd48588a3a751cf4f6) | 156,954 rows in the full synthesized training file | A geometric description and executable CadQuery answer. The release identifies the smaller subset used for supervised fine-tuning. | [Dataset](https://huggingface.co/datasets/gudo7208/CAD-Coder) |
| **Text-to-CadQuery** | [2025-05](https://huggingface.co/ricemonster/NeurIPS11092/commit/3ade5c4f8a1d9bfae4e55bf19751b9124dfa97fb) | 170,000 annotated Text2CAD examples | A part description paired with CadQuery code that constructs the solid. | [Annotations](https://huggingface.co/ricemonster/NeurIPS11092/blob/main/CadQuery.zip) · [Scripts](https://github.com/Text-to-CadQuery/Text-to-CadQuery) |
| **GenCAD-Code (Doris et al.)** | [2025-05](https://huggingface.co/datasets/CADCoder/GenCAD-Code/commit/d2262c5e3a7a77ca21d7c28b8888b83c4c1992f8) | Over 163,000 image–code pairs | A CAD render paired with the CadQuery Python script for reconstructing the solid from that view. | [Dataset](https://github.com/anniedoris/GenCAD-Code) · [Paper](https://arxiv.org/abs/2505.14646) |
| **CAD-Recode** | [2025-01](https://huggingface.co/datasets/filapro/cad-recode/commit/5e6439e5cc2e1a6bc2403c341c9c01154b8adf35) | 1 million generated CAD sequences in the ICCV study | A sequence of sketch and extrusion operations expressed in Python. The authors sample points on the resulting geometry to train a model to recover the code. | [Project and data releases](https://cad-recode.github.io/) |
| **Text2CAD** | [2024-12](https://github.com/SadilKhan/Text2CAD/blob/39361828b0907a8c06ee3ec4893ac68f12f8b852/README.md) | About 170,000 models and 660,000 text annotations | DeepCAD construction sequences paired with descriptions ranging from a short shape specification to detailed modeling instructions. | [Code](https://github.com/SadilKhan/Text2CAD) · [Dataset](https://huggingface.co/datasets/SadilKhan/Text2CAD) |
| **DeepCAD** | [2021-07](https://github.com/ChrisWu1997/DeepCAD/blob/ed8b8a6ceb342ad2bf1bb837a0c4aa2d0a91c877/README.md) | 178,238 CAD models | A solid paired with the sequence of sketch and extrusion commands that constructs it, encoded as operations and parameters. | [Project](https://www.cs.columbia.edu/cg/deepcad/index.html) |
| **Fusion 360 Gallery Reconstruction** | [2020-10](https://github.com/AutodeskAILab/Fusion360GalleryDataset/blob/76f9e8e41112388ac1e5e5afdbb622d219b74f92/README.md) | 8,625 human design sequences | The ordered sketches and extrusions that a user performed to build a CAD part. The project includes tools to replay the construction history. | [Dataset](https://github.com/AutodeskAILab/Fusion360GalleryDataset/blob/master/docs/reconstruction.md) · [Paper](https://arxiv.org/abs/2010.02392) |

<a name="models-for-3d-code-generation"></a>

## 🧊 Methods and Representations

### Text to CAD

| Method | Release date | Publication | Input → program | Highlight | Resources |
| --- | --- | --- | --- | --- | --- |
| **Text-to-CadQuery** | [2025-05](https://arxiv.org/abs/2505.06507v1) | arXiv 2025 | Part description → CadQuery Python | Fine-tunes language models to turn a specification into an editable parametric solid. | [Paper](https://arxiv.org/abs/2505.06507) · [Code](https://github.com/Text-to-CadQuery/Text-to-CadQuery) |
| **CAD-Coder (Guan et al.)** | [2025-05](https://arxiv.org/abs/2505.19713v1) | NeurIPS 2025 | Part description → CadQuery Python | Trains on paired examples, then uses distance between the generated and target shapes as a reward. | [Paper](https://arxiv.org/abs/2505.19713) · [Code](https://github.com/gudo7208/CAD-Coder) |
| **CAD-Editor** | [2025-02](https://arxiv.org/abs/2502.03997v1) | ICML 2025 | Existing CAD sequence + edit request → revised sequence | Locates the operations affected by an instruction, then infills that portion of the construction sequence. | [Paper](https://proceedings.mlr.press/v267/yuan25g.html) · [Code](https://github.com/microsoft/CAD-Editor) |
| **BlenderLLM** | [2024-12](https://arxiv.org/abs/2412.14203v1) | arXiv 2024 | Modeling instruction → Blender Python | Fine-tunes a code model on BlendNet and uses iterative self-improvement to refine script generation. | [Paper](https://arxiv.org/abs/2412.14203) · [Code](https://github.com/FreedomIntelligence/BlenderLLM) · [Weights](https://huggingface.co/FreedomIntelligence/BlenderLLM) |
| **Text2CAD** | [2024-09](https://arxiv.org/abs/2409.17106v1) | NeurIPS 2024 | Description → CAD operation sequence | Predicts sketch and extrusion operations from instructions with different levels of detail. | [Paper](https://arxiv.org/abs/2409.17106) · [Code](https://github.com/SadilKhan/Text2CAD) |

### Shape to Code

| Method | Release date | Publication | Input → program | Highlight | Resources |
| --- | --- | --- | --- | --- | --- |
| **MeshCoder** | [2025-08](https://arxiv.org/abs/2508.14879v1) | NeurIPS 2025 | Point cloud → Blender Python | Represents a mesh as a program organized by part, so a user can modify one component of the reconstruction. | [Paper](https://arxiv.org/abs/2508.14879) · [Code](https://github.com/InternRobotics/MeshCoder) · [Project](https://daibingquan.github.io/MeshCoder/) |
| **cadrille** | [2025-05](https://arxiv.org/abs/2505.22914v1) | ICLR 2026 | Point cloud, image, or text → CAD code | Trains one model across all three input modalities and refines it using feedback from program execution. | [Paper](https://arxiv.org/abs/2505.22914) · [Code](https://github.com/col14m/cadrille) |
| **CAD-Recode** | [2024-12](https://arxiv.org/abs/2412.14042v1) | ICCV 2025 | Point cloud → CadQuery Python | Recovers the sketches and extrusions that build a solid. Editing a sketch dimension changes the reconstructed part. | [Paper](https://openaccess.thecvf.com/content/ICCV2025/html/Rukhovich_CAD-Recode_Reverse_Engineering_CAD_Code_from_Point_Clouds_ICCV_2025_paper.html) · [Code](https://github.com/filaPro/cad-recode) · [Project](https://cad-recode.github.io/) |
| **CAD-SIGNet** | [2024-02](https://arxiv.org/abs/2402.17678v1) | CVPR 2024 | Point cloud → sketch-and-extrude sequence | Recovers a design history or proposes several plausible next operations for a partially specified part. | [Paper](https://arxiv.org/abs/2402.17678) · [Project](https://skazizali.com/cadsignet.github.io/) |

<a name="images-and-drawings-to-programs"></a>

### Images and Drawings to Code

| Method | Release date | Publication | Input → program | Highlight | Resources |
| --- | --- | --- | --- | --- | --- |
| **Ortho2CAD** | [2026-07](https://arxiv.org/abs/2607.08891v1) | arXiv 2026 | Orthographic drawing → CadQuery Python | Uses dimensioned projections for reconstruction. Its refinement loop renders the predicted solid from the drawing views to guide code corrections. | [Paper](https://arxiv.org/abs/2607.08891) · [Code](https://github.com/AdityaJoglekar/Ortho2CAD) |
| **CADFS-2B** | [2026-05](https://arxiv.org/abs/2605.01925v1) | CVPR 2026 | Multiview images or text → Onshape FeatureScript | Learns from feature histories spanning 15 CAD operations, including operations beyond sketching and extrusion. | [Paper](https://arxiv.org/abs/2605.01925) · [Code](https://github.com/VladPyatov/CADFS) · [Weights](https://huggingface.co/VladPyatov/CADFS-2B) |
| **CAD-Coder (Doris et al.)** | [2025-05](https://arxiv.org/abs/2505.14646v1) | arXiv 2025 | Part image → CadQuery Python | Fine-tunes a vision-language model on the GenCAD-Code image–program pairs for editable single-view CAD reconstruction. | [Paper](https://arxiv.org/abs/2505.14646) · [Code](https://github.com/anniedoris/CAD-Coder) |
| **VLMaterial** | [2025-01](https://arxiv.org/abs/2501.18623v1) | ICLR 2025 | Material image → Blender shader program | Predicts Python that builds a procedural material graph, exposing its nodes and parameters for later edits. | [Paper](https://arxiv.org/abs/2501.18623) · [Code](https://github.com/mit-gfx/VLMaterial) |
| **Img2CAD** | [2024-07](https://arxiv.org/abs/2408.01437v1) | SIGGRAPH Asia 2025 | Image → parametric CAD representation | Predicts the discrete structure of a design first, then estimates its continuous parameters conditioned on that structure. | [Paper](https://arxiv.org/abs/2408.01437) · [Code](https://github.com/qq456cvb/Img2CAD) |
| **Real2Code** | [2024-06](https://arxiv.org/abs/2406.08474v1) | ICLR 2025 | Object views → joint articulation code | Reconstructs part geometry first. A language model uses oriented part boxes to infer where and how the joints move. | [Paper](https://arxiv.org/abs/2406.08474) · [Project](https://real2code.github.io/) |

### Shape Program Synthesis

| Method | Release date | Publication | Input → program | Highlight | Resources |
| --- | --- | --- | --- | --- | --- |
| **ShapeCoder** | [2023-05](https://arxiv.org/abs/2305.05661v1) | SIGGRAPH 2023 | Unstructured primitives → reusable shape programs | Learns functions shared across shapes and infers a program for each shape using those functions. | [Project](https://rkjones4.github.io/shapecoder.html) · [Code](https://github.com/rkjones4/shapecoder) |
| **SkexGen** | [2022-07](https://arxiv.org/abs/2207.04632v1) | ICML 2022 | Latent codes → sketch-and-extrude sequence | Separate codebooks control topology, geometry, and extrusion, so a designer can vary one property across generated solids. | [Paper](https://arxiv.org/abs/2207.04632) · [Code](https://github.com/samxuxiang/SkexGen) |
| **ShapeMOD** | [2021-04](https://arxiv.org/abs/2104.06392v1) | SIGGRAPH 2021 | Shape programs → reusable macros | Refactors repeated operations across a collection into shared functions, exposing editable parameters such as leg spacing. | [Project](https://rkjones4.github.io/shapeMOD.html) · [Code](https://github.com/rkjones4/ShapeMOD) |
| **ShapeAssembly** | [2020-09](https://arxiv.org/abs/2009.08026v1) | SIGGRAPH Asia 2020 | Learned shape representation → assembly program | Generates hierarchical cuboid programs with attachment and symmetry operations. Varying their parameters creates related shapes. | [Paper](https://arxiv.org/abs/2009.08026) · [Code](https://github.com/rkjones4/ShapeAssembly) |
| **CSGNet** | [2017-12](https://arxiv.org/abs/1712.08290v1) | CVPR 2018 | Shape → constructive solid geometry program | Parses a target shape into primitives and Boolean operations whose execution reconstructs the geometry. | [Project](https://hippogriff.github.io/CSGNet/) |

<a name="3d-modeling-agents"></a>

## 🤖 Modeling Systems

### Objects and Articulation

| System | Release date | Publication | Runtime | How it builds or edits 3D content | Resources |
| --- | --- | --- | --- | --- | --- |
| **3DCodeVerse** | [2026-10](https://arxiv.org/abs/2610.22341v1) | arXiv 2026 | Blender, CAD, and web graphics | Runs the generated program, measures the resulting asset, and inspects renders to identify which part of the program to revise. | [Paper](https://arxiv.org/abs/2610.22341) · [Code](https://github.com/gaoypeng/3dcodeverse) |
| **aDSL** | [2026-08](https://arxiv.org/abs/2608.17975v1) | arXiv 2026 | Assembly DSL | Plans and generates shapes with relational placement operators. Execution feedback lets the agent repair violated constraints. | [Paper](https://arxiv.org/abs/2608.17975) · [Code](https://github.com/sig-pku/aDSL) |
| **Procedura** | [2026-08](https://arxiv.org/abs/2608.26238v1) | arXiv 2026 | Parametric assembly programs | Builds named parts joined by typed mates. It checks compilation and connectivity before using rendered views to refine individual parts. | [Paper](https://arxiv.org/abs/2608.26238) |
| **CADSmith** | [2026-03](https://arxiv.org/abs/2603.26512v1) | arXiv 2026 | CadQuery / OpenCASCADE | Writes a part from text, repairs execution errors, and revises its geometry using kernel measurements and rendered views. | [Paper](https://arxiv.org/abs/2603.26512) |
| **LL3M** | [2025-08](https://arxiv.org/abs/2508.08228v1) | arXiv 2025 | Blender | Writes and debugs scripts for geometry and materials. Rendered views and follow-up instructions guide subsequent edits. | [Paper](https://arxiv.org/abs/2508.08228) · [Gallery](https://threedle.github.io/ll3m/) |
| **Articulate-Anything** | [2024-10](https://arxiv.org/abs/2410.13882v1) | ICLR 2025 | Python → URDF | Retrieves part meshes and generates joint and link programs from text, images, or video. Simulated motion gives the critic feedback about articulation. | [Paper](https://arxiv.org/abs/2410.13882) · [Code](https://github.com/vlongle/articulate-anything) |

### Scene Layout and Generation

| System | Release date | Publication | Runtime | How it builds or edits 3D content | Resources |
| --- | --- | --- | --- | --- | --- |
| **SimWorlds** | [2026-07](https://arxiv.org/abs/2607.01766v1) | arXiv 2026 | Blender | Coordinates layout, physics solvers, and timing to build dynamic scenes from text. The reviewer inspects simulation state to diagnose motion failures. | [Paper](https://arxiv.org/abs/2607.01766) · [Project](https://dynsimworlds.github.io/) |
| **SceneCode** | [2026-05](https://arxiv.org/abs/2605.19587v1) | arXiv 2026 | Blender Python → simulation assets | Turns a room brief into object requests, generates part-level programs, and assembles the results into an editable scene with articulated objects. | [Paper](https://arxiv.org/abs/2605.19587) |
| **Code-as-Room** | [2026-05](https://arxiv.org/abs/2605.18451v1) | arXiv 2026 | Blender Python | Parses objects and spatial relationships from a top-down room image, then writes code for geometry, materials, and lighting. | [Paper](https://arxiv.org/abs/2605.18451) · [Code](https://github.com/YxuanAr/Code-as-Room) |
| **Procedural Scene Programs** | [2025-10](https://arxiv.org/abs/2510.16147v1) | SIGGRAPH Asia 2025 | Imperative layout programs | Places each object relative to earlier objects. A program search corrects invalid layouts while preserving the proposed arrangement. | [Paper](https://arxiv.org/abs/2510.16147) |
| **SceneWeaver** | [2025-09](https://arxiv.org/abs/2509.20414v1) | NeurIPS 2025 | Blender + Infinigen | Combines a scene planner with an executor and uses feedback on intermediate scenes to revise its construction plan. | [Paper](https://arxiv.org/abs/2509.20414) · [Code](https://github.com/Scene-Weaver/SceneWeaver) |
| **The Scene Language** | [2024-10](https://arxiv.org/abs/2410.16770v1) | CVPR 2025 | Scene programs with multiple renderers | Infers a hierarchy of entity functions from text or an image. Words encode each entity’s class and embeddings capture its visual identity. | [Paper](https://arxiv.org/abs/2410.16770) · [Project](https://ai.stanford.edu/~yzzhang/projects/scene-language/) |
| **SceneCraft** | [2024-03](https://arxiv.org/abs/2403.01248v1) | ICML 2024 | Blender | Assembles assets from a scene description, checks their spatial relationships, and reuses placement functions across scenes. | [Paper](https://proceedings.mlr.press/v235/hu24g.html) |
| **Open-Universe Indoor Scene Generation** | [2024-02](https://arxiv.org/abs/2403.09675v1) | arXiv 2024 | Layout DSL + constraint solver | Compiles language into spatial constraints, solves for object poses, and retrieves meshes to populate the layout. | [Paper](https://arxiv.org/abs/2403.09675) |
| **3D-GPT** | [2023-10](https://arxiv.org/abs/2310.12945v1) | 3DV 2025 | Blender + Infinigen | Selects procedural functions, infers their parameters from instructions, and writes Python calls to build the scene. | [Paper](https://arxiv.org/abs/2310.12945) · [Code](https://github.com/Chuny1/3DGPT) |

<a name="visual-editing-and-inverse-graphics"></a>
<a name="human-ai-co-creation"></a>

### Editing and Reconstruction

| System | Release date | Publication | Runtime | How it builds or edits 3D content | Resources |
| --- | --- | --- | --- | --- | --- |
| **Treellis** | [2026-11](https://doi.org/10.1145/3830398.3830694) | UIST 2026 · Best Paper | Browser | Generates an editable assembly tree of parts, operations, and repeats. Designers can adjust part parameters directly or prompt the AI to revise a selected subtree. | [Paper](https://doi.org/10.1145/3830398.3830694) · [Project](https://www.aid-lab.org/treellis) · [Demo](https://www.treellis.art/) |
| **Thinking in Blender (SEIG)** | [2026-06](https://arxiv.org/abs/2606.02580v1) | arXiv 2026 | Blender | Reconstructs one image as an editable scene by refining geometry, materials, composition, and lighting in stages. | [Paper](https://arxiv.org/abs/2606.02580) |
| **VIGA** | [2026-01](https://arxiv.org/abs/2601.11109v1) | arXiv 2026 | Blender Python | Alternates between writing code, rendering a scene, and inspecting differences from the target to guide the next edit. | [Paper](https://arxiv.org/abs/2601.11109) · [Code](https://github.com/Fugtemypt123/VIGA) |
| **BlenderAlchemy** | [2024-04](https://arxiv.org/abs/2404.17672v1) | ECCV 2024 | Blender | Proposes program edits and evaluates the renders against the visual goal. The examples show how changes to procedural materials affect a scene. | [Paper](https://arxiv.org/abs/2404.17672) · [Code](https://github.com/ianhuang0630/BlenderAlchemyOfficial) |

<a name="evaluation-metrics"></a>

## 📐 Evaluation Metrics

Dates refer to the linked scoring implementation or evaluation protocol.

| Property | Release date | Measure | What the evaluator inspects | Implementation or protocol |
| --- | --- | --- | --- | --- |
| **Interactive behavior** | [2026-06](https://arxiv.org/abs/2606.01869v1) | Verification coverage | Runtime states and transitions observed while the evaluator interacts with the generated scene. | [StateProbe](https://arxiv.org/abs/2606.01869) |
| **Executability** | [2026-05](https://github.com/gaoypeng/3dcodebench/blob/fe881f4c15b7273aedbccb6725ec98f11f8d18d1/metrics/README.md) | Execution rate | Whether each script completes in the target runtime. | [3DCodeBench scorers](https://github.com/gaoypeng/3dcodebench/blob/main/metrics/README.md) |
| **Shape** | [2026-05](https://github.com/gaoypeng/3dcodebench/blob/fe881f4c15b7273aedbccb6725ec98f11f8d18d1/metrics/README.md) | Chamfer distance | Distances between points sampled on generated and reference surfaces. | [3DCodeBench scorers](https://github.com/gaoypeng/3dcodebench/blob/main/metrics/README.md) |
| **Appearance** | [2026-05](https://github.com/gaoypeng/3dcodebench/blob/fe881f4c15b7273aedbccb6725ec98f11f8d18d1/metrics/README.md) | Multi-view image similarity | Corresponding renders of the generated and reference assets. Camera placement affects the comparison. | [3DCodeBench scorers](https://github.com/gaoypeng/3dcodebench/blob/main/metrics/README.md) |
| **CAD requirements** | [2026-05](https://arxiv.org/abs/2605.07807v1) | Test pass rate | Predicates over a solid's geometry and topology, derived from the design brief. | [CADTests](https://github.com/dimitrismallis/CADTestBench) |

<a name="development-tools"></a>

## 🛠️ Tools

| Tool | Release date | Description | Resources |
| --- | --- | --- | --- |
| **MCP for Blender** | [2025-03](https://github.com/ahujasid/mcp-for-blender/commit/320461d2fec4f911b5fa73272d4c5cc3c496bc46) | Connects a coding agent to a running Blender session to inspect objects and execute Python edits. | [Code](https://github.com/ahujasid/mcp-for-blender) |
| **Infinigen** | [2023-06](https://arxiv.org/abs/2306.09310v1) | Generates Blender assets and scenes from procedural rules. Researchers can reuse its generators to sample variations of the same asset or scene. | [Code](https://github.com/princeton-vl/infinigen) · [Project](https://infinigen.org/) |
| **CQ-editor** | [2020-05](https://github.com/CadQuery/CQ-editor/releases/tag/0.1) | Provides a graphical debugger for CadQuery. Step through a generated script to see which operation changes a face, edge, or solid. The date is for the stable 0.1 release. | [Code](https://github.com/CadQuery/CQ-editor) |

<a name="related-collections"></a>

## 📚 Related Collections

| Collection | Release date | Description | Resources |
| --- | --- | --- | --- |
| **Awesome 3D Skills** | [2026-11](https://github.com/zhuyansen/awesome-3d-skills/blob/bf2344b7d58acd3a8e7a702effce6e2824d97ded/README.md) | Catalogs agent integrations for Blender, CAD systems, and game engines. | [Repository](https://github.com/zhuyansen/awesome-3d-skills) |
| **Awesome Code as X** | [2026-09](https://github.com/kkakkkka/awesome-code-as-x/blob/ac951e90bc000ceed89bcdc6add960af403fb392/README.md) | Covers executable representations for agents. Its *Code as World* section includes scene and simulation programs. | [Repository](https://github.com/kkakkkka/awesome-code-as-x) |
| **Awesome AIGC 3D** | [2023-11](https://github.com/hitcslj/Awesome-AIGC-3D/blob/7ddf2592ed42d47e05defd23908ac85f3e04c000/README.md) | Organizes 3D generation research by asset type and production stage. Its survey tables inspired the format of this collection. | [Repository](https://github.com/hitcslj/Awesome-AIGC-3D) |

<a name="contributing"></a>

## 🤝 Contributing

Papers, datasets, tools, and corrections are welcome. See [How to open a pull request](how-to-PR.md) for entry formats and a worked example.

This collection is available under the [MIT License](LICENSE). Linked papers, datasets, and software carry their own terms.

<a name="citation"></a>

## 🔖 Citation

If you use this collection in your research, you can cite it with the BibTeX entry below or import the [citation file](CITATION.cff).

```bibtex
@misc{awesome3dcoding2026,
  author = {{Awesome-3D-Coding contributors}},
  title  = {{Awesome-3D-Coding}},
  year   = {2026},
  url    = {https://github.com/jweihe/Awesome-3D-Coding}
}
```
