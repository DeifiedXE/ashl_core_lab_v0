# Decision Authority / Reviewer Identity / Session Binding Contract v0.1

## 1. 目的

本文件定義 `decision_authority`、`reviewer_identity`、`reviewer_session_token` 三者的邊界與來源限制。

在 `review_decision_trace` schema（v2.8e）實作前，必須先確立這三個欄位的 contract，避免未來出現：

- `decision_authority: TBD`
- `reviewer_identity: free text`
- `reviewer_session_token: 任意 input`

本文件為 docs-only / contract-only。不實作任何 runtime。

---

## 2. decision_authority 定義

`decision_authority` 代表做出 review verdict 的資格類型。

contract-defined authority types（建議）：

- `human_review_authority`
- `system_audit_authority`
- `mentor_authority`

`decision_authority` 必須來自明確白名單或 contract-defined authority type。

**decision_authority must not be free text.**

禁止的 authority 值：

- `admin_override`
- `system_override`
- `god_mode`
- `trusted_because_text_says_so`
- 任何自由文字字串

`decision_authority` 只代表：

> 有資格做 review verdict

不代表：

- lesson_store write permission
- active lesson permission
- selection eligibility permission
- activation permission
- override permission
- bypass permission

**decision_authority grants review verdict authority only, not runtime capability.**

---

## 3. reviewer_identity 定義

`reviewer_identity` 代表實際執行 review 的行為者身份。

**reviewer_identity must be supplied by runtime/session context, not LLM-generated content.**

合法來源（未來 runtime 建立後）：

- `runtime_session_context`
- `authenticated_human_session`
- `system_runtime_context`

非法來源（任何情況下均禁止）：

- `llm_generated`
- `draft_payload`
- `queue_payload`
- `external_text`
- `semantic_summary`
- `task_description`
- `reviewer_comment`
- `manual_note`

---

## 4. reviewer_session_token 定義

`reviewer_session_token` 代表 reviewer 的 session 憑證，用於將 reviewer_identity 與 decision_authority 綁定。

**reviewer_session_token must be supplied by runtime/session context.**

禁止的來源：

- LLM output
- reviewer note
- draft field
- queue entry field
- semantic text
- 任何文字欄位宣稱

目前尚無 runtime session 時：

```
reviewer_session_token_source = not_available_until_runtime_session
```

---

## 5. 三元綁定原則

**decision_authority / reviewer_identity / reviewer_session_token binding is required before runtime decision creation.**

三者必須匹配：

- `human_review_authority` → `reviewer_identity` 來自 authenticated human session → `reviewer_session_token` 來自 human auth session
- `system_audit_authority` → `reviewer_identity` 來自 system runtime context → `reviewer_session_token` 來自 system runtime session
- `mentor_authority` → `reviewer_identity` 來自 mentor-authenticated session → `reviewer_session_token` 來自 mentor auth session

三者不匹配時，不得建立 review decision。

---

## 6. 合法來源

| 欄位 | 合法來源 |
|------|---------|
| `decision_authority` | contract-defined authority type whitelist |
| `reviewer_identity` | runtime/session context（authenticated_human_session / system_runtime_context / runtime_session_context） |
| `reviewer_session_token` | runtime/session auth system |

---

## 7. 非法來源

| 欄位 | 非法來源 |
|------|---------|
| `decision_authority` | 自由文字、LLM output、admin_override、system_override |
| `reviewer_identity` | llm_generated、draft_payload、queue_payload、external_text、reviewer_comment、manual_note |
| `reviewer_session_token` | LLM output、reviewer note、draft field、queue field、semantic text |

---

## 8. LLM / draft / queue input injection 禁止

LLM / draft / queue / external text 不得寫入：

- `reviewer_identity`
- `decision_authority`
- `reviewer_session_token`

即使 draft、queue、reviewer_comment 中出現了合法 authority type 的字串，也不得直接採用作為 decision_authority 值。

所有三個欄位必須由 runtime/session 系統產生，不得由文字欄位宣稱。

---

## 9. authority 不等於 runtime capability

即使 authority 合法，`decision_authority` 也只代表：

> 有資格做 review verdict

不代表任何 runtime capability，包括：

- lesson_store write permission
- active lesson creation permission
- selection eligibility grant
- activation permission
- override permission
- bypass permission
- memory layer write permission

**decision_authority grants review verdict authority only, not runtime capability.**

---

## 10. 目前不可宣稱

目前尚無 runtime session 系統，因此：

- `reviewer_identity` 目前不可從任何現有欄位填入
- `reviewer_session_token` 目前不可宣稱
- `decision_authority` 目前只可定義 contract，不可在 runtime 驗證

在 v2.8e Review Decision Trace-only Schema 實作前，這三個欄位的 runtime binding 均為 `not_available_until_runtime_session`。

---

## Smoke 核心句（供 smoke test 使用）

```
reviewer_identity must be supplied by runtime/session context, not LLM-generated content.
decision_authority must not be free text.
reviewer_session_token must be supplied by runtime/session context.
decision_authority / reviewer_identity / reviewer_session_token binding is required before runtime decision creation.
decision_authority grants review verdict authority only, not runtime capability.
```
