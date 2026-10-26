# Interface evidence

Checked on 2026-10-26. Versioned generated engine documentation is primary interface output hosted by community maintainers; it is not an engine execution test.

- [1.13.11 effects](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/1.13.11/docs/effects.log)
- [1.14.5-openbeta effects](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/1.14.5-openbeta/docs/effects.log)
- [1.13.11 triggers](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/1.13.11/docs/triggers.log)
- [1.14.5-openbeta triggers](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/1.14.5-openbeta/docs/triggers.log)
- [Shared journal-entry guidance](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/journal_entries.md): auto-activation, immediate, weekly pulse, scripted buttons, triggered status text.
- [Shared scripted-button guidance](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/scripted_buttons.md): visible, possible, country-scoped effects, AI weight.
- [Shared script-value guidance](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/script_values.md): formulas, conditional arithmetic and scope chains.

Machine-readable signature findings are in `evidence/bindings.json`. The shipped scripts use documented variable effects, numeric comparisons, treasury effects and nested script values. Journal/UI guidance is shared, not independently version-certified. Runtime visibility, scope propagation, localization functions and pulse execution remain unverified.

The military investigation rejected two unsafe assumptions: `transfer_to_formation` transfers a character, not an army; `destroy_container` destroys a script container, not a formation. See `MILITARY_BACKEND.md`.
