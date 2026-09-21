# Aprovação humana — Canon Freeze 0001 (SEM ROSTO / Redmur)

**Sujeito:** `books/sem-rosto/canon/sources/REDMUR_CANON_RESOLUTION_DOSSIER_FINAL.md`
**SDD:** `docs/sdd/SEM_ROSTO_CANONICAL_STORY_SYSTEM_SDD_v0.1.md` (OQ-SR-01)
**Aprovador:** Pedro, por instrução explícita em sessão ("01-sim").
**Decidido e registrado em:** 2026-09-21

subject_sha256: 7be721624539c6e1c9d5db983e4d643feea4fba77a6a59e0426645ed72cfbf86

## Decisão

`REDMUR_CANON_RESOLUTION_DOSSIER_FINAL = CANON_SOURCE_OF_TRUTH` (dossiê §27).

A partir deste registro:

- P0–P14 permanecem `CANON_APPROVED`; R1–R11 permanecem `CANON_PATCH_APPROVED`;
- `CANON_UNKNOWN` permanece desconhecido; `RESERVED` permanece reservado;
- nenhuma instância narrativa nasce apenas de capacidade sistêmica;
- mudanças futuras exigem Canon Proposal / Patch explícito (R12+), por decisão humana;
- o arquivo pinado não é editado: correção = nova fonte com `supersedes`.

O motor nunca escreve nem altera este arquivo. Se o sha256 do sujeito mudar,
o validador reporta `SOURCE_HASH_MISMATCH` (BLOCKER).
