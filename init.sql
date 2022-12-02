create table public.user
(
    id serial primary key,
    username varchar(255) not null unique,
    email varchar(255) not null unique,
    fio varchar(255),
    password varchar(255) not null,
    created_at date,
    tg varchar(255),
    vk varchar(255),
    phone varchar(255)
);

create table public.group_journal
(
    id serial primary key,
    name varchar(255) not null,
    edu varchar(255) not null,
    owner_id int references public.user(id)
);

create table public.administrator_list
(
    id serial primary key,
    group_journal_id int references public.group_journal(id),
    user_id int references public.user(id)
);

create table public.student
(
    id serial primary key,
    name varchar(255),
    subscribed_tg varchar(255),
    subscribed_vk varchar(255),
    journal_id int references public.group_journal(id)
);

-- create table public.group_journal_members
-- (
--     id serial primary key,
--     group_journal_id int references public.group_journal(id),
--     student_id int references public.student(id)
-- );

create table public.discipline
(
    id serial primary key,
    name varchar(255)
);

create table public.group_journal_disciplines
(
    id serial primary key,
    group_journal_id int references public.group_journal(id),
    discipline_id int references public.discipline(id)
);


-- Фиерия всей комедии
create table public.group_journal_state
(
    id serial primary key,
    group_journal_id int references public.group_journal(id),
    student_id int references public.student(id),
    discipline_id int references public.discipline(id),
    state int,
    date_day date,
    record_sum int unique
);
