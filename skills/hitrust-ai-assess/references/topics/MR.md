# MR: Model robustness

## MR-01 Data minimization or anonymization

HITRUST ID `19.13jAISecOrganizational.1` · Domain 19 Data Protection & Privacy · Control 13.j Data Minimization  
Inheritable: Fully · Applies: ML models (predictive, generative), Q2 yes (sensitive data used to train/tune/RAG)

> Data used for training, fine-tuning, and RAG prompt enhancement is reviewed to find fields or records that can be removed or anonymized to prevent leakage, and findings are acted on.

Evaluative elements:
- `MR-01[1]` Training data reviewed and minimized/anonymized
- `MR-01[2]` Fine-tuning data reviewed and minimized/anonymized _(if fine-tuning)_
- `MR-01[3]` RAG data reviewed and minimized/anonymized _(if RAG)_

Note: Only when confidential or sensitive data was used to train, tune, or enhance prompts (tailoring Q2). Not for rule-based-only systems. Fully inheritable.

## MR-02 Limit output specificity and precision

HITRUST ID `07.10mAISecOrganizational.3` · Domain 07 Vulnerability Management · Control 10.m Control of Technical Vulnerabilities  
Inheritable: No · Applies: ML models (predictive, generative), Q2 or Q3 yes

> The precision and specificity of AI outputs are reduced to limit an adversary's ability to extract information from the model or optimize attacks.

Evaluative elements:
- `MR-02[1]` Output precision reduced (e.g., rounded confidence values)
- `MR-02[2]` Output specificity reduced (e.g., coarser class labels)

Note: Only when sensitive data was used (Q2) or the model architecture is confidential (Q3). AI application provider's sole responsibility.

## MR-03 Additional training data measures

HITRUST ID `17.03bAISecOrganizational.3` · Domain 17 Risk Management · Control 03.b Performing Risk Assessments  
Inheritable: Fully · Applies: predictive (non-generative ML) only

> The organization evaluates whether additional training-data measures (e.g., adversarial training) are needed to make its ML models resistant to evasion and poisoning, documents the evaluation, repeats it at least semiannually and after AI security incidents, and implements the measures deemed necessary.

Evaluative elements:
- `MR-03[1]` Evaluation documented
- `MR-03[2]` Evaluation performed at least semiannually
- `MR-03[3]` Evaluation revisited after AI-related security incidents
- `MR-03[4]` Necessary measures implemented

Note: Non-generative (predictive) ML only. Fully inheritable (AI model creator).
