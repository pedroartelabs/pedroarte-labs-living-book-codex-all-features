"""Gera uma imagem editorial via API de imagem da OpenAI e entrega um JPEG
que satisfaz o contrato de `validate_media_assets.py`.

Este script é o irmão simétrico do validador: um gera, o outro confere.
Ele existe para que a geração de imagem deixe de ser uma capacidade
implícita do CLI hospedeiro (Codex, Claude Code, outro) e passe a ser
código explícito do motor — funcionando igual em qualquer host que saiba
executar Python.

CREDENCIAL: a chave é lida de `OPENAI_API_KEY` no ambiente. Ela nunca é
escrita, logada ou persistida por este script. Não coloque chave em
arquivo dentro do repositório (ver .env.example e .gitignore).

DIMENSÕES: a API de imagem não produz 1600x2560 nem 1080x1920 nativamente.
Este script gera no tamanho suportado mais próximo em proporção e depois
faz cover-fit (escala + corte centralizado, sem distorcer) até as
dimensões exatas exigidas, gravando o DPI no cabeçalho JPEG. Sem esse
pós-processamento, o artefato reprova em GATE_MEDIA_ASSETS.

Dependências: apenas Pillow (já em requirements.txt) e a biblioteca padrão.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image

API_URL = "https://api.openai.com/v1/images/generations"
# Endpoint de edição: recebe imagem(ns) de referência e devolve uma nova.
# É por aqui que a ancoragem de identidade acontece.
API_EDIT_URL = "https://api.openai.com/v1/images/edits"
ENV_VAR = "OPENAI_API_KEY"


def load_dotenv(start: Path | None = None) -> str | None:
    """Carrega variáveis de um arquivo .env, subindo os diretórios a partir de
    `start` até encontrá-lo.

    Variáveis já presentes no ambiente têm precedência — o .env preenche
    lacunas, nunca sobrescreve o que o operador definiu explicitamente na
    sessão. Implementação em biblioteca padrão de propósito: o motor não
    adiciona dependência só para ler um arquivo de chave=valor.

    Retorna o caminho do .env usado (como str) ou None se nenhum foi achado.
    """
    here = (start or Path(__file__).resolve().parent)
    for directory in [here, *here.parents]:
        candidate = directory / ".env"
        if not candidate.is_file():
            continue
        for raw in candidate.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value
        return str(candidate)
    return None


# O .env é lido no import para que qualquer consumidor deste módulo (inclusive
# os testes) encontre a credencial sem precisar exportá-la na mão.
load_dotenv()
DEFAULT_MODEL = os.environ.get("LIVINGBOOK_IMAGE_MODEL", "gpt-image-1")

# Tamanhos que os modelos de imagem aceitam. O script escolhe o mais
# próximo em proporção do alvo pedido e depois corrige por cover-fit.
SUPPORTED_SIZES = {
    "gpt-image-1": [(1024, 1024), (1024, 1536), (1536, 1024)],
    "dall-e-3": [(1024, 1024), (1024, 1792), (1792, 1024)],
    "dall-e-2": [(1024, 1024)],
}


def nearest_size(model: str, target_w: int, target_h: int) -> str:
    """Escolhe o tamanho suportado cuja proporção mais se aproxima do alvo."""
    candidates = SUPPORTED_SIZES.get(model) or SUPPORTED_SIZES["gpt-image-1"]
    target_ratio = target_w / target_h
    best = min(candidates, key=lambda wh: abs((wh[0] / wh[1]) - target_ratio))
    return f"{best[0]}x{best[1]}"


def cover_fit(image: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Escala preservando proporção até cobrir o alvo, depois corta o centro.
    Evita distorcer rostos, que é justamente o que FACE_QA reprovaria."""
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = round(src_w * scale), round(src_h * scale)
    resized = image.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def request_image(api_key: str, model: str, prompt: str, size: str, quality: str | None = None) -> tuple[bytes, dict]:
    payload = {"model": model, "prompt": prompt, "size": size, "n": 1}
    # dall-e-* aceita response_format; gpt-image-* já devolve b64 e rejeita o campo.
    if not model.startswith("gpt-image"):
        payload["response_format"] = "b64_json"
    # `quality` é a alavanca de custo mais direta da API de imagem: a mesma
    # dosagem que aplicamos a modelos de texto (S/M/XS) vale aqui — alta só
    # onde o artefato é comercialmente crítico (capa).
    if quality and quality != "auto":
        payload["quality"] = quality

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        hint = ""
        if "billing_hard_limit" in detail or "billing" in detail.lower():
            hint = (
                "\nCAPABILITY_BLOCKER: a credencial e valida, mas a conta atingiu o limite "
                "de faturamento. Adicione creditos ou eleve o limite de uso em "
                "platform.openai.com/settings/organization/limits. Nenhum credito foi gasto "
                "nesta tentativa."
            )
        elif exc.code == 401:
            hint = f"\nA chave em {ENV_VAR} e invalida ou foi revogada."
        elif exc.code == 429:
            hint = "\nRate limit atingido; aguarde e tente novamente."
        raise SystemExit(f"IMAGE GENERATION FAILED: HTTP {exc.code}\n{detail}{hint}")
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"IMAGE GENERATION FAILED: sem acesso a rede ({exc.reason}).\n"
            "Ambientes sandboxed sem internet nao conseguem chamar a API; "
            "emita CAPABILITY_BLOCKER em vez de fingir sucesso."
        )

    try:
        return base64.b64decode(body["data"][0]["b64_json"]), body.get("usage", {}) or {}
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"IMAGE GENERATION FAILED: resposta inesperada da API ({exc})")


MIME_BY_SUFFIX = {".png": "image/png", ".jpg": "image/jpeg",
                  ".jpeg": "image/jpeg", ".webp": "image/webp"}


def encode_multipart(fields: dict[str, str], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    """Monta um corpo multipart/form-data com biblioteca padrão.

    A API de edição de imagem não aceita JSON: precisa de upload de arquivo.
    Fazer isso sem `requests` custa este helper, e evita adicionar dependência
    a um motor que hoje roda com stdlib + PyYAML + Pillow + python-docx.
    """
    boundary = uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += f"{value}\r\n".encode()
    for name, path in files:
        mime = MIME_BY_SUFFIX.get(path.suffix.lower(), "application/octet-stream")
        body += f"--{boundary}\r\n".encode()
        body += (f'Content-Disposition: form-data; name="{name}"; '
                 f'filename="{path.name}"\r\n').encode()
        body += f"Content-Type: {mime}\r\n\r\n".encode()
        body += path.read_bytes()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def request_image_edit(api_key: str, model: str, prompt: str, size: str,
                       references: list[Path], mask: Path | None = None,
                       quality: str | None = None) -> tuple[bytes, dict]:
    """Gera a partir de imagem(ns) de referência.

    É este o mecanismo que resolveu a consistência facial na execução real do
    Codex: quando o rosto de uma personagem derivou entre capítulos, a correção
    não foi tentar de novo por prompt textual — foi regenerar ancorando numa
    imagem já aprovada. Redescrever um rosto em palavras não converge; mostrar
    o rosto converge.

    Serve aos dois modos do CLI:
      --reference  cena nova, identidade ancorada em imagem aprovada;
      --edit       correção pontual de uma imagem existente.
    """
    for path in references:
        if not path.is_file():
            raise SystemExit(f"IMAGE EDIT FAILED: referência ausente: {path}")

    fields = {"model": model, "prompt": prompt, "size": size, "n": "1"}
    if quality and quality != "auto":
        fields["quality"] = quality

    # gpt-image-* aceita múltiplas referências em `image[]`; os modelos
    # anteriores aceitam uma única imagem em `image`.
    if model.startswith("gpt-image"):
        files = [("image[]", p) for p in references]
    else:
        files = [("image", references[0])]
        if len(references) > 1:
            print(f"AVISO: {model} aceita uma referência; usando apenas "
                  f"{references[0].name}.", file=sys.stderr)
    if mask:
        if not mask.is_file():
            raise SystemExit(f"IMAGE EDIT FAILED: máscara ausente: {mask}")
        files.append(("mask", mask))

    data, content_type = encode_multipart(fields, files)
    request = urllib.request.Request(
        API_EDIT_URL, data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": content_type},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        hint = ""
        if "billing" in detail.lower():
            hint = ("\nCAPABILITY_BLOCKER: credencial válida, mas a conta atingiu o "
                    "limite de faturamento. Nenhum crédito foi gasto nesta tentativa.")
        elif exc.code == 401:
            hint = f"\nA chave em {ENV_VAR} é inválida ou foi revogada."
        raise SystemExit(f"IMAGE EDIT FAILED: HTTP {exc.code}\n{detail}{hint}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"IMAGE EDIT FAILED: sem acesso a rede ({exc.reason}).")

    try:
        return base64.b64decode(body["data"][0]["b64_json"]), body.get("usage", {}) or {}
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit(f"IMAGE EDIT FAILED: resposta inesperada da API ({exc})")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera um JPEG editorial nas dimensoes exatas exigidas pelo motor."
    )
    parser.add_argument("--prompt", help="Prompt visual (normalmente vindo de /images/prompts/).")
    parser.add_argument("--out", type=Path, help="Caminho do JPEG de saida.")
    parser.add_argument("--width", type=int, default=1600, help="Largura final exata (padrao: capa KDP).")
    parser.add_argument("--height", type=int, default=2560, help="Altura final exata (padrao: capa KDP).")
    parser.add_argument("--dpi", type=int, default=300, help="DPI gravado no cabecalho JPEG.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Modelo de imagem (padrao: {DEFAULT_MODEL}).")
    parser.add_argument("--quality", type=int, default=95, help="Qualidade de compressao JPEG local (1-95).")
    parser.add_argument(
        "--api-quality",
        default="medium",
        choices=["low", "medium", "high", "auto"],
        help="Qualidade pedida a API: principal alavanca de CUSTO por imagem. "
             "Use 'high' so em artefato comercialmente critico (capa).",
    )
    parser.add_argument(
        "--reference", type=Path, action="append", metavar="IMG",
        help="Imagem aprovada usada como ancora de IDENTIDADE ao gerar uma cena "
             "nova. Repita a flag para varias referencias. Este e o mecanismo "
             "que faz um rosto recorrente sobreviver entre capitulos: "
             "redescrever um rosto em palavras nao converge, mostrar converge.",
    )
    parser.add_argument(
        "--edit", type=Path, metavar="IMG",
        help="Corrige pontualmente uma imagem existente em vez de regerar do "
             "zero. Mais barato e nao reintroduz problemas ja resolvidos em "
             "outras partes da imagem.",
    )
    parser.add_argument(
        "--mask", type=Path,
        help="Mascara PNG opcional: area transparente e a regiao a alterar.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verifica credencial e parametros sem chamar a API (nao gasta creditos).",
    )
    args = parser.parse_args()

    api_key = os.environ.get(ENV_VAR)
    size = nearest_size(args.model, args.width, args.height)

    references = list(args.reference or [])
    if args.edit:
        references.insert(0, args.edit)
    if args.edit and args.reference:
        print("AVISO: --edit e --reference juntos; a imagem de --edit e a base, "
              "as demais entram como referencia de identidade.", file=sys.stderr)
    mode = "EDIT" if args.edit else ("REFERENCE" if references else "GENERATE")

    if args.dry_run:
        print("DRY RUN — nenhuma chamada de API feita, nenhum credito gasto.")
        print(f"- credencial {ENV_VAR}: {'PRESENTE' if api_key else 'AUSENTE'}")
        print(f"- modo: {mode}")
        print(f"- modelo: {args.model}")
        print(f"- qualidade de API: {args.api_quality}")
        print(f"- tamanho pedido a API: {size}")
        print(f"- pos-processamento ate: {args.width}x{args.height} @ {args.dpi} DPI (cover-fit)")
        if references:
            print(f"- endpoint: {API_EDIT_URL}")
            for ref in references:
                mark = "OK " if ref.is_file() else "AUSENTE"
                print(f"  [{mark}] {ref}")
            if args.mask:
                print(f"  mascara: {args.mask} "
                      f"({'OK' if args.mask.is_file() else 'AUSENTE'})")
        else:
            print(f"- endpoint: {API_URL}")
        if not api_key:
            print(
                f"\nDefina a credencial antes de gerar. PowerShell:\n"
                f'  $env:{ENV_VAR} = "sua-chave"',
                file=sys.stderr,
            )
            return 1
        return 0

    if not api_key:
        print(
            f"CAPABILITY_BLOCKER: variavel de ambiente {ENV_VAR} nao definida.\n"
            "A geracao de imagem e uma capacidade declarada em "
            "capability_requirements.yaml. Sem credencial, pare e sinalize; "
            "nao substitua o artefato por um brief ou mockup.",
            file=sys.stderr,
        )
        return 1
    if not args.prompt or not args.out:
        print("Erro: --prompt e --out sao obrigatorios fora do --dry-run.", file=sys.stderr)
        return 2

    if references:
        raw, usage = request_image_edit(
            api_key, args.model, args.prompt, size, references,
            mask=args.mask, quality=args.api_quality,
        )
    else:
        raw, usage = request_image(api_key, args.model, args.prompt, size, args.api_quality)
    with Image.open(BytesIO(raw)) as generated:
        image = generated.convert("RGB")
        final = cover_fit(image, args.width, args.height)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        final.save(args.out, format="JPEG", quality=args.quality, dpi=(args.dpi, args.dpi))

    size_bytes = args.out.stat().st_size
    print(f"IMAGE OK | {args.out} | {args.width}x{args.height} | RGB | {args.dpi} DPI | {size_bytes} bytes")
    # Telemetria real devolvida pela API — alimenta o COST_LEDGER.
    if usage:
        print(
            f"USAGE | input_tokens={usage.get('input_tokens', 'N/D')} "
            f"output_tokens={usage.get('output_tokens', 'N/D')} "
            f"total_tokens={usage.get('total_tokens', 'N/D')} "
            f"api_quality={args.api_quality}"
        )
    print("Valide o pacote final com: python scripts/validate_media_assets.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
