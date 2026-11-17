# EN: Encryption of AI assets

## EN-01 Encrypt traffic to and from the AI model

HITRUST ID `09.09sAISecOrganizational.1` · Domain 09 Transmission Protection · Control 09.s Information Exchange Policies and Procedures  
Inheritable: Fully · Applies: all model types

> Communication channels between the model and the interface that displays its outputs are encrypted with secure protocols such as TLS.

Evaluative elements:
- `EN-01[1]` Model-to-interface channels encrypted with secure protocols

Note: Fully inheritable; may be the AI application provider's sole responsibility.

## EN-02 Encrypt AI assets at rest

HITRUST ID `11.01vAISecSystem.1` · Domain 11 Access Control · Control 01.v Information Access Restriction  
Inheritable: Fully · Applies: ML models (predictive, generative), Q2 or Q3 yes

> Training, testing, validation and fine-tuning datasets, embeddings, and models are encrypted at rest in line with the organization's encryption strength and key management policies.

Evaluative elements:
- `EN-02[1]` Training/testing/validation data encrypted at rest
- `EN-02[2]` Fine-tuning data encrypted at rest _(if fine-tuning)_
- `EN-02[3]` Embeddings encrypted at rest _(if RAG)_
- `EN-02[4]` Models encrypted at rest
- `EN-02[5]` Encryption strength follows policy
- `EN-02[6]` Key management follows policy

Note: Only when sensitive data was used (Q2) or the architecture is confidential (Q3). Fully inheritable.
