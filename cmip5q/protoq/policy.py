"""
Maps Centre ids to the Django auth group which controls access to that centre.

Unfortunately there seems to be no alternative to hard-wiring the centre id into
this table.

"""

# Exported from NDG-security policy file
centre_to_group = {
    1: 'cmip5q_ncas',
    3: 'cmip5q_ncar',
    5: 'cmip5q_mohc',
    7: 'cmip5q_gfdl',
    9: 'cmip5q_ipsl',
    11: 'cmip5q_mpim',
    13: 'cmip5q_admin',
    15: 'cmip5q_any',
    17: 'cmip5q_norclim',
    19: 'cmip5q_mri',
    21: 'cmip5q_utnies',
    23: 'cmip5q_inm',
    25: 'cmip5q_nimr',
    27: 'cmip5q_lasg',
    29: 'cmip5q_csiro',
    31: 'cmip5q_cnrm_cerfacs',
    33: 'cmip5q_cccma',
    35: 'cmip5q_cawcr',
    39: 'cmip5q_any',
    37: 'cmip5q_cmabcc',
    41: 'cmip5q_ecearth',
    113: 'cmip5q_nasagiss',
    121: 'cmip5q_ccsm',
    123: 'cmip5q_cmcc',
    125: 'cmip5q_gcess',
    127: 'cmip5q_fio',
    129: 'cmip5q_rsmas',
    202: 'cmip5q_ncep',
    209: 'cmip5q_nasagmao',
    211: 'cmip5q_lasg',
    217: 'cmip51_inpe',
}
