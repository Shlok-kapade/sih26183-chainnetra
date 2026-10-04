from datetime import datetime, timezone
from typing import Dict, List


class FreezeRequestGenerator:
    """
    Generates a draft Freeze Request letter to a Virtual Asset Service Provider (VASP).
    """

    TEMPLATE = """\
[DRAFT] URGENT ASSET FREEZE REQUEST
-----------------------------------
Date: {date}
To: {vasp_name} Compliance & Legal Team
From: [Law Enforcement Agency / Investigating Body]
Case Reference: {case_id}

SUBJECT: URGENT REQUEST TO FREEZE ASSETS - SUSPECTED ILLICIT ACTIVITY

Dear {vasp_name} Compliance Team,

We are writing to urgently request the temporary freezing of assets held in the following address(es), which our investigations indicate are linked to illicit activities:

Target Deposit Address: {deposit_address}
Chain/Network: {chain}
Asset: {asset}

Summary of Evidence:
The address {deposit_address} has received funds directly traced from known illicit sources. 
Below are the supporting transaction hashes showing the flow of funds to your platform:

{evidence_table}

Action Requested:
1. Immediately freeze all withdrawals and transfers from the aforementioned deposit address.
2. Preserve all KYC/AML records, login IPs, and activity logs associated with the user account holding this deposit address.
3. Acknowledge receipt of this request and confirm the current balance of the account.

A formal subpoena/court order will follow in accordance with mutual legal assistance treaties and local jurisdiction requirements.

Thank you for your prompt cooperation.

Sincerely,
[Agent/Officer Name]
[Title]
[Contact Information]
"""

    @staticmethod
    def generate(
        vasp_name: str,
        case_id: str,
        deposit_address: str,
        chain: str,
        asset: str,
        evidence_txs: List[Dict[str, str]]  # list of {"tx_hash": ..., "amount": ...}
    ) -> str:

        table_lines = []
        for tx in evidence_txs:
            table_lines.append(f"- Tx: {tx.get('tx_hash', 'N/A')} | Amount: {tx.get('amount', 'N/A')}")

        evidence_table = "\n".join(table_lines) if table_lines else "No specific transactions provided."

        return FreezeRequestGenerator.TEMPLATE.format(
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            vasp_name=vasp_name,
            case_id=case_id,
            deposit_address=deposit_address,
            chain=chain,
            asset=asset,
            evidence_table=evidence_table
        )
