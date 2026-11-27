# Upstream component policy

SIKE FORENSICS uses upstream projects as references and optional adapters rather than blindly copying repositories.

- **ForensiX**: optional multimodal runtime adapter. The framework is MIT, but model/weight licenses must be checked individually.
- **image-forensics-toolkit**: current repository is non-commercial; current code/weights are reference-only for the commercial SIKE build.
- **Forensic-Image-Analysis-Toolkit**: BSD-3-Clause techniques may be reused with required notices.
- **AI-Voice-Forensics**: architecture reference; non-commercial dataset/model assets are not shipped.
- **Image-Forensics-Tool**: browser-side metadata/file-structure UX reference.

Production rule: code license, model license, weight license, dataset license and usage restrictions must all be recorded before enabling a detector.
