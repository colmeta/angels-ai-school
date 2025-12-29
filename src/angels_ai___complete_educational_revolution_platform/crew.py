import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	SerperDevTool,
	BraveSearchTool,
	EXASearchTool,
	ScrapeWebsiteTool,
	FileReadTool,
	OCRTool,
	SpiderTool
)

from angels_ai___complete_educational_revolution_platform.tools import (
	ClarityAnalyzeTool,
)
@CrewBase
class AngelsAiCompleteEducationalRevolutionPlatformCrew:
    """AngelsAiCompleteEducationalRevolutionPlatform crew"""

    
    @agent
    def angels_ai_digital_ceo(self) -> Agent:

        
        return Agent(
            config=self.agents_config["angels_ai_digital_ceo"],
            
            
              tools=[
  				SerperDevTool(),
  				BraveSearchTool(),
  				EXASearchTool(),
  				ScrapeWebsiteTool(),
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def command_intelligence_agent___clarity_engine(self) -> Agent:

        
        return Agent(
            config=self.agents_config["command_intelligence_agent___clarity_engine"],
            
            
              tools=[
  				FileReadTool(),
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def document_intelligence_agent___rag_master(self) -> Agent:

        
        return Agent(
            config=self.agents_config["document_intelligence_agent___rag_master"],
            
            
              tools=[
  				OCRTool(),
  				FileReadTool(),
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def opportunity_intelligence_agent___funding_hunter(self) -> Agent:

        
        return Agent(
            config=self.agents_config["opportunity_intelligence_agent___funding_hunter"],
            
            
              tools=[
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def parent_engagement_agent___the_oracle(self) -> Agent:

        
        return Agent(
            config=self.agents_config["parent_engagement_agent___the_oracle"],
            
            
              tools=[
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def financial_operations_agent___automated_treasurer(self) -> Agent:

        
        return Agent(
            config=self.agents_config["financial_operations_agent___automated_treasurer"],
            
            
              tools=[
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def academic_operations_agent___educational_excellence_manager(self) -> Agent:

        
        return Agent(
            config=self.agents_config["academic_operations_agent___educational_excellence_manager"],
            
            
              tools=[
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def teacher_liberation_agent___administrative_freedom_fighter(self) -> Agent:

        
        return Agent(
            config=self.agents_config["teacher_liberation_agent___administrative_freedom_fighter"],
            
            
              tools=[
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def executive_assistant_agent___ultimate_administrative_coordinator(self) -> Agent:

        
        return Agent(
            config=self.agents_config["executive_assistant_agent___ultimate_administrative_coordinator"],
            
            
              tools=[
  				FileReadTool(),
  				ClarityAnalyzeTool(),
              ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def security_safety_guardian_agent(self) -> Agent:

        
        return Agent(
            config=self.agents_config["security_safety_guardian_agent"],
            
            
            tools=[

            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def daily_strategic_intelligence_briefing_and_executive_leadership(self) -> Task:
        return Task(
            config=self.tasks_config["daily_strategic_intelligence_briefing_and_executive_leadership"],
            markdown=False,
            
            
        )
    
    @task
    def process_natural_language_administrative_commands(self) -> Task:
        return Task(
            config=self.tasks_config["process_natural_language_administrative_commands"],
            markdown=False,
            
            
        )
    
    @task
    def comprehensive_funding_and_opportunity_discovery(self) -> Task:
        return Task(
            config=self.tasks_config["comprehensive_funding_and_opportunity_discovery"],
            markdown=False,
            
            
        )
    
    @task
    def advanced_document_intelligence_and_rag_processing(self) -> Task:
        return Task(
            config=self.tasks_config["advanced_document_intelligence_and_rag_processing"],
            markdown=False,
            
            
        )
    
    @task
    def 24_7_parent_engagement_and_oracle_services(self) -> Task:
        return Task(
            config=self.tasks_config["24_7_parent_engagement_and_oracle_services"],
            markdown=False,
            
            
        )
    
    @task
    def execute_advanced_financial_compliance_and_revenue_optimization(self) -> Task:
        return Task(
            config=self.tasks_config["execute_advanced_financial_compliance_and_revenue_optimization"],
            markdown=False,
            
            
        )
    
    @task
    def academic_excellence_and_predictive_intelligence(self) -> Task:
        return Task(
            config=self.tasks_config["academic_excellence_and_predictive_intelligence"],
            markdown=False,
            
            
        )
    
    @task
    def complete_teacher_liberation_and_administrative_automation(self) -> Task:
        return Task(
            config=self.tasks_config["complete_teacher_liberation_and_administrative_automation"],
            markdown=False,
            
            
        )
    
    @task
    def executive_operations_and_strategic_administration(self) -> Task:
        return Task(
            config=self.tasks_config["executive_operations_and_strategic_administration"],
            markdown=False,
            
            
        )
    
    @task
    def comprehensive_security_and_safety_management(self) -> Task:
        return Task(
            config=self.tasks_config["comprehensive_security_and_safety_management"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the AngelsAiCompleteEducationalRevolutionPlatform crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
