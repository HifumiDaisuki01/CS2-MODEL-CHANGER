# Lime E source-conversion development record

These scripts record the actual local conversion and serialized-DMX verification; they contain private-workspace input paths and require srctools plus the existing server/ag2-port/tools modules/vendor porter. They are NOT portable one-click builders. Review and substitute paths, create a new output directory, supply your own authorized model source and original phase2 mesh, and verify rigid bind transforms before any reuse. No model binaries/DMX are included. Use the parent directory Run-Build.ps1 / Build-AG2.ps1 for the already prepared private compile package. Do not run these against live server or original model files.

Do not interpret source-stage reports' WindowsCompiled=false as the final state: those reports are immutable stage evidence. The final v0.5.0 compile reports and user feedback are recorded separately.
