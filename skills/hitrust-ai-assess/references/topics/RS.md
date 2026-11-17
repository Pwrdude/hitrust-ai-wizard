# RS: Resilience of the AI system

## RS-01 Updating incident response for AI specifics

HITRUST ID `15.11cAISecOrganizational.1` · Domain 15 Incident Management · Control 11.c Responsibilities and Procedures  
Inheritable: No · Applies: all model types

> Incident detection and response addresses AI-specific threats (e.g., poisoning, evasion) through updated plans and playbooks, AI-focused tabletop exercises, recorded AI incidents, and logs and alerts from deployed AI systems feeding monitoring and detection tools.

Evaluative elements:
- `RS-01[1]` Incident plans/playbooks updated for AI-specific threats
- `RS-01[2]` AI-specific threats included in tabletop exercises
- `RS-01[3]` Specifics of AI security incidents recorded
- `RS-01[4]` AI system logs feed monitoring/detection tools
- `RS-01[5]` AI system alerts feed monitoring/detection tools

Note: Dual responsibility.

## RS-02 Backing up AI system assets

HITRUST ID `16.09lAISecOrganizational.1` · Domain 16 Business Continuity & Disaster Recovery · Control 09.l Back-up  
Inheritable: Partially · Applies: all model types

> Backups are made of AI training, test and validation data, model creation and deployment code, fine-tuning data, models, language model tools, AI configurations, and RAG data, and are managed under the backup policies.

Evaluative elements:
- `RS-02[1]` Training/test/validation datasets backed up
- `RS-02[2]` Model create/train/deploy code backed up
- `RS-02[3]` Fine-tuning data backed up _(if fine-tuning)_
- `RS-02[4]` Models backed up
- `RS-02[5]` Language model tools backed up _(if agents/plugins)_
- `RS-02[6]` AI configurations (e.g., metaprompts) backed up
- `RS-02[7]` RAG prompt-enhancement data backed up _(if RAG)_
- `RS-02[8]` Backups managed under data and software backup policies

Note: Partially inheritable.
