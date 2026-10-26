"""Generate contract choices and bilingual localization; no runtime dependencies."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def outputs():
    buttons, effects, links = [], [], []
    translations = {"english": {}, "simp_chinese": {}}
    names = {"english": ["Temporary", "Professional", "Veteran"],
             "simp_chinese": ["临时佣兵", "职业佣兵", "老兵团"]}
    for level in range(1, 4):
        for size in (5, 10):
            key = f"mc_demo_{level}_{size}"
            weekly = int(400 * size * (1.25, 1.5, 1.8)[level - 1])
            links.append(f"    scripted_button = {key}")
            buttons.append(f'''{key} = {{
    name = {key}
    desc = {key}_desc
    visible = {{ always = yes }}
    possible = {{
        mc_contract_idle = yes
        OR = {{
            NOT = {{ has_variable = mc_demo_account }}
            var:mc_sandbox_balance >= {weekly * 4}
        }}
    }}
    ai_chance = {{ base = 0 }}
    effect = {{ {key}_start = yes }}
}}
''')
            effects.append(f'''{key}_start = {{
    mc_initialize = yes
    if = {{
        limit = {{ mc_contract_idle = yes }}
        if = {{
            limit = {{ NOT = {{ has_variable = mc_demo_account }} }}
            set_variable = {{ name = mc_demo_account value = yes }}
            set_variable = {{ name = mc_sandbox_balance value = 1000000 }}
        }}
        set_variable = {{ name = mc_level value = {level} }}
        set_variable = {{ name = mc_size value = {size} }}
        set_variable = {{ name = mc_sandbox value = yes }}
        mc_sign_contract = yes
        if = {{
            limit = {{ var:mc_state = 0 }}
            remove_variable = mc_sandbox
        }}
    }}
}}
''')
            translations["english"][key] = f"SIMULATION: Lv.{level} {names['english'][level - 1]}, {size} battalions"
            translations["english"][key + "_desc"] = f"No real troops or treasury charges. Demo entry fee: {weekly * 4}; weekly: {weekly}. Four muster pulses, then 52 service pulses."
            translations["simp_chinese"][key] = f"模拟：Lv.{level} {names['simp_chinese'][level - 1]}，{size} 营"
            translations["simp_chinese"][key + "_desc"] = f"不交付真实部队，不扣国库。模拟入场费 {weekly * 4}，周费 {weekly}。四次周更新集结后，服役 52 次周更新。"
    common = {
        "mc_je": ("Mercenary Affairs (Development Preview)", "雇佣兵事务（开发预览）"),
        "mc_je_reason": ("Contract sandbox only. Military delivery is not implemented.", "当前仅开放合同沙盒，军事交付尚未实现。"),
        "mc_je_status": ("Choose a free simulation below. No actual troops will be delivered.", "选择下方免费模拟。此版本不会交付真实部队。"),
        "mc_status_idle": ("Ready for a free simulation.", "可以开始免费合同模拟。"),
        "mc_status_muster": ("SIMULATION: mustering. Weekly service fees have not started.", "模拟集结中；尚未收取服役周费。"),
        "mc_status_active": ("SIMULATION: in service.", "模拟服役中。"),
        "mc_status_withdrawing": ("SIMULATION: withdrawing. No further weekly fees.", "模拟撤离中；不再新增周费。"),
        "mc_status_cooldown": ("SIMULATION: resting. Debt must be settled before another contract.", "模拟休整中；新合同还需结清旧债。"),
        "mc_status_late1": ("SIMULATION: missed payment. Restore funds to settle the invoice.", "模拟欠薪警告：补足模拟余额可清偿账单。"),
        "mc_status_late2": ("SIMULATION: two weeks overdue; replenishment would be suspended.", "模拟欠薪达到两周；正式后端应暂停补员。当前没有真实部队。"),
        "mc_status_late4": ("SIMULATION: four weeks overdue; termination at six.", "模拟欠薪达到四周；六周将终止合同。"),
        "mc_status_debt": ("SIMULATION: outstanding debt blocks new contracts.", "存在模拟欠款，结清后才能签订新合同。"),
        "mc_live_hire": ("Hire real mercenaries (unavailable)", "正式雇佣（尚不可用）"),
        "mc_live_hire_desc": ("Locked: independent troop delivery, replenishment, safe release and live pricing must be verified first.", "尚未验证独立部队交付、补员、安全清退及实际成本，正式入口锁定。"),
        "mc_cancel": ("Cancel simulation", "解约模拟合同"),
        "mc_cancel_desc": ("Pay four weekly fees from the demo account, then withdraw. Requires no outstanding debt.", "从模拟账户支付四周费用后撤离，需先结清欠款。"),
        "mc_renew": ("Renew simulation for 52 weeks", "模拟续约 52 周"),
        "mc_renew_desc": ("Available in the last four service weeks, without debt. Keeps the contracted weekly rate; no new entry fee.", "剩余四周内且无欠薪时可续约；保留合同周费，不重复收入场费。"),
        "mc_topup": ("Add 100,000 demo funds", "增加 100,000 模拟余额"),
        "mc_topup_desc": ("Changes only the demo account, never the treasury.", "仅修改模拟账户，不影响真实国库。"),
        "mc_drain": ("Empty demo account (test arrears)", "清空模拟余额（测试欠薪）"),
        "mc_drain_desc": ("Use during simulated service to observe warnings and termination. Does not clear debt.", "用于观察欠薪警告与合同终止；不会清除既有债务。"),
        "mc_settle": ("Settle demo debt", "结清模拟欠款"),
        "mc_settle_desc": ("Uses demo funds, including after withdrawal. Credit strikes remain recorded.", "从模拟余额结清欠款，撤离后仍可操作；保留失信记录。"),
    }
    stats = {
        "english": "\\nState (0 idle, 1 muster, 2 service, 3 withdrawal): [GetPlayer.MakeScope.Var('mc_state').GetValue|0]\\nDemo funds: [GetPlayer.MakeScope.Var('mc_sandbox_balance').GetValue|0]\\nWeekly fee: [GetPlayer.MakeScope.Var('mc_weekly_fee').GetValue|0]\\nDebt: [GetPlayer.MakeScope.Var('mc_debt').GetValue|0]\\nService weeks left: [GetPlayer.MakeScope.Var('mc_remaining').GetValue|0]\\nMuster weeks left: [GetPlayer.MakeScope.Var('mc_muster').GetValue|0]\\nRest weeks left: [GetPlayer.MakeScope.Var('mc_cooldown').GetValue|0]\\nCredit strikes: [GetPlayer.MakeScope.Var('mc_credit_strikes').GetValue|0]",
        "simp_chinese": "\\n阶段（0空闲／1集结／2服役／3撤离）：[GetPlayer.MakeScope.Var('mc_state').GetValue|0]\\n模拟余额：[GetPlayer.MakeScope.Var('mc_sandbox_balance').GetValue|0]\\n合同周费：[GetPlayer.MakeScope.Var('mc_weekly_fee').GetValue|0]\\n欠款：[GetPlayer.MakeScope.Var('mc_debt').GetValue|0]\\n剩余服役周：[GetPlayer.MakeScope.Var('mc_remaining').GetValue|0]\\n剩余集结周：[GetPlayer.MakeScope.Var('mc_muster').GetValue|0]\\n剩余休整周：[GetPlayer.MakeScope.Var('mc_cooldown').GetValue|0]\\n失信次数：[GetPlayer.MakeScope.Var('mc_credit_strikes').GetValue|0]",
    }
    for key, pair in common.items():
        for lang, value in zip(translations, pair):
            translations[lang][key] = value
    for lang in translations:
        for key in list(translations[lang]):
            if key.startswith("mc_status_"):
                translations[lang][key] += stats[lang]
    result = {
        "mod/common/scripted_buttons/mc_generated_choices.txt": "\n".join(buttons),
        "mod/common/scripted_effects/mc_generated_choices.txt": "\n".join(effects),
    }
    status_cases = [
        ("mc_status_withdrawing", "var:mc_state = 3"),
        ("mc_status_late4", "var:mc_state = 2 var:mc_arrears >= 4"),
        ("mc_status_late2", "var:mc_state = 2 var:mc_arrears >= 2"),
        ("mc_status_late1", "var:mc_state = 2 var:mc_arrears >= 1"),
        ("mc_status_muster", "var:mc_state = 1"),
        ("mc_status_active", "var:mc_state = 2"),
        ("mc_status_cooldown", "var:mc_cooldown > 0"),
        ("mc_status_debt", "var:mc_debt > 0"),
        ("mc_status_idle", "always = yes"),
    ]
    statuses = "\n".join(f"            triggered_desc = {{ desc = {key} trigger = {{ {condition} }} }}" for key, condition in status_cases)
    result["mod/common/journal_entries/mc_mercenary_journal.txt"] = '''# No periodic global scan or delayed event chain. One weekly hook per JE.
mc_je = {
    is_shown_when_inactive = { is_player = yes }
    possible = { is_player = yes }
    immediate = { mc_initialize = yes }
    on_weekly_pulse = { effect = { mc_weekly_tick = yes } }
    transferable = no
    can_revolution_inherit = no
    weight = 10
''' + "\n".join(links) + '''
    scripted_button = mc_live_hire
    scripted_button = mc_cancel
    scripted_button = mc_renew
    scripted_button = mc_topup
    scripted_button = mc_drain
    scripted_button = mc_settle
    status_desc = {
        first_valid = {
''' + statuses + '''
        }
    }
}
'''
    for lang, entries in translations.items():
        result[f"mod/localization/{lang}/mc_contract_l_{lang}.yml"] = "\ufeffl_" + lang + ":\n" + "\n".join(f' {key}:0 "{value}"' for key, value in entries.items()) + "\n"
    return result


if __name__ == "__main__":
    for name, content in outputs().items():
        path = ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print("Generated six contract choices, journal and bilingual localization.")
