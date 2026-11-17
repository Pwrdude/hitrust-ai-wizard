# AX: Access to the AI system

## AX-01 Limit the release of technical information about the AI system

HITRUST ID `19.09zAISecOrganizational.1` · Domain 19 Data Protection & Privacy · Control 09.z Publicly Available Information  
Inheritable: No · Applies: ML models (predictive, generative), Q3 yes (confidential model architecture)

> The release of technical AI project details is limited: architecture, datasets, algorithms, language model tools, safety and security checkpoints, and team information.

Evaluative elements:
- `AX-01[1]` Overall technical architecture
- `AX-01[2]` Training/testing/validation/tuning datasets of confidential or closed-source models
- `AX-01[3]` RAG datasets _(if RAG)_
- `AX-01[4]` Algorithms of confidential or closed-source models
- `AX-01[5]` Architecture of confidential or closed-source models
- `AX-01[6]` Language model tools _(if agents/plugins)_
- `AX-01[7]` Safety and security checkpoints
- `AX-01[8]` Teams that develop and support the system

Note: Only when model architectures are confidential to the organization (Q3). Dual responsibility.

## AX-02 Model rate limiting / throttling

HITRUST ID `07.10mAISecOrganizational.5` · Domain 07 Vulnerability Management · Control 10.m Control of Technical Vulnerabilities  
Inheritable: Partially · Applies: all model types

> The total number and the rate of API calls a user can make to the AI model over a period are limited, to resist denial of service and hinder attack experimentation.

Evaluative elements:
- `AX-02[1]` Total API calls per user per period limited
- `AX-02[2]` Rate of API calls per user limited

Note: Partially inheritable (AI application and AI platform providers).

## AX-03 GenAI model least privilege

HITRUST ID `11.01cAISecSystem.5` · Domain 11 Access Control · Control 01.c Privilege Management  
Inheritable: No · Applies: generative only

> The data and capabilities granted to generative models, including through agents and plugins, are restricted to least privilege and governed by the access management and authentication policies.

Evaluative elements:
- `AX-03[1]` Generative model data access least privilege (incl. via agents/plugins)
- `AX-03[2]` Generative model capabilities least privilege (incl. via agents/plugins)
- `AX-03[3]` Access governed by access management policy (approvals, revocations, reviews)
- `AX-03[4]` Access governed by authentication policy

Note: Generative AI only. AI application provider's sole responsibility.

## AX-04 Restrict access to data used for AI

HITRUST ID `11.01cAISecSystem.6` · Domain 11 Access Control · Control 01.c Privilege Management  
Inheritable: Fully · Applies: ML models (predictive, generative)

> Access to training, testing, validation, fine-tuning, and RAG data (original and embedded) is restricted to least privilege under the access management policy and MFA-level authentication.

Evaluative elements:
- `AX-04[1]` Training/testing/validation data access least privilege
- `AX-04[2]` Fine-tuning data access least privilege _(if fine-tuning)_
- `AX-04[3]` Original (non-vectorized) RAG data access least privilege _(if RAG)_
- `AX-04[4]` RAG embeddings access least privilege _(if RAG)_
- `AX-04[5]` Access governed by access management policy
- `AX-04[6]` Access governed by authentication policy (MFA or equivalent)

Note: ML models only. Fully inheritable; may be the model creator's sole responsibility.

## AX-05 Restrict access to AI models

HITRUST ID `11.01cAISecSystem.7` · Domain 11 Access Control · Control 01.c Privilege Management  
Inheritable: Fully · Applies: ML models (predictive, generative)

> The ability to access and modify deployed AI models is restricted to least privilege under the access management policy and MFA-level authentication.

Evaluative elements:
- `AX-05[1]` Access to and modification of deployed models least privilege
- `AX-05[2]` Access governed by access management policy
- `AX-05[3]` Access governed by authentication policy (MFA or equivalent)

Note: ML models only. Fully inheritable; may be the AI platform provider's sole responsibility.

## AX-06 Restrict access to interact with the AI model

HITRUST ID `11.01cAISecSystem.8` · Domain 11 Access Control · Control 01.c Privilege Management  
Inheritable: Partially · Applies: all model types

> The ability to interact with the production model through APIs, the AI application, and agents/plugins is restricted to least privilege under the access management and authentication policies.

Evaluative elements:
- `AX-06[1]` Interaction via APIs least privilege
- `AX-06[2]` Interaction via the AI application least privilege
- `AX-06[3]` Interaction via agents/plugins least privilege _(if agents/plugins)_
- `AX-06[4]` Access governed by access management policy
- `AX-06[5]` Access governed by authentication policy

Note: Partially inheritable.

## AX-07 Restrict access to the AI engineering environment and AI code

HITRUST ID `11.01cAISecSystem.9` · Domain 11 Access Control · Control 01.c Privilege Management  
Inheritable: Partially · Applies: all model types

> Access to AI engineering environments, code that creates, trains, or deploys models, and agent/plugin code is restricted to least privilege under the access management policy and MFA-level authentication.

Evaluative elements:
- `AX-07[1]` AI engineering environment access least privilege
- `AX-07[2]` Model create/train/deploy code access least privilege
- `AX-07[3]` Agent/plugin code access least privilege _(if agents/plugins)_
- `AX-07[4]` Access governed by access management policy
- `AX-07[5]` Access governed by authentication policy (MFA or equivalent)

Note: Partially inheritable.
