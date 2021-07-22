class Country:
    countries = 'Andorra (AD), Argentina (AR), American Samoa (AS), Austria (AT), Australia (AU), Åland Islands (AX), ' \
                'Bangladesh (BD), Belgium (BE), Bulgaria (BG), Bermuda (BM), Brazil (BR), Belarus (BY), Canada (CA), ' \
                'Switzerland (CH), Colombia (CO), Costa Rica (CR), Czechia (CZ), Germany (DE), Denmark (DK), ' \
                'Dominican Republic (DO), Algeria (DZ), Spain (ES), Finland (FI), Faroe Islands (FO), France (FR), ' \
                'United Kingdom of Great Britain and Northern Ireland (GB), French Guiana (GF), Guernsey (GG), ' \
                'Greenland (GL), Guadeloupe (GP), Guatemala (GT), Guam (GU), Croatia (HR), Hungary (HU), Ireland (IE), ' \
                'Isle of Man (IM), India (IN), Iceland (IS), Italy (IT), Jersey (JE), Japan (JP), Liechtenstein (LI), ' \
                'Sri Lanka (LK), Lithuania (LT), Luxembourg (LU), Latvia (LV), Monaco (MC), Republic of Moldova (MD), ' \
                'Marshall Islands (MH), The former Yugoslav Republic of Macedonia (MK), Northern Mariana Islands (MP), ' \
                'Martinique (MQ), Malta (MT), Mexico (MX), Malaysia (MY), New Caledonia (NC), Netherlands (NL), ' \
                'Norway (NO), New Zealand (NZ), Philippines (PH), Pakistan (PK), Poland (PL), Saint Pierre and Miquelon (' \
                'PM), Puerto Rico (PR), Portugal (PT), Réunion (RE), Romania (RO), Russian Federation (RU), Sweden (SE), ' \
                'Slovenia (SI), Svalbard and Jan Mayen Islands (SJ), Slovakia (SK), San Marino (SM), Thailand (TH), ' \
                'Turkey (TR), Ukraine (UA), United States of America (US), Uruguay (UY), Holy See (VA), United States ' \
                'Virgin Islands (VI), Wallis and Futuna Islands (WF), Mayotte (YT), South Africa (ZA) '

    def __init__(self):
        pass

    def getCountries(self):
        country_list = self.countries.split(",")
        countryWithShortName = ()
        for country in country_list:
            c = country.strip()
            countryTupple = (c[-3:-1], c[:-5])
            x = list(countryWithShortName)
            x.append(countryTupple)
            countryWithShortName = tuple(x)
        return countryWithShortName
