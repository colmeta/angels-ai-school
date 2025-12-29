from dotenv import load_dotenv
load_dotenv()

from src.angels_ai___complete_educational_revolution_platform.crew import AngelsAiCompleteEducationalRevolutionPlatformCrew

# Test the crew
print("🚀 Testing Executive Assistant Agent...")

crew = AngelsAiCompleteEducationalRevolutionPlatformCrew()

# Run with sample input
result = crew.crew().kickoff(inputs={
    'school_id': 'your-school-id-here',
    'command': 'Show me enrollment statistics for this week'
})

print(result)
