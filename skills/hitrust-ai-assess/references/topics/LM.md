# LM: AI system logging and monitoring

## LM-01 Log AI system inputs and outputs

HITRUST ID `12.09abAISecSystem.6` · Domain 12 Audit Logging & Monitoring · Control 09.aa Audit Logging  
Inheritable: Partially · Applies: all model types

> Every model input and output is logged with the exact content, timestamp, requesting account, request origin, and model version, and the logs are retained, protected, and sanitized under policy.

Evaluative elements:
- `LM-01[1]` Exact input logged
- `LM-01[2]` Date and time of input logged
- `LM-01[3]` Requesting user account logged
- `LM-01[4]` Request origin logged
- `LM-01[5]` Exact output logged
- `LM-01[6]` Model version logged
- `LM-01[7]` Logs retained, protected, and sanitized per policy

Note: Partially inheritable.

## LM-02 Monitor AI system inputs and outputs

HITRUST ID `12.09abAISecSystem.4` · Domain 12 Audit Logging & Monitoring · Control 09.ab Monitoring System Use  
Inheritable: Partially · Applies: all model types

> At least monthly, model inputs and outputs are monitored for signs of attack or compromise, and filters and guardrails are confirmed to work as intended.

Evaluative elements:
- `LM-02[1]` Inputs monitored at least monthly and input filters confirmed working
- `LM-02[2]` Outputs monitored at least monthly and output filters confirmed working

Note: Partially inheritable.

## LM-03 Monitoring data, models, and configurations for suspicious changes

HITRUST ID `12.09abAISecSystem.5` · Domain 12 Audit Logging & Monitoring · Control 09.ab Monitoring System Use  
Inheritable: Partially · Applies: all model types

> At least monthly, AI datasets, models, AI-relevant code (including agent and plugin code), and AI configurations such as metaprompts are checked for suspicious manipulation.

Evaluative elements:
- `LM-03[1]` AI datasets monitored monthly for manipulation
- `LM-03[2]` AI models monitored monthly for manipulation
- `LM-03[3]` AI-relevant code monitored monthly for manipulation
- `LM-03[4]` AI configurations (e.g., metaprompts) monitored monthly for manipulation

Note: Partially inheritable.
