# TM: AI security threat management

## TM-01 Identifying security threats to the AI system

HITRUST ID `17.03bAISecOrganizational.4` · Domain 17 Risk Management · Control 03.b Performing Risk Assessments  
Inheritable: No · Applies: all model types

> AI-specific security threats to the deployed AI system are identified before new models are deployed, at least semiannually, and after AI-related security incidents, and are recorded in a threat register that describes each threat and the system components it affects.

Evaluative elements:
- `TM-01[1]` Threats identified before new models are deployed
- `TM-01[2]` Threats identified at least semiannually
- `TM-01[3]` Threats identified after AI-related security incidents
- `TM-01[4]` Threat register describes each threat
- `TM-01[5]` Threat register names the affected components (training data, models, APIs, etc.)

Note: Dual responsibility: the AI application provider and each AI service provider perform this independently.

## TM-02 Threat modeling for the AI system

HITRUST ID `17.03bAISecOrganizational.5` · Domain 17 Risk Management · Control 03.b Performing Risk Assessments  
Inheritable: No · Applies: all model types

> Threat modeling evaluates the AI system's exposure to the identified threats, the countermeasures already in place, and the additional countermeasures needed given risk tolerance and the system's risk category; it is repeated when new threats are identified, before new models are deployed, at least semiannually, and after AI-related security incidents.

Evaluative elements:
- `TM-02[1]` Threat modeling evaluates exposure to the identified threats
- `TM-02[2]` Threat modeling identifies countermeasures currently in place
- `TM-02[3]` Threat modeling identifies additional countermeasures needed, given risk tolerance and risk category
- `TM-02[4]` Performed when new threats are identified
- `TM-02[5]` Performed before new models are deployed
- `TM-02[6]` Performed at least semiannually
- `TM-02[7]` Performed after AI-related security incidents

Note: Dual responsibility.

## TM-03 Security evaluations such as AI red teaming

HITRUST ID `07.06hAISecOrganizational.1` · Domain 07 Vulnerability Management · Control 06.h Technical Compliance Checking  
Inheritable: No · Applies: all model types

> The AI system is security-assessed (e.g., AI red teaming, penetration testing) for AI-specific threats such as poisoning and model inversion before new models are deployed, before new or significantly changed supporting infrastructure is deployed, and at least annually, and risk treatment follows from the results.

Evaluative elements:
- `TM-03[1]` Assessed before new models are deployed
- `TM-03[2]` Assessed before new or significantly modified supporting infrastructure is deployed
- `TM-03[3]` Assessed at least annually
- `TM-03[4]` Risk treatment, including added countermeasures, taken based on results

Note: Dual responsibility.
