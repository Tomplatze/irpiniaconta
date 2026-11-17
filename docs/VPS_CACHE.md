# VPS public response cache

When `NUXT_PUBLICATION_MODE=database` and `NUXT_PUBLIC_RESPONSE_CACHE_ENABLED=true`,
each Nitro process caches anonymous successful responses from the explicit public
API allowlist for at most 30 days. Requests with cookies or authorization bypass
the cache. The complete query string forms part of the key. Errors and responses
setting cookies are excluded. Entries are limited to 4 MiB each, 256 entries and
64 MiB of response bodies per process, with least-recently-used eviction.

The cache is volatile and independent per process. After a successful data
publication, restart every application instance to invalidate both this cache
and the existing territory cache. Verify a fresh `MISS` followed by a `HIT` on
a public API endpoint, and compare its response with the newly published data.
Restarting before the database transaction commits can repopulate old content.
Do not enable this cache until the restart step is part of the publication
procedure. `X-Public-Cache` reports `MISS` or `HIT` for eligible responses.
The Netlify CDN policy remains separate and applies to the Netlify deployment.
