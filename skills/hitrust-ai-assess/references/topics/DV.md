# DV: Development of AI software

## DV-01 Provide AI security training to AI builders and deployers

HITRUST ID `13.02eAISecOrganizational.1` · Domain 13 Education, Training and Awareness · Control 02.e Information Security Awareness, Education, and Training  
Inheritable: No · Applies: all model types

> At least annually, AI security training (vulnerabilities, threats, policy requirements and similar topics) is provided to all teams that build and deploy AI software and models, including development, data science, and cybersecurity personnel.

Evaluative elements:
- `DV-01[1]` Annual AI security training for development personnel
- `DV-01[2]` Annual AI security training for data science personnel
- `DV-01[3]` Annual AI security training for cybersecurity personnel

Note: Inheritance not confirmed from the public spec; treat as the organization's own responsibility unless MyCSF says otherwise.

## DV-02 Version control of AI assets

HITRUST ID `06.10jAISecSystem.1` · Domain 06 Configuration Management · Control 10.j Access Control to Program Source Code  
Inheritable: Fully · Applies: all model types

> AI assets are versioned and tracked: model-creation code, training and fine-tuning datasets, RAG datasets, pipeline configurations, language model tool code, and models.

Evaluative elements:
- `DV-02[1]` Code used to create, train, and/or deploy models
- `DV-02[2]` Training datasets
- `DV-02[3]` Fine-tuning datasets _(if fine-tuning)_
- `DV-02[4]` RAG datasets _(if RAG)_
- `DV-02[5]` Pipeline configurations
- `DV-02[6]` Language model tool code (agents, plugins) _(if agents/plugins)_
- `DV-02[7]` Models

Note: Fully inheritable; may be the AI platform provider's and/or model creator's sole responsibility.

## DV-03 Inspection of AI software assets

HITRUST ID `07.10mAISecOrganizational.6` · Domain 07 Vulnerability Management · Control 10.m Control of Technical Vulnerabilities  
Inheritable: Fully · Applies: all model types

> Downloaded models, software packages, and language model tools are inspected for exploitable vulnerabilities before use, and the organization acts on the results.

Evaluative elements:
- `DV-03[1]` Downloaded models inspected before use
- `DV-03[2]` Downloaded software packages inspected before use
- `DV-03[3]` Language model tools inspected before use _(if agents/plugins)_
- `DV-03[4]` Results acted on

Note: Fully inheritable.

## DV-04 Change control over AI models

HITRUST ID `06.09bAISecSystem.1` · Domain 06 Configuration Management · Control 09.b Change Management  
Inheritable: Partially · Applies: all model types

> Model changes, including version upgrades and model replacements, are documented, tested, and approved under the software change control policy before deployment, and release notes are obtained and reviewed for upgrades to externally developed models.

Evaluative elements:
- `DV-04[1]` Model changes documented
- `DV-04[2]` Model changes tested
- `DV-04[3]` Model changes approved before deployment
- `DV-04[4]` Release notes obtained and reviewed for upgrades to externally developed models _(if external models)_

Note: Partially inheritable (AI application provider and AI platform provider). Can be N/A if no new models or versions were deployed in the past 12 months.

## DV-05 Change control over language model tools

HITRUST ID `06.10hAISecSystem.5` · Domain 06 Configuration Management · Control 10.h Control of Operational Software  
Inheritable: No · Applies: generative only, only when agents/plugins/language model tools used

> Changes to agents and plugins are documented, tested, and approved under the software change control policy before deployment.

Evaluative elements:
- `DV-05[1]` Changes to agents/plugins documented
- `DV-05[2]` Changes to agents/plugins tested
- `DV-05[3]` Changes to agents/plugins approved before deployment

Note: Generative AI only; applies only when agents or plugins are used. AI application provider's sole responsibility.

## DV-06 Documentation of AI specifics during system design and development

HITRUST ID `06.10hAISecSystem.6` · Domain 06 Configuration Management · Control 10.h Control of Operational Software  
Inheritable: Partially · Applies: all model types

> System documentation covers the creation, operation, and lifecycle management of models, datasets, configurations, and language model tools, and the tooling, computing, and human resources the system needs.

Evaluative elements:
- `DV-06[1]` Documentation covers models
- `DV-06[2]` Documentation covers datasets
- `DV-06[3]` Documentation covers configurations
- `DV-06[4]` Documentation covers language model tools _(if agents/plugins)_
- `DV-06[5]` Documentation covers tooling resources
- `DV-06[6]` Documentation covers system and computing resources
- `DV-06[7]` Documentation covers human resources

Note: Partially inheritable.

## DV-07 Linkage between dataset, model, and pipeline configuration

HITRUST ID `06.10hAISecSystem.7` · Domain 06 Configuration Management · Control 10.h Control of Operational Software  
Inheritable: Fully · Applies: ML models (predictive, generative)

> When creating machine learning models, the link between training dataset versions, pipeline configuration, and the resulting model is explicitly documented.

Evaluative elements:
- `DV-07[1]` Dataset version, pipeline configuration, and resulting model linkage documented

Note: ML models only. Fully inheritable; may be the AI model creator's sole responsibility (inherit when the client only consumes third-party models).

## DV-08 Verification of origin and integrity of AI assets

HITRUST ID `07.10mAISecOrganizational.2` · Domain 07 Vulnerability Management · Control 10.m Control of Technical Vulnerabilities  
Inheritable: Fully · Applies: all model types

> Before use, cryptographic hashes and/or digital signatures are verified on downloaded models, software packages, datasets, and language model tools.

Evaluative elements:
- `DV-08[1]` Hash/signature verified on downloaded models
- `DV-08[2]` Hash/signature verified on downloaded software packages
- `DV-08[3]` Hash/signature verified on downloaded datasets
- `DV-08[4]` Hash/signature verified on language model tools _(if agents/plugins)_

Note: Fully inheritable (AI platform provider and/or model creator).
