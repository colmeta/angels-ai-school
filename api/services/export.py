"""
Data Export Service - CSV, Excel, PDF exports
Export data for reporting, analysis, and archival
"""
import csv
import io
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from api.services.database import get_db_manager


class ExportService:
    """Export data in various formats"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()
    
    # ============================================================================
    # CSV EXPORTS
    # ============================================================================
    
    def export_students_csv(self, class_name: Optional[str] = None) -> str:
        """Export students to CSV"""
        query = """
            SELECT 
                admission_number, first_name, last_name, date_of_birth,
                gender, class_name, status, created_at
            FROM students
            WHERE school_id = %s
        """
        params = [self.school_id]
        
        if class_name:
            query += " AND class_name = %s"
            params.append(class_name)
        
        query += " ORDER BY class_name, last_name, first_name"
        
        students = self.db.execute_query(query, tuple(params), fetch=True)
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'admission_number', 'first_name', 'last_name', 'date_of_birth',
            'gender', 'class_name', 'status', 'created_at'
        ])
        writer.writeheader()
        writer.writerows(students)
        
        return output.getvalue()
    
    def export_attendance_csv(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        class_name: Optional[str] = None
    ) -> str:
        """Export attendance records to CSV"""
        query = """
            SELECT 
                a.date, s.admission_number, s.first_name, s.last_name,
                s.class_name, a.status, a.notes
            FROM attendance a
            JOIN students s ON s.id = a.student_id
            WHERE a.school_id = %s
        """
        params = [self.school_id]
        
        if start_date:
            query += " AND a.date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND a.date <= %s"
            params.append(end_date)
        
        if class_name:
            query += " AND s.class_name = %s"
            params.append(class_name)
        
        query += " ORDER BY a.date DESC, s.class_name, s.last_name"
        
        records = self.db.execute_query(query, tuple(params), fetch=True)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'date', 'admission_number', 'first_name', 'last_name',
            'class_name', 'status', 'notes'
        ])
        writer.writeheader()
        writer.writerows(records)
        
        return output.getvalue()
    
    def export_grades_csv(
        self,
        assessment_name: Optional[str] = None,
        class_name: Optional[str] = None
    ) -> str:
        """Export grades to CSV"""
        query = """
            SELECT 
                s.admission_number, s.first_name, s.last_name, s.class_name,
                a.name as assessment, a.subject, a.max_marks,
                ar.marks_obtained, ar.grade, ar.comments
            FROM assessment_results ar
            JOIN assessments a ON a.id = ar.assessment_id
            JOIN students s ON s.id = ar.student_id
            WHERE a.school_id = %s
        """
        params = [self.school_id]
        
        if assessment_name:
            query += " AND a.name = %s"
            params.append(assessment_name)
        
        if class_name:
            query += " AND s.class_name = %s"
            params.append(class_name)
        
        query += " ORDER BY a.name, s.class_name, s.last_name"
        
        records = self.db.execute_query(query, tuple(params), fetch=True)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'admission_number', 'first_name', 'last_name', 'class_name',
            'assessment', 'subject', 'max_marks', 'marks_obtained', 'grade', 'comments'
        ])
        writer.writeheader()
        writer.writerows(records)
        
        return output.getvalue()
    
    def export_fees_csv(self, status: Optional[str] = None) -> str:
        """Export fee records to CSV"""
        query = """
            SELECT 
                s.admission_number, s.first_name, s.last_name, s.class_name,
                sf.term, sf.amount_due, sf.amount_paid, sf.balance, sf.due_date, sf.status
            FROM student_fees sf
            JOIN students s ON s.id = sf.student_id
            WHERE sf.school_id = %s
        """
        params = [self.school_id]
        
        if status:
            query += " AND sf.status = %s"
            params.append(status)
        
        query += " ORDER BY s.class_name, s.last_name"
        
        records = self.db.execute_query(query, tuple(params), fetch=True)
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'admission_number', 'first_name', 'last_name', 'class_name',
            'term', 'amount_due', 'amount_paid', 'balance', 'due_date', 'status'
        ])
        writer.writeheader()
        writer.writerows(records)
        
        return output.getvalue()
    
    # ============================================================================
    # PDF EXPORTS
    # ============================================================================
    
    def export_report_card_pdf(self, student_id: str) -> bytes:
        """Generate PDF report card for student"""
        # Get student info
        student = self.db.execute_query(
            "SELECT * FROM students WHERE id = %s AND school_id = %s",
            (student_id, self.school_id),
            fetch=True
        )[0]
        
        # Get grades
        grades = self.db.execute_query(
            """
            SELECT a.name, a.subject, a.max_marks, ar.marks_obtained, ar.grade, ar.comments
            FROM assessment_results ar
            JOIN assessments a ON a.id = ar.assessment_id
            WHERE ar.student_id = %s
            ORDER BY a.date DESC
            LIMIT 20
            """,
            (student_id,),
            fetch=True
        )
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("REPORT CARD", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Student Info
        info_data = [
            ['Student Name:', f"{student['first_name']} {student['last_name']}"],
            ['Admission Number:', student['admission_number']],
            ['Class:', student['class_name']],
            ['Date:', datetime.now().strftime('%Y-%m-%d')],
        ]
        
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Grades Table
        grade_data = [['Assessment', 'Subject', 'Marks', 'Grade', 'Comments']]
        for grade in grades:
            grade_data.append([
                grade['name'],
                grade['subject'],
                f"{grade['marks_obtained']}/{grade['max_marks']}",
                grade['grade'],
                grade['comments'] or '-'
            ])
        
        grade_table = Table(grade_data, colWidths=[1.5*inch, 1.3*inch, 1*inch, 0.7*inch, 2*inch])
        grade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(grade_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    
    def export_fee_receipt_pdf(self, payment_id: str) -> bytes:
        """Generate PDF fee receipt"""
        # Get payment details
        payment = self.db.execute_query(
            """
            SELECT p.*, s.first_name, s.last_name, s.admission_number, s.class_name
            FROM payments p
            JOIN students s ON s.id = p.student_id
            WHERE p.id = %s AND p.school_id = %s
            """,
            (payment_id, self.school_id),
            fetch=True
        )[0]
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("FEE PAYMENT RECEIPT", title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Receipt details
        receipt_data = [
            ['Receipt Number:', payment['reference_number'] or payment['id'][:8]],
            ['Date:', str(payment['payment_date'])],
            ['Student Name:', f"{payment['first_name']} {payment['last_name']}"],
            ['Admission Number:', payment['admission_number']],
            ['Class:', payment['class_name']],
            ['Amount Paid:', f"{payment['amount']:,.0f} UGX"],
            ['Payment Method:', payment['payment_method'].replace('_', ' ').title()],
            ['Status:', payment['status'].upper()],
        ]
        
        receipt_table = Table(receipt_data, colWidths=[2 * inch, 4 * inch])
        receipt_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 0.5 * inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Thank you for your payment!", footer_style))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", footer_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    def export_payslip_pdf(self, payroll_id: str) -> bytes:
        """Generate PDF Payslip for Staff"""
        from api.services.payroll import get_payroll_service
        
        # Get Payroll Data
        payroll_service = get_payroll_service(self.school_id)
        payslip = payroll_service.get_payslip(payroll_id)
        
        if not payslip:
            raise ValueError("Payslip not found")
            
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        elements.append(Paragraph("SALARY SLIP", styles['Title']))
        elements.append(Paragraph(f"Period: {payslip['month'].title()} {payslip['year']}", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Staff Info
        elements.append(Paragraph(f"Name: {payslip['first_name']} {payslip['last_name']}", styles['Normal']))
        elements.append(Paragraph(f"Employee ID: {payslip['employee_id']}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Table Data
        data = [
            ["Description", "Earnings", "Deductions"],
            ["Basic & Allowances", f"{payslip['gross_salary']:,.0f}", ""],
            ["Bonus", f"{payslip['bonus']:,.0f}", ""],
            ["PAYE Tax", "", f"{payslip['paye_tax']:,.0f}"],
            ["NSSF (5%)", "", f"{payslip['nssf']:,.0f}"],
            ["Other Deductions", "", f"{payslip['deductions']:,.0f}"],
            ["TOTAL", f"{(payslip['gross_salary'] + payslip['bonus']):,.0f}", f"{(payslip['paye_tax'] + payslip['nssf'] + payslip['deductions']):,.0f}"],
        ]
        
        t = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2*inch))
        
        # Net Pay
        net_style = ParagraphStyle('NetPay', parent=styles['Heading2'], alignment=TA_RIGHT)
        elements.append(Paragraph(f"NET PAY: {payslip['net_salary']:,.0f} UGX", net_style))
        
        # Build
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


def get_export_service(school_id: str) -> ExportService:
    """Helper to get export service instance"""
    return ExportService(school_id)
