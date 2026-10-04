import csv
import io

from .manifest import EvidenceManifest


class ReportGenerator:
    """
    Generates human-readable and structured reports from an EvidenceManifest.
    """

    @staticmethod
    def to_markdown(manifest: EvidenceManifest) -> str:
        """
        Generate a Markdown report (can be converted to PDF by frontend or Pandoc).
        """
        md = []
        md.append(f"# Investigation Report: {manifest.case_id}")
        md.append(f"**Generated At**: {manifest.generated_at.isoformat()}")
        md.append(f"**Target**: {manifest.target_address} ({manifest.target_chain})")
        md.append("")

        md.append("## Triage & Risk Assessment")
        md.append(f"- **Severity Level**: {manifest.severity_level}")
        md.append(f"- **Urgency Score**: {manifest.urgency_score:.2f}")
        md.append("")

        md.append("## Attributions & Labels")
        if manifest.labels:
            md.append("| Address | Label | Confidence | Source |")
            md.append("|---|---|---|---|")
            for lbl in manifest.labels:
                md.append(f"| {lbl.address} | {lbl.label} | {lbl.confidence} | {lbl.source} |")
        else:
            md.append("*No labeled addresses found in this trace.*")
        md.append("")

        md.append("## Trace Evidence (Transactions)")
        if manifest.traces:
            md.append("| Timestamp | Tx Hash | From | To | Asset | Amount | Type |")
            md.append("|---|---|---|---|---|---|---|")
            for tx in manifest.traces:
                md.append(f"| {tx.timestamp.strftime('%Y-%m-%d %H:%M')} | {tx.tx_hash} | {tx.from_address} | {tx.to_address} | {tx.asset} | {tx.amount} | {tx.evidence_type} |")
        else:
            md.append("*No trace evidence recorded.*")

        md.append("\n## Verification")
        md.append(f"**Manifest Hash**: `{manifest.manifest_hash}`")

        return "\n".join(md)

    @staticmethod
    def to_csv(manifest: EvidenceManifest) -> str:
        """
        Export the traces to CSV format.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["case_id", "timestamp", "tx_hash", "chain", "from_address", "to_address", "asset", "amount", "evidence_type", "notes"])

        for tx in manifest.traces:
            writer.writerow([
                manifest.case_id,
                tx.timestamp.isoformat(),
                tx.tx_hash,
                tx.chain,
                tx.from_address,
                tx.to_address,
                tx.asset,
                tx.amount,
                tx.evidence_type,
                tx.notes or ""
            ])

        return output.getvalue()
