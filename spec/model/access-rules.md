---
type: Component Design
title: Access rules
description: "Grist's ACL model implemented in the engine: resources, rules, the permissions grammar, the predicate grammar and its parsed form, user attributes, the default rule set, the SPECIAL table, and where each check runs."
tags: [model, acl, security]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-aclrules
    resource: https://github.com/gristlabs/grist-core/blob/main/app/common/ACLRuleCollection.ts
    title: ACLRuleCollection.ts (DEFAULT_RULE_SET, SPECIAL_RULES, ruleSet handling)
  - id: grist-granular
    resource: https://github.com/gristlabs/grist-core/blob/main/app/server/lib/GranularAccess.ts
    title: GranularAccess.ts (checkUserActions, canApplyBundle, filterOutgoingDocActions, censoring)
  - id: grist-acl-help
    resource: https://support.getgrist.com/access-rules/
    title: Grist help, access rules
---

# Data

`_grist_ACLResources(tableId, colIds)`: `tableId = '*'` means all tables, `colIds = '*'` means
all columns, else a comma-separated list. Row id 1 with empty `tableId`/`colIds` is a legacy
placeholder and is ignored. `_grist_ACLRules(resource, aclFormula, aclFormulaParsed,
permissionsText, rulePos, userAttributes, memo)` ordered by `rulePos` within a resource.

# Permissions grammar

`permissionsText := [ '+' bits ] [ '-' bits ] | 'all' | 'none' | ''`, `bits ⊂ {C, R, U, D, S}`.
Column rules may only mention `R` and `U`; table rules `C R U D`; `S` only on `*SPECIAL:SchemaEdit`.

```rust
#[derive(Copy, Clone, Default)] pub struct PermissionSet { pub allow: Bits, pub deny: Bits }  // Bits = u8 flags CRUDS
pub fn parse_permissions(s: &str) -> Result<PermissionSet, AclParseError>;
```

Evaluation: rules in order; the first rule whose predicate is true decides each bit it
mentions; bits not mentioned fall through; an unmentioned bit after the last rule is denied
(`mixed` in Grist's terms is treated as "ask per row").

# Predicate grammar

```
pred     := or
or       := and ('or' and)*
and      := not ('and' not)*
not      := 'not' not | cmp
cmp      := arith (('==' | '!=' | '<' | '<=' | '>' | '>=' | 'in' | 'not' 'in' | 'is' | 'is' 'not') arith)*
arith    := term (('+' | '-') term)*
term     := factor (('*' | '/' | '%') factor)*
factor   := ('-' | '+') factor | atom trailer*
atom     := NAME | NUMBER | STRING | 'True' | 'False' | 'None' | '(' pred ')' | '[' [pred (',' pred)*] ']'
trailer  := '.' NAME
NAME     := user | rec | newRec | OWNER | EDITOR | VIEWER
```

Parsed to the same `[NODE_TYPE, ...]` JSON tree Grist stores in `aclFormulaParsed` (`And`,
`Or`, `Not`, `Eq`, `NotEq`, `Lt`, `LtE`, `Gt`, `GtE`, `In`, `NotIn`, `Is`, `IsNot`, `Add`,
`Sub`, `Mult`, `Div`, `Mod`, `Attr`, `Name`, `Const`, `List`), so a document saved by sheetbase
has a parse tree Grist's `compilePredicateFormula` accepts. An empty formula or `True` is the
default rule and must be last. Attribute access on a missing attribute yields `None` (not an
error), as in Grist.

```rust
pub struct Predicate { tree: PredNode }
pub struct AclInput<'a> { pub user: &'a User, pub rec: Option<RowView<'a>>, pub new_rec: Option<RowView<'a>> }
impl Predicate {
    pub fn parse(src: &str) -> Result<Predicate, AclParseError>;
    pub fn to_grist_json(&self) -> serde_json::Value;
    pub fn eval(&self, input: &AclInput) -> Result<bool, AclEvalError>;   // Err only on type errors (e.g. "a" < 1), which deny
}
```

# User and attributes

```rust
pub struct User {
    pub name: SmolStr, pub email: SmolStr, pub access: Access /* Owners | Editors | Viewers | None */,
    pub user_id: i64, pub user_ref: SmolStr, pub origin: Option<SmolStr>, pub link_key: IndexMap<SmolStr, SmolStr>,
    pub session_id: SmolStr, pub share_ref: Option<RowId>, pub is_logged_in: bool,
    pub attributes: IndexMap<SmolStr, Option<RowView>>,   // user.<name> from userAttributes rules
}
```

A rule row with `userAttributes = {name, tableId, lookupColId, charId}` on the `*:*` resource
defines `user.<name>` as the first row of `tableId` where `lookupColId == user.<charId>`
(case-insensitive when `charId == Email`), or an empty record (every attribute `None`).

# Defaults and SPECIAL[^grist-aclrules]

Default rule set when a document has no rules: `user.Access in [EDITOR, OWNER]` -> `all`;
`user.Access in [VIEWER]` -> `+R`; else `none`. Enabling any rule flips `*SPECIAL:SchemaEdit`
to owners only unless the "editors may edit structure" rule exists. `*SPECIAL:AccessRules`
(who may read `_grist_ACLRules`), `*SPECIAL:FullCopies`, `*SPECIAL:SeedRule` (prepended to new
table rule sets) are honoured. Share links (`user.ShareRef`) are parsed and preserved but no
share exists in a desktop session, so those rules never fire.

# Enforcement points[^grist-granular]

| Point | What | Failure |
|---|---|---|
| `check_user_actions` | user with nuanced access (not full owner by rules) may not run `ApplyDocActions`, `ApplyUndoActions`, `Calculate`, `UpdateCurrentTime`, `RespondToRequests`, `RemoveStaleObjects`; schema actions need `S` | `ActionError::Denied { action, memo: None }` |
| per doc action | `C` on add, `D` on remove, `U` on update per row (before and after row views, `newRec`), per column for `U`; indirect (`direct = false`) actions pass | `ActionError::Denied { action, memo }` |
| rule changes in a bundle | rules recompiled against the post-bundle metadata before the data checks run | `ActionError::BadRule { rule_pos, reason }` |
| `view:section:{id}:rows` | rows without `R` pruned | none (data hidden) |
| `view:section:{id}:cells` | columns without `R` censored to `Value::Censored` | none |
| `view:page:*` | pages whose sections are all unreadable hidden; `_grist_ACLRules` readable only with `AccessRules` | none |
| undo/redo metadata | bundles with any censored content are not offered for redo to a user who cannot read everything | the item is absent from the history list |

Locked tables (`_grist_Tables.locked`) refuse data doc actions with `ActionError::TableLocked`
unless the user carries `SystemOnly.CanEditLockedTables` (never, in v1).

ACL evaluation is a precondition of the commit, not a node: changing a rule writes `model:acl`,
which the `view:*` nodes depend on, so the screen updates through the same commit.

Golden tests: `ACL-Test.grist`, `BadRules.grist`; `test_acl_formula.py`, `test_acl_renames.py`
(rules follow renames of tables and columns), `test_predicate_formula.py`.[^grist-acl-help]

[^grist-aclrules]: ACLRuleCollection.ts (DEFAULT_RULE_SET, SPECIAL_RULES, ruleSet handling)
[^grist-granular]: GranularAccess.ts (checkUserActions, canApplyBundle, filterOutgoingDocActions, censoring)
[^grist-acl-help]: Grist help, access rules
