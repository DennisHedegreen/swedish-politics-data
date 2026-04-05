from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent


BASE_FACTOR_CATALOG = {'population': {'label': 'Population',
                'metric_label': 'Population (reference count)',
                'question': 'Do larger municipalities vote differently?',
                'filename': 'population.csv',
                'comparability_status': 'country_local'},
 'age65': {'label': 'Age 65+',
           'metric_label': 'Share aged 65+ (%)',
           'question': 'Do older municipalities vote differently?',
           'filename': 'age65_pct.csv',
           'comparability_status': 'family_mapped'},
 'education': {'label': 'Education',
               'metric_label': 'Higher education share (%)',
               'question': 'Do more educated municipalities vote differently?',
               'filename': 'education.csv',
               'comparability_status': 'family_mapped'},
 'income': {'label': 'Income',
            'metric_label': 'Avg. disposable income',
            'question': 'Do wealthier municipalities vote differently?',
            'filename': 'income.csv',
            'comparability_status': 'family_mapped'},
 'turnout': {'label': 'Turnout',
             'metric_label': 'Votes cast as share of voters (%)',
             'question': 'Do high-turnout municipalities vote differently?',
             'filename': 'turnout_pct.csv',
             'comparability_status': 'family_mapped'},
 'density': {'label': 'Population density',
             'metric_label': 'Residents per km²',
             'question': 'Does dense settlement correlate with voting '
                         'behaviour?',
             'filename': 'population_density.csv',
             'comparability_status': 'country_local'},
 'cars': {'label': 'Cars',
          'metric_label': 'Passenger cars per 1,000 residents',
          'question': 'Do car-heavy (rural) areas vote differently from urban '
                      'ones?',
          'filename': 'cars_per_1000.csv',
          'comparability_status': 'country_local'}}

PARTY_METADATA = {'Arbetarepartiet-Socialdemokraterna': {'native': 'Arbetarepartiet-Socialdemokraterna',
                                        'english': 'Social Democrats',
                                        'short_native': 'Socialdemokraterna',
                                        'short_english': 'Social Democrats'},
 'Arbetarepartiet Socialdemokraterna': {'native': 'Arbetarepartiet-Socialdemokraterna',
                                        'english': 'Social Democrats',
                                        'short_native': 'Socialdemokraterna',
                                        'short_english': 'Social Democrats'},
 'Moderaterna': {'native': 'Moderaterna',
                 'english': 'Moderates',
                 'short_native': 'Moderaterna',
                 'short_english': 'Moderates'},
 'Sverigedemokraterna': {'native': 'Sverigedemokraterna',
                         'english': 'Sweden Democrats',
                         'short_native': 'Sverigedemokraterna',
                         'short_english': 'Sweden Democrats'},
 'Vänsterpartiet': {'native': 'Vänsterpartiet',
                    'english': 'Left Party',
                    'short_native': 'Vänsterpartiet',
                    'short_english': 'Left Party'},
 'Centerpartiet': {'native': 'Centerpartiet',
                   'english': 'Centre Party',
                   'short_native': 'Centerpartiet',
                   'short_english': 'Centre Party'},
 'Kristdemokraterna': {'native': 'Kristdemokraterna',
                       'english': 'Christian Democrats',
                       'short_native': 'Kristdemokraterna',
                       'short_english': 'Christian Democrats'},
 'Folkpartiet liberalerna': {'native': 'Liberalerna (tidigare Folkpartiet)',
                             'english': 'Liberals',
                             'short_native': 'Liberalerna',
                             'short_english': 'Liberals'},
 'Liberalerna (tidigare Folkpartiet)': {'native': 'Liberalerna',
                                        'english': 'Liberals',
                                        'short_native': 'Liberalerna',
                                        'short_english': 'Liberals'},
 'Miljöpartiet de gröna': {'native': 'Miljöpartiet de gröna',
                           'english': 'Green Party',
                           'short_native': 'Miljöpartiet',
                           'short_english': 'Green Party'},
 'Alternativ för Sverige': {'native': 'Alternativ för Sverige',
                            'english': 'Alternative for Sweden',
                            'short_native': 'AfS',
                            'short_english': 'AfS'},
 'Medborgerlig Samling': {'native': 'Medborgerlig Samling',
                          'english': "Citizens' Coalition",
                          'short_native': 'MED',
                          'short_english': 'MED'},
 'Nyans': {'native': 'Nyans',
           'english': 'Nuance Party',
           'short_native': 'Nyans',
           'short_english': 'Nyans'},
 'Partiet Nyans': {'native': 'Partiet Nyans',
                   'english': 'Nuance Party',
                   'short_native': 'Partiet Nyans',
                   'short_english': 'Nyans'},
 'NY REFORM (NR)': {'native': 'NY REFORM (NR)',
                    'english': 'NY REFORM (NR)',
                    'short_native': 'NY REFORM',
                    'short_english': 'NY REFORM'},
 'SKÅNEPARTIET': {'native': 'SKÅNEPARTIET',
                  'english': 'SKÅNEPARTIET',
                  'short_native': 'SKÅNEPARTIET',
                  'short_english': 'SKÅNEPARTIET'},
 'Klassiskt liberala partiet': {'native': 'Klassiskt liberala partiet',
                                'english': 'Classical Liberal Party',
                                'short_native': 'KLP',
                                'short_english': 'KLP'},
 'Feministiskt initiativ': {'native': 'Feministiskt initiativ',
                            'english': 'Feminist Initiative',
                            'short_native': 'Feministiskt initiativ',
                            'short_english': 'Feminist Initiative'},
 'Övriga partier': {'native': 'Övriga partier',
                    'english': 'Other parties',
                    'short_native': 'Övriga partier',
                    'short_english': 'Other parties'},
 'Övriga anmälda partier': {'native': 'Övriga partier',
                            'english': 'Other parties',
                            'short_native': 'Övriga partier',
                            'short_english': 'Other parties'}}


@dataclass(frozen=True)
class CountryConfig:
    country_id: str
    display_name: str
    adjective: str
    language: str
    statistics_source_name: str
    default_election_type: str
    election_label: str
    public_geography_type: str
    public_geography_label: str
    public_geography_label_plural: str
    public_geography_count: int
    supported_factors: tuple[str, ...]
    supported_elections: tuple[str, ...]
    internal_ready: bool
    public_ready: bool
    municipal_vote_path: Path
    national_vote_path: Path | None
    factor_dir: Path
    party_metadata: dict[str, dict[str, str]]
    source_note: str
    secondary_source_note: str | None = None

    def factor_catalog(self) -> list[dict[str, str]]:
        return [{**BASE_FACTOR_CATALOG[key], "key": key} for key in self.supported_factors]


COUNTRY = CountryConfig(
    country_id='sweden',
    display_name='Sweden',
    adjective='Swedish',
    language='English',
    statistics_source_name='Statistics Sweden',
    default_election_type='riksdag',
    election_label='Riksdag election',
    public_geography_type='municipality',
    public_geography_label='municipality',
    public_geography_label_plural='municipalities',
    public_geography_count=290,
    supported_factors=('population', 'age65', 'education', 'income', 'turnout', 'density', 'cars'),
    supported_elections=('riksdag',),
    internal_ready=True,
    public_ready=True,
    municipal_vote_path=ROOT / "sweden/riksdag/riksdag_party_share_by_municipality.csv",
    national_vote_path=ROOT / "sweden/riksdag/riksdag_national_vote_share.csv",
    factor_dir=ROOT / "sweden/factors",
    party_metadata=PARTY_METADATA,
    source_note='Valmyndigheten municipality election exports for 2014, 2018, and 2022 + Statistics Sweden municipal indicators',
    secondary_source_note=None,
)


def get_country_config(country_id: str) -> CountryConfig:
    if country_id != COUNTRY.country_id:
        raise KeyError(f"Unknown country_id: {country_id}")
    return COUNTRY


def list_public_countries() -> list[CountryConfig]:
    return [COUNTRY]


def list_internal_countries() -> list[CountryConfig]:
    return [COUNTRY]


def country_data_pack_exists(config: CountryConfig) -> bool:
    if not config.municipal_vote_path.exists():
        return False
    if not config.factor_dir.exists():
        return False
    return True


def _normalize_allowed_country_ids(allowed_country_ids: Iterable[str] | None) -> list[str] | None:
    if allowed_country_ids is None:
        return None
    return [country_id.strip().lower() for country_id in allowed_country_ids if country_id.strip()]


def list_exposed_countries(
    allowed_country_ids: Iterable[str] | None = None,
    *,
    allow_internal: bool = False,
    require_data_pack: bool = True,
) -> list[CountryConfig]:
    allowed = _normalize_allowed_country_ids(allowed_country_ids)
    if allowed is None:
        if require_data_pack and not country_data_pack_exists(COUNTRY):
            return []
        return [COUNTRY]
    if COUNTRY.country_id not in allowed:
        return []
    if require_data_pack and not country_data_pack_exists(COUNTRY):
        return []
    return [COUNTRY]


def list_exposed_public_countries(
    allowed_country_ids: Iterable[str] | None = None,
    require_data_pack: bool = True,
) -> list[CountryConfig]:
    return list_exposed_countries(
        allowed_country_ids,
        allow_internal=False,
        require_data_pack=require_data_pack,
    )
