create table produtos (
  id bigint generated always as identity primary key,
  nome text not null,
  categoria text not null,
  preco numeric(10,2) not null,
  estoque int not null default 0,
  created_at timestamptz default now()
);

alter table produtos disable row level security;

insert into produtos (nome, categoria, preco, estoque) values
('Notebook Dell', 'Eletrônicos', 3499.90, 10),
('Fone Bluetooth', 'Eletrônicos', 199.90, 40),
('Clean Code', 'Livros', 89.90, 25),
('Camiseta Preta', 'Roupas', 59.90, 100),
('Luminária de Mesa', 'Casa', 79.90, 30);
