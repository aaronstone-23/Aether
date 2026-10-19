import json
import httpx

B = "http://127.0.0.1:5000/api"
print(httpx.get(f"{B}/health").json())

sms = ("URGENT: Your SBI account will be blocked within 24 hours. "
       "Update KYC now at http://sbi-kyc-update.xyz/login or pay Rs 10 processing fee to rahul@ybl")
r = httpx.post(f"{B}/analyze", json={"text": sms}, timeout=60).json()
print("SMS:", r["verdict"], r["risk_score"]); print(*r["red_flags"], sep="\n  - ")

email = """Received: from mail.sender-host.example ([103.21.58.10]) by mx.google.com with ESMTP
Authentication-Results: mx.google.com; spf=fail smtp.mailfrom=microsoft.com; dkim=none; dmarc=fail header.from=microsoft.com
From: "David - Microsoft Support" <david@microsoft.com>
Reply-To: <help.desk.991@gmail.com>
Date: Wed, 14 Oct 2026 09:30:00 +0500
Subject: Urgent: Your Microsoft account will be suspended

Verify now or your account will be closed. Call +91 98765 43210."""
r = httpx.post(f"{B}/analyze", json={"text": email}, timeout=60).json()
print("EMAIL:", r["verdict"], r["risk_score"])
print(json.dumps(r["technical_evidence"], indent=2)[:900])