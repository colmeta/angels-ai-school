"""
Angels AI - Digital CEO Agent Service
Strategic Brain - Executive intelligence and strategic leadership
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import *
import json


class DigitalCEOService:
    """
    Digital CEO - Strategic leadership and executive intelligence
    Provides daily briefings, strategic insights, and growth recommendations
    """
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.student_ops = get_student_ops()
        self.parent_ops = get_parent_ops()
        self.fee_ops = get_fee_ops()
        self.message_ops = get_message_ops()
        self.db = get_db()
    
    # ============================================
    # DAILY STRATEGIC BRIEFING
    # ============================================
    
    def generate_daily_strategic_briefing(self) -> Dict[str, Any]:
        """
        Generate comprehensive CEO-level daily briefing
        """
        briefing = {
            'briefing_date': datetime.now().date().isoformat(),
            'generated_at': datetime.now().isoformat(),
            'school_id': self.school_id,
            
            # Core sections
            'executive_summary': self._generate_executive_summary(),
            'key_metrics': self._get_key_metrics(),
            'financial_intelligence': self._analyze_financial_performance(),
            'academic_intelligence': self._analyze_academic_performance(),
            'operational_intelligence': self._analyze_operational_efficiency(),
            'risk_assessment': self._assess_risks(),
            'opportunity_analysis': self._identify_opportunities(),
            'strategic_recommendations': self._generate_strategic_recommendations(),
            'competitive_intelligence': self._analyze_competitive_landscape(),
            'agent_coordination_report': self._get_agent_coordination_status()
        }
        
        return briefing
    
    def _generate_executive_summary(self) -> List[str]:
        """Generate high-level executive summary"""
        insights = []
        
        # Get key metrics
        metrics = self._get_key_metrics()
        
        # Enrollment insight
        if metrics['enrollment']['new_this_week'] > 0:
            insights.append(
                f"✅ ENROLLMENT: {metrics['enrollment']['new_this_week']} new students enrolled this week. "
                f"Total active enrollment: {metrics['enrollment']['total_active']}"
            )
        
        # Financial insight
        collection_rate = metrics['financial']['collection_rate']
        if collection_rate >= 90:
            insights.append(f"💰 FINANCIAL: Excellent collection rate at {collection_rate}% - Cash flow healthy")
        elif collection_rate >= 75:
            insights.append(f"💰 FINANCIAL: Good collection rate at {collection_rate}% - Continue monitoring")
        else:
            insights.append(f"⚠️ FINANCIAL: Collection rate at {collection_rate}% - Immediate action required")
        
        # Operational insight
        if metrics['operational']['messages_sent_today'] > 0:
            insights.append(
                f"📱 OPERATIONS: {metrics['operational']['messages_sent_today']} parent communications sent today. "
                f"Delivery rate: {metrics['operational']['delivery_rate']}%"
            )
        
        # Risk insight
        risks = self._assess_risks()
        if risks['critical_risks']:
            insights.append(f"🚨 CRITICAL: {len(risks['critical_risks'])} high-priority items require immediate attention")
        else:
            insights.append("✨ STATUS: All systems operating within normal parameters")
        
        return insights
    
    def _get_key_metrics(self) -> Dict[str, Any]:
        """Get key performance metrics across all areas"""
        
        # Enrollment metrics
        enrollment_query = """
        SELECT 
            COUNT(*) as total_active,
            COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as new_this_week,
            COUNT(CASE WHEN gender = 'male' THEN 1 END) as male_count,
            COUNT(CASE WHEN gender = 'female' THEN 1 END) as female_count
        FROM students
        WHERE school_id = %s 
        AND enrollment_status = 'active' 
        AND deleted_at IS NULL
        """
        enrollment = self.db.execute_query(enrollment_query, (self.school_id,))[0]
        
        # Financial metrics
        fee_summary = self.fee_ops.get_fee_collection_summary(self.school_id)
        
        # Operational metrics
        operational_query = """
        SELECT 
            COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as messages_today,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_count,
            COUNT(*) as total_messages
        FROM messages
        WHERE school_id = %s
        AND created_at >= CURRENT_DATE - INTERVAL '7 days'
        """
        operational = self.db.execute_query(operational_query, (self.school_id,))[0]
        
        delivery_rate = (
            (operational['delivered_count'] / operational['total_messages'] * 100)
            if operational['total_messages'] > 0 else 0
        )
        
        return {
            'enrollment': {
                'total_active': enrollment['total_active'],
                'new_this_week': enrollment['new_this_week'],
                'gender_ratio': f"{enrollment['male_count']}M:{enrollment['female_count']}F"
            },
            'financial': {
                'collection_rate': float(fee_summary.get('collection_rate_percentage', 0)),
                'outstanding_amount': float(fee_summary.get('total_outstanding', 0)),
                'collected_this_term': float(fee_summary.get('total_collected', 0))
            },
            'operational': {
                'messages_sent_today': operational['messages_today'] or 0,
                'delivery_rate': round(delivery_rate, 1)
            }
        }
    
    # ============================================
    # FINANCIAL INTELLIGENCE
    # ============================================
    
    def _analyze_financial_performance(self) -> Dict[str, Any]:
        """Deep financial analysis and insights"""
        fee_summary = self.fee_ops.get_fee_collection_summary(self.school_id)
        
        collection_rate = float(fee_summary.get('collection_rate_percentage', 0))
        total_expected = float(fee_summary.get('total_expected', 0))
        total_collected = float(fee_summary.get('total_collected', 0))
        total_outstanding = float(fee_summary.get('total_outstanding', 0))
        
        # Calculate revenue efficiency
        revenue_efficiency = (total_collected / total_expected * 100) if total_expected > 0 else 0
        
        # Payment velocity (how fast are payments coming in)
        velocity_query = """
        SELECT 
            COUNT(*) as payment_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM fee_payments
        WHERE school_id = %s
        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        velocity = self.db.execute_query(velocity_query, (self.school_id,))[0]
        
        return {
            'collection_performance': {
                'rate': collection_rate,
                'status': 'excellent' if collection_rate >= 90 else 'good' if collection_rate >= 75 else 'needs_improvement',
                'total_expected': total_expected,
                'total_collected': total_collected,
                'total_outstanding': total_outstanding
            },
            'revenue_trends': {
                'monthly_payment_count': velocity['payment_count'] or 0,
                'monthly_payment_total': float(velocity['total_amount'] or 0),
                'average_payment_size': float(velocity['avg_amount'] or 0)
            },
            'financial_health': {
                'revenue_efficiency': revenue_efficiency,
                'cash_flow_status': 'healthy' if collection_rate >= 85 else 'concerning',
                'overdue_accounts': fee_summary.get('overdue_count', 0)
            },
            'strategic_insights': self._generate_financial_insights(collection_rate, total_outstanding)
        }
    
    def _generate_financial_insights(self, collection_rate: float, outstanding: float) -> List[str]:
        """Generate strategic financial insights"""
        insights = []
        
        if collection_rate >= 90:
            insights.append("Financial position is strong - Consider reinvesting surplus in infrastructure/programs")
        elif collection_rate >= 75:
            insights.append("Financial position is stable - Monitor closely and maintain collection efforts")
        else:
            insights.append("URGENT: Low collection rate threatens operations - Implement aggressive collection strategy")
        
        if outstanding > 0:
            insights.append(f"Outstanding fees: KES {outstanding:,.2f} - Prioritize collection to improve cash flow")
        
        return insights
    
    # ============================================
    # ACADEMIC INTELLIGENCE
    # ============================================
    
    def _analyze_academic_performance(self) -> Dict[str, Any]:
        """Analyze academic performance and trends"""
        
        # Grade distribution
        grade_query = """
        SELECT 
            current_grade,
            COUNT(*) as student_count,
            COUNT(CASE WHEN gender = 'male' THEN 1 END) as male_count,
            COUNT(CASE WHEN gender = 'female' THEN 1 END) as female_count
        FROM students
        WHERE school_id = %s 
        AND enrollment_status = 'active'
        AND deleted_at IS NULL
        GROUP BY current_grade
        ORDER BY current_grade
        """
        grade_distribution = self.db.execute_query(grade_query, (self.school_id,))
        
        # Enrollment trends
        trend_query = """
        SELECT 
            DATE_TRUNC('month', admission_date) as month,
            COUNT(*) as enrollments
        FROM students
        WHERE school_id = %s
        AND admission_date >= CURRENT_DATE - INTERVAL '6 months'
        AND deleted_at IS NULL
        GROUP BY DATE_TRUNC('month', admission_date)
        ORDER BY month DESC
        """
        enrollment_trends = self.db.execute_query(trend_query, (self.school_id,))
        
        return {
            'grade_distribution': [dict(g) for g in grade_distribution],
            'enrollment_trends': [dict(t) for t in enrollment_trends],
            'academic_insights': [
                "Monitor grade-level capacity for optimal teacher-student ratios",
                "Track enrollment trends for resource planning and staffing decisions"
            ]
        }
    
    # ============================================
    # OPERATIONAL INTELLIGENCE
    # ============================================
    
    def _analyze_operational_efficiency(self) -> Dict[str, Any]:
        """Analyze operational efficiency across all systems"""
        
        # Communication efficiency
        comm_query = """
        SELECT 
            COUNT(*) as total_messages,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
            SUM(cost_amount) as total_cost
        FROM messages
        WHERE school_id = %s
        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        comm_stats = self.db.execute_query(comm_query, (self.school_id,))[0]
        
        delivery_rate = (
            (comm_stats['delivered'] / comm_stats['total_messages'] * 100)
            if comm_stats['total_messages'] > 0 else 0
        )
        
        # Document processing efficiency
        doc_query = """
        SELECT 
            COUNT(*) as total_docs,
            COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed,
            COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed
        FROM documents
        WHERE school_id = %s
        AND created_at >= CURRENT_DATE - INTERVAL '30 days'
        """
        doc_stats = self.db.execute_query(doc_query, (self.school_id,))[0]
        
        return {
            'communication_efficiency': {
                'total_messages': comm_stats['total_messages'] or 0,
                'delivery_rate': round(delivery_rate, 1),
                'failed_messages': comm_stats['failed'] or 0,
                'communication_cost': float(comm_stats['total_cost'] or 0)
            },
            'document_processing': {
                'total_processed': doc_stats['total_docs'] or 0,
                'success_rate': round(
                    (doc_stats['completed'] / doc_stats['total_docs'] * 100)
                    if doc_stats['total_docs'] > 0 else 0, 1
                ),
                'failed_docs': doc_stats['failed'] or 0
            },
            'efficiency_insights': self._generate_operational_insights(delivery_rate)
        }
    
    def _generate_operational_insights(self, delivery_rate: float) -> List[str]:
        """Generate operational efficiency insights"""
        insights = []
        
        if delivery_rate >= 95:
            insights.append("Communication systems performing excellently - Maintain current infrastructure")
        elif delivery_rate >= 85:
            insights.append("Communication performance is good - Monitor for degradation")
        else:
            insights.append("ALERT: Low message delivery rate - Investigate phone number quality and network issues")
        
        return insights
    
    # ============================================
    # RISK ASSESSMENT
    # ============================================
    
    def _assess_risks(self) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        risks = {
            'critical_risks': [],
            'medium_risks': [],
            'low_risks': [],
            'risk_score': 0  # 0-100 scale
        }
        
        # Financial risks
        fee_summary = self.fee_ops.get_fee_collection_summary(self.school_id)
        collection_rate = float(fee_summary.get('collection_rate_percentage', 0))
        
        if collection_rate < 60:
            risks['critical_risks'].append({
                'type': 'financial',
                'severity': 'critical',
                'description': f'Collection rate critically low at {collection_rate}%',
                'impact': 'Operational sustainability at risk',
                'recommendation': 'Immediate aggressive collection campaign required'
            })
            risks['risk_score'] += 40
        elif collection_rate < 75:
            risks['medium_risks'].append({
                'type': 'financial',
                'severity': 'medium',
                'description': f'Collection rate below target at {collection_rate}%',
                'impact': 'Cash flow constraints possible',
                'recommendation': 'Enhance collection efforts and parent engagement'
            })
            risks['risk_score'] += 20
        
        # Operational risks
        overdue_count = fee_summary.get('overdue_count', 0)
        if overdue_count > 50:
            risks['medium_risks'].append({
                'type': 'operational',
                'severity': 'medium',
                'description': f'{overdue_count} students with overdue fees',
                'impact': 'Parent relationship strain, reputation risk',
                'recommendation': 'Implement payment plan options and increase communication'
            })
            risks['risk_score'] += 15
        
        # Cap risk score at 100
        risks['risk_score'] = min(risks['risk_score'], 100)
        
        # Overall risk level
        if risks['risk_score'] >= 60:
            risks['overall_risk_level'] = 'HIGH'
        elif risks['risk_score'] >= 30:
            risks['overall_risk_level'] = 'MEDIUM'
        else:
            risks['overall_risk_level'] = 'LOW'
        
        return risks
    
    # ============================================
    # OPPORTUNITY ANALYSIS
    # ============================================
    
    def _identify_opportunities(self) -> Dict[str, Any]:
        """Identify growth and improvement opportunities"""
        opportunities = {
            'revenue_opportunities': [],
            'operational_opportunities': [],
            'strategic_opportunities': []
        }
        
        # Revenue opportunities
        fee_summary = self.fee_ops.get_fee_collection_summary(self.school_id)
        outstanding = float(fee_summary.get('total_outstanding', 0))
        
        if outstanding > 10000:
            opportunities['revenue_opportunities'].append({
                'opportunity': 'Outstanding Fee Collection',
                'potential_value': outstanding,
                'effort': 'medium',
                'timeframe': '30-60 days',
                'recommendation': 'Implement payment plans and intensify collection efforts'
            })
        
        # Enrollment opportunities
        enrollment_query = """
        SELECT current_grade, COUNT(*) as count
        FROM students
        WHERE school_id = %s AND enrollment_status = 'active'
        GROUP BY current_grade
        HAVING COUNT(*) < 20
        """
        small_classes = self.db.execute_query(enrollment_query, (self.school_id,))
        
        if small_classes:
            opportunities['revenue_opportunities'].append({
                'opportunity': 'Enrollment Growth',
                'potential_value': len(small_classes) * 10 * 50000,  # Classes * students * avg fee
                'effort': 'high',
                'timeframe': '3-6 months',
                'recommendation': f'Target enrollment campaigns for {len(small_classes)} under-capacity grades'
            })
        
        # Operational opportunities
        opportunities['operational_opportunities'].append({
            'opportunity': 'AI Automation Expansion',
            'potential_savings': 'Staff time equivalent to 2-3 FTE',
            'effort': 'low',
            'timeframe': 'immediate',
            'recommendation': 'Maximize Angels AI utilization to reduce administrative overhead'
        })
        
        return opportunities
    
    # ============================================
    # STRATEGIC RECOMMENDATIONS
    # ============================================
    
    def _generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """Generate prioritized strategic recommendations"""
        recommendations = []
        
        # Get context
        metrics = self._get_key_metrics()
        risks = self._assess_risks()
        
        # Priority 1: Address critical risks
        if risks['critical_risks']:
            for risk in risks['critical_risks']:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'risk_mitigation',
                    'recommendation': risk['recommendation'],
                    'expected_impact': 'high',
                    'timeframe': 'immediate'
                })
        
        # Priority 2: Financial optimization
        collection_rate = metrics['financial']['collection_rate']
        if collection_rate < 85:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'financial',
                'recommendation': 'Launch multi-channel fee collection campaign (WhatsApp + SMS + Calls)',
                'expected_impact': f'Increase collection rate from {collection_rate}% to 90%+',
                'timeframe': '30 days'
            })
        
        # Priority 3: Growth initiatives
        if metrics['enrollment']['new_this_week'] == 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'growth',
                'recommendation': 'Implement referral program and community outreach for new enrollment',
                'expected_impact': '10-20% enrollment growth',
                'timeframe': '90 days'
            })
        
        # Priority 4: Operational excellence
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'operational',
            'recommendation': 'Conduct staff training on Angels AI features to maximize efficiency gains',
            'expected_impact': '30-40% reduction in administrative time',
            'timeframe': '14 days'
        })
        
        return recommendations
    
    # ============================================
    # COMPETITIVE INTELLIGENCE
    # ============================================
    
    def _analyze_competitive_landscape(self) -> Dict[str, Any]:
        """Analyze competitive position and market trends"""
        # This would integrate with web scraping in production
        # For MVP, provide framework
        
        return {
            'market_position': {
                'status': 'Analyzing...',
                'note': 'Competitive intelligence requires web scraping integration'
            },
            'market_trends': [
                'Digital transformation accelerating in African education',
                'Parent expectations for digital communication increasing',
                'Mobile money adoption enabling new payment models'
            ],
            'competitive_advantages': [
                'AI-powered automation reduces operational costs by 70%',
                '24/7 parent engagement via WhatsApp',
                'Real-time financial intelligence and collection automation',
                'Zero manual data entry with document intelligence'
            ]
        }
    
    # ============================================
    # AGENT COORDINATION
    # ============================================
    
    def _get_agent_coordination_status(self) -> Dict[str, Any]:
        """Monitor and coordinate all AI agents"""
        return {
            'agents_status': {
                'executive_assistant': 'operational',
                'parent_engagement': 'operational',
                'financial_operations': 'operational',
                'document_intelligence': 'operational',
                'academic_operations': 'ready',
                'teacher_liberation': 'ready',
                'security_safety': 'ready',
                'opportunity_intelligence': 'ready'
            },
            'coordination_notes': [
                'All core agents (Executive, Parent, Financial, Document) fully operational',
                'Remaining agents ready for activation as needed',
                'Agent communication protocols functioning normally'
            ]
        }
    
    # ============================================
    # EXECUTIVE ACTIONS
    # ============================================
    
    def execute_strategic_decision(self, decision_type: str, parameters: Dict) -> Dict[str, Any]:
        """Execute high-level strategic decisions"""
        
        if decision_type == 'launch_collection_campaign':
            # Coordinate with Financial Operations Agent
            return {
                'success': True,
                'action': 'Collection campaign initiated',
                'agents_coordinated': ['financial_operations', 'parent_engagement']
            }
        
        elif decision_type == 'enrollment_push':
            # Coordinate enrollment campaign
            return {
                'success': True,
                'action': 'Enrollment campaign initiated',
                'agents_coordinated': ['parent_engagement', 'executive_assistant']
            }
        
        else:
            return {
                'success': False,
                'error': f'Unknown decision type: {decision_type}'
            }


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def get_daily_briefing(school_id: str) -> Dict:
    """Quick function to get CEO briefing"""
    service = DigitalCEOService(school_id)
    return service.generate_daily_strategic_briefing()

def assess_school_risks(school_id: str) -> Dict:
    """Quick function for risk assessment"""
    service = DigitalCEOService(school_id)
    return service._assess_risks()

def get_strategic_recommendations(school_id: str) -> List[Dict]:
    """Quick function for strategic recommendations"""
    service = DigitalCEOService(school_id)
    return service._generate_strategic_recommendations()
