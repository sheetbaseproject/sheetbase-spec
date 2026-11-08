# Component Design

* [Performance budgets](performance-budgets.md) - Numbers the implementation must hit, how each is measured, and the CI gate for each; engine, storage, import and UI.
* [Security model](security-model.md) - Trust boundaries of a desktop document app: untrusted files, untrusted formulas, the clipboard, imports, the headless surface; what each boundary enforces and how it is tested.
* [Testing strategy](testing.md) - Unit tests per module, proptest over the engine and the graph facade with a differential oracle, golden tests against the 118 Grist fixture documents and the ported sandbox test suites, egui_kittest UI tests with snapshots, fuzzing, and what gates a PR.

# Overview

* [About the quality section](_about.md) - Testing strategy, performance budgets with benchmark gates, the security model and the error catalogue.

# Reference

* [Error catalogue](errors.md) - Every error enum variant across the crates with its stable code, retryable flag, user message and the UI behaviour when it surfaces.
