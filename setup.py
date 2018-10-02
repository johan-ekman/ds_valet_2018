import pandas as pd
import os
import shutil
import zipfile
import io
import requests
import xml.etree.ElementTree as ET

def folder_maker(years=['2010','2014','2018']):
    """Följande funktion skapar ett träd med mappar \
där varje reporter får sitt material. Skapar också \
mappar åt grafiken. Använder sig av relativ path."""
    
    
    if not os.path.isdir('redaktionsmaterial'):
        os.makedirs("redaktionsmaterial")

    if not os.path.isdir('data'):
        os.makedirs("data")

    if not os.path.isdir('data/resultat'):
        os.makedirs("data/resultat")

    if not os.path.isdir('data/xml_filer'):
        os.makedirs("data/xml_filer")

    for year in years:
        if not os.path.isdir(f'data/xml_filer/val_{year}'):
            os.makedirs(f'data/xml_filer/val_{year}')

    for year in years:
        if not os.path.isdir(f'data/resultat/resultat_{year}'):
            os.makedirs(f'data/resultat/resultat_{year}')

    if not os.path.isdir('redaktionsmaterial/valdata'):
        os.makedirs("redaktionsmaterial/valdata")
        os.makedirs("redaktionsmaterial/valdata/JOHAN_blockstyren")
        os.makedirs("redaktionsmaterial/valdata/JOHAN_blockstyren/grunddata")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
2_3an_blockstyren_JOHAN_D'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
2_3an_blockstyren_JOHAN_D")

    if not os.path.isdir('redaktionsmaterial/valdata/SAMUEL_kommunvalet'):
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet")
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet/\
1_partiresultat_kommunvalet_2006_till_2018")
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet/\
2_partiernas_stöd_i_kommunerna")
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet/\
2_partiernas_stöd_i_kommunerna/resultat_per_parti")
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet/\
3_största_lokala_framgångarna")
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet/\
4_starkaste_fästena")
        os.makedirs("redaktionsmaterial/valdata/SAMUEL_kommunvalet/\
5_mandatfördelning")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
så_gick_det_i_kommunerna_SAMUEL'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
så_gick_det_i_kommunerna_SAMUEL")

    if not os.path.isdir('redaktionsmaterial/valdata/HANS_landstingsvalen'):
        os.makedirs("redaktionsmaterial/valdata/HANS_landstingsvalen")
        os.makedirs("redaktionsmaterial/valdata/HANS_landstingsvalen/\
1_mandatfördelning")
        os.makedirs("redaktionsmaterial/valdata/HANS_landstingsvalen/\
2_starkaste_stödet")
        os.makedirs("redaktionsmaterial/valdata/HANS_landstingsvalen/\
3_största_lokala_framgången")
        os.makedirs("redaktionsmaterial/valdata/HANS_landstingsvalen/\
4_sjukvårdspartierna")
        os.makedirs("redaktionsmaterial/valdata/HANS_landstingsvalen/\
5_resultat_åren_2010_2018")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
så_gick_det_i_landstingen_HANS'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
så_gick_det_i_landstingen_HANS")

    if not os.path.isdir('redaktionsmaterial/valdata/MICKE_Göteborg'):
        os.makedirs("redaktionsmaterial/valdata/MICKE_Göteborg")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
Wannholt_Göteborg_MICKE'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
Wannholt_Göteborg_MICKE")

    if not os.path.isdir('redaktionsmaterial/valdata/MÅNS_KD'):
        os.makedirs("redaktionsmaterial/valdata/MÅNS_KD")
        os.makedirs("redaktionsmaterial/valdata/MÅNS_KD/1_KDs_tio_bästa")
        os.makedirs("redaktionsmaterial/valdata/MÅNS_KD/2_mest_ökning_minskning")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
KD_förlorare_vinnare_MÅNS'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
KD_förlorare_vinnare_MÅNS")

    if not os.path.isdir('redaktionsmaterial/valdata/MÅNS_KD/grundfil'):
        os.makedirs("redaktionsmaterial/valdata/MÅNS_KD/grundfil")

    if not os.path.isdir('redaktionsmaterial/valdata/PÅHL_SD'):
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD")
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD/\
1_SD_största_parti")
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD/\
1_SD_största_parti/per_parti")
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD/\
2_SD_resultat_totalt")
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD/\
3_SD_mandat")
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD/\
4_SD_mest_ökning_minskning")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
SD_så_gick_det_PÅHL'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
SD_så_gick_det_PÅHL")

    if not os.path.isdir('redaktionsmaterial/valdata/PÅHL_SD/grundfil'):
        os.makedirs("redaktionsmaterial/valdata/PÅHL_SD/grundfil")

    if not os.path.isdir('redaktionsmaterial/valdata/\
JOHAN_majoritetskommunerna'):
        os.makedirs("redaktionsmaterial/valdata/\
JOHAN_majoritetskommunerna")

    if not os.path.isdir('redaktionsmaterial/valdata/\
JOHAN_majoritetskommunerna/grundfil'):
        os.makedirs("redaktionsmaterial/valdata/\
JOHAN_majoritetskommunerna/grundfil")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
sista_majoritetskommunerna_JOHAN_D'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
sista_majoritetskommunerna_JOHAN_D")

    if not os.path.isdir('redaktionsmaterial/valdata/CISSI_FI'):
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI")
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI/\
1_FIs_mandat")
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI/\
2_FIs_kommuner")
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI/\
3_FIs_röstandelar")
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI/\
4_FIs_mandat_landstinget")
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI/\
5_FIs_representation_landstinget")
        os.makedirs("redaktionsmaterial/valdata/CISSI_FI/\
6_FIs_röstandelar_landstinget_totalt")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
FI_hur_det_gick_CISSI'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
FI_hur_det_gick_CISSI")

    if not os.path.isdir('redaktionsmaterial/valdata/\
SAMUEL_lokala_partier'):
        os.makedirs("redaktionsmaterial/valdata/\
SAMUEL_lokala_partier")

    if not os.path.isdir('redaktionsmaterial/tabeller_till_grafik/\
de_lokala_partierna_SAMUEL'):
        os.makedirs("redaktionsmaterial/tabeller_till_grafik/\
de_lokala_partierna_SAMUEL")

    if not os.path.isdir('redaktionsmaterial/valdata/\
MÅNS_valdeltagande'):
        os.makedirs("redaktionsmaterial/valdata/\
MÅNS_valdeltagande")

    if not os.path.isdir('redaktionsmaterial/valdata/\
MÅNS_valdeltagande/grundfiler'):
        os.makedirs("redaktionsmaterial/valdata/\
MÅNS_valdeltagande/grundfiler")

    if not os.path.isdir('redaktionsmaterial/\
tabeller_till_grafik/valdeltagande_MÅNS'):
        os.makedirs("redaktionsmaterial/\
tabeller_till_grafik/valdeltagande_MÅNS")

    if not os.path.isdir('redaktionsmaterial/valdata/\
PÅHL_storstäderna'):
        os.makedirs("redaktionsmaterial/valdata/\
PÅHL_storstäderna")

    if not os.path.isdir('redaktionsmaterial/\
tabeller_till_grafik/storstäderna_PÅHL'):
        os.makedirs("redaktionsmaterial/\
tabeller_till_grafik/storstäderna_PÅHL")

    if not os.path.isdir('redaktionsmaterial/valdata/\
HANS_valförlorarna'):
        os.makedirs("redaktionsmaterial/valdata/\
HANS_valförlorarna")

    if not os.path.isdir('redaktionsmaterial/\
tabeller_till_grafik/förlorarna_HANS'):
        os.makedirs("redaktionsmaterial/\
tabeller_till_grafik/förlorarna_HANS")

    if not os.path.isdir('redaktionsmaterial/valdata/\
ANNA_L_röstmagneter'):
        os.makedirs("redaktionsmaterial/valdata/\
ANNA_L_röstmagneter")

    if not os.path.isdir('redaktionsmaterial/\
tabeller_till_grafik/lokala_röstmagneter_ANNA_L'):
        os.makedirs("redaktionsmaterial/\
tabeller_till_grafik/lokala_röstmagneter_ANNA_L")

    if not os.path.isdir('redaktionsmaterial/valdata/\
NICKLAS_datawrapper'):
        os.makedirs("redaktionsmaterial/valdata/\
NICKLAS_datawrapper")

# Funktioner till hämtning och bearbetning av
# xml-filerna:

def xml_data_fetcher(count_type="prelresultat",years=['2010',
                                                      '2014',
                                                      '2018']):
    """Den här funktionen hämtar xml-filer med valdata \
för 2010, 2014 och 2018. De två första valen så är \
xml-datat från sluträkningen respektive år. I skrivande \
stund är sluträkningen för 2018 inte färdig. Parametern \
'count_type' bestämmer vilken räkning man vill hämta \
för 2018. 'prelresultat', 'valnatt' eller 'sluträkning'. \
För 2010 och 2014 är det alltid 'slutresultat'.

PARAMETERAR
-----------
count_type : vilken data som ska hämtas för valresultatet \
2018. "prelresultat" är default. Men kan sedan ändras till \
'slutresultat' när detta är färdigt. 

years : vilka år man ska hämta ifrån. Koden är byggd \
för att hämta från åren 2010-2018, så detta är default. 

"""
    
    

    for year in years:

        if os.path.isdir(f'data/xml_filer/val_{year}'):
            shutil.rmtree(f'data/xml_filer/val_{year}')

        if not os.path.isdir(f'data/xml_filer/val_{year}'):
            os.makedirs(f'data/xml_filer/val_{year}')


        if year == '2018':
            url = f"https://data.val.se/val/\
val2018/{count_type}/{count_type}.zip"
        else:
            url = f"https://data.val.se/val/\
val{year}/slutresultat/slutresultat.zip"

        request = requests.get(url)

        file = zipfile.ZipFile(io.BytesIO(request.content))
        file.extractall(f'data/xml_filer/val_{year}/')







class ExtractData:
    """Följande klass innehåller funktioner som extraherar \
information från Valmyndighetens xml-filer med valresultatet. \
"""
    import pandas as pd
    import os
    import xml.etree.ElementTree as ET
    import warnings
    warnings.filterwarnings("ignore")

    def fast_elec_calc(self, year, count_type='prelresultat'):
        """Huvudfunktionen för att ta fram valresultaten."""
        elec_types = ['K','L','R']
        for types in elec_types:
            if not os.path.isdir(f'data/resultat'):
                os.makedirs(f'data/resultat')
            if not os.path.isdir(f'data/resultat/resultat_{year}'):
                os.makedirs(f'data/resultat/resultat_{year}')
        
            if year == '2018':
                with open(f"data/xml_filer/val_{year}/\
{count_type}_00{types}.xml", encoding="ISO-8859-1") as f:
                    xml_data = f.read()
            else:
                with open(f"data/xml_filer/val_{year}/\
slutresultat_00{types}.xml", encoding="ISO-8859-1") as f:
                    xml_data = f.read()

            root_nation = [child for child in ET.XML(xml_data) \
                         if child.tag == 'NATION'][0].getchildren()

            a_list = []
            for child in root_nation:
                #print('Nivå 1', child)
                if child.tag == 'LÄN':
                    if types == 'L':
                        name = child.attrib.get('NAMN')
                        code = child.attrib.get('KOD')
                        [a_list.append(self.muni_data_fetcher(x,
                                                              year=year,
                                                              name=name,
                                                              code=code)) \
                                        for x in child \
                                        if x.tag not in ['KRETS_LANDSTING',
                                                         'KRETS_RIKSDAG',
                                                         'VALDELTAGANDE',
                                                         'SAMMANFATTNING_VALDA',
                                                         'ÖVRIGA_GILTIGA']]
                        for subchild in child:    
                            if subchild.tag == 'ÖVRIGA_GILTIGA':
                                [a_list.append(self.muni_data_fetcher(x,
                                                                      year=year,
                                                                      name=name,
                                                                      code=code)) \
                                        for x in subchild if x.tag == 'GILTIGA']
                                
                    else:
                        for subchild in child:
                            if subchild.tag == 'KRETS_RIKSDAG':
                                for subsubchild in subchild:
                                    
                                    if subsubchild.tag == 'KOMMUN':
                                    
                                        name = subsubchild.attrib.get('NAMN')
                                        code = subsubchild.attrib.get('KOD')
                                    
                                        [a_list.append(self.muni_data_fetcher(x,
                                                                         year,
                                                                         name=name,
                                                                         code=code)) \
                                             for x in subsubchild\
                                             if x.tag != 'VALDELTAGANDE']
                                    
                                        for subsubsubchild in subsubchild:
                                            if subsubsubchild.tag == \
                                                'ÖVRIGA_GILTIGA':
                                                [a_list.append(self.muni_data_fetcher(x,
                                                                                 year,
                                                                                 name=name,
                                                                                 code=code)) \
                                                 for x in subsubsubchild \
                                                    if x.tag == 'GILTIGA']
            results = pd.DataFrame(a_list)

            # Folkpartiet heter idag 'Liberalerna':
            results.loc[results.parti=='FP','parti'] = 'L'
            
            # Båstad hade omval 2015 i kommunen. 
            # Detta block kompletterar dessa siffror
            # från en fil med data från SCB. 
            # Denna ligger i meta_filer-mappen
            if (types == 'K') and (year == '2014'):
                #print(types, year)
                båstad = pd.read_excel('data/\
omval_båstad_2015.xlsx')
                for parti in båstad.parti:
                    for var in ['procent','röster','mandat']:
                        #print(parti)
                        val = båstad.loc[båstad['parti']==f'{parti}',
                                    f'{var}'].iloc[0]
                        #print(var)
                        results.loc[(results['kommun']=='Båstad')&\
                        (results['parti']==f'{parti}'),f'{var}'] = val
                        
            
            # Följande avkommenterade rader är ifall man vill
            # addera Gotland till landstingsdatat:
            #if types == 'L':
            #    results = gotland_adder(results,year)
            
            results.to_excel(f'data/resultat/resultat_{year}/\
valresultat_{year}{types}.xlsx',index=False)

    def fast_particip_calc(self, year, count_type="prelresultat"):
        """Hämtar all meta-data om valen, dvs all information om totalt antal \
röstande samt valdeltagande."""
        elec_types = ['K','L','R']
        for types in elec_types:
            
            
            if not os.path.isdir(f'data/meta_filer'):
                os.makedirs(f'data/meta_filer')
                
            
            if not os.path.isdir(f'data/meta_filer/valdeltagande'):
                os.makedirs(f'data/meta_filer/valdeltagande')
            
            if year == '2018':
                with open(f"data/xml_filer/val_{year}/\
{count_type}_00{types}.xml", 
                        encoding="ISO-8859-1") as f:
                    xml_data = f.read()
            else:
                with open(f"data/xml_filer/val_{year}/\
slutresultat_00{types}.xml", 
                        encoding="ISO-8859-1") as f:
                    xml_data = f.read()

            root_nation = [child for child in ET.XML(xml_data) \
                         if child.tag == 'NATION'][0].getchildren()

            a_list = []
            for child in root_nation:
                #print('Nivå 1', child)
                if child.tag == 'LÄN':
                    län_name = child.attrib.get('NAMN')
                    län_code = child.attrib.get('KOD')
                    län_nr_mandat = child.attrib.get('MANDAT_VALOMRÅDE')
                    if types == 'L':
                        for subchild in child:    
                            if subchild.tag == 'VALDELTAGANDE':
                                a_list.append(self.valdeltagande(län_name,
                                                            län_code,
                                                            län_nr_mandat,
                                                            subchild))

                    else:
                        for subchild in child:
                            if subchild.tag == 'KRETS_RIKSDAG':
                                for subsubchild in subchild:
                                    if subsubchild.tag == 'KOMMUN':
                                        name = \
                                            subsubchild.attrib.get('NAMN')
                                        
                                        code = \
                                            subsubchild.attrib.get('KOD')
                                        
                                        nr_mandat = \
                                            subsubchild.attrib\
                                                .get('MANDAT_VALOMRÅDE')
                                        
                                        for subsubsubchild in subsubchild:
                                            if subsubsubchild.tag == 'VALDELTAGANDE':
                                                a_list.append(\
                                                    self.valdeltagande(name,
                                                                  code,
                                                                  nr_mandat,
                                                                  subsubsubchild))
                                            
            results = pd.DataFrame(a_list)
            
            for col in ['valdeltagande','valdeltagande_fgval']:
                results[col] = self.comma_remover(results[col])
            
            results.to_excel(f'data/meta_filer/valdeltagande/\
valdeltagande_{year}{types}.xlsx',index=False)


    def all_parties(self, count_type="prelresultat"):
        """Hämtar all metadata om alla partier för åren 2006, 2010, \
2014 och 2018. Partierna för 2006 finns i samma data som för \
2010."""
        
        def partier(election,year,child):
            a_dict = {}
            a_dict['val'] = year + election
            a_dict['parti'] = child.attrib.get('FÖRKORTNING')
            a_dict['beteckning'] = child.attrib.get('BETECKNING')
            a_dict['färg'] = child.attrib.get('FÄRG')

            return a_dict
        
        elec_types = ['K','L','R']
        a_list = []
        for year in ['2010','2014','2018']:
            for types in elec_types:
                if year == '2018':
                    with open(f"data/xml_filer/val_{year}/{count_type}_00{types}.xml",
                                encoding="ISO-8859-1") as f:
                        xml_data = f.read()
                else:
                    with open(f"data/xml_filer/val_{year}/slutresultat_00{types}.xml",
                                encoding="ISO-8859-1") as f:
                        xml_data = f.read()
                [a_list.append(partier(types,year,x)) for x in \
                               ET.XML(xml_data).getchildren() if x.tag != 'NATION']

        df = pd.DataFrame(a_list)
        
        df.loc[df.parti=='FP','parti'] = 'L'
        df.loc[df.parti=='L','beteckning'] = 'Liberalerna (tidigare Folkpartiet)'
        
        df.loc[df.parti=='M','beteckning'] = 'Moderaterna'
        
        df.loc[:,['val',
                    'parti',
                    'beteckning']]\
            .to_excel('data/resultat/alla_partier.xlsx',index=False)


    def data_fetcher(self,elec_type,count_type='prelresultat'):
        import numpy as np

        partierna = pd.read_excel('data/resultat/alla_partier.xlsx')


        ph = pd.DataFrame(columns=['mandat',
                                   'mandat_fgval',
                                   'parti',
                                   'procent',
                                   'procent_fgval',
                                   'röster',
                                   'röster_fgval',
                                   'val',
                                   'beteckning'])

        for year in ['2010','2014','2018','2006']:
            if year == '2006':
                df = ph.loc[ph['val']==f'2010{elec_type}']
                df['val'] = f'{year}{elec_type}'
                df.rename(columns={'procent':'skräp',
                                   'röster':'skräp',
                                   'mandat':'skräp',
                                   'procent_fgval':'procent',
                                   'röster_fgval':'röster',
                                   'mandat_fgval':'mandat'},
                         inplace=True)
                del df['skräp']

                ph = pd.concat([ph,df])
                continue

            a_list = []

            if year == '2018':
                with open(f"data/xml_filer/val_{year}/{count_type}_00{elec_type}.xml",
                            encoding="ISO-8859-1") as f:
                    xml_data = f.read()
            else:
                with open(f"data/xml_filer/val_{year}/slutresultat_00{elec_type}.xml",
                            encoding="ISO-8859-1") as f:
                    xml_data = f.read()
            a_list=[]

            for child in ET.XML(xml_data).getchildren():
                if child.tag == 'NATION':
                    [a_list.append(self.muni_data_fetcher(x,year)) for x in \
                            child.getchildren() if x.tag not in ['OGILTIGA',
                                                                'VALDELTAGANDE',
                                                                'LÄN']]
                    #for subchild in child:
                    #    if subchild.tag == 'ÖVRIGA_GILTIGA':
                    #        [a_list.append(self.muni_data_fetcher(x,year)) for x in \
                    #        subchild.getchildren() if x.tag not in ['HANDSKRIVNA',
                    #                                                'ÖVRIGA_FGVAL']]
            # spara ned årsdatan i en df
            df = pd.DataFrame(a_list)

            # märk datan efter vilket val det gäller
            df['val'] = f'{year}{elec_type}'

            # lägg till partinamnen
            df = df.merge(partierna.loc[partierna['val']==f'{year}{elec_type}'],
                                        on=['parti','val'],
                                        how='left')

            # lägg till data med tidigare år
            ph = pd.concat([ph,df])

        # formattera nummerdata
        for col in ['procent','procent_fgval']:
            ph[col] = ph[col].fillna(0).str.replace(',','.').astype('float')

        # formattera nummerdata
        for col in ['röster','röster_fgval']:
            ph[col] = ph[col].fillna(0).astype('int')

        ph.loc[ph.parti=='FP','parti'] = 'L'
        ph.loc[ph['val']==f'2006{elec_type}',['procent_fgval',
                                              'mandat_fgval',
                                              'röster_fgval']] = np.nan
        return ph

    def macro_results(self, count_type="prelresultat"):
        """Denna funktion hämtar alla valresultat på riksnivå från xml-filerna \
för riksdata (dvs de som har namnet 00{valtyp}.xml). Valdata från dessa \
sätts här ihop till en samlad fil för resultat på riksnivå i en fil \
som heter 'alla_valresultat_2006_2018.xlsx' och ligger i mappen 'resultat'."""
        
        
        
            #df.to_excel('data/resultat/valresultat_riket.xlsx',index=False)
            
        
        df = pd.DataFrame(columns=['beteckning','mandat','mandat_fgval',
                                   'parti','procent','procent_fgval',
                                   'röster','röster_fgval','val'])
        
        for types in ['K','L','R']:
            df = pd.concat([df,self.data_fetcher(types,count_type)])
        df.loc[df['parti']=='FP','parti'] = 'L'
        df.loc[df.parti=='L','beteckning'] = 'Liberalerna (tidigare Folkpartiet)'
        #df = df.loc[df['parti']!='övriga_mindre_partier_totalt']
        df.to_excel('data/resultat/alla_valresultat_2006_2018.xlsx',index=False)

    def muni_elec_meta_data(self, year):
        """Hämtar all metadata om kommunernas valkretsar. \
Behövs för att ta reda på ifall kommunerna har en val-\
spärr på 2 (1 valkrets) eller 3 procent (>1 valkrets)."""
        
        
        def get_district_data(xml_data):
            for child in ET.XML(xml_data).getchildren():
                a_list = []
                if child.tag == 'KOMMUN':
                    kommun_name = child.attrib.get('NAMN')
                    kommun_code = child.attrib.get('KOD')
                    region_counter = \
                    len([x for x in child.getchildren() if x.tag == 'KRETS_KOMMUN'])

                    for subchild in child:
                        if subchild.tag == 'KRETS_KOMMUN':
                            a_dict = {}
                            a_dict['kommun'] = kommun_name
                            a_dict['kommunkod'] = kommun_code
                            a_dict['valkrets'] = subchild.attrib.get('NAMN')
                            a_dict['antal_valkretsar'] = region_counter
                            a_dict['antal_distrikt'] = len([child for child in subchild \
                                                     if child.tag == 'VALDISTRIKT'])

                            a_list.append(a_dict)

            return pd.DataFrame(a_list)
         
        year = str(year)
        files = os.listdir(f'data/xml_filer/val_{year}/')
        files = [file for file in files if 'K.xml' in file \
                 and not '00K.xml' in file]

        placeholder = pd.DataFrame(columns=['kommun',
                                            'kommunkod',
                                            'antal_valkretsar',
                                            'valkrets',
                                            'antal_distrikt'])
        for file in files:
            with open(f"data/xml_filer/val_{year}/{file}", encoding="ISO-8859-1") as f:
                xml_data = f.read()
            placeholder = pd.concat([placeholder,get_district_data(xml_data)])
        
        placeholder.to_excel(f'data/meta_filer/valkretsdata_{year}.xlsx',index=False)


    def muni_data_fetcher(self,child, year, name=None, code=None):
        """Den här funktionen används att sammanställa \
all valdata från xml-filerna till sammansatta \
resultatsfiler. Dessa sparas i mappen 'resultat'. \
Denna funktion används i huvudfunktionen fast_elec_calc()."""
        
        
        a_dict = {}
        if name:
            a_dict['kommun'] = name
            a_dict['kommunkod'] = code

        if child.tag == 'ÖVRIGA_GILTIGA':
            a_dict['parti'] = 'övriga_mindre_partier_totalt'
        elif child.tag == 'OGILTIGA':
            if child.attrib.get('TEXT'):
                a_dict['parti'] = child.attrib.get('TEXT')
            else:
                a_dict['parti'] = 'ogiltiga'
        else:
            a_dict['parti'] = child.attrib.get('PARTI')
        #a_dict['parti'] = child.attrib.get('PARTI')
        a_dict['mandat'] = child.attrib.get('MANDAT')
        #print('1. ',a_dict['parti'])
        #print('2. ',a_dict['mandat'])
        a_dict['mandat_fgval'] = child.attrib.get('MANDAT_FGVAL')
        a_dict['röster'] = child.attrib.get('RÖSTER')
        a_dict['röster_fgval'] = child.attrib.get('RÖSTER_FGVAL')
        a_dict['procent'] = child.attrib.get('PROCENT')
        a_dict['procent_fgval'] = child.attrib.get('PROCENT_FGVAL')
        #a_list.append(a_dict)

        return a_dict


    def gotland_adder(self,df,year):
        """Gotland räknas inte som ett landsting, därav finns \
inget formellt landstingsval på Gotland. Problem för oss \
då allmänheten ser Gotland som en region. Denna funktion \
används för att koppla landstingsdata med Gotlands \
kommundata. Denna funktion används inte längre då vi \
sedan valde att inte räkna Gotland bland landstingen.
"""
        if year == '2006':
            data = pd.read_excel(f'data/resultat/resultat_2010/\
valresultat_2010K.xlsx')
            data = data.loc[:,['kommun',
                                'kommunkod',
                                'mandat_fgval',
                                'parti',
                                'procent_fgval',
                                'röster_fgval']].rename(columns={
                'mandat_fgval':'mandat',
                'procent_fgval':'procent',
                'röster_fgval':'röster'
            })
        else:
            data = pd.read_excel(f'data/resultat/resultat_{year}/\
valresultat_{year}K.xlsx')
        data = data.loc[data['kommun']=='Gotland']
        return pd.concat([df,data])

    

    def comma_remover(self,series):
        """Programmet plockar hem data från xml-filerna, \
men dess siffror är textsträngar där komma skrivs \
med ett kommatecken, inte punkt - som är standard \
för python. Därför måste dessa omformas med denna \
funktion."""
        return series.str.replace(',','.')\
                    .convert_objects(convert_numeric=True)


    


    def valdeltagande(self,name,code,nr_mandat,child):
        """Samma typ av funktion som muni_data_fetcher() ovan, \
    då den används i huvudfunktionen fast_particip_calc() \
    för att organisera valdata i en dictionary."""
        a_dict = {}
        a_dict['kommun'] = name
        a_dict['kommunkod'] = code
        a_dict['summa_mandat'] = nr_mandat
        a_dict['summa_röster'] = child.attrib.get('SUMMA_RÖSTER')
        a_dict['summa_röster_fgval'] = \
                    child.attrib.get('SUMMA_RÖSTER_FGVAL')
        
        a_dict['summa_röstberättigade'] = \
                    child.attrib.get('RÖSTBERÄTTIGADE_KLARA_VALDISTRIKT')
        
        a_dict['summa_röstberättigade_fgval'] = \
                    child.attrib.get('RÖSTBERÄTTIGADE_KLARA_VALDISTRIKT_FGVAL')
        
        a_dict['valdeltagande'] = child.attrib.get('PROCENT')
        a_dict['valdeltagande_fgval'] = child.attrib.get('PROCENT_FGVAL')
        return a_dict

    


    



    

    

