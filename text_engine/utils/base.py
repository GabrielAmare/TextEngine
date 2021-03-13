from ..core import *

BASE = 0
SYMBOLS = 100
UNITS = 200
FINAL = 300

PATTERN_LIBS = {
    "natural": [
        dict(identifier="WORD", mode="kw", expr=r"[A-Za-zÀ-ÖØ-öø-ÿ-]+", priority=UNITS),
        dict(identifier="PONCT", mode="re", expr=r"[.!?]+", priority=SYMBOLS)
    ],
    "units": [
        dict(identifier="ID", mode="re", expr=r"[a-zA-Z_][a-zA-Z0-9_]*", priority=UNITS),
        dict(identifier="FLOAT", mode="re", expr=r"[0-9]*\.[0-9]+|[0-9]+\.", priority=UNITS, value=float),
        dict(identifier="INT", mode="re", expr=r"[0-9]+", priority=UNITS, value=int),
        dict(identifier="STR", mode="re", expr=r"'.*?'", flag=16, priority=UNITS),
        dict(identifier="STR", mode="re", expr=r'".*?"', flag=16, priority=UNITS),
    ],
    "maths": [
        dict(identifier="PLUS.SYMBOL", mode="str", expr="+", priority=SYMBOLS),
        dict(identifier="MINUS.SYMBOL", mode="str", expr="-", priority=SYMBOLS),
        dict(identifier="STAR.SYMBOL", mode="str", expr="*", priority=SYMBOLS),
        dict(identifier="SLASH.SYMBOL", mode="str", expr="/", priority=SYMBOLS),
        dict(identifier="HAT.SYMBOL", mode="str", expr="^", priority=SYMBOLS),
        dict(identifier="EQUAL.SYMBOL", mode="str", expr="=", priority=SYMBOLS),
    ],
    "blocs": [
        dict(identifier="LV", mode="str", expr="<", priority=SYMBOLS),
        dict(identifier="RV", mode="str", expr=">", priority=SYMBOLS),
        dict(identifier="LP", mode="str", expr="(", priority=SYMBOLS),
        dict(identifier="RP", mode="str", expr=")", priority=SYMBOLS),
        dict(identifier="LB", mode="str", expr="[", priority=SYMBOLS),
        dict(identifier="RB", mode="str", expr="]", priority=SYMBOLS),
        dict(identifier="LS", mode="str", expr="{", priority=SYMBOLS),
        dict(identifier="RS", mode="str", expr="}", priority=SYMBOLS),
    ],
    "ponctuation": [
        dict(identifier="PERIOD", mode="str", expr=".", priority=SYMBOLS),
        dict(identifier="COMMA", mode="str", expr=",", priority=SYMBOLS),
        dict(identifier="COLON", mode="str", expr=":", priority=SYMBOLS),
        dict(identifier="SEMICOLON", mode="str", expr=";", priority=SYMBOLS),
        dict(identifier="EXCALAMATION_MARK", mode="str", expr="!", priority=SYMBOLS),
        dict(identifier="QUESTION_MARK", mode="str", expr="?", priority=SYMBOLS),
        dict(identifier="QUOTATION_MARK", mode="str", expr="'", priority=SYMBOLS),
        dict(identifier="DOUBLE_QUOTATION_MARK", mode="str", expr='"', priority=SYMBOLS),
        dict(identifier="HYPHEN", mode="str", expr="-", priority=SYMBOLS),
        dict(identifier="DASH", mode="str", expr="—", priority=SYMBOLS),
        dict(identifier="ELLPISIS", mode="str", expr="…", priority=SYMBOLS),
    ],
    "greek": [
        # http://www.cfa-digne.fr/site_sec/web/html/balises/codages_caracteres_speciaux.html
        dict(identifier="ALPHA_M", mode="str", expr="Α", priority=SYMBOLS),
        dict(identifier="ALPHA", mode="str", expr="α", priority=SYMBOLS),
        dict(identifier="BETA_M", mode="str", expr="Β", priority=SYMBOLS),
        dict(identifier="BETA", mode="str", expr="β", priority=SYMBOLS),
        dict(identifier="GAMMA_M", mode="str", expr="Γ", priority=SYMBOLS),
        dict(identifier="GAMMA", mode="str", expr="γ", priority=SYMBOLS),
        dict(identifier="DELTA_M", mode="str", expr="Δ", priority=SYMBOLS),
        dict(identifier="DELTA", mode="str", expr="δ", priority=SYMBOLS),
        dict(identifier="EPSILON_M", mode="str", expr="Ε", priority=SYMBOLS),
        dict(identifier="EPSILON", mode="str", expr="ε", priority=SYMBOLS),
        dict(identifier="ZETA_M", mode="str", expr="Ζ", priority=SYMBOLS),
        dict(identifier="ZETA", mode="str", expr="ζ", priority=SYMBOLS),
        dict(identifier="ETA_M", mode="str", expr="Η", priority=SYMBOLS),
        dict(identifier="ETA", mode="str", expr="η", priority=SYMBOLS),
        dict(identifier="THETA_M", mode="str", expr="Θ", priority=SYMBOLS),
        dict(identifier="THETA", mode="str", expr="θ", priority=SYMBOLS),
        dict(identifier="IOTA_M", mode="str", expr="Ι", priority=SYMBOLS),
        dict(identifier="IOTA", mode="str", expr="ι", priority=SYMBOLS),
        dict(identifier="KAPPA_M", mode="str", expr="Κ", priority=SYMBOLS),
        dict(identifier="KAPPA", mode="str", expr="κ", priority=SYMBOLS),
        dict(identifier="LAMBDA_M", mode="str", expr="Λ", priority=SYMBOLS),
        dict(identifier="LAMBDA", mode="str", expr="λ", priority=SYMBOLS),
        dict(identifier="MU_M", mode="str", expr="Μ", priority=SYMBOLS),
        dict(identifier="MU", mode="str", expr="μ", priority=SYMBOLS),
        dict(identifier="NU_M", mode="str", expr="Ν", priority=SYMBOLS),
        dict(identifier="NU", mode="str", expr="ν", priority=SYMBOLS),
        dict(identifier="XI_M", mode="str", expr="Ξ", priority=SYMBOLS),
        dict(identifier="XI", mode="str", expr="ξ", priority=SYMBOLS),
        dict(identifier="OMICRON_M", mode="str", expr="Ο", priority=SYMBOLS),
        dict(identifier="OMICRON", mode="str", expr="ο", priority=SYMBOLS),
        dict(identifier="PI_M", mode="str", expr="Π", priority=SYMBOLS),
        dict(identifier="PI", mode="str", expr="π", priority=SYMBOLS),
        dict(identifier="RHO_M", mode="str", expr="Ρ", priority=SYMBOLS),
        dict(identifier="RHO", mode="str", expr="ρ", priority=SYMBOLS),
        dict(identifier="SIGMA_M", mode="str", expr="Σ", priority=SYMBOLS),
        dict(identifier="SIGMAF", mode="str", expr="ς", priority=SYMBOLS),
        dict(identifier="SIGMA", mode="str", expr="σ", priority=SYMBOLS),
        dict(identifier="TAU_M", mode="str", expr="Τ", priority=SYMBOLS),
        dict(identifier="TAU", mode="str", expr="τ", priority=SYMBOLS),
        dict(identifier="UPSILON_M", mode="str", expr="Υ", priority=SYMBOLS),
        dict(identifier="UPSILON", mode="str", expr="υ", priority=SYMBOLS),
        dict(identifier="PHI_M", mode="str", expr="Φ", priority=SYMBOLS),
        dict(identifier="PHI", mode="str", expr="φ", priority=SYMBOLS),
        dict(identifier="CHI_M", mode="str", expr="Χ", priority=SYMBOLS),
        dict(identifier="CHI", mode="str", expr="χ", priority=SYMBOLS),
        dict(identifier="PSI_M", mode="str", expr="Ψ", priority=SYMBOLS),
        dict(identifier="PSI", mode="str", expr="ψ", priority=SYMBOLS),
        dict(identifier="OMEGA_M", mode="str", expr="Ω", priority=SYMBOLS),
        dict(identifier="OMEGA", mode="str", expr="ω", priority=SYMBOLS),
        dict(identifier="THETASYM", mode="str", expr="ϑ", priority=SYMBOLS),
        dict(identifier="UPSIH", mode="str", expr="ϒ", priority=SYMBOLS),
        dict(identifier="PIV", mode="str", expr="ϖ", priority=SYMBOLS),
    ],
    "maths_special": [
        # http://www.cfa-digne.fr/site_sec/web/html/balises/codages_caracteres_speciaux.html
        dict(identifier="MS_FORALL", mode="str", expr="∀", priority=SYMBOLS),
        dict(identifier="MS_PART", mode="str", expr="∂", priority=SYMBOLS),
        dict(identifier="MS_EXIST", mode="str", expr="∃", priority=SYMBOLS),
        dict(identifier="MS_EMPTY", mode="str", expr="∅", priority=SYMBOLS),
        dict(identifier="MS_NABLA", mode="str", expr="∇", priority=SYMBOLS),
        dict(identifier="MS_ISIN", mode="str", expr="∈", priority=SYMBOLS),
        dict(identifier="MS_NOTIN", mode="str", expr="∉", priority=SYMBOLS),
        dict(identifier="MS_NI", mode="str", expr="∋", priority=SYMBOLS),
        dict(identifier="MS_PROD", mode="str", expr="∏", priority=SYMBOLS),
        dict(identifier="MS_SUM", mode="str", expr="∑", priority=SYMBOLS),
        dict(identifier="MS_MINUS", mode="str", expr="−", priority=SYMBOLS),
        dict(identifier="MS_LOWAST", mode="str", expr="∗", priority=SYMBOLS),
        dict(identifier="MS_RADIC", mode="str", expr="√", priority=SYMBOLS),
        dict(identifier="MS_PROP", mode="str", expr="∝", priority=SYMBOLS),
        dict(identifier="MS_INFIN", mode="str", expr="∞", priority=SYMBOLS),
        dict(identifier="MS_ANG", mode="str", expr="∠", priority=SYMBOLS),
        dict(identifier="MS_AND", mode="str", expr="∧", priority=SYMBOLS),
        dict(identifier="MS_OR", mode="str", expr="∨", priority=SYMBOLS),
        dict(identifier="MS_CAP", mode="str", expr="∩", priority=SYMBOLS),
        dict(identifier="MS_CUP", mode="str", expr="∪", priority=SYMBOLS),
        dict(identifier="MS_INT", mode="str", expr="∫", priority=SYMBOLS),
        dict(identifier="MS_THERE4", mode="str", expr="∴", priority=SYMBOLS),
        dict(identifier="MS_SIM", mode="str", expr="∼", priority=SYMBOLS),
        dict(identifier="MS_CONG", mode="str", expr="≅", priority=SYMBOLS),
        dict(identifier="MS_ASYMP", mode="str", expr="≈", priority=SYMBOLS),
        dict(identifier="MS_NE", mode="str", expr="≠", priority=SYMBOLS),
        dict(identifier="MS_EQUIV", mode="str", expr="≡", priority=SYMBOLS),
        dict(identifier="MS_LE", mode="str", expr="≤", priority=SYMBOLS),
        dict(identifier="MS_GE", mode="str", expr="≥", priority=SYMBOLS),
        dict(identifier="MS_SUB", mode="str", expr="⊂", priority=SYMBOLS),
        dict(identifier="MS_SUP", mode="str", expr="⊃", priority=SYMBOLS),
        dict(identifier="MS_NSUB", mode="str", expr="⊄", priority=SYMBOLS),
        dict(identifier="MS_SUBE", mode="str", expr="⊆", priority=SYMBOLS),
        dict(identifier="MS_SUPE", mode="str", expr="⊇", priority=SYMBOLS),
        dict(identifier="MS_OPLUS", mode="str", expr="⊕", priority=SYMBOLS),
        dict(identifier="MS_OTIMES", mode="str", expr="⊗", priority=SYMBOLS),
        dict(identifier="MS_PERP", mode="str", expr="⊥", priority=SYMBOLS),
        dict(identifier="MS_SDOT", mode="str", expr="⋅", priority=SYMBOLS),
        dict(identifier="MS_LOZ", mode="str", expr="◊", priority=SYMBOLS),
    ]
}


def base(*cls_rules, **config):
    lexer = Lexer()

    for pattern_lib_name in config.get("pattern_libs", []):
        for pattern_config in PATTERN_LIBS.get(pattern_lib_name, []):
            lexer.add_pattern(**pattern_config)

    lexer.add_pattern("WHITESPACE", mode="re", expr="[ \t\n]+", flag=16, ignore=True, priority=FINAL)
    lexer.add_pattern("ERROR", mode="re", expr=".+", flag=16, priority=FINAL)

    parser = Parser()

    classes = set()
    for cls, *rules in cls_rules:
        classes.add(cls)
        for rule in rules:
            parser.add_builder(cls.__name__, rule)

    builder = ASTB(*classes)

    engine = Engine(lexer, parser, builder)

    return lexer, parser, builder, engine
