# Tasks, failures and reliability record

| Item | Finding or failure condition | Resolution / evidence |
|---|---|---|
| Dataset dictionary encoding | UTF-8 decoding failed on the source square-kilometre symbol | Read publisher dictionary with cp1252; preserve original bytes |
| Jupyter transport | Build environment denied TCP and IPC kernel sockets | Execute unchanged cells through in-process IPython; capture actual text and rich outputs |
| Missing/invalid input | Wrong schema, invalid area/percentage, empty data or unknown district would make results meaningless | Explicit validation and clear exceptions; tests and CLI checks |
| Repeated district-year keys | Would duplicate examples and distort joins | Reject duplicates before feature creation |
| Missing intervening year | A simple shift could mislabel a two-year gap | Exact year-minus-one merge; dedicated gap test |
| Target leakage | Same-year area and spatial fields derive from the outcome | Feature whitelist, chronological split, pipeline preprocessing and mutation test |
| Weak final generalisation | Forest R² is negative; median has better MAE | Preserve the result and do not retune on final test data |
| Team and Git evidence | Two members, no repository supplied | Mark unresolved; no fabricated history |

These are engineering observations and deliberate failure-condition tests. Mutated test inputs are temporary test fixtures; they are not part of the training data. Runtime timings vary. Data checksums and deterministic model settings support repeatability, not proof of operational validity.
