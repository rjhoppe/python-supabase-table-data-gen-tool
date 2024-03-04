drop table if exists public.rules;

create table
  public.rules (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    rule_id text null,
    police_dpt text null,
    client_code bigint null,
    created_by text null,
    last_date_modified timestamp with time zone not null default now(),
    last_modified_by text null,
    delay text null,
    status text null,
    if_logic text null,
    then_logic text null,
    constraint rules_pkey primary key (id)
  ) tablespace pg_default;