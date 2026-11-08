# Scope

Official repository6be4453024c5acae9dcd0a191e26ee524e743310. SFT modelrevisionf972bd4b4b9e3852133cc5da954d87bc32cd8fb9;smallconfigs fetchedpinned andmatchedinitialmainread. No fullmodelweights downloaded. 42layer5B DiT isnotwholepipeline;Qwen3.5textencoderandFLUX2VAE areseparatecomponents. ModelcardsApache2,standalonepipelineApache2,communityadapters/components haveownterms.

Actual commands executed in temporary clone:
- python3 -m unittest discover -s skills/moss-image-prompt-enhancer/scripts -p test_compile_prompt.py -v :8pass.
- HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /tmp/moss-image-test-env/bin/python -m unittest discover -s tests -p test_mps_runtime.py -v :11pass.
MPS checks usemockedloaders/fakepipes/CPUarith/UIconstruction; notrealweightinference. Initialcollection lackedtransformers;installing it in temporaryenv resolvedtheenvironmentissue beforefinal11checks. No claimofnetworkisolation beyondHubofflineflags. FinalenvPython3.12.15 Torch2.15.0 Diffusers0.41.0 Transformers5.20.1 Accelerate1.15.0 Gradio6.30.0;notidenticaltodocumentedrealweightenvironment.

Ownworkedexample draft compiled usingactualscript, outputtwo boxeschecked andwidth/heightomissionverified. ItdoesnotcallimageAPI. No imagequality/OCRbenchmark/latency/peakRAM/GPUthroughput measured. AuthorLLTB96.3coverage ismultisetOCRrecall notexacttext/order/punctuationaccuracy;RLAwholePEsystemandsharedpromptbackbonecomparisons distinct. AuthorCUDAminimalmodepeaks3.65/3.85GiBGPU+14GiBRAM andMPSM1Max32GBminutes arequotedreportsnotours oruniversalmemoryminimums.

Banneradopts officialREADMEShanghai panorama samplewithsourceURLprovenance,1200x63093559bytes,machine0fail/manualpass. ItisnotourgeneratedMOSSresult. BodyfigsareLittleM explanatoryillustrations. Articleconstruction script ishistorical;donotrerunoverfinalfrozeninputs.
