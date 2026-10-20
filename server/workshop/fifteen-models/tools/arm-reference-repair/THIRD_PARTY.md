# Dependencies and attribution

ValveResourceFormat 20.1.7467: MIT, https://github.com/ValveResourceFormat/ValveResourceFormat (https://github.com/ValveResourceFormat/ValveResourceFormat/blob/master/LICENSE). Transitive ValveKeyValue 0.70.0.499: MIT, https://github.com/ValveResourceFormat/ValveKeyValue. Restore pinned NuGet dependencies and retain their license files on binary redistribution. This package includes our repair source, not third-party runtime binaries or model source licenses.

Build: dotnet build -c Release. See Program.cs for exact accepted models/CLI usage and safety checks. Do not apply the removal to arbitrary models: separate-arm-only models would lose their hands. This tool was validated on the four report-listed models with embedded FP meshes.
