from __future__ import annotations
import argparse, copy, fnmatch, json, re, shutil, sys, tomllib
from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO/'engine'
SUCCESS = {'APPROVED','CANON_APPROVED','FINAL'}


def load_yaml(p: Path): return yaml.safe_load(p.read_text(encoding='utf-8'))
def save_yaml(p: Path, d): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=120),encoding='utf-8')
def rel(p: Path):
    try: return str(p.relative_to(REPO))
    except Exception: return str(p)

def get_book(path: str|Path) -> Path:
    p=Path(path); return p if p.is_absolute() else REPO/p

def agent_filename(profile: str) -> str: return Path(profile).name

VALID_MODEL_TIERS = {'S', 'M', 'XS'}

# (task-id fnmatch pattern, override tier) -- applied after the per-owner
# tagging pass in build_standard_graph(). See discovery-books/
# 04-plano-desenvolvimento-custo.md, secao 6.4, para a justificativa.
TASK_TIER_OVERRIDES = [
    ('T4??_FACE_QA', 'XS'),
]

# Tarefas 100% mecanicas -> comando que as resolve sem nenhuma chamada de LLM.
# `{runtime}` vira a raiz do runtime e `{python}` vira o interpretador que
# executa o runner. Usar `python` puro aqui seria um bug: em ambiente com venv,
# o `python` do PATH e outro interpretador, sem as dependencias do motor.
TOOL_BY_TASK = {
    'T020_CANON_DIGEST': '{python} scripts/build_canon_digest.py --runtime {runtime}',
    'T703_BUILD_DOCX': '{python} scripts/build_kdp_docx.py --runtime {runtime}',
    'T801_KDP_BOOK_COVER': '{python} scripts/build_cover_and_stories.py --runtime {runtime}',
    # BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM (docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md).
    # So existem estas tarefas quando features.visual_narrative.enabled=true
    # (ver build_standard_graph); inofensivo para todo outro livro, porque
    # nenhuma tarefa deles casa com estes ids.
    'T044_VISUAL_CANON_SNAPSHOT': '{python} scripts/check_visual_canon.py --runtime {runtime} --snapshot-as PLAN',
    'T312_VISUAL_CANON_SNAPSHOT': '{python} scripts/check_visual_canon.py --runtime {runtime} --snapshot-as FREEZE',
    'T698_EDITION_PLAN': '{python} scripts/check_visual_canon.py --runtime {runtime} --edition-plan-all',
    'T707_PRINT_GEOMETRY': '{python} scripts/check_visual_canon.py --runtime {runtime} --print-geometry-all',
}
TOOL_BY_PATTERN: list[tuple[str,str]] = [
    # Snapshot do ledger causal (capability DARK_ROMANCE_CANON_ARCHITECT --
    # docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md). So existe tarefa
    # correspondente quando features.causal_ledger.enabled=true (ver
    # build_standard_graph); o padrao aqui e module-level e inofensivo para
    # todo outro livro, porque nenhuma tarefa deles casa com este glob.
    ('T*_LEDGER_SNAPSHOT', '{python} scripts/check_causal_ledger.py --runtime {runtime} --snapshot-auto'),
]

def _causal_ledger_threshold_flags(cfg: dict) -> str:
    """Traduz overrides opcionais de BOOK_SPEC.features.causal_ledger em
    flags de linha de comando. Ausentes = o script usa seus proprios
    defaults (DEFAULT_CONFIG em check_causal_ledger.py)."""
    parts=[]
    if 'min_payoff_feeds' in cfg: parts.append(f"--min-payoff-feeds {cfg['min_payoff_feeds']}")
    if 'max_monotonic_run' in cfg: parts.append(f"--max-monotonic-run {cfg['max_monotonic_run']}")
    if 'max_loop_silence' in cfg: parts.append(f"--max-loop-silence {cfg['max_loop_silence']}")
    return (' '+' '.join(parts)) if parts else ''

def validate_profiles(profile_dir: Path):
    errors=[]; count=0
    for p in sorted(profile_dir.glob('*.toml')):
        count+=1
        try: d=tomllib.loads(p.read_text(encoding='utf-8'))
        except Exception as e: errors.append(f'{p}: invalid TOML: {e}'); continue
        for k in ['name','description','developer_instructions']:
            if not d.get(k): errors.append(f'{p}: missing {k}')
        # model_tier is optional during the phased cost-tiering rollout (see
        # discovery-books/04-plano-desenvolvimento-custo.md, Fase 2): an agent
        # without it simply has no declared dosage yet. When present, it must
        # be one of the three tiers defined in MODEL_TIERS.yaml.
        tier = d.get('model_tier')
        if tier is not None and tier not in VALID_MODEL_TIERS:
            errors.append(f"{p}: invalid model_tier {tier!r} (must be one of {sorted(VALID_MODEL_TIERS)})")
    return errors,count

def load_agent_tiers(*profile_dirs: Path) -> dict[str, str]:
    """Scan agent .toml files and return {AGENT_NAME: model_tier} for those
    that declare a tier. Agents without model_tier are simply absent from the
    result — callers must not assume every agent has an entry."""
    tiers: dict[str, str] = {}
    for profile_dir in profile_dirs:
        if not profile_dir.exists():
            continue
        for p in sorted(profile_dir.glob('*.toml')):
            try:
                d = tomllib.loads(p.read_text(encoding='utf-8'))
            except Exception:
                continue
            tier = d.get('model_tier')
            if tier in VALID_MODEL_TIERS:
                tiers[d.get('name', p.stem.upper())] = tier
    return tiers

def validate_engine_data(g):
    errors=[]
    if g.get('kind')!='LivingBookEngineGraph': errors.append('ENGINE_GRAPH kind must be LivingBookEngineGraph')
    agents=g.get('spec',{}).get('agents',{})
    for name,cfg in agents.items():
        p=REPO/cfg['profile'].lstrip('/')
        if not p.exists(): errors.append(f'Agent {name}: missing profile {cfg["profile"]}')
    return errors

def validate_book_data(book: Path, s, x):
    errors=[]
    if s.get('kind')!='BookSpec': errors.append('BOOK_SPEC kind must be BookSpec')
    md=s.get('metadata',{}); sp=s.get('spec',{})
    count=md.get('chapter_count'); titles=sp.get('chapter_titles',{})
    if not sp.get('features',{}).get('media_package',{}).get('enabled'):
        errors.append('features.media_package.enabled must be true; final KDP cover and five Instagram Stories are mandatory')
    if len(titles)!=count: errors.append(f'chapter_titles={len(titles)} expected {count}')
    expected=set(range(1,count+1)); got={int(k) for k in titles}
    if got!=expected: errors.append('chapter title numbers must cover 1..chapter_count')
    waves=sp.get('writing_waves',[]); flat=[c for w in waves for c in w]
    if flat!=list(range(1,count+1)): errors.append('writing_waves must cover chapters in order exactly once')
    for req in ['immutable_rules_file','protected_scenes_file','chapter_architecture_file','quality_profile_file','capability_requirements_file']:
        if not (book/sp[req]).exists(): errors.append(f'missing {sp[req]}')
    for src in sp.get('creative_sources',[]):
        if not (book/src).exists(): errors.append(f'missing creative source {src}')
    engine_agents=set(load_yaml(ENGINE/'ENGINE_GRAPH.yaml')['spec']['agents'])
    book_agents=set(sp.get('agent_packs',{}).get('book_agents',{}))
    known=engine_agents|book_agents
    for pack, names in sp.get('agent_packs',{}).items():
        if pack=='book_agents': continue
        for name in names:
            if name not in known: errors.append(f'agent pack {pack}: unknown agent {name}')
    for name,cfg in sp.get('agent_packs',{}).get('book_agents',{}).items():
        p=(book/'agents'/Path(cfg['profile']).name) if cfg['profile'].startswith('/book/agents/') else book/cfg['profile']
        if not p.exists(): errors.append(f'book agent {name}: missing profile {p}')
    arch=load_yaml(book/sp['chapter_architecture_file'])
    if len(arch.get('chapters',[]))!=count: errors.append('chapter architecture count mismatch')
    if (sp.get('features',{}).get('images') or {}).get('illustration_slots'):
        slots=[slot for c in arch.get('chapters',[]) for slot in (c.get('illustration_slots') or [])]
        if not slots: errors.append('features.images.illustration_slots requires illustration_slots in chapter_architecture')
        invalid=[s for s in slots if not ILLUSTRATION_SLOT_RE.match(str(s))]
        if invalid: errors.append(f'illustration_slots: invalid ids {invalid} (expected IL-NN)')
        duplicated=sorted({s for s in slots if slots.count(s)>1})
        if duplicated: errors.append(f'illustration_slots: duplicated ids {duplicated}')
    # BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM (docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md).
    # OFF por padrao (le-se com .get() em build_standard_graph, ver D9/INV-VN-01).
    # O Author Visual DNA mora fora do pacote do livro (authors/<profile>/,
    # decisao OQ-1), entao precisa ser validado aqui, contra o REPOSITORIO --
    # nao existe arquivo correspondente dentro do proprio pacote a checar.
    vn = sp.get('features', {}).get('visual_narrative') or {}
    if vn.get('enabled'):
        profile = vn.get('author_profile')
        version = vn.get('author_dna_version')
        if not profile or not version:
            errors.append('features.visual_narrative.enabled requires author_profile and author_dna_version')
        else:
            dna_path = REPO/'authors'/profile/f'AUTHOR_VISUAL_DNA.v{version}.yaml'
            if not dna_path.exists():
                errors.append(f'features.visual_narrative: missing {rel(dna_path)}')
        valid_targets = {'kindle_ebook', 'kdp_paperback', 'kdp_hardcover', 'collector'}
        unknown_targets = [t for t in (vn.get('edition_targets') or []) if t not in valid_targets]
        if unknown_targets:
            errors.append(f'features.visual_narrative.edition_targets: unknown targets {unknown_targets}')
    return errors

ILLUSTRATION_SLOT_RE = re.compile(r'^IL-\d{2}$')

def illustration_slots_by_chapter(book: Path, sp: dict) -> list[tuple[int, str]]:
    """Pares (capitulo, id) na ordem de chapter_architecture.yaml. So chamado
    quando features.images.illustration_slots esta ligado."""
    arch=load_yaml(book/sp['chapter_architecture_file']) or {}
    return [(c.get('number'), slot) for c in arch.get('chapters',[]) for slot in (c.get('illustration_slots') or [])]

def task(id,phase,owner,deps=None,**kw):
    d={'id':id,'phase':phase,'owner':owner,'depends_on':deps or []}; d.update(kw); return d

def load_execution_profile(name: str|None):
    """Carrega o perfil de execucao (a 'torneira' velocidade x qualidade).

    O padrao e PREMIUM: nenhum livro existente muda de comportamento sem
    declarar spec.execution_profile explicitamente."""
    path = ENGINE/'templates/EXECUTION_PROFILES.yaml'
    if not path.exists():
        return {}, 'PREMIUM'
    data = load_yaml(path).get('spec', {})
    chosen = (name or data.get('default') or 'PREMIUM').upper()
    profiles = data.get('profiles', {})
    if chosen not in profiles:
        raise SystemExit(
            f"execution_profile desconhecido: {chosen!r}. "
            f"Disponiveis: {sorted(profiles)}")
    profile = dict(profiles[chosen])
    profile['human_checkpoints'] = (data.get('human_checkpoints') or {}).get(chosen, [])
    return profile, chosen

def rotate_pack(names, limit, index):
    """Seleciona `limit` revisores do pack, ROTACIONANDO conforme a wave.

    Truncar sempre nos mesmos deixaria parte do pack sem nunca ler o livro.
    Rotacionando, cada wave paga por menos revisores e a obra inteira ainda
    recebe a cobertura completa do pack."""
    if not names or not limit or limit >= len(names):
        return list(names or [])
    start = (index * limit) % len(names)
    doubled = list(names) + list(names)
    return doubled[start:start + limit]

def build_standard_graph(book: Path):
    e=load_yaml(ENGINE/'ENGINE_GRAPH.yaml'); s=load_yaml(book/'BOOK_SPEC.yaml'); ext=load_yaml(book/'BOOK_GRAPH.yaml')
    md=s['metadata']; sp=s['spec']; count=md['chapter_count']; packs=sp['agent_packs']
    agents=copy.deepcopy(e['spec']['agents']); agents.update(packs.get('book_agents',{}))
    rejections=e['spec']['generic_rejection_states']+sp.get('book_specific_rejection_states',[])
    tiers=load_agent_tiers(ENGINE/'agents', book/'agents')
    profile, profile_name = load_execution_profile(sp.get('execution_profile'))
    # O perfil pode desligar features inteiras (som, traducao) para um rascunho.
    for feature in profile.get('disable_features') or []:
        if feature in sp.get('features', {}):
            sp['features'][feature] = dict(sp['features'][feature])
            sp['features'][feature]['enabled'] = False
    # DARK_ROMANCE_CANON_ARCHITECT (docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md).
    # OFF por padrao: ausencia de features.causal_ledger e lida com .get(), entao
    # nenhum livro existente muda de comportamento (INV-14). Le-se do dict `sp`
    # ORIGINAL (antes do loop de disable_features acima), porque causal_ledger nao
    # e uma feature que perfis de execucao desligam.
    causal_ledger_cfg = sp.get('features', {}).get('causal_ledger') or {}
    causal_ledger_enabled = bool(causal_ledger_cfg.get('enabled'))
    # BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM (docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md).
    # Mesmo padrao do causal_ledger: OFF por padrao, lido com .get() do dict
    # ORIGINAL (antes do loop de disable_features), porque visual_narrative
    # tambem nao e uma feature que perfis de execucao desligam sozinhos.
    visual_narrative_cfg = sp.get('features', {}).get('visual_narrative') or {}
    visual_narrative_enabled = bool(visual_narrative_cfg.get('enabled'))
    vn_author_profile = visual_narrative_cfg.get('author_profile')
    vn_author_dna_version = visual_narrative_cfg.get('author_dna_version')
    vn_edition_targets = visual_narrative_cfg.get('edition_targets') or []
    tasks=[]; gates={}
    # Bootstrap
    tasks += [
      task('T000_INITIALIZE_RUNTIME','BOOTSTRAP','MASTER_ORCHESTRATOR',outputs=['/project_state/PROJECT_STATUS.yaml','/logs/ORCHESTRATION_LOG.md','/integration/MERGE_LOG.md']),
      task('T001_VALIDATE_CAPABILITIES','BOOTSTRAP','SPEC_ARCHITECT',['T000_INITIALIZE_RUNTIME'],outputs=['/project_state/CAPABILITY_STATUS.yaml']),
      task('T002_REGISTER_AGENTS','BOOTSTRAP','MASTER_ORCHESTRATOR',['T000_INITIALIZE_RUNTIME'],outputs=['/project_state/AGENT_REGISTRY.yaml'])]
    gates['GATE_BOOTSTRAP']={'blocking':True,'requires':['T000_INITIALIZE_RUNTIME','T001_VALIDATE_CAPABILITIES','T002_REGISTER_AGENTS']}
    # Canon
    tasks += [
      task('T010_MASTER_BRIEF','CANON','BRIEFING_ARCHITECT',['GATE_BOOTSTRAP'],inputs=['/book/CREATIVE_BRIEF.md','/book/BOOK_CONSTITUTION.md'],outputs=['/specs/MASTER_BRIEF.md']),
      task('T011_STORY_BIBLE','CANON','NARRATIVE_ARCHITECT',['T010_MASTER_BRIEF'],locks=['STORY_BIBLE_WRITE'],inputs=['/book/chapter_architecture.yaml'],outputs=['/specs/STORY_BIBLE.md']),
      task('T012_WORLD_RULES','CANON','WORLD_ARCHITECT',['T010_MASTER_BRIEF'],inputs=['/book/'+sp.get('world_rules_seed','')],outputs=['/specs/WORLD_RULES.md']),
      task('T013_CHARACTER_BIBLE','CANON','CHARACTER_PSYCHOLOGIST',['T011_STORY_BIBLE'],locks=['CHARACTER_BIBLE_WRITE'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':packs.get('character_support',[]),'wait_for_all':True},outputs=['/specs/CHARACTER_BIBLE.md']),
      task('T014_WORLD_BIBLE','CANON','WORLD_ARCHITECT',['T011_STORY_BIBLE','T012_WORLD_RULES'],outputs=['/specs/WORLD_BIBLE.md']),
      task('T015_SYMBOL_BIBLE','CANON','SYMBOLISM_ARCHITECT',['T011_STORY_BIBLE'],outputs=['/specs/SYMBOL_BIBLE.md']),
      task('T016_PLOT_DEPENDENCY_MAP','CANON','PLOT_ENGINEER',['T011_STORY_BIBLE','T013_CHARACTER_BIBLE','T015_SYMBOL_BIBLE'],outputs=['/specs/PLOT_DEPENDENCY_MAP.md']),
      task('T017_TIMELINE','CANON','TEMPORAL_ARCHITECT',['T011_STORY_BIBLE','T016_PLOT_DEPENDENCY_MAP'],locks=['TIMELINE_WRITE'],outputs=['/specs/TIMELINE.md']),
      task('T018_CANON_REGISTRY','CANON','CANON_GUARDIAN',['T012_WORLD_RULES','T013_CHARACTER_BIBLE','T014_WORLD_BIBLE','T015_SYMBOL_BIBLE','T016_PLOT_DEPENDENCY_MAP','T017_TIMELINE'],locks=['CANON_WRITE'],outputs=['/canon/CANON_REGISTRY.yaml']),
      task('T019_CANON_REVIEW','CANON','EXECUTIVE_EDITOR',['T018_CANON_REGISTRY'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':['CANON_GUARDIAN','GENRE_GUARDIAN','ANTI_MANIPULATION_GUARDIAN']+packs.get('canon_guardians',[]),'wait_for_all':True},outputs=['/reviews/CANON_REVIEW.md'])]
    gates['GATE_CANON']={'blocking':True,'requires':[f'T01{i}_'+x for i,x in []] + ['T010_MASTER_BRIEF','T011_STORY_BIBLE','T012_WORLD_RULES','T013_CHARACTER_BIBLE','T014_WORLD_BIBLE','T015_SYMBOL_BIBLE','T016_PLOT_DEPENDENCY_MAP','T017_TIMELINE','T018_CANON_REGISTRY','T019_CANON_REVIEW']}
    if causal_ledger_enabled:
        # Mesmo dono, mesmo lock CANON_WRITE, mesmo protocolo de CANON_PROPOSALS
        # que ja rege CANON_REGISTRY.yaml -- so um segundo arquivo de canon com
        # contrato estrito (SDD, secao E.1). T021 nao pode depender de
        # GATE_CANON (ele proprio exigido por GATE_CANON seria um ciclo);
        # depende de T018, o mesmo predecessor de T019.
        next(t for t in tasks if t['id']=='T018_CANON_REGISTRY')['outputs'].append('/canon/CAUSAL_LEDGER.yaml')
        tasks.append(task('T021_LEDGER_SNAPSHOT','CANON','CANON_GUARDIAN',['T018_CANON_REGISTRY'],
                          inputs=['/canon/CAUSAL_LEDGER.yaml'],
                          outputs=['/canon/snapshots/CAUSAL_LEDGER.WAVE_00.yaml']))
        gates['GATE_CANON']['requires'].append('T021_LEDGER_SNAPSHOT')
    # Digest de canon: destila o CANON_REGISTRY a ~11% do tamanho das biblias,
    # para as tarefas de CONFERENCIA lerem no lugar do corpo completo. E
    # deterministico (le YAML, escreve Markdown), entao roda sem LLM.
    tasks.append(task('T020_CANON_DIGEST','CANON','CANON_GUARDIAN',['GATE_CANON'],
                      inputs=['/canon/CANON_REGISTRY.yaml'],
                      outputs=['/canon/CANON_DIGEST.md']))
    # Living book
    tasks += [
      task('T030_LIVING_BOOK_BIBLE','LIVING_BOOK','EMOTIONAL_PHYSIOLOGY_ARCHITECT',['GATE_CANON'],outputs=['/living_book/LIVING_BOOK_BIBLE.md']),
      task('T031_LIVRO_BIOME','LIVING_BOOK','EMOTIONAL_PHYSIOLOGY_ARCHITECT',['GATE_CANON'],outputs=['/living_book/LIVRO_BIOME.md']),
      task('T032_READER_VITALS','LIVING_BOOK','READER_VITALS_AGENT',['GATE_CANON'],outputs=['/living_book/READER_VITALS.md']),
      task('T033_EMOTIONAL_RESPIRATION','LIVING_BOOK','EMOTIONAL_PHYSIOLOGY_ARCHITECT',['T032_READER_VITALS'],outputs=['/living_book/EMOTIONAL_RESPIRATION_MAP.md']),
      task('T034_PAGE_BIBLE','LIVING_BOOK','PAGE_BREATHING_ARCHITECT',['T032_READER_VITALS','T033_EMOTIONAL_RESPIRATION'],outputs=['/living_book/PAGE_BIBLE.md']),
      task('T035_MEMORY_MOTIF_MAP','LIVING_BOOK','SYMBOLISM_ARCHITECT',['GATE_CANON'],outputs=['/living_book/MEMORY_MOTIF_MAP.md']),
      task('T036_VISUAL_LIFE_SPEC','LIVING_BOOK','VISUAL_DIRECTOR',['GATE_CANON','T035_MEMORY_MOTIF_MAP'],inputs=['/book/visual_profile.md'],outputs=['/living_book/VISUAL_LIFE_SPEC.md']),
      task('T037_IMAGE_BIOME','LIVING_BOOK','VISUAL_DIRECTOR',['T036_VISUAL_LIFE_SPEC'],outputs=['/living_book/IMAGE_BIOME.md']),
      task('T038_FACE_CANON','LIVING_BOOK','FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT',['T013_CHARACTER_BIBLE'],locks=['FACE_CANON_WRITE'],outputs=['/images/canon/FACE_CANON.md']),
      task('T039_CHARACTER_VISUAL_BIBLE','LIVING_BOOK','FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT',['T038_FACE_CANON','T037_IMAGE_BIOME'],locks=['FACE_CANON_WRITE'],outputs=['/images/canon/CHARACTER_VISUAL_BIBLE.md']),
      task('T040_SOUND_BIOME_DRAFT','LIVING_BOOK','SOUND_BIOME_ARCHITECT',['GATE_CANON','T032_READER_VITALS'],inputs=['/book/sound_profile.md'],outputs=['/sound/SOUND_BIOME_DRAFT.md']),
      task('T041_LIVING_BOOK_REVIEW','LIVING_BOOK','EXECUTIVE_EDITOR',['T030_LIVING_BOOK_BIBLE','T031_LIVRO_BIOME','T032_READER_VITALS','T033_EMOTIONAL_RESPIRATION','T034_PAGE_BIBLE','T035_MEMORY_MOTIF_MAP','T036_VISUAL_LIFE_SPEC','T037_IMAGE_BIOME','T038_FACE_CANON','T039_CHARACTER_VISUAL_BIBLE','T040_SOUND_BIOME_DRAFT'],outputs=['/reviews/LIVING_BOOK_ARCHITECTURE_REVIEW.md'])]
    if visual_narrative_enabled:
        # BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM, pipeline DISCOVERY/DECISION/
        # CANONIZATION (SDD, secao 10.3). Fase LIVING_BOOK (nao uma fase
        # propria) para entrar automaticamente em GATE_LIVING_BOOK.requires
        # via a list comprehension logo abaixo -- mesmo truque que evita
        # apendar manualmente a cada tarefa nova, como o causal_ledger faz
        # em GATE_CANON.requires.
        author_dna_ref = f'/authors/{vn_author_profile}/AUTHOR_VISUAL_DNA.v{vn_author_dna_version}.yaml'
        t042_inputs = ['/book/visual_profile.md', '/specs/SYMBOL_BIBLE.md',
                       '/living_book/MEMORY_MOTIF_MAP.md', '/book/chapter_architecture.yaml',
                       '/book/protected_scenes.yaml', '/canon/CANON_REGISTRY.yaml', author_dna_ref]
        if causal_ledger_enabled:
            t042_inputs.append('/canon/CAUSAL_LEDGER.yaml')
        tasks += [
          task('T042_VISUAL_DISCOVERY','LIVING_BOOK','SYMBOLISM_ARCHITECT',['GATE_CANON'],
               inputs=t042_inputs, outputs=['/canon/CANON_PROPOSALS/VISUAL_CANDIDATES.yaml']),
          task('T043_VISUAL_NARRATIVE_CANON','LIVING_BOOK','VISUAL_DIRECTOR',['T042_VISUAL_DISCOVERY'],
               locks=['VISUAL_CANON_WRITE'],
               spawn={'mode':'PARALLEL_SUBAGENTS','agents':['CANON_GUARDIAN','GENRE_GUARDIAN','COMMERCIAL_EDITOR_CRITIC'],'wait_for_all':True},
               inputs=['/canon/CANON_PROPOSALS/VISUAL_CANDIDATES.yaml', author_dna_ref],
               outputs=['/canon/VISUAL_NARRATIVE_CANON.yaml']),
          task('T044_VISUAL_CANON_SNAPSHOT','LIVING_BOOK','VISUAL_DIRECTOR',['T043_VISUAL_NARRATIVE_CANON'],
               inputs=['/canon/VISUAL_NARRATIVE_CANON.yaml'],
               outputs=['/canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml']),
        ]
        # T036 passa a citar ids do canon visual (17.3/28.2 da SDD) -- muda
        # sua dependencia (T041 herda a ordem nova transitivamente; ver
        # "Risco: T041 depender de T043" no Slice 5 da SDD, coberto por
        # teste de ciclo em test_compose_regression.py).
        t036 = next(t for t in tasks if t['id']=='T036_VISUAL_LIFE_SPEC')
        t036['depends_on'] = t036['depends_on']+['T043_VISUAL_NARRATIVE_CANON']
        t036.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
        t036['parameters']={**t036.get('parameters',{}),'visual_narrative':
            'Cite ids de elements[] do canon visual (SYM-/SIG-/ART-) ao descrever a '
            'linguagem visual -- o canon e a fonte de significado, esta biblia e a fonte '
            'de prosa/exemplo.'}
    gates['GATE_LIVING_BOOK']={'blocking':True,'requires':[t['id'] for t in tasks if t['phase']=='LIVING_BOOK']}
    # briefs
    for ch in range(1,count+1):
        tasks.append(task(f'T1{ch:02d}_BRIEF_CHAPTER','CHAPTER_BRIEFS','SCENE_ARCHITECT',['GATE_LIVING_BOOK'],inputs=['/book/chapter_architecture.yaml','/specs/STORY_BIBLE.md','/specs/CHARACTER_BIBLE.md','/specs/PLOT_DEPENDENCY_MAP.md','/specs/TIMELINE.md','/living_book/READER_VITALS.md'],outputs=[f'/briefs/chapters/CHAPTER_{ch:02d}_BRIEF.md'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':['EMOTIONAL_PHYSIOLOGY_ARCHITECT','GENRE_GUARDIAN','ANTI_MANIPULATION_GUARDIAN'],'wait_for_all':True}))
    gates['GATE_CHAPTER_BRIEFS']={'blocking':True,'requires':[f'T1{ch:02d}_BRIEF_CHAPTER' for ch in range(1,count+1)]}
    if visual_narrative_enabled:
        # 28.2 da SDD: briefs de capitulo passam a citar os elementos
        # relevantes do canon visual (sigils, artefatos, progressoes
        # ancoradas naquele ponto da historia).
        for ch in range(1,count+1):
            brief = next(t for t in tasks if t['id']==f'T1{ch:02d}_BRIEF_CHAPTER')
            brief.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
            brief['parameters']={**brief.get('parameters',{}),'visual_narrative':
                'Cite os elementos (SYM-/SIG-/ART-) do canon visual relevantes a este '
                'capitulo -- sigils, artefatos e progressoes ancoradas neste ponto da '
                'historia; heat profile e camera narrativa nunca resetam um estado ja '
                'registrado (INV-04-like, ver seção 14 da SDD).'}
    # voice calibration
    # Em DRAFT ela e pulada: calibrar voz e serial por natureza (escreve,
    # revisa, reescreve, so entao o proximo capitulo) e nao vale o tempo numa
    # leitura de teste. O VOICE_REFERENCE ainda e produzido, a partir do guia
    # de estilo, para as waves nao ficarem sem referencia.
    cal=sp.get('voice_calibration_chapters',[1,2]) if profile.get('voice_calibration',True) else []
    voice_ids=[]
    for ch in cal:
        wid=f'T15{ch}A_WRITE_CHAPTER_{ch:02d}'; rid=f'T15{ch}B_REVIEW_CHAPTER_{ch:02d}'; vid=f'T15{ch}C_REVISE_CHAPTER_{ch:02d}'
        dep=['GATE_CHAPTER_BRIEFS'] if not voice_ids else [voice_ids[-1]]
        tasks.append(task(wid,'VOICE_CALIBRATION','LEAD_NOVELIST',dep,outputs=[f'/manuscript/raw/chapter_{ch:02d}.md']))
        tasks.append(task(rid,'VOICE_CALIBRATION','EXECUTIVE_EDITOR',[wid],spawn={'mode':'PARALLEL_SUBAGENTS','agents':packs.get('voice_reviewers',[]),'wait_for_all':True},outputs=[f'/reviews/chapter_{ch:02d}_voice_review.md']))
        tasks.append(task(vid,'VOICE_CALIBRATION','LEAD_NOVELIST',[rid],outputs=[f'/manuscript/approved/chapter_{ch:02d}.md']))
        voice_ids.append(vid)
    # Sem calibracao (perfil DRAFT), voice_ids fica vazio: a referencia de voz
    # passa a depender dos briefs, senao ficaria sem dependencia nenhuma e
    # viraria READY ja no bootstrap, antes de existir qualquer prosa.
    voice_ref_deps=voice_ids if voice_ids else ['GATE_CHAPTER_BRIEFS']
    tasks.append(task('T156_BUILD_VOICE_REFERENCE','VOICE_CALIBRATION','LITERARY_STYLE_GUARDIAN',voice_ref_deps,outputs=['/specs/VOICE_REFERENCE.md'],parameters=({'derive_from':'style_guide_only','reason':'calibracao pulada pelo perfil de execucao'} if not voice_ids else {})))
    tasks.append(task('T157_APPROVE_VOICE','VOICE_CALIBRATION','EXECUTIVE_EDITOR',['T156_BUILD_VOICE_REFERENCE'],outputs=['/reviews/VOICE_APPROVAL.md']))
    gates['GATE_VOICE']={'blocking':True,'requires':voice_ids+['T156_BUILD_VOICE_REFERENCE','T157_APPROVE_VOICE']}
    # waves
    prev_gate='GATE_VOICE'; calset=set(cal)
    for wi, chapters in enumerate(sp['writing_waves'],1):
        base=f'T2{wi:02d}'
        pre=f'{base}_PREFLIGHT'; wr=f'{base}_WRITE'; mg=f'{base}_MERGE'; rv=f'{base}_REVIEW'; rev=f'{base}_REVISION'; cu=f'{base}_CANON_UPDATE'; ap=f'{base}_APPROVAL'
        tasks.append(task(pre,f'WRITING_WAVE_{wi}','MASTER_ORCHESTRATOR',[prev_gate],parameters={'chapters':chapters}))
        groups=[]; remaining=[c for c in chapters if c not in calset]
        # groups of max 2, protected lead chapters isolated
        i=0
        while i<len(remaining):
            ch=remaining[i]
            if ch in sp.get('lead_novelist_owned_chapters',[]): groups.append({'agent':'LEAD_NOVELIST','chapters':[ch]}); i+=1
            else:
                grp=[ch]; i+=1
                if i<len(remaining) and remaining[i] not in sp.get('lead_novelist_owned_chapters',[]): grp.append(remaining[i]); i+=1
                groups.append({'agent':'CHAPTER_WRITER','chapters':grp})
        tasks.append(task(wr,f'WRITING_WAVE_{wi}','MASTER_ORCHESTRATOR',[pre],spawn={'mode':'PARALLEL_SUBAGENTS','jobs':groups,'shared_inputs':['/specs/VOICE_REFERENCE.md','/canon/CANON_REGISTRY.yaml'],'wait_for_all':True}))
        tasks.append(task(mg,f'WRITING_WAVE_{wi}','MERGE_COORDINATOR',[wr],locks=['MANUSCRIPT_MERGE']))
        wave_pack=rotate_pack(packs.get('wave_reviewers',[]),profile.get('wave_reviewers_limit'),wi-1)
        tasks.append(task(rv,f'WRITING_WAVE_{wi}','EXECUTIVE_EDITOR',[mg],spawn={'mode':'PARALLEL_SUBAGENTS','agents':wave_pack,'wait_for_all':True},outputs=[f'/reviews/WAVE_{wi:02d}_REVIEW.md']))
        tasks.append(task(rev,f'WRITING_WAVE_{wi}','LEAD_NOVELIST',[rv],locks=['MANUSCRIPT_FINAL_WRITE']))
        tasks.append(task(cu,f'WRITING_WAVE_{wi}','CANON_GUARDIAN',[rev],locks=['CANON_WRITE']))
        tasks.append(task(ap,f'WRITING_WAVE_{wi}','EXECUTIVE_EDITOR',[cu]))
        gid=f'GATE_WAVE_{wi}'
        gate_requires=[pre,wr,mg,rv,rev,cu,ap]
        if causal_ledger_enabled:
            # Congela o ledger logo apos o CANON_UPDATE da wave, antes de a
            # proxima comecar -- e o snapshot que V_CAUSAL_LEDGER_WAVE_{n+1}
            # usa como baseline de imutabilidade (L10/INV-10).
            snap_id=f'{base}Z_LEDGER_SNAPSHOT'
            tasks.append(task(snap_id,f'WRITING_WAVE_{wi}','CANON_GUARDIAN',[cu],
                              inputs=['/canon/CAUSAL_LEDGER.yaml'],
                              outputs=[f'/canon/snapshots/CAUSAL_LEDGER.WAVE_{wi:02d}.yaml']))
            gate_requires.append(snap_id)
        gates[gid]={'blocking':True,'requires':gate_requires}
        prev_gate=gid
    if causal_ledger_enabled:
        # DARK_ROMANCE_CANON_ARCHITECT, Slice 5 (SDD, secao C.3.1): instrui as
        # tarefas JA EXISTENTES a ler, propor e manter o ledger causal -- zero
        # agentes novos, so inputs/outputs/parameters condicionais. Mutacao
        # por referencia sobre os dicts ja presentes em `tasks`; a ordem em
        # que cada task() foi originalmente construida nao importa aqui.
        tasks_by_id={t['id']:t for t in tasks}
        ledger_template='/engine/templates/CAUSAL_LEDGER_TEMPLATE.yaml'
        def annotate(task_id,note,extra_inputs=(ledger_template,)):
            t=tasks_by_id.get(task_id)
            if t is None: return
            inputs=t.setdefault('inputs',[])
            for inp in extra_inputs:
                if inp not in inputs: inputs.append(inp)
            t['parameters']={**t.get('parameters',{}),'causal_ledger':note}
        annotate('T013_CHARACTER_BIBLE',
                 'Para personagens maiores, proponha em canon/CANON_PROPOSALS as camadas '
                 'GROUND_TRUTH, SELF_MODEL e SOCIAL_PERSONA (LAW 01), no formato do template. '
                 'CANON_GUARDIAN decide o que vira canon.')
        annotate('T016_PLOT_DEPENDENCY_MAP',
                 'Proponha eventos PLANNED (com caused_by, loops de divida narrativa e '
                 'crencas do leitor a formar) para o ledger causal, no mesmo formato.')
        annotate('T018_CANON_REGISTRY',
                 'Voce e o unico dono de canon/CAUSAL_LEDGER.yaml (mesmo lock CANON_WRITE de '
                 'CANON_REGISTRY.yaml). Promova propostas de T013/T016 a eventos e camadas '
                 'aprovados; rode scripts/check_causal_ledger.py --mode plan antes de fechar o gate.',
                 extra_inputs=(ledger_template,'/canon/CANON_PROPOSALS'))
        annotate('T032_READER_VITALS',
                 'O pulso e o gap informacional planejados aqui NAO sao canon (READER '
                 'EXPERIENCE != READER MODEL) -- alimentam as propostas de crenca do leitor que '
                 'T016/T018 registram no ledger; nunca substituem o julgamento de causalidade.',
                 extra_inputs=())
        annotate('T035_MEMORY_MOTIF_MAP',
                 'Onde uma pista de releitura corresponder a uma crenca do leitor no ledger, '
                 'cite o id da crenca (RB-*) para T018 poder ligar motivo a revisao de crenca.',
                 extra_inputs=(ledger_template,'/canon/CAUSAL_LEDGER.yaml'))
        for ch in range(1,count+1):
            annotate(f'T1{ch:02d}_BRIEF_CHAPTER',
                     'Cite os EV-* deste capitulo do ledger causal; heat profile e camera '
                     'narrativa sao planejamento de cena (nao canon) e nunca resetam um estado '
                     'de personagem/relacao que o ledger ja registrou (INV-04).',
                     extra_inputs=(ledger_template,'/canon/CAUSAL_LEDGER.yaml'))
        for wi2 in range(1,len(sp['writing_waves'])+1):
            base2=f'T2{wi2:02d}'
            wr_task=tasks_by_id.get(f'{base2}_WRITE')
            if wr_task is not None:
                shared=wr_task.get('spawn',{}).get('shared_inputs')
                if isinstance(shared,list) and '/canon/CAUSAL_LEDGER.yaml' not in shared:
                    shared.append('/canon/CAUSAL_LEDGER.yaml')
                wr_task['parameters']={**wr_task.get('parameters',{}),'causal_ledger':
                    'Proponha deltas realizados (relationship_delta, knowledge_delta, efeitos de '
                    'loop) em canon/CANON_PROPOSALS -- nunca promova PLANNED a REALIZED '
                    'diretamente; isso e exclusivo de CANON_GUARDIAN.'}
            annotate(f'{base2}_CANON_UPDATE',
                     'Promova as propostas desta wave: PLANNED->REALIZED, com evidence_to_reader '
                     'real. facts/caused_by/consent de eventos ja REALIZED sao imutaveis (INV-10) '
                     '-- uma correcao vira mutation_log, nunca edicao silenciosa.',
                     extra_inputs=('/canon/CAUSAL_LEDGER.yaml','/canon/CANON_PROPOSALS'))
    # integration + protected scene audits
    tasks.append(task('T300_ASSEMBLE_FULL_MANUSCRIPT','INTEGRATION','MERGE_COORDINATOR',[prev_gate],locks=['MANUSCRIPT_MERGE'],outputs=['/manuscript/revised/FULL_MANUSCRIPT_PRE_INTEGRATION.md']))
    tasks.append(task('T301_WHOLE_BOOK_INTEGRATION','INTEGRATION','MASTER_INTEGRATOR',['T300_ASSEMBLE_FULL_MANUSCRIPT'],outputs=['/integration/INTEGRATION_REPORT.md']))
    critic_pack=rotate_pack(packs.get('critic_panel',[]),profile.get('critic_panel_limit'),0)
    tasks.append(task('T302_CRITIC_PANEL','INTEGRATION','MASTER_ORCHESTRATOR',['T300_ASSEMBLE_FULL_MANUSCRIPT'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':critic_pack,'wait_for_all':True},outputs=['/reviews/CRITIC_PANEL/']))
    protected=load_yaml(book/sp['protected_scenes_file']).get('scenes',[]); audit_ids=[]
    for idx,scene in enumerate(protected,1):
        tid=f'T32{idx:02d}_PROTECTED_{scene["id"]}'; audit_ids.append(tid)
        tasks.append(task(tid,'INTEGRATION',scene.get('auditor','PROTECTED_SCENE_AUDITOR'),['T300_ASSEMBLE_FULL_MANUSCRIPT'],inputs=['/book/protected_scenes.yaml'],parameters={'scene_id':scene['id'],'chapters':scene['chapters']},outputs=[f'/reviews/PROTECTED_{scene["id"]}_AUDIT.md']))
    tasks += [
      task('T303_REVIEW_SYNTHESIS','INTEGRATION','EXECUTIVE_EDITOR',['T301_WHOLE_BOOK_INTEGRATION','T302_CRITIC_PANEL']+audit_ids,outputs=['/reviews/MASTER_REVISION_DIRECTIVE.md']),
      task('T304_LEAD_NOVELIST_REVISION','INTEGRATION','LEAD_NOVELIST',['T303_REVIEW_SYNTHESIS'],locks=['MANUSCRIPT_FINAL_WRITE'])]
    line_pack=rotate_pack(packs.get('line_reviewers',[]),profile.get('line_reviewers_limit'),0)
    if profile.get('consolidate_integration_reviews'):
        # Uma passada de polimento em vez de tres barreiras sequenciais
        # (desenvolvimento -> linha -> revisao literaria final). Os mesmos
        # revisores participam; o que desaparece e a espera entre elas.
        tasks.append(task('T307_FINAL_LITERARY_REVISION','INTEGRATION','LEAD_NOVELIST',['T304_LEAD_NOVELIST_REVISION'],locks=['MANUSCRIPT_FINAL_WRITE'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':sorted(set(line_pack+['DEVELOPMENTAL_EDITOR'])),'wait_for_all':True},parameters={'consolidated':True,'replaces':['T305_DEVELOPMENTAL_REVIEW','T306_LINE_REVIEW']}))
        integration_review_ids=['T307_FINAL_LITERARY_REVISION']
    else:
        tasks += [
          task('T305_DEVELOPMENTAL_REVIEW','INTEGRATION','DEVELOPMENTAL_EDITOR',['T304_LEAD_NOVELIST_REVISION']),
          task('T306_LINE_REVIEW','INTEGRATION','MASTER_ORCHESTRATOR',['T304_LEAD_NOVELIST_REVISION'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':line_pack,'wait_for_all':True}),
          task('T307_FINAL_LITERARY_REVISION','INTEGRATION','LEAD_NOVELIST',['T305_DEVELOPMENTAL_REVIEW','T306_LINE_REVIEW'],locks=['MANUSCRIPT_FINAL_WRITE'])]
        integration_review_ids=['T305_DEVELOPMENTAL_REVIEW','T306_LINE_REVIEW','T307_FINAL_LITERARY_REVISION']
    tasks += [
      task('T308_PTBR_REVIEW','INTEGRATION','PTBR_GRAMMAR_EDITOR',['T307_FINAL_LITERARY_REVISION']),
      task('T309_FINAL_PROOF','INTEGRATION','FINAL_PROOFREADER',['T308_PTBR_REVIEW']),
      task('T310_FREEZE_MANUSCRIPT','INTEGRATION','EXECUTIVE_EDITOR',['T309_FINAL_PROOF'],locks=['MANUSCRIPT_FINAL_WRITE'],outputs=['/manuscript/final/MANUSCRIPT_FINAL_PTBR.md','/manuscript/final/MANUSCRIPT_FINAL_PTBR.txt'])]
    gates['GATE_FULL_MANUSCRIPT']={'blocking':True,'requires':['T300_ASSEMBLE_FULL_MANUSCRIPT','T301_WHOLE_BOOK_INTEGRATION','T302_CRITIC_PANEL']+audit_ids+['T303_REVIEW_SYNTHESIS','T304_LEAD_NOVELIST_REVISION']+integration_review_ids+['T308_PTBR_REVIEW','T309_FINAL_PROOF','T310_FREEZE_MANUSCRIPT']}
    if visual_narrative_enabled:
        # REALIZATION (SDD, secao 10.3): so depois do manuscrito congelado as
        # ancoras TEXT: podem resolver de verdade. T311 promove PLANNED ->
        # REALIZED (mesmo lock VISUAL_CANON_WRITE de T043 -- um so dono
        # escrevendo o arquivo em qualquer ponto do tempo). T312 congela o
        # snapshot FREEZE que ST-08/VISUAL_RETCON compara depois.
        tasks += [
          task('T311_VISUAL_STATE_REALIZATION','INTEGRATION','VISUAL_DIRECTOR',['T310_FREEZE_MANUSCRIPT'],
               locks=['VISUAL_CANON_WRITE'],
               inputs=(['/canon/VISUAL_NARRATIVE_CANON.yaml','/manuscript/final/MANUSCRIPT_FINAL_PTBR.md']
                       +(['/canon/CAUSAL_LEDGER.yaml'] if causal_ledger_enabled else [])),
               outputs=['/canon/VISUAL_NARRATIVE_CANON.yaml']),
          task('T312_VISUAL_CANON_SNAPSHOT','INTEGRATION','VISUAL_DIRECTOR',['T311_VISUAL_STATE_REALIZATION'],
               inputs=['/canon/VISUAL_NARRATIVE_CANON.yaml'],
               outputs=['/canon/snapshots/VISUAL_NARRATIVE_CANON.FREEZE.yaml']),
        ]
        gates['GATE_FULL_MANUSCRIPT']['requires'] += ['T311_VISUAL_STATE_REALIZATION','T312_VISUAL_CANON_SNAPSHOT']
    # visual matrix
    # Ilustracao por slot (docs/sdd/NARCISO_CANONICAL_SDD_v0.1.md, 28.3): OFF por
    # padrao, lido com .get(). Com a flag, as pranchas declaradas em
    # chapter_architecture.yaml (illustration_slots) substituem a imagem unica
    # por capitulo; sem ela, o bloco original abaixo roda igual (goldens).
    illustration_slot_pairs = illustration_slots_by_chapter(book, sp) if (sp['features'].get('images') or {}).get('illustration_slots') else None
    if sp['features']['images']['enabled'] and illustration_slot_pairs is not None:
      image_ids=[]
      vn_inputs=['/canon/VISUAL_NARRATIVE_CANON.yaml'] if visual_narrative_enabled else []
      for ch, il in illustration_slot_pairs:
        nn=il.split('-')[1]; params={'illustration_id':il,'chapter':ch}
        b=f'T45{nn}_IL_BRIEF'; g=f'T45{nn}_IL_GENERATE'; fq=f'T45{nn}_IL_FACE_QA'; cq=f'T45{nn}_IL_CONTINUITY_QA'; a=f'T45{nn}_IL_APPROVE'; image_ids.append(a)
        tasks += [task(b,'VISUAL_PRODUCTION','CHAPTER_IMAGE_DIRECTOR',['GATE_FULL_MANUSCRIPT'],inputs=list(vn_inputs),parameters=dict(params),outputs=[f'/images/prompts/{il}_IMAGE_BRIEF.md']),task(g,'VISUAL_PRODUCTION','IMAGE_GENERATOR',[b],parameters=dict(params),outputs=[f'/images/illustrations/{il}/']),task(fq,'VISUAL_PRODUCTION','FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT',[g],parameters=dict(params),outputs=[f'/images/illustrations/{il}/FACE_QA.md']),task(cq,'VISUAL_PRODUCTION','IMAGE_CONTINUITY_QA',[g],parameters=dict(params),outputs=[f'/images/illustrations/{il}/CONTINUITY_QA.md']),task(a,'VISUAL_PRODUCTION','VISUAL_DIRECTOR',[fq,cq],parameters=dict(params),outputs=[f'/images/approved/{il}.jpg'])]
      gates['GATE_VISUAL']={'blocking':True,'requires':image_ids}
    elif sp['features']['images']['enabled']:
      image_ids=[]
      for ch in range(1,count+1):
        b=f'T4{ch:02d}_IMAGE_BRIEF'; g=f'T4{ch:02d}_IMAGE_GENERATE'; fq=f'T4{ch:02d}_FACE_QA'; cq=f'T4{ch:02d}_CONTINUITY_QA'; a=f'T4{ch:02d}_IMAGE_APPROVE'; image_ids.append(a)
        tasks += [task(b,'VISUAL_PRODUCTION','CHAPTER_IMAGE_DIRECTOR',['GATE_FULL_MANUSCRIPT'],outputs=[f'/images/prompts/CHAPTER_{ch:02d}_IMAGE_BRIEF.md']),task(g,'VISUAL_PRODUCTION','IMAGE_GENERATOR',[b],outputs=[f'/images/chapters/chapter_{ch:02d}/']),task(fq,'VISUAL_PRODUCTION','FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT',[g],outputs=[f'/images/chapters/chapter_{ch:02d}/FACE_QA.md']),task(cq,'VISUAL_PRODUCTION','IMAGE_CONTINUITY_QA',[g],outputs=[f'/images/chapters/chapter_{ch:02d}/CONTINUITY_QA.md']),task(a,'VISUAL_PRODUCTION','VISUAL_DIRECTOR',[fq,cq],outputs=[f'/images/approved/chapter_{ch:02d}.jpg'])]
      gates['GATE_VISUAL']={'blocking':True,'requires':image_ids}
    # sound
    if sp['features']['living_sound']['enabled']:
      tasks += [task('T500_SOUNDTRACK_BIBLE_FINAL','LIVING_SOUND','LIVING_SOUNDTRACK_ARCHITECT',['GATE_FULL_MANUSCRIPT'],outputs=['/sound/LIVING_SOUNDTRACK_BIBLE.md']),task('T501_CHAPTER_SOUND_MAP_FINAL','LIVING_SOUND','LIVING_SOUNDTRACK_ARCHITECT',['T500_SOUNDTRACK_BIBLE_FINAL'],outputs=['/sound/CHAPTER_SOUND_MAP.md']),task('T502_ENVIRONMENT_ACOUSTIC_EVOLUTION','LIVING_SOUND','ENVIRONMENT_ACOUSTIC_EVOLUTION_AGENT',['T500_SOUNDTRACK_BIBLE_FINAL'],parameters={'environment_organism':sp.get('acoustic_environment_organism')},outputs=['/sound/ENVIRONMENT_ACOUSTIC_EVOLUTION.md']),task('T503_SOUND_PROMPTS','LIVING_SOUND','MASTER_ORCHESTRATOR',['T501_CHAPTER_SOUND_MAP_FINAL','T502_ENVIRONMENT_ACOUSTIC_EVOLUTION'],spawn={'mode':'PARALLEL_SUBAGENTS','template_agent':'LIVING_SOUND_PROMPT_ENGINEER','foreach_chapter':f'1..{count}','max_parallel':e['spec']['execution_policy']['max_parallel_sound_tasks'],'wait_for_all':True},outputs=[f'/sound/prompts/CHAPTER_{{chapter:02d}}_SOUND_PROMPT.md']),task('T504_SOUND_REVIEW','LIVING_SOUND','SOUND_BIOME_ARCHITECT',['T503_SOUND_PROMPTS'],outputs=['/reviews/LIVING_SOUND_REVIEW.md'])]
      gates['GATE_SOUND']={'blocking':True,'requires':['T500_SOUNDTRACK_BIBLE_FINAL','T501_CHAPTER_SOUND_MAP_FINAL','T502_ENVIRONMENT_ACOUSTIC_EVOLUTION','T503_SOUND_PROMPTS','T504_SOUND_REVIEW']}
    # legal
    tasks += [task('T600_LEGAL_BR','LEGAL','LEGAL_EDITOR_BR',['GATE_FULL_MANUSCRIPT'],outputs=['/legal/LEGAL_REVIEW_BR.md']),task('T601_LEGAL_GLOBAL','LEGAL','LEGAL_EDITOR_GLOBAL',['GATE_FULL_MANUSCRIPT'],outputs=['/legal/LEGAL_REVIEW_GLOBAL.md']),task('T602_ORIGINALITY_AUDIT','LEGAL','COPYRIGHT_ORIGINALITY_AUDITOR',['GATE_FULL_MANUSCRIPT'],outputs=['/legal/ORIGINALITY_REPORT.md']),task('T603_LEGAL_SYNTHESIS','LEGAL','EXECUTIVE_EDITOR',['T600_LEGAL_BR','T601_LEGAL_GLOBAL','T602_ORIGINALITY_AUDIT'],outputs=['/legal/LEGAL_BLOCKERS.md']),task('T604_BLOCKING_LEGAL_FIXES','LEGAL','LEAD_NOVELIST',['T603_LEGAL_SYNTHESIS'],condition='LEGAL_BLOCKERS contains blocking findings')]
    gates['GATE_LEGAL']={'blocking':True,'requires':['T600_LEGAL_BR','T601_LEGAL_GLOBAL','T602_ORIGINALITY_AUDIT','T603_LEGAL_SYNTHESIS','T604_BLOCKING_LEGAL_FIXES']}
    if visual_narrative_enabled:
        # 26.3 da SDD: originalidade tambem cobre composicao/simbolo, nao so
        # texto. Sem mudar outputs nem dependencias -- so o que o auditor le.
        t602 = next(t for t in tasks if t['id']=='T602_ORIGINALITY_AUDIT')
        t602.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
        t602['parameters']={**t602.get('parameters',{}),'visual_narrative':
            'Comparar tambem composicao de capa e simbolos do canon visual contra '
            'identidades reconheciveis de terceiros -- nao so o texto do manuscrito.'}
    # translation prep
    if sp['features']['translation_preparation']['enabled']:
      tasks += [task('T650_TRANSLATION_ARCHITECTURE','TRANSLATION','TRANSLATION_ARCHITECT',['GATE_FULL_MANUSCRIPT'],outputs=['/translation/TRANSLATION_PLAN.md']),task('T651_ENGLISH_STYLE_BIBLE','TRANSLATION','ENGLISH_LITERARY_EDITOR',['T650_TRANSLATION_ARCHITECTURE'],outputs=['/translation/ENGLISH_STYLE_BIBLE.md']),task('T652_TRANSLATION_GLOSSARY','TRANSLATION','CULTURAL_ADAPTATION_GUARDIAN',['T650_TRANSLATION_ARCHITECTURE'],outputs=['/translation/PTBR_EN_GLOSSARY.md'])]
      gates['GATE_TRANSLATION_PREP']={'blocking':False,'requires':['T650_TRANSLATION_ARCHITECTURE','T651_ENGLISH_STYLE_BIBLE','T652_TRANSLATION_GLOSSARY']}
    # KDP
    if sp['features']['kdp_docx']['enabled']:
      deps=['GATE_LEGAL']
      if 'GATE_VISUAL' in gates: deps.append('GATE_VISUAL')
      if 'GATE_SOUND' in gates: deps.append('GATE_SOUND')
      tasks += [task('T699_KDP_REQUIREMENTS_REFRESH','KDP','KDP_REQUIREMENTS_RESEARCHER',['GATE_FULL_MANUSCRIPT'],outputs=['/layout/KDP_CURRENT_REQUIREMENTS.md']),task('T700_LAYOUT_BIBLE','KDP','BOOK_LAYOUT_ARCHITECT',['GATE_FULL_MANUSCRIPT'],outputs=['/layout/PAGE_BIBLE.md']),task('T701_TABLE_OF_CONTENTS','KDP','TABLE_OF_CONTENTS_AGENT',['T700_LAYOUT_BIBLE'],outputs=['/layout/TABLE_OF_CONTENTS_SPEC.md']),task('T702_IMAGE_PLACEMENT','KDP','IMAGE_LAYOUT_AGENT',(['GATE_VISUAL'] if 'GATE_VISUAL' in gates else [])+['T700_LAYOUT_BIBLE'],outputs=['/layout/IMAGE_PLACEMENT_REPORT.md']),task('T703_BUILD_DOCX','KDP','KDP_FORMATTER',deps+['T699_KDP_REQUIREMENTS_REFRESH','T701_TABLE_OF_CONTENTS','T702_IMAGE_PLACEMENT'],locks=['DOCX_BUILD'],outputs=['/outputs/KDP_DRAFT.docx']),task('T704_KDP_QA','KDP','MASTER_ORCHESTRATOR',['T703_BUILD_DOCX'],spawn={'mode':'PARALLEL_SUBAGENTS','agents':['BOOK_LAYOUT_ARCHITECT','TABLE_OF_CONTENTS_AGENT','IMAGE_LAYOUT_AGENT','FINAL_PROOFREADER'],'wait_for_all':True},outputs=['/reviews/KDP_QA_REPORT.md']),task('T705_DOCX_FINAL_FIXES','KDP','KDP_FORMATTER',['T704_KDP_QA'],locks=['DOCX_BUILD'],outputs=['/outputs/BOOK_KDP_FINAL.docx']),task('T706_APPROVE_KDP','KDP','EXECUTIVE_EDITOR',['T705_DOCX_FINAL_FIXES'])]
      gates['GATE_KDP']={'blocking':True,'requires':['T699_KDP_REQUIREMENTS_REFRESH','T700_LAYOUT_BIBLE','T701_TABLE_OF_CONTENTS','T702_IMAGE_PLACEMENT','T703_BUILD_DOCX','T704_KDP_QA','T705_DOCX_FINAL_FIXES','T706_APPROVE_KDP']}
      if illustration_slot_pairs is not None:
          t702_slots = next(t for t in tasks if t['id']=='T702_IMAGE_PLACEMENT')
          t702_slots['parameters']={**t702_slots.get('parameters',{}),'illustration_slots':
              'Escrever layout/IMAGE_PLACEMENT.yaml com illustrations[] (id, chapter, placement, anchor '
              'literal, category, alt, pair_with SPREAD quando o canon declarar) para cada slot aprovado; '
              'build_kdp_docx.py insere por id.'}
      if visual_narrative_enabled:
          # EDITION PLAN (SDD, secao 10.3/21.1). T698 resolve superficie x
          # acabamento por alvo (nao precisa de contagem de paginas); T707
          # precisa da contagem real, so disponivel depois do render/QA de
          # T705 -- por isso aninhado aqui dentro do bloco kdp_docx, e nao
          # logo apos GATE_FULL_MANUSCRIPT. Ambas sao tarefas 100% mecanicas
          # (tool, TOOL_BY_TASK abaixo), sem julgamento de agente.
          edition_plan_outputs = [f'/layout/editions/{t}/EDITION_PLAN.yaml' for t in vn_edition_targets]
          geometry_outputs = [f'/layout/editions/{t}/COVER_GEOMETRY.yaml' for t in vn_edition_targets]
          tasks += [
            task('T698_EDITION_PLAN','KDP','VISUAL_DIRECTOR',['GATE_FULL_MANUSCRIPT'],
                 inputs=['/canon/VISUAL_NARRATIVE_CANON.yaml','/engine/templates/EDITION_CAPABILITIES.yaml'],
                 outputs=edition_plan_outputs or ['/layout/editions/EDITION_PLAN_EMPTY.md']),
            task('T707_PRINT_GEOMETRY','KDP','BOOK_LAYOUT_ARCHITECT',['T705_DOCX_FINAL_FIXES'],
                 inputs=['/layout/PRINT_SPEC.yaml','/engine/templates/PRINT_GEOMETRY.yaml'],
                 outputs=geometry_outputs or ['/layout/editions/COVER_GEOMETRY_EMPTY.md']),
          ]
          gates['GATE_KDP']['requires'] += ['T698_EDITION_PLAN','T707_PRINT_GEOMETRY']
          # 28.2 da SDD: tarefas existentes passam a citar o canon visual e
          # os fatos de fabricacao, sem mudar seus outputs contratuais.
          t699 = next(t for t in tasks if t['id']=='T699_KDP_REQUIREMENTS_REFRESH')
          t699.setdefault('inputs',[]).append('/engine/templates/PRINT_GEOMETRY.yaml')
          t699['parameters']={**t699.get('parameters',{}),'visual_narrative':
              'Revalidar tambem as chaves TO_VERIFY de PRINT_GEOMETRY.yaml contra fontes '
              'oficiais antes do release -- ver MANUFACTURING_FACT_UNVERIFIED.'}
          t700 = next(t for t in tasks if t['id']=='T700_LAYOUT_BIBLE')
          t700.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
          t700['parameters']={**t700.get('parameters',{}),'visual_narrative':
              'Reservar espaco de pagina para os sigils de abertura de capitulo '
              'declarados no canon visual (18.4 da SDD).'}
          t702 = next(t for t in tasks if t['id']=='T702_IMAGE_PLACEMENT')
          t702.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
          t702['parameters']={**t702.get('parameters',{}),'visual_narrative':
              'Artefatos narrativos (NARRATIVE_ARTIFACT) tem placement proprio no canon '
              'visual (anchor/mode) -- respeitar, nao inventar posicao nova.'}
          t703 = next(t for t in tasks if t['id']=='T703_BUILD_DOCX')
          t703.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
          t703['parameters']={**t703.get('parameters',{}),'visual_narrative':
              'Quando existir layout/editions/<target>/EDITION_PLAN.yaml com sigils de '
              'abertura resolvidos, inseri-los -- ausencia = comportamento identico ao '
              'de hoje (Slice 6, ainda nao ligado por esta capability sozinha).'}
    # delivery
    delivery_dep='GATE_KDP' if 'GATE_KDP' in gates else 'GATE_FULL_MANUSCRIPT'
    tasks += [
      task('T800_MEDIA_PACKAGE','DELIVERY','MEDIA_AND_KDP_AGENT',[delivery_dep],outputs=['/media/KDP_DESCRIPTION_4000.txt','/media/KDP_DESCRIPTION_SHORT.txt','/media/KDP_KEYWORDS.md','/media/COVER_BRIEF.md','/media/SHAREABLE_EXCERPTS.md','/media/INSTAGRAM_STORIES_IDEAS.md']),
      task('T801_KDP_BOOK_COVER','DELIVERY','MEDIA_AND_KDP_AGENT',['T800_MEDIA_PACKAGE'],locks=['DELIVERY_BUILD'],parameters={'format':'JPEG','width_px':1600,'height_px':2560,'color_mode':'RGB','minimum_dpi':300,'maximum_bytes':52428800},outputs=['/media/outputs/cover/BOOK_COVER_KDP.jpg','/media/outputs/COVER_PRODUCTION_REPORT.md']),
      task('T802_INSTAGRAM_STORIES','DELIVERY','MEDIA_AND_KDP_AGENT',['T801_KDP_BOOK_COVER'],locks=['DELIVERY_BUILD'],parameters={'count':5,'format':'JPEG','width_px':1080,'height_px':1920,'color_mode':'RGB','minimum_dpi':300,'commercial_promotion':True},outputs=[f'/media/outputs/instagram_stories/story_{i:02d}.jpg' for i in range(1,6)]+['/media/outputs/INSTAGRAM_STORIES_COPY.md','/media/outputs/MEDIA_ASSET_MANIFEST.md']),
      task('T803_DELIVERY_MANIFEST','DELIVERY','DELIVERY_AGENT',['GATE_MEDIA_ASSETS'],outputs=['/outputs/DELIVERY_MANIFEST.md']),
      task('T804_FINAL_ARTIFACT_AUDIT','DELIVERY','MASTER_ORCHESTRATOR',['T803_DELIVERY_MANIFEST'],outputs=['/reviews/FINAL_ARTIFACT_AUDIT.md']),
      task('T805_FINAL_DELIVERY','DELIVERY','DELIVERY_AGENT',['T804_FINAL_ARTIFACT_AUDIT'],locks=['DELIVERY_BUILD'],outputs=['/project_state/FINAL_DELIVERY_APPROVED'])]
    gates['GATE_MEDIA_ASSETS']={'blocking':True,'requires':['T801_KDP_BOOK_COVER','T802_INSTAGRAM_STORIES'],'custom_validators':['V_MEDIA_ASSET_PACKAGE']}
    gates['GATE_DELIVERY']={'blocking':True,'requires':['T800_MEDIA_PACKAGE','GATE_MEDIA_ASSETS','T803_DELIVERY_MANIFEST','T804_FINAL_ARTIFACT_AUDIT','T805_FINAL_DELIVERY']}
    if visual_narrative_enabled:
        # 17.3/21.5 da SDD: capa e Stories passam a citar o canon visual (a
        # composicao FRONT_COVER e a fonte de significado), sem mudar o
        # contrato de outputs que o smoke-test confere byte a byte.
        t800 = next(t for t in tasks if t['id']=='T800_MEDIA_PACKAGE')
        t800.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
        t800['parameters']={**t800.get('parameters',{}),'visual_narrative':
            'A descricao/keywords nunca prometem acabamento nao PHYSICAL no plano de '
            'edicao -- ver FINISH_PROMISE_MISMATCH.'}
        t801 = next(t for t in tasks if t['id']=='T801_KDP_BOOK_COVER')
        t801.setdefault('inputs',[]).append('/canon/VISUAL_NARRATIVE_CANON.yaml')
        t801['parameters']={**t801.get('parameters',{}),'visual_narrative':
            'A capa realiza a composicao FRONT_COVER do canon visual (elemento DOMINANT, '
            'tipografia, paleta dentro dos papeis da autora) -- nunca uma composicao '
            'nova inventada nesta tarefa.'}
    # Apply book extensions
    for t in ext.get('spec',{}).get('additional_tasks',[]): tasks.append(t)
    for gid,gx in ext.get('spec',{}).get('gate_extensions',{}).items():
        if gid in gates:
            gates[gid].setdefault('custom_validators',[]).extend(gx.get('validators',[]))
    # Cost dosage: annotate each task with the model_tier of its owner (and,
    # for tasks that spawn subagents, a per-subagent tier map) whenever that
    # tier is declared. Tasks whose owner has no declared tier are left
    # untouched — see discovery-books/04-plano-desenvolvimento-custo.md.
    for t in tasks:
        owner_tier = tiers.get(t.get('owner'))
        if owner_tier:
            t['model_tier'] = owner_tier
        spawn_block = t.get('spawn')
        if spawn_block:
            sub_tiers = {}
            for a in spawn_block.get('agents', []):
                if a in tiers: sub_tiers[a] = tiers[a]
            for j in spawn_block.get('jobs', []):
                ag = j.get('agent')
                if ag in tiers: sub_tiers[ag] = tiers[ag]
            ta = spawn_block.get('template_agent')
            if ta and ta in tiers: sub_tiers[ta] = tiers[ta]
            if sub_tiers:
                spawn_block['model_tiers'] = sub_tiers
    # Per-task tier overrides: a handful of tasks are cheaper than their
    # owner agent's usual work (e.g. FACIAL_IDENTITY_AND_PHYSIOGNOMY_EXPERT
    # defines the face canon at Tier M once, but the 1-per-chapter identity
    # QA against that already-approved canon is a repetitive comparison, not
    # fresh judgment). Matched by fnmatch pattern against the task id.
    for pattern, override_tier in TASK_TIER_OVERRIDES:
        for t in tasks:
            if fnmatch.fnmatch(t['id'], pattern):
                t['model_tier'] = override_tier
    # Ferramentas deterministicas: tarefas cujo trabalho e inteiramente
    # mecanico e nao exige nenhuma chamada de modelo. run_deterministic.py
    # executa estas sozinho, marca o estado e registra custo zero no ledger.
    # O criterio para entrar aqui e estrito: se a tarefa exige QUALQUER
    # julgamento (escolher uma palavra, aprovar uma imagem, decidir se uma
    # repeticao e deliberada), ela NAO recebe tool -- continua com o agente.
    for t in tasks:
        tool = TOOL_BY_TASK.get(t['id'])
        if tool is None:
            for pattern, candidate in TOOL_BY_PATTERN:
                if fnmatch.fnmatch(t['id'], pattern):
                    tool = candidate; break
        if tool:
            t['tool'] = tool
    # Gates rebaixados pelo perfil: registram achados sem interromper. Canon,
    # manuscrito, legal, midia e entrega nunca entram nessa lista -- economia
    # sai de repeticao de revisao, nao de protecao.
    for gid in profile.get('non_blocking_gates') or []:
        if gid in gates:
            gates[gid]['blocking']=False
            gates[gid]['downgraded_by_profile']=profile_name
    # Checkpoints humanos: o gate so passa quando existir o arquivo de
    # aprovacao. O motor NUNCA cria esse arquivo -- e o unico ponto do
    # pipeline em que a decisao nao e automatizavel por desenho.
    for gid in profile.get('human_checkpoints') or []:
        if gid in gates:
            gates[gid]['requires_human_approval']=True
            gates[gid]['approval_file']=f'/project_state/APPROVALS/{gid}.md'
    engine_validators=[{'id':'V_MEDIA_ASSET_PACKAGE','command':'python scripts/validate_media_assets.py'}]
    if causal_ledger_enabled:
        flags=_causal_ledger_threshold_flags(causal_ledger_cfg)
        engine_validators.append({'id':'V_CAUSAL_LEDGER_PLAN','command':f'python scripts/check_causal_ledger.py --runtime . --mode plan{flags}'})
        gates['GATE_CANON'].setdefault('custom_validators',[]).append('V_CAUSAL_LEDGER_PLAN')
        wave_count=len(sp['writing_waves'])
        for wi in range(1,wave_count+1):
            vid=f'V_CAUSAL_LEDGER_WAVE_{wi}'
            baseline=f'canon/snapshots/CAUSAL_LEDGER.WAVE_{wi-1:02d}.yaml'
            engine_validators.append({'id':vid,'command':f'python scripts/check_causal_ledger.py --runtime . --mode realized --baseline {baseline}{flags}'})
            gates[f'GATE_WAVE_{wi}'].setdefault('custom_validators',[]).append(vid)
        final_baseline=f'canon/snapshots/CAUSAL_LEDGER.WAVE_{wave_count:02d}.yaml'
        engine_validators.append({'id':'V_CAUSAL_LEDGER_FINAL','command':f'python scripts/check_causal_ledger.py --runtime . --mode final --baseline {final_baseline} --chapter-architecture book/chapter_architecture.yaml{flags}'})
        gates['GATE_FULL_MANUSCRIPT'].setdefault('custom_validators',[]).append('V_CAUSAL_LEDGER_FINAL')
    if visual_narrative_enabled:
        # BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM (docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md,
        # secao 23.2): 4 validadores em 4 gates ja existentes, nenhum gate novo --
        # mesmo padrao do causal_ledger acima.
        engine_validators.append({'id':'V_VISUAL_CANON_PLAN','command':'python scripts/check_visual_canon.py --runtime . --mode plan'})
        gates['GATE_LIVING_BOOK'].setdefault('custom_validators',[]).append('V_VISUAL_CANON_PLAN')
        engine_validators.append({'id':'V_VISUAL_CANON_REALIZED','command':'python scripts/check_visual_canon.py --runtime . --mode realized --baseline canon/snapshots/VISUAL_NARRATIVE_CANON.PLAN.yaml'})
        gates['GATE_FULL_MANUSCRIPT'].setdefault('custom_validators',[]).append('V_VISUAL_CANON_REALIZED')
        engine_validators.append({'id':'V_VISUAL_EDITION','command':'python scripts/check_visual_canon.py --runtime . --validate-editions'})
        edition_gate='GATE_KDP' if 'GATE_KDP' in gates else 'GATE_DELIVERY'
        gates[edition_gate].setdefault('custom_validators',[]).append('V_VISUAL_EDITION')
        engine_validators.append({'id':'V_VISUAL_ASSETS','command':'python scripts/check_visual_canon.py --runtime . --mode assets --cover-image media/outputs/cover/BOOK_COVER_KDP.jpg'})
        gates['GATE_MEDIA_ASSETS'].setdefault('custom_validators',[]).append('V_VISUAL_ASSETS')
    return {'apiVersion':'pedroarte.livingbooks/v1','kind':'LiteraryTaskGraph','metadata':{'project_id':md['slug'],'title':md['title'],'author':md['author'],'language':md['language'],'chapter_count':count,'engine_version':e['metadata']['version'],'book_version':md.get('version','1.0.0'),'execution_profile':profile_name},'spec':{'execution_policy':e['spec']['execution_policy'],'task_states':e['spec']['task_states'],'success_states':e['spec']['success_states'],'rejection_states':rejections,'locks':e['spec']['locks'],'agents':agents,'protocols':e['spec']['protocols'],'quality_defaults':e['spec']['quality_defaults'],'quality_profile':load_yaml(book/sp['quality_profile_file']),'immutable_rules':load_yaml(book/sp['immutable_rules_file']),'custom_validators':engine_validators+ext.get('spec',{}).get('custom_validators',[]),'gates':gates,'tasks':tasks}}

def validate_graph(g, root: Path):
    errors=[]; tasks=g['spec']['tasks']; gates=g['spec']['gates']; agents=g['spec']['agents']; tids=[t['id'] for t in tasks]
    if len(tids)!=len(set(tids)): errors.append('duplicate task IDs')
    validators=g['spec'].get('custom_validators',[]); validator_ids=[v.get('id') for v in validators]
    if len(validator_ids)!=len(set(validator_ids)): errors.append('duplicate custom validator IDs')
    for validator in validators:
        if not validator.get('id') or not validator.get('command'): errors.append('custom validators require id and command')
    nodes=set(tids)|set(gates)
    for t in tasks:
        if t.get('owner') not in agents: errors.append(f'{t["id"]}: unknown owner {t.get("owner")}')
        for dep in t.get('depends_on',[]):
            if dep not in nodes: errors.append(f'{t["id"]}: unknown dependency {dep}')
        sp=t.get('spawn',{})
        for a in sp.get('agents',[]):
            if a not in agents: errors.append(f'{t["id"]}: unknown spawned agent {a}')
        for j in sp.get('jobs',[]):
            if j.get('agent') not in agents: errors.append(f'{t["id"]}: unknown job agent {j.get("agent")}')
        ta=sp.get('template_agent')
        if ta and ta not in agents: errors.append(f'{t["id"]}: unknown template agent {ta}')
    for gid,gate in gates.items():
        for req in gate.get('requires',[]):
            if req not in nodes: errors.append(f'{gid}: unknown required node {req}')
        for validator_id in gate.get('custom_validators',[]):
            if validator_id not in validator_ids: errors.append(f'{gid}: unknown custom validator {validator_id}')
    # cycle check tasks and gates as dependency graph including gate aggregation
    deps={t['id']:list(t.get('depends_on',[])) for t in tasks}
    deps.update({gid:list(gdef.get('requires',[])) for gid,gdef in gates.items()})
    temp=set(); perm=set()
    def visit(n):
        if n in perm:return
        if n in temp: errors.append(f'cycle detected at {n}'); return
        temp.add(n)
        for d in deps.get(n,[]): visit(d)
        temp.remove(n); perm.add(n)
    for n in deps: visit(n)
    return errors

def copy_runtime(book: Path, runtime: Path, graph):
    if runtime.exists(): shutil.rmtree(runtime)
    runtime.mkdir(parents=True)
    shutil.copytree(book,runtime/'book')
    (runtime/'.codex/agents').mkdir(parents=True)
    # copy generic agents
    for p in (ENGINE/'agents').glob('*.toml'): shutil.copy2(p,runtime/'.codex/agents'/p.name)
    for p in (book/'agents').glob('*.toml'): shutil.copy2(p,runtime/'.codex/agents'/p.name)
    (runtime/'.codex/config.toml').write_text('[agents]\nmax_threads = 8\nmax_depth = 1\njob_max_runtime_seconds = 1800\n',encoding='utf-8')
    # runtime dirs
    for d in ['specs','canon','canon/snapshots','briefs/chapters','manuscript/raw','manuscript/revised','manuscript/approved','manuscript/final','reviews','integration','living_book','images/canon','images/characters','images/chapters','images/prompts','images/rejected','images/approved','sound/prompts','sound/motifs','sound/prototypes','translation','legal','layout','media','media/outputs/cover','media/outputs/instagram_stories','media/outputs/sources','outputs','logs','project_state','scripts']:
        (runtime/d).mkdir(parents=True,exist_ok=True)
    save_yaml(runtime/'TASK_GRAPH.yaml',graph)
    shutil.copy2(ENGINE/'IMPLEMENT.md',runtime/'IMPLEMENT.md')
    # copy CLI helper for state operations
    # Ferramentas determinísticas do motor. Cada uma destas substitui trabalho
    # que, numa execução real, foi reconstruído do zero dentro do runtime com
    # centenas de linhas de script ad hoc (ver discovery-books/07).
    for script in ('runtime_taskgraph.py','validate_media_assets.py','cost_report.py',
                   '_layout_config.py','build_kdp_docx.py','check_render_capability.py','build_cover_and_stories.py',
                   'generate_image.py','detect_repetition.py','check_typography.py','check_canon_continuity.py','build_canon_digest.py',
                   'run_deterministic.py','check_causal_ledger.py'):
        shutil.copy2(ENGINE/'scripts'/script, runtime/'scripts'/script)
    shutil.copy2(ENGINE/'MODEL_TIERS.yaml',runtime/'MODEL_TIERS.yaml')
    # _layout_config.py resolve os defaults como <raiz>/templates/, então o
    # template precisa acompanhar os scripts no runtime.
    (runtime/'templates').mkdir(parents=True,exist_ok=True)
    shutil.copy2(ENGINE/'templates/KDP_LAYOUT_DEFAULTS.yaml',runtime/'templates/KDP_LAYOUT_DEFAULTS.yaml')
    shutil.copy2(ENGINE/'templates/TEXT_QUALITY_DEFAULTS.yaml',runtime/'templates/TEXT_QUALITY_DEFAULTS.yaml')
    shutil.copy2(ENGINE/'templates/FACE_CANON_TEMPLATE.md',runtime/'templates/FACE_CANON_TEMPLATE.md')
    shutil.copy2(ENGINE/'templates/EXECUTION_PROFILES.yaml',runtime/'templates/EXECUTION_PROFILES.yaml')
    shutil.copy2(ENGINE/'templates/CAUSAL_LEDGER_TEMPLATE.yaml',runtime/'templates/CAUSAL_LEDGER_TEMPLATE.yaml')
    # custom validators
    if (book/'validators').exists(): shutil.copytree(book/'validators',runtime/'book/validators',dirs_exist_ok=True)
    # AGENTS
    md=graph['metadata']
    (runtime/'AGENTS.md').write_text(f'''# Runtime: {md["title"]}\n\nGenerated by PEDRO_ARTE_LIVING_BOOK_ENGINE_v1.\n\nRead TASK_GRAPH.yaml, IMPLEMENT.md and book/BOOK_SPEC.yaml before task execution.\n\nThe repository is memory. Only execute READY tasks. Explicitly spawn declared subagents. Stop, fix and revalidate blocking failures. CANON_GUARDIAN owns canon mutations. LEAD_NOVELIST owns final prose. EXECUTIVE_EDITOR resolves conflicts.\n''',encoding='utf-8')
    # scoped instructions
    (runtime/'manuscript/AGENTS.md').write_text('Final prose is owned by LEAD_NOVELIST. Review agents report; they do not silently rewrite manuscript files. Obey book canon, voice reference, chapter briefs and immutable rules.\n',encoding='utf-8')
    (runtime/'images/AGENTS.md').write_text('Obey VISUAL_LIFE_SPEC, IMAGE_BIOME, FACE_CANON and CHARACTER_VISUAL_BIBLE. A recurring face failing identity QA is rejected, not rationalized.\n',encoding='utf-8')
    (runtime/'sound/AGENTS.md').write_text('Living Sound is physiological. Derive sound from the frozen manuscript, reader vitals and the active book sound profile. Do not default to generic sentimental music.\n',encoding='utf-8')
    (runtime/'media/AGENTS.md').write_text('The media package is incomplete until the actual KDP JPEG cover and exactly five commercial Instagram Story JPEGs exist and GATE_MEDIA_ASSETS passes. Briefs or ideas never substitute for final pixel assets. Obey canon, legal positioning, KDP requirements and platform-safe typography.\n',encoding='utf-8')
    (runtime/'outputs/AGENTS.md').write_text('Reader-facing outputs must contain no prompts, agent names, task metadata, markdown artifacts or internal review comments.\n',encoding='utf-8')
    # DARK_ROMANCE_CANON_ARCHITECT (docs/sdd/DARK_ROMANCE_CANON_ARCHITECT_SDD_v0.1.md).
    # Detectado a partir do proprio grafo (nao de um parametro novo): T021 so
    # existe quando features.causal_ledger.enabled=true. Livros sem a feature
    # nao ganham este arquivo, exatamente como hoje. O runbook completo mora em
    # engine/templates/ (Slice 5) para nao duplicar o mesmo texto em codigo
    # Python e ficar legivel/editavel como qualquer outro template do motor.
    if any(t.get('id')=='T021_LEDGER_SNAPSHOT' for t in graph['spec']['tasks']):
        shutil.copy2(ENGINE/'templates/CAUSAL_LEDGER_RUNBOOK.md', runtime/'canon/AGENTS.md')
    # BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM (docs/sdd/BEA_HALDEN_VISUAL_NARRATIVE_SYSTEM_SDD_v0.1.md).
    # Mesma deteccao via grafo (nao parametro novo): T042 so existe quando
    # features.visual_narrative.enabled=true.
    if any(t.get('id')=='T042_VISUAL_DISCOVERY' for t in graph['spec']['tasks']):
        vn_spec=load_yaml(book/'BOOK_SPEC.yaml')['spec']
        vn_cfg=vn_spec.get('features',{}).get('visual_narrative') or {}
        dna_src=REPO/'authors'/vn_cfg['author_profile']/f"AUTHOR_VISUAL_DNA.v{vn_cfg['author_dna_version']}.yaml"
        (runtime/'author').mkdir(parents=True,exist_ok=True)
        shutil.copy2(dna_src,runtime/'author'/dna_src.name)
        shutil.copy2(ENGINE/'scripts/check_visual_canon.py',runtime/'scripts/check_visual_canon.py')
        shutil.copy2(ENGINE/'templates/EDITION_CAPABILITIES.yaml',runtime/'templates/EDITION_CAPABILITIES.yaml')
        shutil.copy2(ENGINE/'templates/PRINT_GEOMETRY.yaml',runtime/'templates/PRINT_GEOMETRY.yaml')
        shutil.copy2(ENGINE/'templates/VISUAL_NARRATIVE_RUNBOOK.md',runtime/'canon/VISUAL_AGENTS.md')
    (runtime/'logs/COST_LEDGER.md').write_text(
        '# Cost Ledger\n\n'
        'Uma linha por tarefa concluida. Nao reordene as colunas -- '
        '`scripts/cost_report.py` depende da posicao fixa.\n\n'
        '| task_id | phase | owner | model_tier | model_actual | tokens_in | tokens_out | cost_usd | wall_seconds | state |\n'
        '|---|---|---|---|---|---|---|---|---|---|\n',
        encoding='utf-8')
    (runtime/'logs/AGENTS.md').write_text(
        'Ao marcar uma tarefa como concluida (`scripts/runtime_taskgraph.py mark`), adicione tambem uma linha a '
        'COST_LEDGER.md com o custo real dessa chamada: task_id, phase, owner, model_tier (o mesmo declarado no '
        'TASK_GRAPH.yaml para essa tarefa, quando presente), model_actual (o modelo de fato usado), tokens_in, '
        'tokens_out, cost_usd, wall_seconds e state. Use `MODEL_TIERS.yaml` para resolver o modelo concreto de um '
        'model_tier. Nao pule esse registro: sem ele, `scripts/cost_report.py` nao consegue medir se a dosagem de '
        'modelo esta economizando de verdade. Rode `python scripts/cost_report.py` a qualquer momento para ver o '
        'total acumulado por fase, por agente e por tier.\n',
        encoding='utf-8')

def cmd_validate_engine(a):
    g=load_yaml(ENGINE/'ENGINE_GRAPH.yaml'); errors=validate_engine_data(g); pe,c=validate_profiles(ENGINE/'agents'); errors+=pe
    if errors:
        print('ENGINE INVALID'); [print('-',e) for e in errors]; return 1
    print(f'ENGINE VALID | generic agents: {c} | version: {g["metadata"]["version"]}'); return 0

def cmd_validate_book(a):
    b=get_book(a.book); s=load_yaml(b/'BOOK_SPEC.yaml'); x=load_yaml(b/'BOOK_GRAPH.yaml'); errors=validate_book_data(b,s,x); pe,c=validate_profiles(b/'agents'); errors+=pe
    if errors:
        print('BOOK PACKAGE INVALID'); [print('-',e) for e in errors]; return 1
    print(f'BOOK PACKAGE VALID | {s["metadata"]["title"]} | chapters: {s["metadata"]["chapter_count"]} | book agents: {c}'); return 0

def cmd_compose(a):
    b=get_book(a.book); s=load_yaml(b/'BOOK_SPEC.yaml'); runtime=REPO/'runtime'/s['metadata']['slug'] if not a.runtime else get_book(a.runtime)
    g=build_standard_graph(b); errors=validate_graph(g,runtime)
    if errors:
        print('COMPOSE FAILED'); [print('-',e) for e in errors]; return 1
    copy_runtime(b,runtime,g)
    # init state with runtime helper
    import subprocess
    r=subprocess.run([sys.executable,str(runtime/'scripts/runtime_taskgraph.py'),'init-state'],cwd=runtime,text=True,capture_output=True)
    if r.returncode: print(r.stdout,r.stderr); return r.returncode
    print(f'COMPOSED {rel(runtime)} | tasks: {len(g["spec"]["tasks"])} | gates: {len(g["spec"]["gates"])} | agents: {len(g["spec"]["agents"])}')
    return 0

def cmd_smoke(a):
    rt=get_book(a.runtime); errors=[]
    for p in ['TASK_GRAPH.yaml','AGENTS.md','IMPLEMENT.md','book/BOOK_SPEC.yaml','project_state/PROJECT_STATUS.yaml','scripts/runtime_taskgraph.py','scripts/validate_media_assets.py']:
        if not (rt/p).exists(): errors.append(f'missing {p}')
    if not errors:
        g=load_yaml(rt/'TASK_GRAPH.yaml'); errors+=validate_graph(g,rt)
        pe,c=validate_profiles(rt/'.codex/agents'); errors+=pe
        import subprocess
        r=subprocess.run([sys.executable,str(rt/'scripts/runtime_taskgraph.py'),'ready'],cwd=rt,text=True,capture_output=True)
        ready=[x for x in r.stdout.splitlines() if x.startswith('T')]
        if ready!=['T000_INITIALIZE_RUNTIME']: errors.append(f'initial READY tasks are {ready}, expected T000_INITIALIZE_RUNTIME')
        tasks={t['id']:t for t in g['spec']['tasks']}
        media_gate=g['spec']['gates'].get('GATE_MEDIA_ASSETS',{})
        if tasks.get('T801_KDP_BOOK_COVER',{}).get('outputs')!=['/media/outputs/cover/BOOK_COVER_KDP.jpg','/media/outputs/COVER_PRODUCTION_REPORT.md']: errors.append('KDP cover output contract is missing or changed')
        expected_stories=[f'/media/outputs/instagram_stories/story_{i:02d}.jpg' for i in range(1,6)]
        story_outputs=tasks.get('T802_INSTAGRAM_STORIES',{}).get('outputs',[])
        if story_outputs[:5]!=expected_stories or len([x for x in story_outputs if x.endswith('.jpg')])!=5: errors.append('Instagram Story output contract must declare exactly story_01.jpg..story_05.jpg')
        if media_gate.get('requires')!=['T801_KDP_BOOK_COVER','T802_INSTAGRAM_STORIES'] or 'V_MEDIA_ASSET_PACKAGE' not in (media_gate.get('custom_validators') or []): errors.append('GATE_MEDIA_ASSETS contract is invalid')
    if errors:
        print('SMOKE TEST FAILED'); [print('-',e) for e in errors]; return 1
    print(f'SMOKE TEST OK | runtime: {rt.name} | first READY: T000_INITIALIZE_RUNTIME | agents: {c} | tasks: {len(g["spec"]["tasks"])} | gates: {len(g["spec"]["gates"])}'); return 0

def cmd_ready(a):
    rt=get_book(a.runtime); import subprocess
    return subprocess.run([sys.executable,str(rt/'scripts/runtime_taskgraph.py'),'ready'],cwd=rt).returncode

def cmd_new_book(a):
    b=REPO/'books'/a.slug
    if b.exists(): print(f'Book exists: {b}',file=sys.stderr); return 2
    (b/'agents').mkdir(parents=True); (b/'validators').mkdir(); (b/'seeds').mkdir()
    titles={i:f'Capítulo {i}' for i in range(1,a.chapters+1)}
    # reasonable 5 waves
    import math
    size=math.ceil(a.chapters/5); waves=[list(range(i,min(i+size,a.chapters+1))) for i in range(1,a.chapters+1,size)]
    sp={'apiVersion':'pedroarte.livingbooks/v1','kind':'BookSpec','metadata':{'slug':a.slug,'title':a.title,'author':'Pedro Arte','language':'pt-BR','genre':'TO_DEFINE','chapter_count':a.chapters,'version':'0.1.0'},'spec':{'execution_profile':'STANDARD','creative_sources':['CREATIVE_BRIEF.md','BOOK_CONSTITUTION.md'],'chapter_titles':titles,'movements':[],'writing_waves':waves,'voice_calibration_chapters':[1,2] if a.chapters>=2 else [1],'lead_novelist_owned_chapters':[1,a.chapters],'features':{'living_book':{'enabled':True},'images':{'enabled':True,'primary_per_chapter':1,'face_consistency_required':True},'living_sound':{'enabled':True},'translation_preparation':{'enabled':True,'target':'en'},'kdp_docx':{'enabled':True},'media_package':{'enabled':True}},'agent_packs':{'book_agents':{},'character_support':['CHILD_VOICE_GUARDIAN'],'canon_guardians':[],'wave_reviewers':['PLOT_CONTINUITY_REVIEWER','CHARACTER_CONTINUITY_REVIEWER','WORLD_RULES_REVIEWER','EMOTIONAL_EDITOR','GENRE_GUARDIAN','ANTI_MANIPULATION_GUARDIAN'],'voice_reviewers':['LITERARY_STYLE_GUARDIAN','DIALOGUE_DIRECTOR','PHYSICALITY_AND_BODY_AGENT','ANTI_MANIPULATION_GUARDIAN'],'critic_panel':['LITERARY_CRITIC','CINEMA_CRITIC','COMMERCIAL_EDITOR_CRITIC','REPETITION_AND_CLICHE_REVIEWER','DEVELOPMENTAL_EDITOR','PLOT_CONTINUITY_REVIEWER'],'line_reviewers':['DIALOGUE_DIRECTOR','LITERARY_STYLE_GUARDIAN','SUBTEXT_EDITOR','SENSORY_AGENT','PHYSICALITY_AND_BODY_AGENT','TYPOGRAPHY_TEXT_REVIEWER','REPETITION_AND_CLICHE_REVIEWER']},'immutable_rules_file':'immutable_rules.yaml','protected_scenes_file':'protected_scenes.yaml','chapter_architecture_file':'chapter_architecture.yaml','quality_profile_file':'quality_profile.yaml','capability_requirements_file':'capability_requirements.yaml','world_rules_seed':'seeds/WORLD_RULES_SEED.md','symbol_priorities':[],'acoustic_environment_organism':'TO_DEFINE','book_specific_rejection_states':[]}}
    save_yaml(b/'BOOK_SPEC.yaml',sp); save_yaml(b/'BOOK_GRAPH.yaml',{'apiVersion':'pedroarte.livingbooks/v1','kind':'BookGraphExtensions','metadata':{'slug':a.slug,'version':'0.1.0'},'spec':{'custom_validators':[],'gate_extensions':{},'additional_tasks':[]}}); save_yaml(b/'immutable_rules.yaml',{'apiVersion':'pedroarte.livingbooks/v1','kind':'ImmutableRules','rules':[]}); save_yaml(b/'protected_scenes.yaml',{'apiVersion':'pedroarte.livingbooks/v1','kind':'ProtectedScenes','scenes':[]}); save_yaml(b/'quality_profile.yaml',{'apiVersion':'pedroarte.livingbooks/v1','kind':'BookQualityProfile','chapter_scores':{},'risk_scores':{}}); save_yaml(b/'capability_requirements.yaml',{'apiVersion':'pedroarte.livingbooks/v1','kind':'CapabilityRequirements','capabilities':{}}); save_yaml(b/'chapter_architecture.yaml',{'apiVersion':'pedroarte.livingbooks/v1','kind':'ChapterArchitecture','chapters':[{'number':i,'title':titles[i],'movement':'TO_DEFINE','function':'TO_DEFINE'} for i in range(1,a.chapters+1)]})
    (b/'CREATIVE_BRIEF.md').write_text('# Creative Brief\n\nTO_DEFINE\n',encoding='utf-8'); (b/'BOOK_CONSTITUTION.md').write_text('# Book Constitution\n\nTO_DEFINE\n',encoding='utf-8'); (b/'seeds/WORLD_RULES_SEED.md').write_text('# World Rules Seed\n\nTO_DEFINE\n',encoding='utf-8'); (b/'visual_profile.md').write_text('# Visual Profile\n\nTO_DEFINE\n',encoding='utf-8'); (b/'sound_profile.md').write_text('# Sound Profile\n\nTO_DEFINE\n',encoding='utf-8'); (b/'AGENTS.md').write_text(f'# Book package: {a.title}\n\nBook-specific literary DNA only.\n',encoding='utf-8')
    print(f'CREATED {rel(b)}'); return 0

def main():
    p=argparse.ArgumentParser(description='Pedro Arte Living Book Engine v1'); sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('validate-engine').set_defaults(fn=cmd_validate_engine)
    q=sub.add_parser('validate-book'); q.add_argument('--book',required=True); q.set_defaults(fn=cmd_validate_book)
    q=sub.add_parser('compose'); q.add_argument('--book',required=True); q.add_argument('--runtime'); q.set_defaults(fn=cmd_compose)
    q=sub.add_parser('smoke-test'); q.add_argument('--runtime',required=True); q.set_defaults(fn=cmd_smoke)
    q=sub.add_parser('ready'); q.add_argument('--runtime',required=True); q.set_defaults(fn=cmd_ready)
    q=sub.add_parser('new-book'); q.add_argument('--slug',required=True); q.add_argument('--title',required=True); q.add_argument('--chapters',required=True,type=int); q.set_defaults(fn=cmd_new_book)
    a=p.parse_args(); return a.fn(a)
if __name__=='__main__': raise SystemExit(main())
