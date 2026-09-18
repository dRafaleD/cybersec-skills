# Correctness

Spend the budget on behavior, not commas.

| Ask | Flag when | Fix |
|-----|-----------|-----|
| Empty/error | New path ignores failure or nil | Return/raise; test the case |
| Boundary | Off-by-one, exclusive range, timezone | One test with the edge |
| Compat | Changed signature without callers | Update callers or overload |
| Tests | Logic changed, tests not | Add the smallest failing test |
| Concurrency | Shared mutable without a lock/queue | Document or serialize |

Skip import order, naming taste, and comments that restate the code.
