# Component Design

* [Formula language (SFL)](language.md) - The grammar, the semantics, the compile pipeline ($col rewriting, implicit return, lazy arguments) and the interpreter of the sheetbase formula language, a Grist-compatible Python-expression subset.
* [Formula migration from Grist](migration.md) - How each formula in an opened .grist document is classified (compiles in SFL, valid Python both ways, Python only), what the user sees, how conversion works, and the measurement that decides whether the optional Python feature is ever needed.
* [Formula sandbox](sandbox.md) - Formula code is untrusted; the interpreter has no host access by construction, and every resource it can consume is bounded with a named error on overflow.

# Overview

* [About the formula section](_about.md) - SFL, the sheetbase formula language: grammar and semantics, the function library, the sandbox, and migration of Grist Python formulas.

# Reference

* [Function library](functions.md) - Every function Grist's functions/ package exposes, grouped as Grist groups them, with where the sheetbase implementation comes from (harvested from gridcraft-functions, new, or not in v1) and the Grist-specific argument conventions kept.
