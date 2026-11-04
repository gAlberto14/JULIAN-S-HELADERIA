-- Majö Helado Yogurt · esquema Supabase
-- Pégalo en Supabase > SQL Editor > Run

create table public.profiles (
  id uuid primary key references auth.users on delete cascade,
  name text,
  role text not null default 'mesero' check (role in ('admin','mesero'))
);

create table public.products (
  id bigint generated always as identity primary key,
  name text not null,
  cat text not null default 'General',
  price numeric not null check (price >= 0),
  active boolean not null default true
);

create table public.sales (
  id bigint generated always as identity primary key,
  sale_date date not null default current_date,
  sale_time text,
  items jsonb not null,
  total numeric not null check (total >= 0),
  pay text not null,
  by_name text,
  by_id uuid default auth.uid() references auth.users
);

create table public.expenses (
  id bigint generated always as identity primary key,
  exp_date date not null default current_date,
  concept text not null,
  amount numeric not null check (amount > 0)
);

-- Función para saber si el usuario es admin
create function public.is_admin() returns boolean
language sql security definer set search_path = public stable as $$
  select exists (select 1 from profiles where id = auth.uid() and role = 'admin')
$$;

-- Al crear un usuario se crea su perfil como mesero
create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into profiles (id, name)
  values (new.id, coalesce(new.raw_user_meta_data->>'name', split_part(new.email,'@',1)));
  return new;
end $$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- Seguridad por filas (RLS)
alter table profiles enable row level security;
alter table products enable row level security;
alter table sales enable row level security;
alter table expenses enable row level security;

create policy "perfil propio o admin" on profiles for select using (id = auth.uid() or is_admin());

create policy "productos: público ve activos" on products for select using (active or is_admin());
create policy "productos: admin inserta" on products for insert with check (is_admin());
create policy "productos: admin edita" on products for update using (is_admin());
create policy "productos: admin borra" on products for delete using (is_admin());

create policy "ventas: personal registra" on sales for insert to authenticated with check (by_id = auth.uid());
create policy "ventas: ve las suyas o admin todas" on sales for select to authenticated using (by_id = auth.uid() or is_admin());

create policy "gastos: solo admin" on expenses for all to authenticated using (is_admin()) with check (is_admin());

-- Productos de ejemplo
insert into products (name, cat, price) values
 ('Helado de yogurt natural','Helados',6000),
 ('Yogurt combinado con frutas','Helados',9000),
 ('Maxi cono','Conos',8500),
 ('Copa con kiwi y cerezas','Copas',11000),
 ('Topping extra','Extras',2000);

-- Después de crear tu usuario en Authentication > Users, hazlo admin:
-- update public.profiles set role = 'admin' where id = (select id from auth.users where email = 'TU_CORREO');
