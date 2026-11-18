# Measurement scope

No performance benchmark was run for this article. Upstream claims (about20x batch-search speedup,7925 x18n cases and29 functions) are attributed to upstream reports, not measured here. That README's opening narrative says6925cases while its table and rootREADME say7925; article explicitly follows the table/root figure as author-reported rather than adding them or claiming independently verified coverage.

Local tests count toolkit tests, not migrated business functions. The loop suite includes JS stand-ins for some replay tests, native build checks for others, and runtime-presence skips that return success rather than Rust ignored status. Therefore no claim that all six language runtimes were fully exercised. Initial loop17/19 plus selected Node22 recovery is not a clean full-suite rerun; Ruby build remains unresolved.

Library116/116 and PythonCLI1/1 ran and passed. The Python negative control changes only the fixture's division-by-zero error text; the test asserts mismatches appear in stderr and original replay passes. This is harness behavior verification, not speed testing or a complete Rust application lift. Source tracked diff remains empty.
