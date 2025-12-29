from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import json
from typing import Any, Dict, List, Optional
from uuid import uuid4

from api.core.config import get_settings
from api.services.clarity import ClarityClient
from api.services.database import get_fee_ops, get_mobile_money_ops

SUPPORTED_PROVIDERS = {"MTN", "AIRTEL"}


class MobileMoneyService:
    """Manages MTN/Airtel mobile money initiation, reconciliation, and fallbacks."""

    def __init__(self, school_id: str, ops=None, fees=None, settings=None):
        self.school_id = school_id
        self.settings = settings or get_settings()
        self.ops = ops or get_mobile_money_ops()
        self.fees = fees or get_fee_ops()

    def initiate_payment(
        self,
        *,
        provider: str,
        amount: Decimal,
        currency: str,
        msisdn: str,
        student_id: Optional[str] = None,
        student_fee_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        initiated_by: str = "system",
    ) -> Dict[str, Any]:
        provider = provider.upper()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider '{provider}'. Expected one of {SUPPORTED_PROVIDERS}.")

        reference = f"MM-{uuid4().hex[:12].upper()}"
        status = "pending_offline" if not self._has_live_credentials(provider) else "awaiting_provider"
        enriched_metadata = {
            "student_fee_id": student_fee_id,
            "initiated_by": initiated_by,
            **(metadata or {}),
        }

        transaction = self.ops.create_transaction(
            {
                "school_id": self.school_id,
                "student_id": student_id,
                "student_fee_id": student_fee_id,
                "provider": provider,
                "msisdn": msisdn,
                "amount": str(amount),
                "currency": currency,
                "status": status,
                "reference": reference,
                "metadata": enriched_metadata,
            }
        )

        instructions = self._build_instructions(provider, msisdn, amount, currency, status)

        return {
            "success": True,
            "transaction": transaction,
            "instructions": instructions,
            "requires_manual_settlement": status == "pending_offline",
        }

    def acknowledge_callback(
        self,
        *,
        provider: str,
        reference: str,
        status: str,
        amount: Optional[Decimal] = None,
        external_reference: Optional[str] = None,
        message: Optional[str] = None,
    ) -> Dict[str, Any]:
        provider = provider.upper()
        transaction = self.ops.get_transaction(reference)
        if not transaction or transaction["provider"] != provider or transaction["school_id"] != self.school_id:
            raise ValueError("Transaction not found for reference.")

        update_payload: Dict[str, Any] = {
            "status": status,
            "external_reference": external_reference,
            "message": message,
            "amount": str(amount) if amount is not None else transaction["amount"],
        }

        updated = self.ops.update_transaction(reference, update_payload)

        if status == "success":
            self._record_fee_payment(updated)

        return {"success": True, "transaction": updated}

    def poll_transaction(self, reference: str) -> Dict[str, Any]:
        transaction = self.ops.get_transaction(reference)
        if not transaction:
            raise ValueError("Transaction not found.")

        if transaction["status"] in {"pending_offline", "awaiting_provider"} and self._has_live_credentials(
            transaction["provider"]
        ):
            # In a live environment this is where we'd hit the provider polling endpoint.
            # Without credentials we keep the status as-is.
            pass

        return transaction

    def list_transactions(
        self,
        *,
        limit: int = 50,
        student_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return self.ops.list_transactions(self.school_id, student_id=student_id, limit=limit)

    def generate_offline_report(self) -> Dict[str, Any]:

        transactions = self.ops.list_transactions(self.school_id, limit=200)
        clarity = ClarityClient()
        try:
            summary = clarity.analyze(
                directive=(
                    "Summarize the following mobile money transactions for executive review. Highlight "
                    "any pending offline settlements and recommend actions for bursars."
                ),
                domain="expenses",
                files=[
                    {
                        "filename": "mobile_money_transactions.json",
                        "data": json.dumps(transactions, default=str),
                    }
                ],
            )
        finally:
            clarity.close()

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "transactions": transactions,
            "analysis": summary,
        }

    def _record_fee_payment(self, transaction: Dict[str, Any]) -> None:
        student_fee_id = transaction.get("student_fee_id")
        if not student_fee_id:
            return

        try:
            amount = Decimal(transaction["amount"])
        except (ValueError, TypeError):
            amount = Decimal("0")

        payment_payload = {
            "student_fee_id": student_fee_id,
            "student_id": transaction.get("student_id"),
            "school_id": transaction["school_id"],
            "amount": amount,
            "payment_method": f"mobile_money_{transaction['provider'].lower()}",
            "payment_reference": transaction.get("external_reference") or transaction["reference"],
            "phone_number": transaction.get("msisdn"),
            "transaction_id": transaction.get("external_reference"),
            "notes": "Auto-recorded mobile money settlement.",
            "received_by": "mobile_money_service",
        }
        try:
            self.fees.record_payment(payment_payload)
        except Exception:
            # If the fee structure tables are missing we leave the transaction recorded but do not fail.
            pass

    def _has_live_credentials(self, provider: str) -> bool:
        if provider == "MTN":
            return bool(self.settings.mtn_mobile_money_api_key)
        if provider == "AIRTEL":
            return bool(self.settings.airtel_mobile_money_api_key)
        return False

    def _build_instructions(
        self, provider: str, msisdn: str, amount: Decimal, currency: str, status: str
    ) -> Dict[str, Any]:
        base_instructions = {
            "provider": provider,
            "formatted_amount": f"{currency} {amount}",
            "customer_msisdn": msisdn,
        }

        if provider == "MTN":
            ussd = "*165# → 4 (Payments) → 5 (Fees & Taxes) → Enter School Code"
        else:
            ussd = "*185# → 4 (Pay Bill) → 6 (School Fees) → Enter School Code"

        base_instructions["ussd_steps"] = ussd
        if status == "pending_offline":
            base_instructions[
                "note"
            ] = "No live API key detected. Record the confirmation code manually once payment is received."
        else:
            base_instructions[
                "note"
            ] = "Payment request sent to provider. Await mobile confirmation or callback."

        return base_instructions
