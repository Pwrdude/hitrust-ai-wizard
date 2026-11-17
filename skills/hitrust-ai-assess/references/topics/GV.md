# GV: AI security governance and oversight

## GV-01 Assign roles and responsibilities for AI

HITRUST ID `01.02aAISecOrganizational.1` · Domain 01 Information Protection Program · Control 02.a Roles and Responsibilities  
Inheritable: No · Applies: all model types

> Roles and responsibilities for governance, security, and risk management of the deployed AI system are formally defined (by extending an existing RACI or creating an AI-specific one), and human accountability for the system's actions, outputs, and decisions is formally assigned.

Evaluative elements:
- `GV-01[1]` Roles defined for AI governance
- `GV-01[2]` Roles defined for AI security
- `GV-01[3]` Roles defined for AI risk management
- `GV-01[4]` Human accountability formally assigned for AI actions, outputs, and decisions

Note: Dual responsibility.

## GV-02 Augment written policies to address AI specificities

HITRUST ID `01.00aAISecOrganizational.1` · Domain 01 Information Protection Program · Control 00.a Information Security Management Program  
Inheritable: No · Applies: all model types

> Where appropriate to the deployment context, written policies explicitly cover the organization's AI systems and their AI-specific characteristics across security administration, data governance, software development, risk management, incident management, business continuity, and disaster recovery.

Evaluative elements:
- `GV-02[1]` Security administration policy covers AI systems
- `GV-02[2]` Data governance policy covers AI systems
- `GV-02[3]` Software development policy covers AI systems
- `GV-02[4]` Risk management policy covers AI systems
- `GV-02[5]` Incident management policy covers AI systems
- `GV-02[6]` Business continuity policy covers AI systems
- `GV-02[7]` Disaster recovery policy covers AI systems

Note: Dual responsibility: the AI application provider and its AI service providers each perform this.

## GV-03 Humans can intervene if needed

HITRUST ID `12.09abAISecSystem.3` · Domain 12 Audit Logging & Monitoring · Control 09.ab Monitoring System Use  
Inheritable: No · Applies: all model types

> The AI application lets human operators evaluate model outputs before relying on them and intervene in model-initiated actions (e.g., sending email, modifying records) when needed.

Evaluative elements:
- `GV-03[1]` Operators can evaluate model outputs before relying on them
- `GV-03[2]` Operators can intervene in model-initiated actions when needed

Note: AI application provider's sole responsibility. Addresses confabulation and excessive agency.
