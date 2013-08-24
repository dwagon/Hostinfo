aka=['site', 'location (site)', 'location']

def convert(str):
    sitemap={
        'victoria gardens': '678victoria',
        'vg': '678victoria',
        'vic.gardens': '678victoria',
        'qv': '222lonsdale',
        'surry hills': '268canterbury',
        'melbourne central e.i.s': '360lonsdale',
        'lp - liverpool st': '175liverpool',
        'liverpool st': '175liverpool',
        '175 liverpool st': '175liverpool',
        'sydney': '175liverpool',
        'co-lo exhibition street': '300exhibition',
        'co-lo': '300exhibition',
        'george st': '580george',
        '300 exhibition st': '300exhibition',
        'colo': '300exhibition',
        'exhibition st': '300exhibition',
        'dr site': '1822dandenong',
        'clayton': '1822dandenong',
        '150 lonsdale st': '150lonsdale',
        '150 lonsdale': '150lonsdale',
        '151 lonsdale': '150lonsdale',  # Doofus people
        '152 lonsdale': '150lonsdale',  # Doofus people
        '8 govan': '8govan',
        '303 montague st': '303montague',
        'brisbane': '151roma',
        'perth': '100hay',
        'hobart': '70collins',
        'adelaide': '30pirie',
        'wollongong': '90crown',
        }
    if str in ('n/a', 'none', None):
        return None
    if str and 'virtual' in str:
        return { 'type': 'virtual', 'vmtype': 'vmware' }
    if str.lower() in sitemap:
        return sitemap[str.lower()]
    Warning("Unhandled site: %s" % str)
    return str

