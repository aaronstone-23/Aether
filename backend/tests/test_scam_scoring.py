import unittest

from app.services.brands import brand_in_host
from app.services.rules import analyse_links, extract_urls, score_text, verdict_from_score


class ScamScoringTests(unittest.TestCase):
    def test_urgent_account_threat_with_link_is_high_risk(self):
        result = score_text(
            "Urgent: your bank account will be suspended. "
            "Verify your account at https://bank-login.xyz/verify"
        )
        self.assertGreaterEqual(result["score"], 60)
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_otp_request_with_urgency_is_high_risk(self):
        result = score_text(
            "Act now and share your OTP immediately to restore access."
        )
        self.assertGreaterEqual(result["score"], 60)
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_otp_safety_advice_is_not_a_credential_request(self):
        result = score_text("Your bank will never ask you to share your OTP.")
        self.assertNotIn("credential_request", result["matches"])
        self.assertEqual(result["score"], 0)

    def test_mild_payment_confirmation_remains_low_risk(self):
        result = score_text("Your payment of $25 was processed today. Thank you.")
        self.assertLess(result["score"], 25)
        self.assertEqual(verdict_from_score(result["score"])[0], "likely_legit")

    def test_urgent_fee_request_is_not_marked_likely_legit(self):
        result = score_text("Urgent: send money now to pay the processing fee.")
        self.assertGreaterEqual(result["score"], 55)
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_text_me_the_otp_is_high_risk(self):
        result = score_text("Text me your one-time password now to restore your account.")
        self.assertIn("credential_request", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_request_for_identity_documents_is_high_risk(self):
        result = score_text("Reply with your Aadhaar number and PAN card details.")
        self.assertIn("credential_request", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_account_threat_negation_is_not_scored_as_a_threat(self):
        result = score_text("Your bank account will not be suspended. Never share your OTP.")
        self.assertNotIn("account_threat", result["matches"])
        self.assertNotIn("credential_request", result["matches"])
        self.assertEqual(result["score"], 0)

    def test_safety_advice_does_not_hide_a_separate_account_threat(self):
        result = score_text(
            "Never share your OTP, your account will be suspended unless you verify "
            "at https://bank-login.xyz."
        )
        self.assertNotIn("credential_request", result["matches"])
        self.assertIn("account_threat", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_any_link_is_at_least_suspicious(self):
        result = score_text("Please review this message: https://example.com/info")
        self.assertIn("link_present", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "suspicious")

    def test_link_with_call_to_action_is_at_least_suspicious(self):
        result = score_text("Track your package at https://parcel.example/track")
        self.assertIn("link_action", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "suspicious")

    def test_bank_statement_link_is_not_automatically_called_fake(self):
        result = score_text(
            "Your bank statement is ready. Visit https://bank.example/statements"
        )
        self.assertLess(result["score"], 55)
        self.assertEqual(verdict_from_score(result["score"])[0], "suspicious")

    def test_remote_access_support_request_is_high_risk(self):
        result = score_text(
            "Bank support says install AnyDesk and share your screen to receive a refund."
        )
        self.assertIn("remote_access", result["matches"])
        self.assertIn("authority_claim", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_job_offer_advance_fee_is_high_risk(self):
        result = score_text("You got the job offer. Pay a registration fee to start work.")
        self.assertIn("advance_fee", result["matches"])
        self.assertIn("financial_request", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_prize_claim_link_is_high_risk(self):
        result = score_text(
            "Congratulations, you won a prize. Claim your prize at https://claim-prize.xyz/win"
        )
        self.assertIn("win", result["matches"])
        self.assertIn("link_action", result["matches"])
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_do_not_pay_safety_advice_is_not_a_payment_request(self):
        result = score_text("Do not pay a processing fee to claim an unexpected prize.")
        self.assertNotIn("financial_request", result["matches"])
        self.assertFalse(result["matches"]["payment"])
        self.assertFalse(result["matches"]["win"])
        self.assertEqual(result["score"], 0)

    def test_plain_and_www_links_are_extracted(self):
        urls = extract_urls("Check www.example.xyz/path and secure.example.top/login.")
        self.assertEqual(urls, ["www.example.xyz/path", "secure.example.top/login"])

    def test_kyc_expiry_with_update_link_is_not_marked_legit(self):
        result = score_text(
            "Your KYC expires today. Update now at "
            "https://novabank-kyc.example/update."
        )
        self.assertGreaterEqual(result["score"], 25)
        self.assertEqual(verdict_from_score(result["score"])[0], "fake")

    def test_microsoft_and_youtube_impersonation_is_detected(self):
        self.assertIsNone(brand_in_host("login.microsoft.com"))
        self.assertIsNone(brand_in_host("www.youtube.com"))
        self.assertEqual(brand_in_host("microsoft-login.xyz"), "microsoft")
        self.assertEqual(brand_in_host("youtube-security.top"), "youtube")
        self.assertEqual(
            len(analyse_links(["https://microsoft-login.xyz"])["lookalike"]),
            1,
        )


if __name__ == "__main__":
    unittest.main()
