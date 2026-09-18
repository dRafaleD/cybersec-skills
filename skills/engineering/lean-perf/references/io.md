# I/O

| Class | Flag when | Fix |
|-------|-----------|-----|
| N+1 | Query/await inside `for` over a list | One query / `IN` / dataloader |
| SELECT * | Wide row on a hot path | Named columns |
| Unbounded | `find()` without limit/page | Cursor or page size |
| Sync I/O | `readFileSync` / `open().read()` on a request | Async or preload |
| Chatty | Per-item HTTP in a loop | Batch API |

Measure later if they have APM. First make the obvious loop cheaper.
