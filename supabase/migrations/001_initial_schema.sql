create extension if not exists pgcrypto;

create table if not exists public.cases (
  id uuid primary key default gen_random_uuid(),
  case_id text not null unique,
  filename text not null,
  media_type text not null,
  mime_type text,
  size_bytes bigint,
  sha256 text not null,
  verdict text,
  confidence text,
  analyzed_at timestamptz not null default now(),
  result jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.media_files (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  storage_bucket text not null,
  storage_path text not null,
  original_filename text not null,
  mime_type text,
  size_bytes bigint,
  sha256 text,
  created_at timestamptz not null default now(),
  unique(case_id, storage_path)
);

create table if not exists public.analyses (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  analysis_type text not null,
  status text not null default 'completed',
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.forensic_signals (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  signal text not null,
  source text,
  score double precision,
  reliability text,
  explanation text,
  model_id text,
  created_at timestamptz not null default now()
);

create table if not exists public.detector_results (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  detector_id text not null,
  status text not null,
  label text,
  score double precision,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.evidence (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  evidence_type text not null,
  payload jsonb not null default '{}'::jsonb,
  sha256 text,
  created_at timestamptz not null default now()
);

create table if not exists public.reports (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  report_type text not null default 'json',
  report jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.removal_requests (
  id uuid primary key default gen_random_uuid(),
  case_id text not null references public.cases(case_id) on delete cascade,
  request jsonb not null,
  status text not null default 'draft',
  created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  case_id text,
  action text not null,
  actor_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.cases enable row level security;
alter table public.media_files enable row level security;
alter table public.analyses enable row level security;
alter table public.forensic_signals enable row level security;
alter table public.detector_results enable row level security;
alter table public.evidence enable row level security;
alter table public.reports enable row level security;
alter table public.removal_requests enable row level security;
alter table public.audit_logs enable row level security;

insert into storage.buckets (id, name, public)
values ('original-media', 'original-media', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('processed-media', 'processed-media', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('reports', 'reports', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('evidence-packages', 'evidence-packages', false)
on conflict (id) do nothing;
