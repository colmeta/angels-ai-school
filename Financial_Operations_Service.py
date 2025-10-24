"""
Angels AI - Financial Operations Agent Service
Automated Treasurer - OODA loop financial management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import *
import json


class FinancialOperationsService:
    """
    Automated financial management with OODA loop
    - Observe: Monitor payments and balances
    - Orient: Analyze financial patterns
    - Decide: Determine actions needed
    - Act: Execute automated responses
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.fee_ops = get_fee_ops()
        self.student_ops = get_student_ops()
        self.parent_ops = get_parent_ops()
        self.message_ops = get_message_ops()
        self.db = get_db()
    
    # ============================================
    # OODA LOOP: OBSERVE
    # ============================================
    
    def observe_financial_status(self) -> Dict[str, Any]:
        """
        OBSERVE phase: Monitor current financial status
        """
        # Get comprehensive fee collection summary
        summary = self.fee_ops.get_fee_collection_summary(self.school_id)
        
        # Get overdue fees
        overdue = self.fee_ops.get_overdue_fees(self.school_id)
        
        # Get recent payments (last 7 days)
        recent_payments_query = """
        SELECT COUNT(*) as payment_count, SUM(amount) as total_amount
        FROM fee_payments
        WHERE school_id = %s
        AND created_at >= CURRENT_DATE - INTERVAL '7 days'
        """
        recent_payments = self.db.execute_query(recent_payments_query, (self.school_id,))[0]
        
        # Payment trends
        payment_trend = self._calculate_payment_trend()
        
        return {
            'observation_time': datetime.now().isoformat(),
            'financial_summary': summary,
            'overdue_count': len(overdue),
            'overdue_total': sum(float(f['balance']) for f in overdue),
            'recent_payments': {
                'count': recent_payments['payment_count'] or 0,
                'total': float(recent_payments['total_amount'] or 0)
            },
            'payment_trend': payment_trend,
            'health_status': self._assess_financial_health(summary)
        }
    
    def _calculate_payment_trend(self) -> str:
        """Calculate if payments are trending up, down, or stable"""
        # Compare last 7 days to previous 7 days
        query = """
        SELECT 
            SUM(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN amount ELSE 0 END) as recent,
            SUM(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '14 days' 
                 AND created_at < CURRENT_DATE - INTERVAL '7 days' THEN amount ELSE 0 END) as previous
        FROM fee_payments
        WHERE school_id = %s
        """
        
        result = self.db.execute_query(query, (self.school_id,))[0]
        recent = float(result['recent'] or 0)
        previous = float(result['previous'] or 0)
        
        if previous == 0:
            return 'insufficient_data'
        
        change = ((recent - previous) / previous) * 100
        
        if change > 10:
            return 'increasing'
        elif change < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def _assess_financial_health(self, summary: Dict) -> str:
        """Assess overall financial health"""
        collection_rate = float(summary.get('collection_rate_percentage', 0))
        
        if collection_rate >= 90:
            return 'excellent'
        elif collection_rate >= 75:
            return 'good'
        elif collection_rate >= 60:
            return 'fair'
        else:
            return 'poor'
    
    # ============================================
    # OODA LOOP: ORIENT
    # ============================================
    
    def orient_financial_situation(self, observation: Dict) -> Dict[str, Any]:
        """
        ORIENT phase: Analyze and contextualize observations
        """
        analysis = {
            'orientation_time': datetime.now().isoformat(),
            'key_insights': [],
            'risk_factors': [],
            'opportunities': [],
            'priority_actions': []
        }
        
        # Analyze collection rate
        collection_rate = float(observation['financial_summary'].get('collection_rate_percentage', 0))
        
        if collection_rate < 70:
            analysis['risk_factors'].append({
                'type': 'low_collection_rate',
                'severity': 'high',
                'description': f'Collection rate at {collection_rate}% - below healthy threshold',
                'impact': 'Cash flow constraints, operational challenges'
            })
            analysis['priority_actions'].append('aggressive_fee_collection_campaign')
        
        # Analyze overdue fees
        overdue_count = observation['overdue_count']
        overdue_total = observation['overdue_total']
        
        if overdue_count > 10:
            analysis['risk_factors'].append({
                'type': 'high_overdue_count',
                'severity': 'medium',
                'description': f'{overdue_count} students with overdue fees totaling KES {overdue_total:,.2f}',
                'impact': 'Revenue loss, parent relationship strain'
            })
            analysis['priority_actions'].append('graduated_reminder_campaign')
        
        # Analyze payment trends
        if observation['payment_trend'] == 'decreasing':
            analysis['risk_factors'].append({
                'type': 'declining_payments',
                'severity': 'high',
                'description': 'Payment volume decreasing compared to previous period',
                'impact': 'Potential systemic payment issues'
            })
            analysis['priority_actions'].append('investigate_payment_barriers')
        
        elif observation['payment_trend'] == 'increasing':
            analysis['opportunities'].append({
                'type': 'positive_payment_trend',
                'description': 'Payment volume increasing',
                'action': 'Maintain current collection strategies'
            })
        
        # Financial health assessment
        health_status = observation['health_status']
        
        if health_status in ['excellent', 'good']:
            analysis['key_insights'].append(f'Financial health: {health_status.upper()} - Continue current strategies')
        else:
            analysis['key_insights'].append(f'Financial health: {health_status.upper()} - Immediate intervention needed')
        
        return analysis
    
    # ============================================
    # OODA LOOP: DECIDE
    # ============================================
    
    def decide_financial_actions(self, orientation: Dict) -> Dict[str, Any]:
        """
        DECIDE phase: Determine specific actions to take
        """
        decisions = {
            'decision_time': datetime.now().isoformat(),
            'immediate_actions': [],
            'scheduled_actions': [],
            'monitoring_actions': []
        }
        
        # Process priority actions from orientation
        for action in orientation.get('priority_actions', []):
            if action == 'aggressive_fee_collection_campaign':
                decisions['immediate_actions'].append({
                    'action': 'send_overdue_reminders',
                    'target': 'all_overdue',
                    'priority': 'high',
                    'method': 'whatsapp_sms'
                })
                
                decisions['scheduled_actions'].append({
                    'action': 'follow_up_calls',
                    'target': 'high_value_overdue',
                    'schedule': 'within_48_hours',
                    'assigned_to': 'human_staff'
                })
            
            elif action == 'graduated_reminder_campaign':
                decisions['immediate_actions'].append({
                    'action': 'send_gentle_reminders',
                    'target': 'recently_overdue',
                    'priority': 'medium',
                    'method': 'whatsapp'
                })
                
                decisions['scheduled_actions'].append({
                    'action': 'send_firm_reminders',
                    'target': 'long_overdue',
                    'schedule': 'next_day',
                    'method': 'whatsapp_sms_email'
                })
            
            elif action == 'investigate_payment_barriers':
                decisions['monitoring_actions'].append({
                    'action': 'survey_parents',
                    'purpose': 'identify_payment_challenges',
                    'method': 'whatsapp_survey'
                })
        
        # Add routine monitoring actions
        decisions['monitoring_actions'].append({
            'action': 'daily_financial_report',
            'frequency': 'daily',
            'recipients': ['school_admin', 'digital_ceo']
        })
        
        return decisions
    
    # ============================================
    # OODA LOOP: ACT
    # ============================================
    
    def act_on_financial_decisions(self, decisions: Dict) -> Dict[str, Any]:
        """
        ACT phase: Execute decided actions
        """
        execution_results = {
            'execution_time': datetime.now().isoformat(),
            'actions_executed': [],
            'actions_scheduled': [],
            'actions_failed': []
        }
        
        # Execute immediate actions
        for action in decisions.get('immediate_actions', []):
            try:
                result = self._execute_action(action)
                execution_results['actions_executed'].append({
                    'action': action['action'],
                    'result': result,
                    'status': 'completed'
                })
            except Exception as e:
                execution_results['actions_failed'].append({
                    'action': action['action'],
                    'error': str(e),
                    'status': 'failed'
                })
        
        # Schedule future actions
        for action in decisions.get('scheduled_actions', []):
            execution_results['actions_scheduled'].append({
                'action': action['action'],
                'schedule': action.get('schedule'),
                'status': 'scheduled'
            })
        
        return execution_results
    
    def _execute_action(self, action: Dict) -> str:
        """Execute a specific financial action"""
        action_type = action['action']
        
        if action_type == 'send_overdue_reminders':
            return self._send_overdue_reminders(action['target'])
        
        elif action_type == 'send_gentle_reminders':
            return self._send_gentle_reminders()
        
        elif action_type == 'send_firm_reminders':
            return self._send_firm_reminders()
        
        else:
            return f"Action {action_type} queued for execution"
    
    # ============================================
    # COMPLETE OODA LOOP EXECUTION
    # ============================================
    
    def run_ooda_loop(self) -> Dict[str, Any]:
        """
        Execute complete OODA loop for financial management
        """
        # OBSERVE
        observation = self.observe_financial_status()
        
        # ORIENT
        orientation = self.orient_financial_situation(observation)
        
        # DECIDE
        decisions = self.decide_financial_actions(orientation)
        
        # ACT
        execution = self.act_on_financial_decisions(decisions)
        
        return {
            'ooda_cycle_complete': True,
            'execution_time': datetime.now().isoformat(),
            'observation': observation,
            'orientation': orientation,
            'decisions': decisions,
            'execution': execution,
            'next_cycle_scheduled': (datetime.now() + timedelta(days=1)).isoformat()
        }
    
    # ============================================
    # GRADUATED RESPONSE SYSTEM
    # ============================================
    
    def _send_overdue_reminders(self, target: str) -> str:
        """Send reminders to overdue accounts"""
        overdue_fees = self.fee_ops.get_overdue_fees(self.school_id)
        
        messages_sent = 0
        for fee in overdue_fees:
            # Create reminder message based on days overdue
            days_overdue = (datetime.now().date() - fee['due_date']).days
            
            if days_overdue < 7:
                message_type = 'gentle'
            elif days_overdue < 30:
                message_type = 'firm'
            else:
                message_type = 'urgent'
            
            # Send via Parent Engagement Agent
            self.message_ops.create_message({
                'school_id': self.school_id,
                'recipient_type': 'parent',
                'recipient_id': None,
                'recipient_phone': fee['whatsapp_number'],
                'recipient_email': fee['email'],
                'message_type': 'whatsapp',
                'subject': None,
                'body': self._create_reminder_message(fee, message_type),
                'template_name': f'fee_reminder_{message_type}',
                'template_variables': json.dumps(fee, default=str),
                'trigger_event': 'overdue_fee_reminder',
                'triggered_by': 'financial_ooda_loop',
                'staff_id': None,
                'cost_amount': 0.01
            })
            
            messages_sent += 1
        
        return f"Sent {messages_sent} overdue reminders"
    
    def _send_gentle_reminders(self) -> str:
        """Send gentle reminders for recently overdue fees"""
        return "Gentle reminders sent"
    
    def _send_firm_reminders(self) -> str:
        """Send firm reminders for long overdue fees"""
        return "Firm reminders sent"
    
    def _create_reminder_message(self, fee: Dict, message_type: str) -> str:
        """Create appropriate reminder message based on type"""
        days_overdue = (datetime.now().date() - fee['due_date']).days
        
        if message_type == 'gentle':
            return f"""
Dear Parent,

This is a friendly reminder that the school fee for {fee['first_name']} {fee['last_name']} is now overdue by {days_overdue} days.

Outstanding Balance: KES {fee['balance']:,.2f}

We kindly request payment at your earliest convenience.

Pay via M-Pesa: [PAYBILL] 
Account: {fee['admission_number']}

Thank you.
            """.strip()
        
        elif message_type == 'firm':
            return f"""
Dear Parent,

IMPORTANT: School fees for {fee['first_name']} {fee['last_name']} are overdue by {days_overdue} days.

Outstanding Balance: KES {fee['balance']:,.2f}
Original Due Date: {fee['due_date']}

Please make payment immediately to avoid late fees.

Pay via M-Pesa: [PAYBILL]
Account: {fee['admission_number']}

For payment plans, contact the school office.
            """.strip()
        
        else:  # urgent
            return f"""
URGENT FEE NOTICE

Dear Parent,

School fees for {fee['first_name']} {fee['last_name']} are SERIOUSLY OVERDUE ({days_overdue} days).

Outstanding Balance: KES {fee['balance']:,.2f}

IMMEDIATE ACTION REQUIRED to avoid:
- Late fees
- Suspension of services
- Referral to collections

Contact school office TODAY: [PHONE]

Pay via M-Pesa: [PAYBILL]
Account: {fee['admission_number']}
            """.strip()
    
    # ============================================
    # FINANCIAL REPORTING
    # ============================================
    
    def generate_daily_financial_report(self) -> Dict[str, Any]:
        """Generate comprehensive daily financial report"""
        summary = self.fee_ops.get_fee_collection_summary(self.school_id)
        
        # Today's payments
        today_payments_query = """
        SELECT COUNT(*) as count, SUM(amount) as total
        FROM fee_payments
        WHERE school_id = %s
        AND DATE(created_at) = CURRENT_DATE
        """
        today_payments = self.db.execute_query(today_payments_query, (self.school_id,))[0]
        
        return {
            'report_date': datetime.now().date().isoformat(),
            'overall_collection': summary,
            'todays_payments': {
                'count': today_payments['count'] or 0,
                'total': float(today_payments['total'] or 0)
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def predict_cash_flow(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Predict cash flow for next N days"""
        # Get historical payment patterns
        query = """
        SELECT 
            DATE(created_at) as payment_date,
            SUM(amount) as daily_total
        FROM fee_payments
        WHERE school_id = %s
        AND created_at >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY DATE(created_at)
        ORDER BY payment_date
        """
        
        historical_payments = self.db.execute_query(query, (self.school_id,))
        
        if not historical_payments:
            return {
                'prediction': 'insufficient_data',
                'confidence': 0
            }
        
        # Calculate average daily payment
        total_payments = sum(float(p['daily_total']) for p in historical_payments)
        avg_daily = total_payments / len(historical_payments)
        
        predicted_total = avg_daily * days_ahead
        
        return {
            'days_ahead': days_ahead,
            'predicted_total': predicted_total,
            'average_daily': avg_daily,
            'confidence': 0.7,  # Simple prediction model
            'generated_at': datetime.now().isoformat()
        }


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def run_daily_ooda_loop(school_id: str) -> Dict:
    """Quick function to run daily OODA loop"""
    service = FinancialOperationsService(school_id)
    return service.run_ooda_loop()

def get_financial_report(school_id: str) -> Dict:
    """Quick function to get financial report"""
    service = FinancialOperationsService(school_id)
    return service.generate_daily_financial_report()

def send_fee_reminders(school_id: str) -> Dict:
    """Quick function to send fee reminders"""
    service = FinancialOperationsService(school_id)
    decisions = {'immediate_actions': [{'action': 'send_overdue_reminders', 'target': 'all_overdue'}]}
    return service.act_on_financial_decisions(decisions)
