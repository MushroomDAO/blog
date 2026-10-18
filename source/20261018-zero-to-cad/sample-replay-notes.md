# Scope of the local replay

One official test ground-truth program, UUID4b3aaa7b-f278-fc6a-8f9f-28fd4893be76. Manually reviewed before execution; only CadQuery imports and geometry operations. Python virtual environment isolates dependencies, not an execution security sandbox. Source2Bmodel not loaded. CadQuery2.6.1 on Python3.12.14,arm64. Valid single solid,14faces equals metadata, reference volume and STEP roundtrip volume agree within1e-7 relative tolerance; STEP53364B/STL60684B.

Bounding-box lengths are recorded for traceability, not asserted identical. Replayed shape was meshed during STL export whereas imported reference had not been meshed; OpenCascade bounding estimates can use triangulation/deflection margins. These numbers are not measured real-world dimensions. No geometry accuracy or model-quality score is derived from this one sample.
