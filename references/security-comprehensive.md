# Comprehensive Security Reference for AI-Generated Code

> **Loaded by:** swarm-orchestrator agents when security guidance is needed.
> **Sources merged:** vibe-security (primary), security-best-practices, security-threat-model
> **Core principle:** *Never trust the client.*

## Table of Contents

1. [Introduction](#introduction)
2. [The Core Principle](#the-core-principle)
3. [Security Audit Process](#security-audit-process)
4. [Secrets & Environment Variables](#secrets--environment-variables)
5. [Database Access Control](#database-access-control)
6. [Authentication & Authorization](#authentication--authorization)
7. [Rate Limiting & Abuse Prevention](#rate-limiting--abuse-prevention)
8. [Payment Security](#payment-security)
9. [Mobile Security](#mobile-security)
10. [AI / LLM Integration Security](#ai--llm-integration-security)
11. [Deployment Security](#deployment-security)
12. [Data Access & Input Validation](#data-access--input-validation)
13. [Threat Modeling](#threat-modeling)
14. [Language & Framework Guidance](#language--framework-guidance)
15. [Output Format](#output-format)
16. [Anti-Patterns](#anti-patterns)

---

## Introduction

AI coding assistants consistently get security patterns wrong, leading to real breaches, stolen API keys, drained billing accounts, and exposed user data. These issues are especially prevalent in "vibe-coded" apps — projects built rapidly with AI assistance where security fundamentals get skipped.

**Severity Classification:**

| Level | Description | Example |
|-------|-------------|---------|
| **Critical** | Immediate exploitation; data/credentials exposed | Exposed service_role key, disabled RLS |
| **High** | Significant vulnerability; attacker gain likely | Client-controlled pricing, auth bypass |
| **Medium** | Exploitable with conditions; limited impact | Missing rate limits, info leakage |
| **Low** | Defense in depth; unlikely exploitation | Verbose errors, missing headers |

## The Core Principle

**Never trust the client.** Every price, user ID, role, subscription status, feature flag, and rate limit counter must be validated or enforced server-side. If it exists only in the browser, mobile bundle, or request body, an attacker controls it. This is the root cause of most critical vulnerabilities in vibe-coded applications.

---

## Security Audit Process

Examine the codebase systematically. Load only sections relevant to technologies used; skip what doesn't apply.

| Step | Area | What to Check |
|------|------|---------------|
| 1 | **Secrets & Environment Variables** | Hardcoded keys, client-side env prefixes (`NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`), `.gitignore` |
| 2 | **Database Access Control** | Supabase RLS policies, Firebase Security Rules, Convex auth guards |
| 3 | **Authentication & Authorization** | JWT handling, middleware auth, Server Action protection, session management |
| 4 | **Rate Limiting & Abuse Prevention** | Auth endpoints, AI calls, expensive operations; tamper-proof counters |
| 5 | **Payment Security** | Client-side price manipulation, webhook signature verification |
| 6 | **Mobile Security** | Secure token storage, API key proxying, deep link validation |
| 7 | **AI / LLM Integration** | Exposed API keys, usage caps, prompt injection, output sanitization |
| 8 | **Deployment Configuration** | Debug mode, source maps, security headers, environment separation |
| 9 | **Data Access & Input Validation** | SQL injection, ORM misuse, missing input validation, mass assignment |

**Core instructions:** Report only genuine security issues. Prioritize by exploitability and impact. If you find a critical issue (exposed secrets, disabled RLS, auth bypass), **flag it immediately** — do not bury it.

---

## Secrets & Environment Variables

### Hardcoded Credentials

Never hardcode API keys, tokens, passwords, or credentials in source code. If a secret was ever committed to Git history, consider it compromised — the key must be rotated. Run `gitleaks detect` to scan for leaked secrets.

### Client-Side Environment Variable Prefixes

These prefixes inline env vars into the client bundle at build time:

| Framework | Client Prefix | Danger |
|-----------|--------------|--------|
| Next.js | `NEXT_PUBLIC_` | Inlined into browser JS |
| Vite | `VITE_` | Inlined into browser JS |
| Expo / React Native | `EXPO_PUBLIC_` | Baked into app bundle |
| Create React App | `REACT_APP_` | Inlined into browser JS |

**Belongs client-side:** Stripe publishable key, Supabase anon key, Firebase client config, public analytics IDs.

**NEVER client-side:** Supabase `service_role` key, Stripe secret key, database connection strings, third-party API secret keys, JWT signing secrets, OAuth client secrets.

### .gitignore and Detection

Ensure `.env`, `.env.local`, `.env.*.local` are in `.gitignore` before the first commit. Check that `.env.example` contains only placeholders.

**Audit searches:** `git ls-files | grep .env`; strings matching `sk_live_`, `sk_test_`, `AKIA`, `ghp_`, `glpat-`, `xoxb-`; `NEXT_PUBLIC_*` referencing "secret"/"private"/"service"/"key"; hardcoded URLs with credentials.

---

## Database Access Control

> **The #1 source of critical vulnerabilities in vibe-coded apps.** AI assistants routinely generate schemas without proper access control, leaving entire tables exposed.

### Supabase Row-Level Security (RLS)

#### Enable RLS on Every Table

Tables created via SQL Editor or migrations have RLS **disabled by default**. A table without RLS is fully readable and writable by anyone with the anon key. Run this migration to catch missed tables:

```sql
DO $$ DECLARE r RECORD;
BEGIN
FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
LOOP
EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', r.tablename);
END LOOP;
END $$;
```

#### Dangerous RLS Policies

**Never use `USING (true)` or `USING (auth.uid() IS NOT NULL)` on SELECT/UPDATE/DELETE.** Always scope to the row owner:

```sql
-- BAD: any logged-in user can read all rows
CREATE POLICY "Users can view data" ON public.documents
FOR SELECT TO authenticated USING (true);

-- GOOD: users can only read their own rows
CREATE POLICY "Users can view own data" ON public.documents
FOR SELECT TO authenticated USING ((SELECT auth.uid()) = user_id);
```

#### Missing WITH CHECK

Always include `WITH CHECK` on INSERT and UPDATE policies. Without it, a user can reassign row ownership:

```sql
-- BAD: user can UPDATE user_id to someone else's ID
CREATE POLICY "Users can update tasks" ON public.tasks
FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = user_id);

-- GOOD: WITH CHECK prevents changing user_id
CREATE POLICY "Users can update tasks" ON public.tasks
FOR UPDATE TO authenticated
USING ((SELECT auth.uid()) = user_id)
WITH CHECK ((SELECT auth.uid()) = user_id);
```

#### Sensitive Fields on User-Accessible Tables

If a `profiles` table lets users UPDATE their own row, they can set `is_admin = true`, `credits = 99999`, or `subscription_tier = 'enterprise'`.

- **Option A:** Move sensitive fields to a `private` schema table; access via `SECURITY DEFINER` functions.
- **Option B:** Use column-level privileges:
```sql
REVOKE UPDATE ON profiles FROM authenticated;
GRANT UPDATE (display_name, avatar_url) ON profiles TO authenticated;
```

#### Other Supabase Notes

- **Junction tables, audit logs, metadata tables** often lack RLS. Every table exposed via REST needs its own policies.
- **`SECURITY DEFINER` functions bypass RLS entirely.** Keep in `private` schema, set `SET search_path = ''`, validate all inputs.
- **Storage buckets need their own policies:**
```sql
CREATE POLICY "Users upload to own folder" ON storage.objects FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'avatars' AND (storage.foldername(name))[1] = (SELECT auth.uid())::TEXT);
```

### Firebase Security Rules

Never ship default rules:
```
// BAD: world-readable and writable
allow read, write: if true;

// BAD: any logged-in user can access everything
allow read, write: if request.auth != null;
```

**Field-level protection:**
```
allow update: if request.auth.uid == userId
&& request.resource.data.diff(resource.data).affectedKeys().hasOnly(['displayName', 'avatarUrl']);
```

**Subcollections are NOT secured by parent rules.** Each needs its own explicit rules. AI assistants frequently miss this.

**Data validation:**
```
allow create: if request.resource.data.displayName is string
&& request.resource.data.displayName.size() <= 50;
allow create: if request.resource.data.createdAt == request.time;
```

Use custom claims (`request.auth.token.role`) instead of querying a users document — claims can't be tampered with and don't require extra reads. Cloud Storage rules must validate `contentType`, `size`, and path ownership.

### Convex

- Every public `query`/`mutation` must call `ctx.auth.getUserIdentity()` and handle the unauthenticated case.
- Mutations must verify ownership — checking auth is not enough.
- Internal functions must use `internalQuery`/`internalMutation`/`internalAction`. Public functions are callable by anyone.

---

## Authentication & Authorization

### JWT Handling

- **Use `jwt.verify()`, never `jwt.decode()` alone.** `decode` reads the payload without checking the signature.
- **Explicitly reject `"alg": "none"`.** Some libraries accept unsigned tokens.
- **Validate issuer, audience, and expiration** — not just the signature.

```typescript
// BAD: reads token without verifying signature
const payload = jwt.decode(token);

// GOOD: verifies signature, rejects tampered tokens
const payload = jwt.verify(token, secret, { algorithms: ['HS256'], issuer: 'your-app' });
```

### Next.js Middleware Is Not Enough

Next.js middleware is **not a reliable sole auth layer**. CVE-2025-29927 demonstrated middleware bypass via a spoofed `x-middleware-subrequest` header. Always verify auth again in Server Actions, Route Handlers, and data access functions. Middleware is a convenience layer, not the only wall.

### Server Actions Are Public Endpoints

Server Actions compile into public POST endpoints. Anyone can call them with `curl`.

```typescript
// BAD: no auth check, no input validation
'use server';
export async function deleteItem(id: string) {
await db.items.delete({ where: { id } });
}

// GOOD: validates input, authenticates, and authorizes
'use server';
export async function deleteItem(input: unknown) {
const parsed = schema.safeParse(input);
if (!parsed.success) return { error: 'Invalid input' };
const session = await auth();
if (!session?.user) redirect('/login');
await db.items.deleteMany({
where: { id: parsed.data.id, userId: session.user.id }
});
}
```

Every Server Action needs at the top: **input validation**, **authentication**, and **authorization**.

### Data Leakage and Session Storage

Never pass entire database objects to Client Components — they may contain hashed passwords, internal IDs, admin flags. Select only needed fields:

```typescript
// BAD: leaks all fields
const user = await db.users.findUnique({ where: { id } });

// GOOD: select only needed fields
const user = await db.users.findUnique({ where: { id }, select: { name: true, avatarUrl: true } });
```

Use `import 'server-only'` at the top of data access modules to prevent accidental import into Client Components.

Store tokens in `HttpOnly + Secure + SameSite=Lax` cookies, **not localStorage**. localStorage is accessible to any JavaScript — a single XSS exposes all tokens.

---

## Rate Limiting & Abuse Prevention

### Where Required

| Endpoint Type | Risk Without Limits |
|---------------|---------------------|
| Auth endpoints (login, register, password reset, OTP) | Brute-force, account enumeration |
| AI API calls | Single user drains entire monthly budget |
| Email / SMS sending | App used as spam relay |
| File processing (upload, resize, convert) | CPU-intensive DoS |
| Webhook-like endpoints | External input flood |

### Implementation Rules

- **Don't store rate limits in public tables.** Users can reset their own counters via REST API. Use Upstash Redis, private schema tables, or middleware-level limiting.
- **Combine per-IP and per-user limiting.** IP-only is defeated by VPNs; user-only by new accounts. Use both.
- **Set billing alerts** on every cloud provider. Set **hard spending caps** on AI APIs. Use per-user quotas with hard limits.
- **Monitor** for anomalous patterns (sudden spikes, odd-hour requests).

```typescript
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
redis: Redis.fromEnv(),
limiter: Ratelimit.slidingWindow(10, '1 m'),
});

export async function POST(request: Request) {
const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1';
const { success } = await ratelimit.limit(ip);
if (!success) return new Response('Too many requests', { status: 429 });
// ...
}
```

---

## Payment Security

### Never Trust Client-Submitted Prices

The #1 payment vulnerability: price comes from the client. An attacker can set any amount, including $0.

```typescript
// BAD: price from client
const session = await stripe.checkout.sessions.create({
line_items: [{ price_data: { currency: 'usd', unit_amount: req.body.price } }]
});

// GOOD: look up server-side
const product = await db.products.findUnique({ where: { id: req.body.productId } });
if (!product) return new Response('Not found', { status: 404 });
const session = await stripe.checkout.sessions.create({
line_items: [{ price: product.stripePriceId, quantity: 1 }],
});
```

Use Stripe Price IDs rather than constructing prices from your database.

### Webhook Signature Verification

Stripe webhooks require the **raw request body** — parsing as JSON destroys the signature.

```typescript
// Express: use express.raw() BEFORE express.json()
app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
const event = stripe.webhooks.constructEvent(req.body, req.headers['stripe-signature'], webhookSecret);
});

// Next.js App Router: use request.text(), NOT request.json()
export async function POST(request: Request) {
const body = await request.text();
const event = stripe.webhooks.constructEvent(body, request.headers.get('stripe-signature')!, webhookSecret);
}
```

### Subscription Status and Metadata

Check subscription status **server-side on every protected request** using your database (synced via webhooks). Don't rely on cached session values, client-side flags, or stale JWT claims.

Validate that checkout session metadata was set **server-side**, not passed from the client.

---

## Mobile Security

### No Secrets in the JavaScript Bundle

All API keys in the JS bundle are extractable — even with Hermes bytecode. The bundle is a file on the device that can be read and searched.

- `react-native-config` and `EXPO_PUBLIC_` values are baked in at build time — not secret.
- **The only safe approach: use a backend proxy** for all third-party API calls requiring secret keys.

```typescript
// BAD: API key in the mobile app
const response = await fetch('https://api.openai.com/v1/chat/completions', {
headers: { 'Authorization': `Bearer ${OPENAI_API_KEY}` }
});

// GOOD: call your backend, which holds the key
const response = await fetch('https://your-api.com/ai/chat', {
headers: { 'Authorization': `Bearer ${userSessionToken}` },
body: JSON.stringify({ message: userInput }),
});
```

### Secure Token Storage

- **Use `expo-secure-store`** (Expo) or **`react-native-keychain`** (bare RN) for auth tokens.
- **Never use `AsyncStorage`** — unencrypted plaintext on disk; trivially readable on rooted/jailbroken devices.

### Deep Link and Biometric Security

Deep links (`myapp://path?param=value`) can be triggered by any app or website. Validate and sanitize all parameters. Never include sensitive data in deep link URLs. Don't perform destructive actions from deep links without user confirmation.

A simple boolean biometric check (`isAuthenticated = true`) can be hooked with Frida on jailbroken devices. Use **cryptographic verification**: server sends a challenge, app signs with a hardware-backed key (Secure Enclave/Strongbox), server verifies the signature.

---

## AI / LLM Integration Security

### API Keys Are Server-Side Only

AI API keys must never appear in client-side code. A leaked key can drain thousands of dollars in minutes. No `NEXT_PUBLIC_OPENAI_API_KEY`, no keys in RN/Expo bundles, no keys in client JS. All AI calls go through your backend.

### Spending Caps and Per-User Limits

- Set hard spending caps on every AI provider (OpenAI dashboard, Anthropic console, Google Cloud).
- Track token usage per user in your database; set daily/monthly caps.
- Don't rely on the AI provider's caps alone — they may have lag.

### Prompt Injection and Output Handling

Never concatenate raw user input into system prompts:

```typescript
// BAD: user can override system instructions
const prompt = `You are a helpful assistant. User says: ${userInput}`;

// BETTER: separate system and user messages
const messages = [
{ role: 'system', content: 'You are a helpful assistant.' },
{ role: 'user', content: userInput },
];
```

Treat LLM responses as untrusted user input:
- Sanitize before rendering as HTML — can contain script tags
- Never execute LLM output as code without sandboxing
- Validate tool/function call parameters against an allowlist/schema before executing

If giving an LLM access to tools: restrict to a safe allowlist, use least-privilege access (read-only where possible), log all invocations, never let the LLM construct raw SQL or shell commands.

---

## Deployment Security

### Production Configuration

- **Disable debug mode** — leaks stack traces, env vars, internal paths.
- **Disable source maps** — exposes entire source code via DevTools.
- **Verify `.git` directory is not accessible** — if `/.git/HEAD` returns content, your entire source and commit history (including any secrets ever committed) are exposed.

### Environment Separation

| Environment | Purpose |
|-------------|---------|
| Production | Live users, real keys |
| Preview | PR previews, use test/staging keys only |
| Development | Local dev, local/test keys |

Preview deployments should **never** use production API keys, database credentials, or payment keys.

### Security Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

Start restrictive and loosen as needed.

### Pre-Ship Checks

Before deploying: run `gitleaks detect`; verify `.env` in `.gitignore`; confirm debug mode disabled; check error pages don't leak stack traces; verify CORS allows only your domains, not `*`. Never use `Access-Control-Allow-Origin: *` on authenticated endpoints. Be careful with `Access-Control-Allow-Credentials: true` — pair with specific origins, not wildcards.

---

## Data Access & Input Validation

### SQL Injection

Always use parameterized queries. Never concatenate user input into SQL:

```typescript
// BAD
const result = await db.query(`SELECT * FROM users WHERE id = '${userId}'`);

// GOOD
const result = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

### ORM Safety (Prisma)

**Validate input with Zod before passing to Prisma.** `findFirst` is vulnerable to operator injection — an attacker can send `{ "email": { "contains": "" } }` to match all records.

```typescript
// BAD: raw body to Prisma
const user = await prisma.user.findFirst({ where: req.body });

// GOOD: validate first
const schema = z.object({ email: z.string().email() });
const parsed = schema.parse(req.body);
const user = await prisma.user.findFirst({ where: { email: parsed.email } });
```

**Never use `$queryRawUnsafe` or `$executeRawUnsafe` with user input:**

```typescript
// BAD
const results = await prisma.$queryRawUnsafe(`SELECT * FROM users WHERE name = '${name}'`);

// GOOD: use safe raw query with parameters
const results = await prisma.$queryRaw`SELECT * FROM users WHERE name = ${name}`;
```

### Input Validation and Mass Assignment

Validate all external input at system boundaries using a runtime schema validator (Zod, Yup, Joi). **Don't rely on TypeScript types alone** — they're compile-time only; an attacker bypasses all TypeScript checks with a malformed request.

Don't spread request bodies into database operations:

```typescript
// BAD: attacker can add { isAdmin: true, credits: 99999 }
await db.users.update({ where: { id }, data: req.body });

// GOOD: pick only allowed fields
const { name, email } = validated.data;
await db.users.update({ where: { id }, data: { name, email } });
```

---

## Threat Modeling

Deliver an actionable AppSec-grade threat model specific to the repository. Anchor every claim to evidence; prioritize realistic attacker goals over generic checklists.

### Workflow

| Step | Activity |
|------|----------|
| 1 | **Scope** — Identify components, data stores, integrations, entrypoints; separate runtime from CI/build/dev |
| 2 | **Boundaries & assets** — Enumerate trust boundaries with protocol/auth/encryption/validation; list risk-driving assets |
| 3 | **Attacker capabilities** — Realistic capabilities based on exposure; note non-capabilities |
| 4 | **Enumerate threats** — Map to goals: exfiltration, privilege escalation, integrity compromise, DoS |
| 5 | **Prioritize** — Qualitative likelihood x impact, adjusted for existing controls |
| 6 | **Validate assumptions** — Ask 1-3 targeted questions about deployment, auth, data sensitivity |
| 7 | **Recommend mitigations** — Distinguish existing from recommended; tie to concrete locations |
| 8 | **Quality check** — Confirm all entrypoints and trust boundaries covered |

### Risk Prioritization

| Priority | Examples |
|----------|----------|
| Critical | Pre-auth RCE, auth bypass, cross-tenant access, key/token theft |
| High | Targeted DoS, partial data exposure, rate-limit bypass |
| Medium | Log/metrics poisoning, issues requiring preconditions |
| Low | Low-sensitivity info leaks, noisy DoS with easy mitigation |

Keep threats small but high quality. Prefer specific implementation hints. Mark recommendations as conditional when assumptions remain unresolved.

---

## Language & Framework Guidance

### Cross-Cutting Advice

**Resource IDs:** Avoid small auto-incrementing IDs for public resources. Use UUID4 or random hex strings to prevent ID guessing and resource enumeration.

**TLS:** Important for production, but most dev work uses TLS disabled or via an out-of-scope proxy. Do not report lack of TLS as a security issue in development. "Secure" cookies only over TLS — provide an env flag to override for local dev. Avoid recommending HSTS without understanding its lasting impacts.

**Report format for framework reviews:** Markdown with executive summary; findings by severity with numeric IDs; critical findings include one-sentence impact statement and line numbers; fix one finding at a time with consideration for second-order impacts; follow existing testing flows.

### Overrides

When customers need to bypass best practices: report it, don't fight it, and suggest documenting why the override exists.

---

## Output Format

Organize findings by severity: **Critical** -> **High** -> **Medium** -> **Low**.

For each issue:
1. State the file and relevant line(s).
2. Name the vulnerability.
3. Explain concrete attacker impact (not abstract risk).
4. Show a before/after code fix.

Skip areas with no issues. End with a prioritized summary.

### Example Output

#### Critical

**`lib/supabase.ts:3` — Supabase `service_role` key exposed in client bundle**

The `service_role` key bypasses all Row-Level Security. Anyone can extract it from the browser bundle and read, modify, or delete every row.

```typescript
// Before
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_KEY!)

// After
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)
```

#### High

**`app/api/checkout/route.ts:15` — Price taken from client request body**

An attacker can set any price (including $0.01). Prices must be looked up server-side.

```typescript
// Before
const session = await stripe.checkout.sessions.create({
line_items: [{ price_data: { unit_amount: req.body.price } }]
})

// After
const product = await db.products.findUnique({ where: { id: req.body.productId } })
const session = await stripe.checkout.sessions.create({
line_items: [{ price: product.stripePriceId }]
})
```

---

## Anti-Patterns

Common security mistakes in vibe-coded apps. Watch for these and correct proactively.

| # | Anti-Pattern | Fix |
|---|-------------|-----|
| 1 | **Supabase service_role key in client** — `NEXT_PUBLIC_SUPABASE_SERVICE_KEY` | Use anon key client-side; service_role server-side only |
| 2 | **Client-controlled pricing** — `req.body.price` passed to Stripe | Look up prices server-side using Stripe Price IDs |
| 3 | **Server Actions without auth** — No auth/validation | Add input validation + authentication + authorization |
| 4 | **RLS disabled/overly permissive** — `USING (true)` | Scope to row owner: `USING (auth.uid() = user_id)` |
| 5 | **AI API keys in client bundles** — `OPENAI_API_KEY` in frontend/mobile | All AI calls through backend proxy |
| 6 | **AsyncStorage for auth tokens** — Unencrypted plaintext | Use `expo-secure-store` or `react-native-keychain` |
| 7 | **Raw request body to Prisma** — `findFirst({ where: req.body })` | Validate with Zod before passing to database |
| 8 | **Middleware as sole auth layer** — No re-verification in actions | Re-verify auth in Server Actions, Route Handlers, data access |
| 9 | **Mass assignment via spread** — `db.update({ data: req.body })` | Pick only allowed fields from validated data |
| 10 | **Webhook without signature verification** — `request.json()` before sig | Use raw body: `request.text()` for Stripe webhooks |
| 11 | **localStorage for session tokens** — XSS-exposed storage | Use `HttpOnly + Secure + SameSite=Lax` cookies |
| 12 | **Debug mode + source maps in production** — Leaks source and stacks | Disable both before deploying |

---

**Prevention is better than detection.** Before writing code that touches auth, payments, database access, API keys, or user data, consult the relevant section above to avoid introducing vulnerabilities.
