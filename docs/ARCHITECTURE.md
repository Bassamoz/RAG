# البنية المقصودة ومخططات المرحلة 00

مخططات تصميم فقط. تفاصيل endpoint/scopes/signature للمزود لا تُحسم قبل وثائقه واختباره. API `/api/v1` وعقد OpenAPI واحد وعميل TS مولد؛ errors آمنة بـcode/trace_id؛ UUID/Decimal/UTC/pagination وحدود أحجام/idempotency. migrations تنشأ عند الحاجة في المراحل المالكة.

## المكونات

```mermaid
flowchart LR
  Browser[Dashboard browser] --> BFF[Next.js BFF]
  BFF --> Auth[Supabase Auth]
  BFF --> API[FastAPI modular monolith]
  Widget[Visitor widget] --> API
  Meta[WhatsApp webhook] --> Inbox[Durable inbox]
  Inbox --> API
  API --> DB[(PostgreSQL RLS and pgvector)]
  API --> Storage[Private object storage]
  API --> Outbox[Durable outbox]
  Outbox --> Worker[Celery worker same codebase]
  Worker --> Redis[Redis queue and scoped cache]
  Worker --> Index[BM25 per store and version]
  Worker --> FAISS[FAISS research adapter]
  Worker --> Providers[Store and model providers]
```

حدود الوحدات: identity/tenancy توفران سياق التفويض لبقية الوحدات؛ stores/catalog/integrations تملك الحقائق التشغيلية؛ knowledge تملك النشر والمصادر؛ retrieval يقرأ المنشور؛ assistant ينسق الأدوات والتحقق؛ conversations/channels/support تملك التسليم والتحويل؛ analytics/lifecycle/operations تتعامل بعقودها دون تجاوز العزل.

## حالات الاستخدام

```mermaid
flowchart LR
  Customer[Customer] --> Ask[Ask within store]
  Ask --> Evidence[Retrieve and verify]
  Ask --> Handoff[Request human]
  Merchant[Owner or admin] --> Connect[Connect authorized store]
  Merchant --> Publish[Review and publish knowledge]
  Merchant --> Reports[Scoped reports]
  Agent[Support agent] --> Handoff
  Agent --> Ticket[Manage assigned tickets]
  Analyst[Analyst] --> Reports
  Operator[Platform admin] --> Ops[Audited operations and isolated restore]
```

## ERD أولي

```mermaid
erDiagram
  users ||--o{ memberships : joins
  tenants ||--o{ memberships : grants
  users ||--o{ sessions : opens
  tenants ||--o{ stores : owns
  tenants ||--o{ invitations : issues
  stores ||--o{ integrations : authorizes
  stores ||--o{ products : contains
  products ||--o{ variants : has
  stores ||--o{ store_policies : publishes
  stores ||--o{ knowledge_sources : owns
  knowledge_sources ||--o{ source_versions : versions
  source_versions ||--o{ knowledge_chunks : contains
  stores ||--o{ index_versions : publishes
  stores ||--o{ channels : binds
  stores ||--o{ conversations : scopes
  conversations ||--o{ messages : records
  conversations ||--o{ conversation_events : transitions
  conversations ||--o{ tickets : escalates
  tickets ||--o{ assignments : allocates
  tenants ||--o{ deletion_requests : requests
  stores ||--o{ evaluation_runs : evaluates
```

كل علاقة مملوكة تُقيد بـtenant/store عبر مفاتيح مركبة وRLS؛ الرسم لا يغني عن DDL. index manifest يربط chunk IDs وإصدار المصدر/النموذج. webhook_inbox/outbox/sync_jobs/export_jobs/audit_events/usage_events/restore_jobs جداول تشغيل تنشأ عند الحاجة. users لا يحوي password_hash محليًا.

## Email OTP

```mermaid
sequenceDiagram
  participant U as Browser
  participant B as BFF
  participant A as Supabase Auth
  participant M as Test mailbox
  U->>B: Request email OTP with abuse controls
  B->>A: Official SDK request
  A->>M: Deliver token template via SMTP
  U->>B: Submit received code
  B->>A: Verify code
  alt valid
    A-->>B: Provider session
    B->>B: Encrypt tokens and create app session
    B-->>U: HttpOnly Secure session cookie
    U->>B: Sensitive action with CSRF protection
    B->>A: Require TOTP challenge and AAL2
  else invalid or expired
    B-->>U: Safe failure without session
  end
```

## إدخال المعرفة

```mermaid
sequenceDiagram
  participant U as Authorized merchant
  participant A as API
  participant D as DB and private storage
  participant W as Worker
  U->>A: Upload or authorized URL
  A->>A: Validate ownership type size and SSRF policy
  A->>D: Quarantine and durable job
  W->>D: Claim job in store context
  W->>W: Extract normalize semantic chunk embed
  W->>D: Build immutable index version and manifest
  W-->>U: Review ready or explicit failure
  U->>A: Approve publication
  A->>D: Atomically switch published version
  Note over A,D: Deleted source denied immediately before eventual index cleanup
```

## سؤال RAG

```mermaid
sequenceDiagram
  participant C as Channel
  participant A as Assistant
  participant R as Retrieval
  participant D as Authoritative data
  participant L as LLM
  C->>A: Verified channel scope and conversation epoch
  A->>A: Intent entities ambiguity and limits
  par lexical
    A->>R: BM25 scoped published version
  and semantic
    A->>R: Cosine same embedding space
  end
  R->>R: Union dedup RRF then Cross-Encoder
  R->>D: Recheck visibility ownership and deletion
  A->>D: Read-only fresh price or stock when needed
  alt sufficient evidence
    A->>L: Bounded context and separate system policy
    L-->>A: Draft structured answer
    A->>A: Validate claims sources safety and current epoch
    A-->>C: Verified answer or safe refusal
  else insufficient or tool unavailable
    A-->>C: Clarify abstain or handoff
  end
```

## OAuth

```mermaid
sequenceDiagram
  participant U as Merchant
  participant B as Server
  participant P as Salla or Zid adapter
  participant D as DB
  U->>B: Connect authorized store
  B->>D: One-use state bound to session and tenant
  B-->>U: Provider authorization redirect
  U->>P: Provider consent
  P-->>B: Callback code and state
  B->>D: Atomically consume state and check binding
  B->>P: Server-side exchange per provider docs
  B->>D: Check store ownership and encrypt tokens
  B->>D: Enqueue initial sync through outbox
  Note over B,P: PKCE only if supported; no invented shared scopes or signatures
```

## التحويل البشري

```mermaid
sequenceDiagram
  participant C as Customer
  participant A as Conversation service
  participant W as Generation worker
  participant H as Support agent
  C->>A: Request human or guardrail failure
  A->>A: bot_active to handoff_pending
  A-->>H: Minimal context reason and identity status
  H->>A: Authorized takeover with version check
  A->>A: human_active and increment epoch
  W->>A: Generated answer with previous epoch
  A-->>W: Reject stale delivery
  H->>A: Reply without intentional delay
  A-->>C: Human response
  Note over A,H: Return to bot requires explicit authorized action
```

## ??????? ?????? ?? ??????? 01

???????? ???????: apps/web ? packages/api-client ? FastAPI health/readiness? ??????? Celery ?? apps/api/src/store_advisor ????. Alembic ???? app ???? ?Supabase local ???? ?? ????? DB/Auth/Storage ?????? ???????. ????? ??????? users/tenants/memberships/stores? ???? ERD ????? ????? ????? ?????. RLS ??????? transaction-local ?????? ??? ???????? ??? DB ??? ?? ??? ???????. ?? ???? RAG ?? ???? ?? Auth endpoint ???? ??01. ?????? ?? ?????? ??? ???? ?? ?????01.
