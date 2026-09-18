# Storage (defensive)

Load for buckets, queues, and metadata.

```text
rg -n "public-read|allUsers|allAuthenticatedUsers|acl.*=.*public"
rg -n "169.254.169.254|IMDSv1|http_tokens"
```

| Class | Flag when | Fix |
|-------|-----------|-----|
| Public bucket | ACL public, `allUsers`, website on a data bucket | Private; signed URLs; block public ACLs |
| Encryption | Bucket or disk without server-side encryption | CMK/managed encryption; TLS in transit |
| Logging | No access logs / versioning on important buckets | Versioning + access logs to a locked bucket |
| IMDS | Instance can hit IMDS v1 or the whole metadata tree | IMDSv2 required; hop limit 1 |
| Egress | Task role can read all S3 | Prefix + account condition |

Do not run anonymous list/get against third-party buckets.
