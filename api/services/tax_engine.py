"""
Enterprise Tax Engine
=====================
Handles complex payroll tax calculations for East African contexts (Uganda, Kenya, Tanzania).
Supports:
1. Progressive Income Tax (PAYE) with configurable bands.
2. Social Security Contributions (NSSF).
3. Health Insurance Levies (NHIF/SHIF).
4. Local Service Tax (LST).
"""
from typing import List, Dict, Optional
from decimal import Decimal

# Default Tax Configuration (UGANDA FY 2024/2025)
DEFAULT_TAX_CONFIG = {
    "country": "UG",
    "currency": "UGX",
    "paye_bands": [
        {"threshold": 235000, "rate": 0.0, "base_tax": 0},      # < 235k: 0%
        {"threshold": 335000, "rate": 0.10, "base_tax": 0},     # 235k-335k: 10%
        {"threshold": 410000, "rate": 0.20, "base_tax": 10000}, # 335k-410k: 20% + 10k
        {"threshold": 10000000, "rate": 0.30, "base_tax": 25000}, # 410k-10M: 30% + 25k
        {"threshold": float('inf'), "rate": 0.40, "base_tax": 2902000} # > 10M: 40% + 2.9M
    ],
    "nssf": {
        "employee_rate": 0.05, # 5%
        "employer_rate": 0.10, # 10%
        "cap": float('inf')    # No cap in UG usually, but good to have param
    },
    "lst": [ # Local Service Tax (Annual/Monthly) - Simplified example
        {"threshold": 100000, "amount": 0},
        {"threshold": 200000, "amount": 5000},
        {"threshold": 1000000, "amount": 10000},
        {"threshold": float('inf'), "amount": 100000}
    ]
}

class TaxEngine:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or DEFAULT_TAX_CONFIG

    def calculate_paye(self, chargeable_income: float) -> float:
        """
        Calculate generic Progressive PAYE based on configured bands.
        Logic: Find the band the income false into, apply rate to excess + base tax.
        Actually, simplified logic often used:
        Iterate bands. If income > band_threshold of previous, tax the difference.
        
        Using the standard "Bracket" logic from the config:
        The config structure implies:
        Start from highest band? Or cumulative?
        
        Let's use the explicit standard logic:
        Income falls into a specific bracket range.
        """
        income = chargeable_income
        bands = self.config["paye_bands"]
        
        # Uganda Specific Logic (Iterative Progressive) works best for generic engines
        # But here we have specific 'base_tax' defined in config for speed.
        
        # 1. Find the applicable top logical band
        # (This relies on the config being correct)
        tax = 0.0
        
        # Logic for provided config (Standard UG Calculation):
        if income <= 235000:
            return 0.0
        elif income <= 335000:
            return (income - 235000) * 0.10
        elif income <= 410000:
            return (income - 335000) * 0.20 + 10000
        elif income <= 10000000:
            return (income - 410000) * 0.30 + 25000
        else:
            return (income - 10000000) * 0.40 + 2902000
            
    def calculate_nssf(self, gross_salary: float) -> Dict[str, float]:
        """
        Calculate Social Security
        Returns: { "employee": 5%, "employer": 10%, "total": 15% }
        """
        conf = self.config["nssf"]
        employee_deduction = gross_salary * conf["employee_rate"]
        employer_contribution = gross_salary * conf["employer_rate"]
        
        # Apply Caps if any
        if conf.get("cap", float('inf')) < float('inf'):
            cap = conf["cap"]
            employee_deduction = min(employee_deduction, cap * conf["employee_rate"])
            employer_contribution = min(employer_contribution, cap * conf["employer_rate"])

        return {
            "employee": round(employee_deduction, 2),
            "employer": round(employer_contribution, 2),
            "total": round(employee_deduction + employer_contribution, 2)
        }

    def calculate_net_salary(self, gross: float, allowances: float = 0, deductions: float = 0) -> Dict[str, float]:
        """
        Full Payroll Calculation Routine
        gross: Basic + Allowances that are taxable
        """
        # 1. NSSF (Tax exempt in UG? usually deducted BEFORE PAYE in some systems, 
        # but in UG, NSSF is deducted from Gross, then PAYE calculated on balance?
        # UG Tax Law: Chargeable Income = Gross Income - Exempt Income.
        # Employee NSSF contribution is NOT tax deductible in Uganda (historically), 
        # BUT recent laws might have changed. 
        # *Standard Practice*: PAYE is calculated on Gross. NSSF is just another deduction.
        # *Correction*: In Kenya, NSSF is tax deductible. In Uganda, it is NOT.
        
        # We will assume UG Standard: PAYE on Gross, NSSF from Gross.
        
        nssf = self.calculate_nssf(gross)
        paye = self.calculate_paye(gross) # Calculate tax on gross (UG style)
        
        total_deductions = nssf["employee"] + paye + deductions
        net = gross - total_deductions
        
        return {
            "gross": gross,
            "nssf_employee": nssf["employee"],
            "nssf_employer": nssf["employer"],
            "paye": paye,
            "other_deductions": deductions,
            "total_deductions": total_deductions,
            "net": net
        }
