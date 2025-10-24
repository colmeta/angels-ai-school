import os
import re

# Files to update
files_to_update = [
    'api/routes/students.py',
    'api/routes/agents.py',
    'api/routes/fees.py',
    'api/routes/parents.py',
    'api/main.py'
]

# Import replacements
replacements = {
    'from Executive_Assistant_Service import': 'from executive_assistant_service import',
    'from Parent_Engagement_Service import': 'from parent_engagement_service import',
    'from Digital_CEO_Service import': 'from digital_ceo_service import',
    'from Document_Intelligence_Service import': 'from document_intelligence_service import',
    'from Financial_Operations_Service import': 'from financial_operations_service import',
    'from Remaining_Agent_Services import': 'from remaining_agent_services import',
    'from Master_Orchestrator_Complete import': 'from master_orchestrator_complete import',
}

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply replacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated: {file_path}")
    else:
        print(f"⚠️  Not found: {file_path}")

print("\n✅ All imports fixed!")