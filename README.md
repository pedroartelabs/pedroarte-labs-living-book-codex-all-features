# PEDRO\_ARTE\_LIVING\_BOOK\_ENGINE\_v1

Motor editorial multiagente, orientado a DAG, para produção de **LIVROS VIVOS**.

## Ideia central

O motor é genérico. Cada obra entra como um `BOOK\\\\\\\\\\\\\\\_PACKAGE` plugável.

```text
engine/                         motor reutilizável
books/<book-slug>/              DNA literário da obra
runtime/<book-slug>/            ambiente composto e executável
```

O motor conhece abstrações como:

* canon;
* regras imutáveis;
* ondas de escrita;
* gates;
* cenas protegidas;
* agentes especialistas;
* revisão;
* merge;
* integração;
* identidade facial;
* imagem por capítulo;
* LIVING SOUND;
* tradução;
* KDP;
* entrega.

O motor **não conhece Mateus, Bento, contadores, café ou Esperança Especulativa**. Esses conceitos pertencem ao primeiro pacote de livro incluído no repositório.

## Primeiro livro plugável

`books/antes-que-as-criancas-crescam/`

## Uso rápido

```bash
python -m pip install -r requirements.txt
python engine/scripts/livingbook.py validate-engine
python engine/scripts/livingbook.py validate-book --book books/antes-que-as-criancas-crescam
python engine/scripts/livingbook.py compose --book books/antes-que-as-criancas-crescam
python engine/scripts/livingbook.py smoke-test --runtime runtime/antes-que-as-criancas-crescam
python engine/scripts/livingbook.py ready --runtime runtime/antes-que-as-criancas-crescam
```

Depois, abra o repositório no Codex e entregue o conteúdo de `CODEX\\\\\\\\\\\\\\\_ENGINE\\\\\\\\\\\\\\\_BOOTSTRAP\\\\\\\\\\\\\\\_PROMPT.md`.

## Criando um livro novo

```bash
python engine/scripts/livingbook.py new-book \\\\\\\\\\\\\\\\
  --slug meu-novo-livro \\\\\\\\\\\\\\\\
  --title "Meu Novo Livro" \\\\\\\\\\\\\\\\
  --chapters 24
```

Preencha o pacote criado em `books/meu-novo-livro/`:

1. `CREATIVE\\\\\\\\\\\\\\\_BRIEF.md`
2. `BOOK\\\\\\\\\\\\\\\_SPEC.yaml`
3. `chapter\\\\\\\\\\\\\\\_architecture.yaml`
4. `immutable\\\\\\\\\\\\\\\_rules.yaml`
5. `protected\\\\\\\\\\\\\\\_scenes.yaml`
6. `quality\\\\\\\\\\\\\\\_profile.yaml`
7. agentes específicos em `agents/\\\\\\\\\\\\\\\*.toml`

O motor cuida da fábrica. O pacote define a criatura.



