# IN: Documenting and inventorying AI systems

## IN-01 Inventory deployed AI systems

HITRUST ID `07.07aAISecOrganizational.3` · Domain 07 Vulnerability Management · Control 07.a Inventory of Assets  
Inheritable: No · Applies: all model types

> A documented inventory of deployed AI systems lists AI platforms, model names and versions, system owner, sensitivity/risk categorization, and AI service providers, and is reviewed and updated at least semiannually.

Evaluative elements:
- `IN-01[1]` Inventory lists AI platforms
- `IN-01[2]` Inventory lists models with name and version
- `IN-01[3]` Inventory lists the system owner
- `IN-01[4]` Inventory lists sensitivity or risk categorization
- `IN-01[5]` Inventory lists AI service providers
- `IN-01[6]` Inventory reviewed and updated at least semiannually

Note: Dual responsibility. The spec's statement says semiannual; its illustrative procedure says annual. Assess to semiannual.

## IN-02 Maintain a catalog of trusted data sources for AI

HITRUST ID `07.07aAISecOrganizational.4` · Domain 07 Vulnerability Management · Control 07.a Inventory of Assets  
Inheritable: Fully · Applies: ML models (predictive, generative)

> A catalog of trusted data sources for training, testing, validation, fine-tuning, and RAG prompt enhancement is maintained and reviewed at least semiannually.

Evaluative elements:
- `IN-02[1]` Trusted sources cataloged for training/testing/validation data
- `IN-02[2]` Trusted sources cataloged for fine-tuning data _(if fine-tuning)_
- `IN-02[3]` Trusted sources cataloged for RAG data _(if RAG)_
- `IN-02[4]` Catalog reviewed and updated at least semiannually

Note: ML models only. Fully inheritable; may be the model creator's sole responsibility.

## IN-03 AI data and data supply inventory

HITRUST ID `07.07aAISecOrganizational.5` · Domain 07 Vulnerability Management · Control 07.a Inventory of Assets  
Inheritable: Fully · Applies: ML models (predictive, generative)

> A documented inventory of data used for training, testing, validation, fine-tuning, and RAG records each source's provenance and sensitivity level and is reviewed at least semiannually.

Evaluative elements:
- `IN-03[1]` Inventory covers training/testing/validation data
- `IN-03[2]` Inventory covers fine-tuning data _(if fine-tuning)_
- `IN-03[3]` Inventory covers RAG data _(if RAG)_
- `IN-03[4]` Inventory records provenance
- `IN-03[5]` Inventory records sensitivity level
- `IN-03[6]` Inventory reviewed and updated at least semiannually

Note: ML models only. Fully inheritable.

## IN-04 Model card publication (for model builders)

HITRUST ID `06.10hAISecSystem.4` · Domain 06 Configuration Management · Control 10.h Control of Operational Software  
Inheritable: No · Applies: ML models (predictive, generative), only when the organization builds models

> Model builders publish a model card for each model they produce, covering model details, intended use, training details, evaluation details, and caveats and recommendations.

Evaluative elements:
- `IN-04[1]` Model card includes model details
- `IN-04[2]` Model card includes intended use
- `IN-04[3]` Model card includes training details
- `IN-04[4]` Model card includes evaluation details
- `IN-04[5]` Model card includes caveats and recommendations

Note: ML models only; applies only to organizations that build models.
