# FS: Filtering and sanitizing AI data, inputs, and outputs

## FS-01 Dataset sanitization

HITRUST ID `07.10bAISecSystem.2` · Domain 07 Vulnerability Management · Control 10.b Input Data Validation  
Inheritable: Fully · Applies: ML models (predictive, generative)

> Data used for training, fine-tuning, and RAG is checked before use for suspicious or adversarial patterns such as poisoned samples, and anomalous entries are removed.

Evaluative elements:
- `FS-01[1]` Training data checked before use
- `FS-01[2]` Fine-tuning data checked before use _(if fine-tuning)_
- `FS-01[3]` RAG data checked before use _(if RAG)_
- `FS-01[4]` Suspicious entries removed

Note: ML models only. Fully inheritable.

## FS-02 Input filtering

HITRUST ID `07.10bAISecSystem.1` · Domain 07 Vulnerability Management · Control 10.b Input Data Validation  
Inheritable: Partially · Applies: all model types

> Before inputs reach the model, user inputs of any modality or source (including attachments) are actively filtered for suspicious or unexpected values or patterns that could be adversarial.

Evaluative elements:
- `FS-02[1]` User inputs filtered for suspicious or unexpected patterns before model processing

Note: Partially inheritable (AI platform provider, if used, and AI application provider).

## FS-03 Output encoding

HITRUST ID `07.10mAISecOrganizational.4` · Domain 07 Vulnerability Management · Control 10.m Control of Technical Vulnerabilities  
Inheritable: Partially · Applies: generative only

> Textual model output is encoded to prevent traditional injection attacks such as remote code execution.

Evaluative elements:
- `FS-03[1]` Output encoding applied to textual model output

Note: Generative AI only. Partially inheritable.

## FS-04 Output filtering

HITRUST ID `07.10eAISecSystem.1` · Domain 19 Data Protection & Privacy · Control 13.k Use and Disclosure  
Inheritable: Partially · Applies: generative only

> Unless specifically required otherwise, sensitive data (e.g., personal phone numbers) in generative model output is filtered or prevented from reaching end users.

Evaluative elements:
- `FS-04[1]` Sensitive data filtered or prevented in generative output

Note: Generative AI only. Partially inheritable.
