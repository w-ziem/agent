CREATE SCHEMA IF NOT EXISTS platform;

CREATE TABLE platform.documents (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source       text        NOT NULL,
    path         text        NOT NULL,
    content_hash text        NOT NULL,
    subject      text,
    doc_type     text,
    year         integer,
    status       text        NOT NULL DEFAULT 'PENDING',
    chunks       integer     NOT NULL DEFAULT 0,
    last_error   text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_documents_source_path UNIQUE (source, path),
    CONSTRAINT ck_documents_status CHECK (status IN ('PENDING', 'INGESTED', 'FAILED'))
);

CREATE TABLE platform.jobs (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    type         text        NOT NULL,
    payload      jsonb       NOT NULL DEFAULT '{}'::jsonb,
    status       text        NOT NULL DEFAULT 'READY',
    attempts     integer     NOT NULL DEFAULT 0,
    max_attempts integer     NOT NULL DEFAULT 5,
    run_after    timestamptz NOT NULL DEFAULT now(),
    locked_at    timestamptz,
    locked_by    text,
    last_error   text,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_jobs_status CHECK (status IN ('READY', 'RUNNING', 'DONE', 'FAILED'))
);

-- pobieranie gotowych jobów: WHERE status = 'READY' AND run_after <= now() ORDER BY run_after
CREATE INDEX idx_jobs_ready ON platform.jobs (run_after) WHERE status = 'READY';
