from decimal import Decimal
import json
import unittest

from script_runtime import Runtime, definitions


class Contracts(unittest.TestCase):
    def start(self, level=2, size=5):
        runtime = Runtime()
        runtime.call("mc_initialize")
        self.assertTrue(runtime.click(f"mc_demo_{level}_{size}"))
        return runtime

    def test_all_quotes_and_complete_lifecycles(self):
        for level, factor in ((1, "1.25"), (2, "1.50"), (3, "1.80")):
            for size in (5, 10):
                with self.subTest(level=level, size=size):
                    r = self.start(level, size)
                    fee = Decimal(400 * size) * Decimal(factor)
                    self.assertEqual(r.variables["mc_weekly_fee"], fee)
                    self.assertEqual(r.variables["mc_sandbox_balance"], 1000000 - 4 * fee)
                    r.tick(3)
                    self.assertEqual(r.variables["mc_state"], 1)
                    r.tick()
                    self.assertEqual(r.variables["mc_state"], 2)
                    self.assertEqual(r.variables["mc_remaining"], 52)
                    r.tick(52)
                    self.assertEqual(r.variables["mc_state"], 3)
                    self.assertEqual(r.variables["mc_sandbox_balance"], 1000000 - 56 * fee)
                    r.tick()
                    self.assertEqual(r.variables["mc_state"], 0)
                    self.assertFalse(r.click("mc_demo_1_5"))
                    r.tick(7)
                    self.assertFalse(r.click("mc_demo_1_5"))
                    r.tick()
                    self.assertTrue(r.click("mc_demo_1_5"))
                    self.assertEqual(r.treasury, 1000000)

    def test_duplicate_signing_cannot_replace_or_charge_contract(self):
        r = self.start()
        before = dict(r.variables)
        self.assertFalse(r.click("mc_demo_3_10"))
        r.call("mc_demo_3_10_start")  # also guard the effect, not just the UI
        self.assertEqual(r.variables, before)

    def test_renewal_only_in_last_four_weeks_and_not_twice(self):
        r = self.start()
        r.tick(4 + 47)
        self.assertFalse(r.click("mc_renew"))
        r.tick()
        self.assertTrue(r.click("mc_renew"))
        self.assertEqual(r.variables["mc_remaining"], 56)
        self.assertFalse(r.click("mc_renew"))
        r.tick(56)
        self.assertEqual(r.variables["mc_state"], 3)

    def test_six_unpaid_weeks_preserve_debt_and_credit_after_release(self):
        r = self.start()
        r.tick(4)
        r.click("mc_drain")
        r.tick(5)
        self.assertEqual(r.variables["mc_state"], 2)
        self.assertEqual(r.variables["mc_arrears"], 5)
        self.assertFalse(r.click("mc_cancel"))
        r.tick()
        self.assertEqual(r.variables["mc_state"], 3)
        self.assertEqual(r.variables["mc_debt"], 6 * 3000)
        r.tick(9)
        self.assertEqual(r.variables["mc_debt"], 18000)
        self.assertFalse(r.click("mc_demo_1_5"))
        r.click("mc_topup")
        self.assertTrue(r.click("mc_settle"))
        self.assertEqual(r.variables["mc_sandbox_balance"], 82000)
        self.assertEqual(r.variables["mc_credit_strikes"], 1)
        self.assertTrue(r.click("mc_demo_1_5"))
        self.assertEqual(r.treasury, 1000000)

    def test_payment_recovers_arrears_without_free_weeks(self):
        r = self.start()
        r.tick(4)
        r.click("mc_drain")
        r.tick(2)
        r.click("mc_topup")
        r.tick()
        self.assertEqual(r.variables["mc_sandbox_balance"], 91000)
        self.assertEqual(r.variables["mc_debt"], 0)
        self.assertEqual(r.variables["mc_arrears"], 0)

    def test_cancel_once_and_no_post_withdrawal_invoices(self):
        r = self.start()
        r.tick(4 + 3)
        balance = r.variables["mc_sandbox_balance"]
        self.assertTrue(r.click("mc_cancel"))
        self.assertFalse(r.click("mc_cancel"))
        r.call("mc_cancel_contract")
        r.tick(10)
        self.assertEqual(r.variables["mc_sandbox_balance"], balance - 12000)
        self.assertEqual(r.treasury, 1000000)

    def test_insufficient_entry_funds_do_not_start_or_leave_sandbox_flag(self):
        r = Runtime()
        r.call("mc_initialize")
        r.variables.update(mc_demo_account=True, mc_sandbox_balance=Decimal(9999))
        r.call("mc_demo_1_5_start")
        self.assertEqual(r.variables["mc_state"], 0)
        self.assertNotIn("mc_sandbox", r.variables)
        self.assertEqual(r.variables["mc_sandbox_balance"], 9999)

    def test_live_hiring_is_fail_closed_even_if_effect_called_directly(self):
        r = Runtime()
        r.call("mc_initialize")
        r.variables.update(mc_level=Decimal(3), mc_size=Decimal(10))
        self.assertFalse(r.click("mc_live_hire"))
        r.call("mc_sign_contract")
        self.assertEqual(r.variables["mc_state"], 0)
        self.assertEqual(r.treasury, 1000000)

    def test_countries_are_isolated(self):
        a, b = self.start(), self.start(3, 10)
        before = dict(b.variables)
        a.tick(4)
        a.click("mc_drain")
        a.tick(6)
        self.assertEqual(b.variables, before)
        self.assertEqual(a.variables["mc_state"], 3)

    def test_last_week_debt_is_not_erased_by_expiration(self):
        r = self.start()
        r.tick(4 + 51)
        r.click("mc_drain")
        r.tick(10)
        self.assertEqual(r.variables["mc_state"], 0)
        self.assertEqual(r.variables["mc_debt"], 3000)
        self.assertFalse(r.click("mc_demo_1_5"))

    def test_exact_entry_balance_and_muster_cancellation(self):
        r = Runtime()
        r.call("mc_initialize")
        r.variables.update(mc_demo_account=True, mc_sandbox_balance=Decimal(20000))
        self.assertTrue(r.click("mc_demo_1_5"))
        self.assertEqual(r.variables["mc_sandbox_balance"], 10000)
        self.assertTrue(r.click("mc_cancel"))
        r.tick()
        self.assertEqual(r.variables["mc_sandbox_balance"], 0)
        self.assertEqual(r.variables["mc_state"], 0)

    def test_journal_display_fields_exist_before_signing_and_after_release(self):
        r = Runtime()
        r.call("mc_initialize")
        keys = ("mc_state", "mc_sandbox_balance", "mc_weekly_fee", "mc_debt",
                "mc_remaining", "mc_muster", "mc_cooldown", "mc_credit_strikes")
        self.assertTrue(all(key in r.variables for key in keys))
        r.click("mc_demo_1_5")
        r.click("mc_cancel")
        r.tick()
        self.assertTrue(all(key in r.variables for key in keys))

    def test_serialized_state_continues_without_reinitialization(self):
        original = self.start()
        original.tick(4 + 9)
        saved = json.dumps(original.variables, default=str)
        restored = Runtime()
        restored.variables = json.loads(saved, parse_float=Decimal, parse_int=Decimal)
        for key, value in restored.variables.items():
            if isinstance(value, str): restored.variables[key] = Decimal(value)
        restored.call("mc_initialize")
        original.tick(43)
        restored.tick(43)
        self.assertEqual(restored.variables, original.variables)

    def test_journal_has_one_weekly_effect_and_no_delayed_event_loop(self):
        journal = dict((k, v) for k, _, v in definitions("journal_entries")["mc_je"])
        pulse = dict((k, v) for k, _, v in journal["on_weekly_pulse"])
        self.assertEqual(pulse["effect"], [("mc_weekly_tick", "=", "yes")])


if __name__ == "__main__":
    unittest.main()
