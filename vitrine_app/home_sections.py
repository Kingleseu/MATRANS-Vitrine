"""Sections repositionnables de l'accueil public."""


HOME_SECTION_LABELS = {
    'map': 'Carte des sites',
    'values': 'Nos valeurs',
    'activities': 'Nos activités',
    'identity': 'Au cœur de vos opérations',
    'partners': 'Nos clients',
    'events': 'Événements et actualités',
    'careers': 'Offres d’emploi',
}


def default_home_sections():
    return list(HOME_SECTION_LABELS)


def normalize_home_sections(value):
    """Ignore les clés inconnues et conserve chaque section une seule fois."""
    if not isinstance(value, list):
        return default_home_sections()
    order = []
    for key in value:
        if isinstance(key, str) and key in HOME_SECTION_LABELS and key not in order:
            order.append(key)
    return order + [key for key in HOME_SECTION_LABELS if key not in order]
