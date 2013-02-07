# -*- coding: utf-8 -*-
from django.conf import settings

NORTH_AMERICA = 0
LATIN_AMERICA = 1
EMEA = 2  # Europe, Middle East, Africa
APAC = 3  # Asia Pacific


# Map region values to countries.
regions = {
    NORTH_AMERICA: (
        'ca',  # Canada
        'us',  # United States
    ),
    LATIN_AMERICA: (
        'ag',  # Antigua and Barbuda
        'ai',  # Anguilla
        'an',  # Netherlands Antilles
        'ar',  # Argentina
        'aw',  # Aruba
        'bb',  # Barbados
        'bl',  # Saint Barthélemy
        'bo',  # Bolivia
        'br',  # Brazil
        'bs',  # Bahamas
        'bz',  # Belize
        'cl',  # Chile
        'co',  # Colombia
        'cr',  # Costa Rica
        'dm',  # Dominica
        'do',  # Dominican Republic
        'ec',  # Ecuador
        'fk',  # Falkland Islands (Malvinas)
        'gd',  # Grenada
        'gf',  # French Guiana
        'gp',  # Guadeloupe
        'gs',  # South Georgia and the South Sandwich Islands
        'gt',  # Guatemala
        'gy',  # Guyana
        'hn',  # Honduras
        'ht',  # Haiti
        'jm',  # Jamaica
        'kn',  # Saint Kitts and Nevis
        'ky',  # Cayman Islands
        'lc',  # Saint Lucia
        'mf',  # Saint Martin
        'mx',  # Mexico
        'mq',  # Martinique
        'ms',  # Montserrat
        'ni',  # Nicaragua
        'pa',  # Panama
        'pe',  # Peru
        'pm',  # Saint Pierre and Miquelon
        'pr',  # Puerto Rico
        'py',  # Paraguay
        'sh',  # Saint Helena
        'sr',  # Suriname
        'sv',  # El Salvador
        'tc',  # Turks and Caicos Islands
        'tt',  # Trinidad and Tobago
        'uy',  # Uruguay
        'vc',  # Saint Vincent and the Grenadines
        've',  # Venezuela
        'vg',  # British Virgin Islands
        'vi',  # U.S. Virgin Islands
    ),
    EMEA: (
        'ad',  # Andorra
        'ae',  # U.A.E.
        'af',  # Afghanistan
        'al',  # Albania
        'am',  # Armenia
        'ao',  # Angola
        'at',  # Austria
        'ax',  # Åland Islands
        'az',  # Azerbaijan
        'ba',  # Bosnia and Herzegovina
        'be',  # Belgium
        'bf',  # Burkina Faso
        'bg',  # Bulgaria
        'bh',  # Bahrain
        'bi',  # Burundi
        'bj',  # Benin
        'bt',  # Bhutan
        'bw',  # Botswana
        'by',  # Belarus
        'cd',  # Congo-Kinshasa
        'cf',  # Central African Republic
        'cg',  # Congo-Brazzaville
        'ch',  # Switzerland
        'ci',  # Ivory Coast
        'cm',  # Cameroon
        'cv',  # Cape Verde
        'cy',  # Cyprus
        'cz',  # Czech Republic
        'de',  # Germany
        'dj',  # Djibouti
        'dk',  # Denmark
        'dz',  # Algeria
        'ee',  # Estonia
        'eg',  # Egypt
        'eh',  # Western Sahara
        'er',  # Eritrea
        'es',  # Spain
        'et',  # Ethiopia
        'fi',  # Finland
        'fo',  # Faroe Islands
        'fr',  # France
        'ga',  # Gabon
        'gb',  # United Kingdom
        'ge',  # Georgia
        'gg',  # Guernsey
        'gh',  # Ghana
        'gi',  # Gibraltar
        'gl',  # Greenland
        'gm',  # Gambia
        'gn',  # Guinea
        'gq',  # Equatorial Guinea
        'gr',  # Greece
        'gw',  # Guinea-Bissau
        'hr',  # Croatia
        'hu',  # Hungary
        'ie',  # Ireland
        'il',  # Israel
        'im',  # Isle of Man
        'io',  # British Indian Ocean Territory
        'iq',  # Iraq
        'is',  # Iceland
        'it',  # Italy
        'je',  # Jersey
        'jo',  # Jordan
        'ke',  # Kenya
        'kg',  # Kyrgyzstan
        'km',  # Comoros
        'kw',  # Kuwait
        'kz',  # Kazakhstan
        'lb',  # Lebanon
        'li',  # Liechtenstein
        'lk',  # Sri Lanka
        'lr',  # Liberia
        'ls',  # Lesotho
        'lt',  # Lithuania
        'lu',  # Luxembourg
        'lv',  # Latvia
        'ly',  # Libya
        'ma',  # Morocco
        'mc',  # Monaco
        'md',  # Moldova
        'me',  # Montenegro
        'mg',  # Madagascar
        'mk',  # Macedonia, F.Y.R. of
        'ml',  # Mali
        'mr',  # Mauritania
        'mt',  # Malta
        'mu',  # Mauritius
        'mw',  # Malawi
        'mz',  # Mozambique
        'na',  # Namibia
        'ne',  # Niger
        'ng',  # Nigeria
        'nl',  # Netherlands
        'no',  # Norway
        'np',  # Nepal
        'om',  # Oman
        'pk',  # Pakistan
        'pl',  # Poland
        'ps',  # Occupied Palestinian Territory
        'pt',  # Portugal
        'qa',  # Qatar
        're',  # Reunion
        'ro',  # Romania
        'rs',  # Serbia
        'ru',  # Russian Federation
        'rw',  # Rwanda
        'sa',  # Saudi Arabia
        'sc',  # Seychelles
        'se',  # Sweden
        'si',  # Slovenia
        'sj',  # Svalbard and Jan Mayen
        'sk',  # Slovakia
        'sl',  # Sierra Leone
        'sm',  # San Marino
        'sn',  # Senegal
        'so',  # Somalia
        'st',  # Sao Tome and Principe
        'sz',  # Swaziland
        'td',  # Chad
        'tg',  # Togo
        'tj',  # Tajikistan
        'tm',  # Turkmenistan
        'tn',  # Tunisia
        'to',  # Tonga
        'tr',  # Turkey
        'tz',  # Tanzania
        'ua',  # Ukraine
        'ug',  # Uganda
        'uz',  # Uzbekistan
        'va',  # Vatican City
        'ye',  # Yemen
        'yt',  # Mayotte
        'za',  # South Africa
        'zm',  # Zambia
        'zw',  # Zimbabwe
    ),
    APAC: (
        'aq',  # Antarctica
        'as',  # American Samoa
        'au',  # Australia
        'bd',  # Bangladesh
        'bn',  # Brunei Darussalam
        'bv',  # Bouvet Island
        'cc',  # Cocos (Keeling) Islands
        'ck',  # Cook Islands
        'cn',  # China
        'cx',  # Christmas Island
        'fj',  # Fiji
        'fm',  # Micronesia
        'gu',  # Guam
        'hk',  # Hong Kong
        'hm',  # Heard Island and McDonald Islands
        'id',  # Indonesia
        'in',  # India
        'jp',  # Japan
        'kh',  # Cambodia
        'ki',  # Kiribati
        'kr',  # South Korea
        'la',  # Laos
        'mh',  # Marshall Islands
        'mm',  # Myanmar
        'mn',  # Mongolia
        'mo',  # Macao
        'mp',  # Northern Mariana Islands
        'mv',  # Maldives
        'my',  # Malaysia
        'nc',  # New Caledonia
        'nf',  # Norfolk Island
        'nr',  # Nauru
        'nu',  # Niue
        'nz',  # New Zealand
        'pf',  # French Polynesia
        'pg',  # Papua New Guinea
        'ph',  # Philippines
        'pn',  # Pitcairn
        'pw',  # Palau
        'sb',  # Solomon Islands
        'sg',  # Singapore
        'tf',  # French Southern Territories
        'th',  # Thailand
        'tk',  # Tokelau
        'tl',  # Timor-Leste
        'tv',  # Tuvalu
        'tw',  # Taiwan
        'um',  # United States Minor Outlying Islands
        'vn',  # Vietnam
        'vu',  # Vanuatu
        'wf',  # Wallis and Futuna
        'ws',  # Samoa
    ),
}


# Map country codes to region numbers.
countries = {}
for region in regions:
    for country in regions[region]:
        countries[country] = region


def get_region(country):
    return countries.get(country, None)


def get_countries(region):
    try:
        return regions[int(region)]
    except (ValueError, KeyError):
        return None
