# AI threats behind the requirements

HITRUST built the AI security requirements against a register of AI-specific threats. Use these names in threat-register reviews (TM-01), red-team scoping (TM-03) and findings. References as HITRUST cites them.

| Threat | Typical references | Requirements that counter it |
|---|---|---|
| Prompt injection (direct and indirect) | OWASP LLM01; NIST AI 100-2 §3.3-3.4; MITRE ATLAS AML.T0051 | FS-02, LM-02, AX-03, GV-03, TM-03 |
| Data poisoning | OWASP LLM03 (2023) / LLM04 (2025), ML02, ML08; NIST AI 100-2 §2.3; AML.T0020 | FS-01, IN-02, IN-03, AX-04, LM-03, MR-03 |
| Model poisoning | OWASP LLM04 (2025), ML10; NIST AI 100-2 §2.3.4; AML.T0018 | AX-05, LM-03, DV-02, DV-04, DV-08 |
| Compromised third-party models or code | OWASP LLM05 (2023) / LLM03 (2025), ML06; AML.T0010 | DV-03, DV-08, SC-01, SC-02, SC-03 |
| Compromised third-party training datasets | OWASP LLM03/LLM05 (2023), ML02/ML06/ML08; AML.T0010.002, AML.T0019 | FS-01, IN-02, IN-03, SC-01, LC-02 |
| Model evasion | OWASP ML01; NIST AI 100-2 §2.2 | MR-03, FS-02, TM-03 |
| Model inversion | OWASP ML03; AML.T0024.001; NIST AI 100-2 §2.4 | MR-02, MR-01, AX-02 |
| Model stealing / extraction | OWASP LLM10 (2023); NIST AI 100-2 §2.4.3; AML.T0024.002 | AX-01, AX-02, MR-02, EN-02, AX-05 |
| Sensitive information disclosed in output | OWASP LLM06 (2023) / LLM02, LLM07 (2025); AML.T0056, AML.T0057 | FS-04, MR-01, AX-03, LM-01 |
| Confabulation (misinformation) | OWASP LLM09; NIST AI 600-1 §2.2 | GV-03, GV-01 |
| Excessive agency | OWASP LLM08 (2023) / LLM06 (2025) | AX-03, GV-03, DV-05, AX-06 |
| Harmful / insecure code generation (insecure output handling) | OWASP LLM02 (2023) | FS-03, GV-03 |
| Denial of AI service | OWASP LLM04 (2023) model DoS | AX-02, RS-02 |

The right-hand column is this tool's working map for interviews, not a HITRUST crosswalk. HITRUST's specification lists, for each requirement, the threats and control functions it addresses; check there when a finding needs the official link.
