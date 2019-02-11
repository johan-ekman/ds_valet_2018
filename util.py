import pandas as pd
import os
import requests
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")


# Här följer alla huvudsakliga beräkningar till Dagens Samhälles 
# valnummer 2018: 

def gov_mandates(year):
    
    slask = ['BLANK','OG','OGEJ','övriga_mindre_partier_totalt']
    
    path_styren = Path('data/styren_2006_2014_formatted.xlsx')

    # hämta valdata
    styren = pd.read_excel(path_styren)
    
    # se till att alla block är i stora bokstäver
    styren.block = styren.block.str.upper().str.strip()
    
    # filtrera rätt år
    styren=styren.loc[styren.valår == year].iloc[:,1:]
    
    # sortera bort onödiga kolumner
    partistyren = styren.loc[:,['kommun','styre']]
    
    # se till att alla styren är i stora bokstäver
    partistyren.styre = partistyren.styre.str.upper()
    
    # här splittas kolumnen med styren så att varje 
    # parti får en egen kolumn
    partier=pd.concat([partistyren,
                    partistyren.styre.str.split(',',expand=True)],
                   axis=1)
    
    # kolumnen 'styre' behövs inte längre
    del partier['styre']
    
    # lägg ihop alla kolumner med partier till en enda så
    # alla partier är i samma kolumn
    partier=partier.melt(id_vars='kommun').iloc[:,[0,-1]]
    
    # bort med alla null-värden
    partier=partier.loc[~partier['value'].isnull()]
    
    # 'value' är defaultnamnet från funktionen .melt()
    # och döps därför om till 'parti'
    partier.rename(columns={'value':'parti'},inplace=True)
    
    # bort med ev mellanslag
    partier.parti=partier.parti.str.strip()
    
    # bort med alla understreck
    partier.parti=partier.parti.str.strip('_')
    
    # hämta valdata
    df = all_elec_years('K')
    
    # filtrera fram rätt år
    df=df.loc[df['valår']==year]
    
    
    
    # bort med onödiga rader med ogiltiga röster
    df=df.loc[~df['parti'].isin(slask)]
    
    # endast nödvändiga kolumner
    ph=df.loc[:,['kommun','parti','mandat','procent']]
    
    # Sätt alla partier i stora bokstäver så matchning
    # blir korrekt
    ph.parti=ph.parti.str.upper()
    
    # lägg till valdata (mandat och procent) till de
    # styrande partierna
    partier=partier.merge(ph,
                          on=['kommun','parti'],
                          how='left')
    
    # lägg till blockkategorisering
    partier=partier.merge(styren.loc[:,['kommun',
                                        'block']],
                          on='kommun',
                          how='left')\
                    .sort_values('kommun')\
                    .reset_index(drop=True)
    
    # gruppera valdata efter kommun och block och återge
    ph = partier.groupby(['kommun','block']).sum().reset_index()
    
    ph=ph.merge(df.loc[:,['kommun','summa_mandat']].drop_duplicates(),on='kommun',how='left')

    ph=ph.loc[:,['kommun','summa_mandat']]
    
    partier=partier.merge(ph,on='kommun',how='left')
    
    partier.columns=pd.Series(partier.columns)\
                        .apply(lambda x: x + f'_{year}' \
                               if x in ['procent',
                                        'mandat',
                                        'majoritet',
                                        'summa_mandat'] else x)
    
    return partier



def block_gov_count(df,\
                    value='mandat',\
                    parameter='minskat',\
                    elec_year='2018',\
                    compare_year='2014',\
                    research_data=None):
    """Räknar ut hur stor andel av alla blocksamarbeten som antingen
ökat eller minskat. Återger en lista där första tinget är en dataframe
på den formatterade data som beräkningarna bygger på (för kontroll).
Andra tinget är en jämförelse mellan de olika blockkonstellationerna.

PARAMETRAR
----------
df : Den blockdata som ska beräknas.

value : Strängvärde på vad man vill jämföra. Antingen 'mandat' eller \
'procent' (default).

parameter : Tar antingen strängvärdet 'minskat' eller 'ökat'. \
Default är 'minskning', dvs ifall inget strängvärde ges så kommer \
resultatet som visas vara hur stor andel av alla kommuner blocken \
styrde 2014 där de regerande partierna har minskat i stöd jämfört \
med 2014.

elec_year : ett årtal på den data man vill jämföra 2014 med. \
Resultatet blir den valdata som hämtas i mappen 'resultat'. Default \
är 2018."""
    
    #value = value + f'_{compare_year}'
    
    elec_year = str(elec_year)
    
    # lista över hur många partier som ingår i varje kommunstyre
    num_govs = df.kommun.value_counts().reset_index().rename(columns={'kommun':'num','index':'kommun'})
    
    # filtrering till en lista på de kommuner som har över ett parti i styret
    # för att endast beräkna på de kommunstyren som är partisamarbeten: 
    coop_govs=num_govs.loc[num_govs.num>1,'kommun']
    
    # filtrering av df:n på dessa kommuner
    df = df.loc[df.kommun.isin(coop_govs)]
    
    # hämtning av valdata att jämföra med:
    valdata = all_elec_years('K')
    
    valdata = valdata.loc[valdata['valår']==int(elec_year)]
    
    del valdata['valår']
    
    # dataformattering för att vara säker på att den importerade datan
    # är siffervärden och inte strängar:
    #valdata['procent'] = valdata['procent'].str.replace(',','.').astype('float')
    
    # Döper om kolumner:
    valdata.columns=pd.Series(valdata.columns)\
                        .apply(lambda x: x + f'_{elec_year}' \
                               if x in ['procent','mandat','summa_mandat'] else x)
    
    # Lägger till den importerade valdatan till df:n
    df = df.merge(valdata, on=['kommun','parti'], how='left')
    #return df
    df.rename(columns={'procent':f'procent_{compare_year}',
                       'mandat':f'mandat_{compare_year}'},inplace=True)
    

    # Här summeras alla partier ihop till ett blockstyre per rad:
    muni_govs = df.loc[:,['kommun',
                   'block',
                   f'procent_{compare_year}',
                   f'mandat_{compare_year}',
                   f'procent_{elec_year}',
                   f'mandat_{elec_year}']]\
            .groupby(['kommun',
                      'block']).sum().reset_index()
    
    # Vi vill också se hur stor mandatminskningen är inom blocken
    # Här bryter vi ur den infon i en ny df som används längre ned
    df2 = muni_govs.groupby(['block']).sum()
    
    # Här räknar vi ut hur stor miskningen/ökningen är per blockstyre
    # i procent:
    df2 = (((df2[f'mandat_{elec_year}'] - df2[f'mandat_{compare_year}']) /\
            df2[f'mandat_{compare_year}'])*100).round(1).reset_index()
    
    df2 = df2.rename(columns={0:'total_mandatminskning_i_procent'})
    
    # uträkning på alla olika styrsamarbeten totalt:
    blockstyren = muni_govs.block.value_counts().reset_index()\
                    .rename(columns={'index':'block',
                                     'block':'antal_styren'})
    
    # uträkning på alla olika styrsamarbeten som har tappat i procent/mandat:
    if parameter == 'minskat':
        development = muni_govs.loc[(muni_govs[f'{value}_{elec_year}'] - \
                                     muni_govs[f'{value}_{compare_year}'])<0,'block']\
                        .value_counts().reset_index()\
                        .rename(columns={'index':'block',
                                         'block':'antal_styren_som_minskat'})
        
    elif parameter == 'ökat':
        development = muni_govs.loc[(muni_govs[f'{value}_{elec_year}'] - \
                                     muni_govs[f'{value}_{compare_year}'])>0,'block']\
                        .value_counts().reset_index()\
                        .rename(columns={'index':'block',
                                         'block':'antal_styren_som_ökat'})
    
    # här bildas en samlad lista 
    blockstyren=blockstyren.merge(development,on='block', how='left')
    
    # Här räknas det ut hur stor andel av respektive blockpartisamarbete
    # som har minskat i om det nya valresultatet. Det är en procentsiffra:
    blockstyren[f'andel_som_{parameter}'] = \
    ((blockstyren[f'antal_styren_som_{parameter}'] / \
      blockstyren.antal_styren)*100).round(1)
    
    # Lägger till mandatförändringen till slutreseultatet och transponerar
    # tabellen för bättre översikt:
    blockstyren = blockstyren.merge(df2,
                                    on='block',
                                    how='left')\
                             .set_index('block')
    
    blockstyren.rename(columns={'antal_styren':f'antal styren mandatperioden {compare_year}-{elec_year}',
                                'antal_styren_som_minskat':\
                                f'antal styren som {parameter} sitt stöd i valet {elec_year}',
                                'andel_som_minskat':f'andelen av styren som {parameter}',
                                'total_mandatminskning_i_procent':\
                                f'total mandat{parameter[:-2]+"ning"} i procent, {elec_year} jämfört {compare_year}'},
                      inplace=True)
    if research_data:
        return df
    
    
    results = df.groupby(['kommun','block']).sum().reset_index().set_index('kommun')
    
    results = results.merge(valdata.loc[:,['kommun',
                                           f'summa_mandat_{elec_year}']]\
                                .drop_duplicates(),
                            on='kommun',
                            how='left')
    
    results[f'procentdiff_{compare_year}_{elec_year}'] = \
        (df[f'procent_{elec_year}']-\
         df[f'procent_{compare_year}']).round(1)
    
    results=results.merge(df.loc[:,['kommun',
                                     f'summa_mandat_{compare_year}']]\
                               .drop_duplicates(),
                           on='kommun',
                           how='left')
    
    results.loc[(results[f'mandat_{elec_year}']>\
                 (results[f'summa_mandat_{elec_year}']/2)),
                f'majoritet_{elec_year}'] = 'JA'
    results.loc[(results[f'mandat_{elec_year}']<\
                 (results[f'summa_mandat_{elec_year}']/2)),
                f'majoritet_{elec_year}'] = 'NEJ'
    
    results.loc[(results[f'mandat_{compare_year}']>\
                 (results[f'summa_mandat_{compare_year}']/2)),
                f'majoritet_{compare_year}'] = 'JA'
    results.loc[(results[f'mandat_{compare_year}']<\
                 (results[f'summa_mandat_{compare_year}']/2)),
                f'majoritet_{compare_year}'] = 'NEJ'
    
    results = results.loc[:,['kommun',
                         'block',
                         f'mandat_{compare_year}',
                         f'summa_mandat_{compare_year}',
                         f'majoritet_{compare_year}',
                         f'procent_{compare_year}',
                         f'mandat_{elec_year}',
                         f'summa_mandat_{elec_year}',
                         f'majoritet_{elec_year}',
                         f'procent_{elec_year}',
                         f'procentdiff_{compare_year}_{elec_year}']]
    
    _2014 = results.loc[results[f'majoritet_{compare_year}']=='JA','block']\
                .value_counts().reset_index()\
                .rename(columns={'index':'block',
                                 'block':f'antal_majoritetsstyren_{compare_year}'})

    _2018 = results.loc[results[f'majoritet_{elec_year}']=='JA','block']\
                .value_counts().reset_index()\
                .rename(columns={'index':'block',
                                 'block':f'antal_majoritetsstyren_{elec_year}'})
    
    styren = _2014.merge(_2018,
                         on='block',
                         how='left')
    
    blockstyren = blockstyren.reset_index()\
                        .merge(styren,
                               on='block',
                               how='left').set_index('block').T
    
    return [results,blockstyren]

def reshape_particip(df):
    df = df.loc[:,['kommun',
                   'kommunkod',
                   'summa_röster_fgval',
                   'valdeltagande_fgval']]
    
    df.rename(columns={
        'summa_röster_fgval':'summa_röster',
        'valdeltagande_fgval':'valdeltagande'
    },inplace=True)
    return df

def comma_remover(series):
    return series.str.replace(',','.').astype('float')



def all_mandates_2006(df):
    """Beräknar mandatsumma för 2006."""
    df1 = df.loc[df['valår']==2006]
    
    all_mandates = df1.groupby('kommun').sum().reset_index()\
                        .loc[:,['kommun',
                                'mandat']]\
                        .rename(columns={'mandat':'mandat_2006'})
    all_mandates['valår'] = 2006
    
    df=df.merge(all_mandates,on=['kommun','valår'],how='left')

    df.loc[df['valår']==2006,'summa_mandat'] = \
    df.loc[df['valår']==2006,'mandat_2006']

    del df['mandat_2006']
    
    return df
    #return df.merge(all_mandates,on='kommun',how='left')

def reshape(df):
    df = df.loc[:,['kommun',
                   'kommunkod',
                   'mandat_fgval',
                   'parti',
                   'procent_fgval',
                   'röster_fgval',
                   'valår']]
    
    df.rename(columns={
        'mandat_fgval':'mandat',
        'procent_fgval':'procent',
        'röster_fgval':'röster'
    },inplace=True)
    
    #df = all_mandates_2006(df)
    #print(df.summa_mandat.iloc[0])
    return df

def majority_calc(df, operator='mandat'):
    df = df.loc[df.parti != 'övriga_mindre_partier_totalt']
    df['summa_mandat'] = df['summa_mandat'].fillna(0).astype('int')
    
    mandat_totalt = df.loc[:,['kommun','valår','summa_mandat']].drop_duplicates()
    
    alliansen = ['M','C','L','KD']
    vänstern = ['S','V']
    
    slask = ['övriga_mindre_partier_totalt','OG','BLANK']

    df.loc[df['parti'].isin(vänstern),'block'] = 'V'

    df.loc[df['parti'].isin(alliansen),'block'] = 'A'

    df.loc[df['block'].isnull(),'block'] = 'Ö'
    
    df=df.groupby(['kommun','valår','block']).sum().reset_index()
    
    del df['summa_mandat']
    
    df=df.merge(mandat_totalt,on=['kommun','valår'],how='left')
    
    if operator == 'mandat':
        df.loc[df.mandat>(df.summa_mandat/2),'majoritet'] = 1

        df.loc[df.mandat<(df.summa_mandat/2),'majoritet'] = 0
    elif operator == 'procent':
        df.loc[df.procent>50,'majoritet'] = 1

        df.loc[df.procent<50,'majoritet'] = 0

        
    alliansen = df.loc[df['block']=='A'].pivot(index='kommun',columns='valår',values='majoritet')

    alliansen=alliansen.sum()

    vänstern = df.loc[df['block']=='V'].pivot(index='kommun',columns='valår',values='majoritet')

    vänstern=vänstern.sum()

    övriga = len(df.kommun.unique())-(vänstern+alliansen)
    #return df
    return pd.concat([alliansen,
               vänstern,
               övriga],axis=1).astype('int')\
        .rename(columns={0:'alliansen',
                         1:'vänstern',
                         2:'övriga'})

def all_particip_years(val):
    path_2010 = Path(f'data/meta_filer/\
valdeltagande/valdeltagande_2010{val}.xlsx')

    df = pd.DataFrame(columns=pd.read_excel(path_2010).columns)
    for year in ['2006','2010','2014','2018']:
        if year == '2006':
            data = pd.read_excel(path_2010)
            data = reshape_particip(data)
        else:
            path = Path(f'data/meta_filer/valdeltagande/valdeltagande_{year}{val}.xlsx')
            data = pd.read_excel(path)
    
        data['valår'] = int(year)
        df = pd.concat([df,data])
        
    return df.loc[:,['kommun','valår','summa_röster','valdeltagande','summa_mandat']]


def all_elec_years(val,exclude=True):
    """Denn funktion formatterar om alla grundfiler \
med respektive års valdata till en enhetlig och korrekt \
formatterad totallista för alla önskat val åren 2006-2018.

Funktionen använder sig också av följande funktioner:
- reshape(), tar bort och döper om kolumner
- comma_remover(), xml-datat plockar hem decimaler som strängar \
som pandas inte kan läsa om inte komman byts ut till punkter, \
vilket denna funktion fixar
- old_data_reshaper(), hämtar rätt siffror för år 2010 och 2014 \
(det kan nämligen vara så att somliga kommuner haft omval, denna \
funktion säkerställer att rätt jämförbart valresultat är med \
för alla kommuner).
"""
    path_2010 = Path(f'data/resultat/\
resultat_2010/valresultat_2010{val}.xlsx')
    df = pd.DataFrame(columns=pd.read_excel(path_2010).columns)
    for year in ['2006','2010','2014','2018']:
        if year == '2006':
            data = pd.read_excel(path_2010)
            data = reshape(data)
            data['procent'] = comma_remover(data['procent'])
        else:
            path = Path(f'data/resultat/resultat_{year}/valresultat_{year}{val}.xlsx')
            data = pd.read_excel(path)
            if (year == '2010') or (year == '2014'):
                data = old_data_reshaper(data,year,val)
            for col in ['procent','procent_fgval']:
                data[col] = comma_remover(data[col])
    
        data['valår'] = int(year)
        df = pd.concat([df,data])
        if exclude:
            df = df.loc[df['parti']!='övriga_mindre_partier_totalt']
        
    # slutligen, lägg till totala röster och mandat i kommunerna:
    munis_meta = all_particip_years(val)
    #munis_meta.valår = munis_meta.valår.astype('str')
    munis_meta = munis_meta.loc[:,['kommun','valår','summa_röster','summa_mandat']]

    #df.valår = df.valår.astype('str')
    df = df.merge(munis_meta, on=['kommun','valår'],how='left')
    
    df.valår = df.valår.astype('int')
    if val == 'K':
        df = all_mandates_2006(df)
    return df.loc[:,['kommun','valår','parti','röster','summa_röster','procent','mandat','summa_mandat']]

def old_data_reshaper(df,year,elec_type):
    """Den här funktionen byter ut valdata hämtade från \
alla grundfiler och byte ut dem med nästföljande vals \
valdata, då från kolumnen "[variabel]_fgval" - där "variabel" \
är mandat, procent och röster.
"""
    path = Path(f'data/resultat/\
resultat_{str(int(year)+4)}/valresultat_{str(int(year)+4)}{elec_type}.xlsx')
    new_data = pd.read_excel(path).loc[:,['kommun',
                                          'kommunkod',
                                          'parti',
                                          'mandat_fgval',
                                          'procent_fgval',
                                          'röster_fgval']]\
                                .rename(columns={
                                        'mandat_fgval':'mandat',
                                        'procent_fgval':'procent',
                                        'röster_fgval':'röster'})
    df = df.loc[:,['kommun','kommunkod','parti','mandat_fgval','procent_fgval','röster_fgval']]
    
    return df.merge(new_data,on=['kommun','kommunkod','parti'])
    
    

def elec_macro_fetcher(elec_type='L',\
                       elec_years=[2010,
                                   2014,
                                   2018],\
                       parties=['M',
                                'C',
                                'L',
                                'KD',
                                'S',
                                'V',
                                'MP',
                                'SD',
                                'FI',
                                'övriga_mindre_partier_totalt'],\
                       grouping='parti',\
                       pivot_value='procent',\
                       all_parties=False):
    path_elec_results = Path('data/resultat/alla_valresultat_2006_2018.xlsx')
    df = pd.read_excel(path_elec_results)
    
    df = df.loc[df['parti']!='Övr']

    elec_years = [str(year)+elec_type for year in elec_years]
    
    if not all_parties:
        df = df.loc[df['parti']=='övriga_mindre_partier_totalt','parti'] = 'Övr'
    else:
        df = df.loc[df['parti']==party]
    


    df = df.loc[df['val'].isin(elec_years)]
    

    #df = df.groupby([f'{grouping}','val']).sum().reset_index()
    
    df = df.pivot(index=f'{grouping}',columns='val',values=pivot_value)
    for col in df.columns:
        df.rename(columns={f'{col}':f'{pivot_value}_{col}'},inplace=True)
    return df
    




def fråga3_reformatter(df,party,year):
    """Liten funktion som döper om kolumnerna i alla df \
    som produceras i funktionen fråga_3() nedan."""
    df = df.rename(columns={party:'skillnad_jämf_riket',
                            'procent':f'valresultat_{year}'})
    return df

def fråga_3(df,andelar_riket,year,calc=True):
    
    df = df.groupby(['kommun','parti'])\
            .sum().reset_index()\
            .loc[:,['kommun',
                    'parti',
                    'procent']]

    df1 = df.pivot(index='kommun',
                  columns='parti',
                  values='procent')
    a_dict = {}
    for party in andelar_riket.parti:
        value = andelar_riket.loc[andelar_riket['parti']==party,'andelar'].iloc[0]
        
        a_dict[party] = df1[party]-value
        a_dict[party] = a_dict[party].sort_values(ascending=calc)
        a_dict[party] = a_dict[party].reset_index()
        a_dict[party]['parti'] = a_dict[party].columns[-1]
        a_dict[party] = a_dict[party].merge(df.loc[:,['kommun',
                                                       'parti',
                                                       'procent']],
                                             on=['kommun','parti'],
                                             how='left')
        a_dict[party]['andelar_riket'] = value
        a_dict[party] = fråga3_reformatter(a_dict[party],party,year)
    
    
    return a_dict

def fråga_4(df,sorter):
    a_dict = {}
    for party in df.parti.unique():
        a_dict[party] = df.loc[df['parti']==party,['kommun',
                                                   'procent']]\
                            .sort_values(by='procent',
                                         ascending=sorter).head(25)
    return a_dict

def fråga_5(df,year,year_compare,sorter=True,parties=['M',
                                                      'C',
                                                      'L',
                                                      'KD',
                                                      'S',
                                                      'V',
                                                      'MP',
                                                      'SD']):
    df = df.loc[~df['parti'].isin(['OG','BLANK'])]
    df = df.loc[df['parti'].isin(parties)]
    df = df.loc[df['valår']==year,['kommun',
                              'parti',
                              'mandat',
                              'summa_mandat']]\
        .rename(columns={'mandat':f'mandat_{year}',
                         'summa_mandat':f'summa_mandat_{year}'})\
        .merge(\
    df.loc[df['valår']==year_compare,
           ['kommun',
            'parti',
            'mandat',
            'summa_mandat']]\
            .rename(columns={'mandat':f'mandat_{year_compare}',
                             'summa_mandat':f'summa_mandat_{year_compare}'}),
               on=['kommun','parti'],
               how='left')
    
    df[f'skillnad_{year}_{year_compare}'] = \
    df[f'mandat_{year}'] - df[f'mandat_{year_compare}']
    df.sort_values(by=['parti',f'skillnad_{year}_{year_compare}'],
                   ascending=sorter,
                   inplace=True)
    return df

def valanalys(df,\
              query,\
              elec_type,\
              year=2018,\
              year_compare=2014,\
              comp_type=None,\
              mandates=None,\
              parties=None,\
              party=None,\
              sorter=True):
    """En multifunktionsfunktion. Används för Samuels jobb till valnumret. \

PARAMETRAR
----------
df : dataframe att omforma. Hämtas från funktionen all_elec_years(). 

query : vad man vill göra.

year : det år man vill få svar på/jämföra från. Default=2018.

year_compare : vilket valår man vill jämföra med. Default=2018.

parties : behövs för query='valresultat' - vilka partier ska \
sorteras fram.

party : behövs för query='jämför' - vilket parti ska sorteras fram.

sorter : behövs för query='jämför' - om ska listan sorteras stegrandes. \
Default=True (sorterar stegrandes). Resultatet blir de 15 kommuner där \
det gått sämst/bäst för partiet (som bestäms av 'party')

"""
    if not parties:
        # parties ska ha som standard att vara riksdagspartierna
        # övriga lokala partier ska klassas som 'övriga':
        parties = ['M','C','L','KD','S','V','MP','SD','FI']
    
    # Sortera bort ogiltiga röster:
    df = df.loc[~df['parti'].isin(['OG','OGEJ','BLANK'])]
    
    df.loc[~df['parti'].isin(parties),'parti'] = 'Övr'
    
    
    
    # för att se valresultatet på riksnivå (fråga 1):
    if query == 'valresultat':
        
        df = df.loc[df['valår']==year]
        
        #df.loc[~df['parti'].isin(parties),'parti'] = 'övriga' 
        
        #totalt = df.loc[:,['parti','röster']].groupby(['parti']).sum().reset_index()


        #return df
        #totalt['andelar'] = ((totalt.röster / \
        #                          df.loc[:,['kommun','summa_röster']]\
        #                          .drop_duplicates().summa_röster.sum())*100).round(1)
        
        #totalt['röster'] = totalt['röster'].astype('int')
        
        path_totalt = Path('data/resultat/alla_valresultat_2006_2018.xlsx')

        totalt=pd.read_excel(path_totalt)
        
        totalt=totalt.loc[totalt['val']==f'{year}{elec_type}']

        totalt.loc[~totalt['parti'].isin(parties),'parti'] = 'Övr'

        totalt=totalt.loc[:,['parti','röster']].groupby('parti').sum()

        if year == 2006:
            path_votes_2010 = Path(f'data/meta_filer/valdeltagande/\
valdeltagande_2010{elec_type}.xlsx')
            sum_votes=pd.read_excel(path_votes_2010).summa_röster_fgval.sum()
        else:
            path_votes = Path(f'data/meta_filer/valdeltagande/\
valdeltagande_{year}{elec_type}.xlsx')
            sum_votes=pd.read_excel(path_votes).summa_röster.sum()

        totalt['procent']=((totalt.röster/sum_votes)*100).round(1)

        totalt=totalt.loc[:,['procent','röster']].reset_index()
        
        df_test = totalt.loc[totalt['parti']!='Övr']
        
        df_test.rename(columns={f'procent':'andelar',
                                f'röster':'röster'},inplace=True)
        
        
        results = fråga_3(df,df_test,year,sorter)
        
        return [totalt,results]
    
    # Fråga 2 och 3:
    elif query == 'jämför':
        parties = ['M','C','L','KD','S','V','MP','SD']
        
        # Blanka och ogiltiga röster måste tas bort:
        df = df.loc[~df['parti'].isin(['BLANK','OG'])]
        
        df = df.loc[df.valår==year]\
            .rename(columns={'procent':f'procent_{year}'})\
            .merge(df.loc[df.valår==year_compare]\
                       .rename(columns={'procent':f'procent_{year_compare}'}),
                   on=['kommun','parti'],
                   how='left')

        df=df.loc[:,['kommun','parti',f'procent_{year_compare}',f'procent_{year}']]

        df=df.fillna(0)

        df['diff'] = df[f'procent_{year}']-df[f'procent_{year_compare}']

        df.loc[~df['parti'].isin(parties),'parti'] = 'övriga'

        df=df.groupby(['kommun','parti']).sum().reset_index()

        df=df.pivot(index='kommun',columns='parti',values='diff')
        
        a_list = []
        for col in df.columns:
            #print(col)
            a_dict = {}
            a_dict['party'] = col
            a_dict['antal_ökat_stöd'] = df.reset_index()\
                                            .loc[df.reset_index()[col]>0,
                                                 'kommun'].shape[0]
            a_dict['antal_minskat_stöd'] = df.reset_index()\
                                                .loc[df.reset_index()[col]<0,
                                                     'kommun'].shape[0]
            a_list.append(a_dict)
        
        
        
        # Följande kan okommenteras för att få hela listan för alla partier:
        
        # return df
        
        # Följande kan okommenteras om man vill använda möjligheten att se var 
        # ett parti har haft sina största motgångar/framgångar:
        if not party:
            return pd.DataFrame(a_list).loc[:,['party','antal_ökat_stöd','antal_minskat_stöd']]
        else:
            return df.loc[:,party].sort_values(ascending=sorter)
    
    # fråga 4:   
    elif query == 'strong_holds':
        
        df=df.loc[df['valår']==year]

        return fråga_4(df,sorter)
    
    elif query == 'mandates':
        return fråga_5(df,year,year_compare,sorter)
    

def bästa_kommunen(df,elec_year=2018):
    a_list = []
    for party in ['M','C','L','KD','S','V','MP','SD']:
        a_dict = {}
        resultat = valanalys(df,
                              year=elec_year,
                              elec_type='K',
                              query='strong_holds',
                              sorter=False)[party]\
            .head(1)
        a_dict['Parti'] = party
        a_dict['Starkaste fästet'] = resultat.kommun.iloc[0]
        a_dict['Kommunvalet, %'] = resultat.procent.iloc[0].round(1)
        a_list.append(a_dict)
    return pd.DataFrame(a_list).loc[:,['Parti','Starkaste fästet','Kommunvalet, %']]
    
    


def mandates_per_parti_in_total(df,elec_year=2018,compare_year=2014):
    partier = ['M','C','L','KD','S','V','MP','SD','FI']
    
    df.loc[~df['parti'].isin(partier),'parti'] = 'Övr'
    
    df = df.groupby(['valår','parti']).sum().reset_index()\
            .loc[:,['valår',
                    'parti',
                    'mandat']]
    
    df = df.loc[df['valår']==elec_year].rename(columns={
                                'mandat':f'mandat_{elec_year}'})\
        .merge(df.loc[df['valår']==compare_year].rename(columns={
                'mandat':f'mandat_{compare_year}'}),
               on='parti',
               how='left').loc[:,['parti',
                                  f'mandat_{elec_year}',
                                  f'mandat_{compare_year}']]
    
    df[f'förändring_{compare_year}_{elec_year}'] = \
        df[f'mandat_{elec_year}']-df[f'mandat_{compare_year}']
    return df

def strongest_region(df,elec_year=2018):
    partier = ['M','C','L','KD','S','V','MP','SD']
    
    df.loc[~df['parti'].isin(partier),'parti'] = 'Övr'

    df = df.loc[df['valår']==elec_year]
    a_list = []
    for party in df.parti.unique():
        a_dict = {}
        a_dict['parti'] = party
        a_dict['landsting'] = df.loc[df['parti']==party]\
                                .sort_values(by='procent',
                                         ascending=False).kommun.iloc[0]
        a_dict['valresultat_procent'] = df.loc[df['parti']==party]\
                                .sort_values(by='procent',
                                         ascending=False).procent.iloc[0].round(1)
        a_list.append(a_dict)
    return pd.DataFrame(a_list)

def vård_partier(df,pattern='vård',elec_year=2018,drop=True,acronyms=False):
    """Funktion som hittar och sorterar fram partinamn \
    ur grunddata. Parametern 'pattern' tar även regex."""
    char = pattern[0]
    pattern = pattern[1:].lower()
    char = '[' + char.upper() + char.lower() + ']'
    pattern = char+pattern
    
    vårdpartier = ['SoL','SJPG','SJV','VåfP','dsp','SJVP','BA','Rf','SPVG']
    # Sjukvårdspartiet i Jönköpings län hittar vi inte förkortningen på
    
    path_partierna = Path('data/resultat/alla_partier.xlsx')

    partierna = pd.read_excel(path_partierna)
    partierna = partierna.loc[partierna['val']==f'{str(elec_year)}L',
                              ['parti','beteckning']]
    
    partierna.parti = partierna.parti.str.upper()
    
    vårdpartier=[party.upper() for party in vårdpartier]
    
    df = df.loc[df['valår']==elec_year]
    
    df = df.merge(partierna,on='parti',how='left')
    
    if acronyms:
        return df.loc[df['parti'].isin(vårdpartier)]
    
    if drop:
        return df.loc[df.beteckning.fillna("").str.contains(pattern)].dropna()
    else:
        return df.loc[df.beteckning.fillna("").str.contains(pattern)]
    
    
def three_elec_eval(df, elec_year=2018,elec_type='L',include_gotland=False):
    if elec_type == 'L':
        if not include_gotland:
            df = df.loc[df['kommun']!='Gotland']
    
    
    return valanalys(df,query='valresultat',year=elec_year,elec_type='L')[0]\
        .rename(columns={'röster':f'röster_{str(elec_year)}',
                         'andelar':f'andelar_{str(elec_year)}'})\
        .merge(valanalys(df,query='valresultat',year=(elec_year-4),elec_type='L')[0],
              on='parti',
              how='left')\
        .rename(columns={'röster':f'röster_{str(elec_year-4)}',
                         'andelar':f'andelar_{str(elec_year-4)}'})\
        .merge(valanalys(df,query='valresultat',year=(elec_year-8),elec_type='L')[0],
              on='parti',
              how='left')\
        .rename(columns={'röster':f'röster_{str(elec_year-8)}',
                         'andelar':f'andelar_{str(elec_year-8)}'})

def muni_sorter(df,\
                elec_year=2018,\
                muni=None,\
                sort_variabel='procent',\
                sorter=False,\
                party=False):
    """Den här funktionen är skapad för att se valresultat i en kommun. \
Men den kan också användas för att kontrollera hur det gick \
för ett särskilt parti i samtliga kommuner, jämfört med förra \
valet.

PARAMETRAR
----------

df : formatterad valdata från funktionen all_elec_years().

elec_year : det valåret man önskar kontrollera. jämförelse-\
året är alltid det fyra år tidigare. Default=2018

muni : den kommun man vill kontrollera med.

sort_variabel : vilket mått man vill sortera efter. \
Default='procent'. Tar också 'mandat'

sorter : Bestämmer ifall man vill se bästa/sämsta kommuner.

party : bestämmer vilket parti man vill kontrollera. Tar \
partiförkortningar."""
    
    sort_variabel = sort_variabel + f'_{elec_year}'
    
    # Sortera bort ogiltiga röster
    df = df.loc[~df['parti'].isin(['OG','OGEJ'])]
    
    # jämför alltid med förra valet
    compare_year = elec_year-4
    
    if not party:
        # om party inte bestämts så ska all valdata från angiven
        # kommun hämtas
        df_muni = df.loc[(df['kommun']==muni)&(df['valår']==elec_year)]
    else:
        # sortera fram angivet partis alla kommuner under givna valåret
        df_muni = df.loc[(df['valår']==elec_year)&(df['parti']==party)]
    
    # hämtar partibeteckningar
    path_partierna = Path('data/resultat/alla_partier.xlsx')
    partierna = pd.read_excel(path_partierna)
    partierna = partierna.loc[partierna['val']==f'{str(elec_year)}K',
                              ['parti','beteckning']]
    
    df_muni = df_muni.merge(partierna,on='parti',how='left')
    
    df_muni = df_muni.sort_values(by='procent',ascending=False)
    
    
    if not party:
        # lägger till data från förra valet
        df_muni = df_muni.merge(df.loc[(df['kommun']==muni)&
                             (df['valår']==compare_year)]\
                          .loc[:,['parti','procent','mandat']]\
                          .rename(columns={'procent':f'procent_{compare_year}',
                                          'mandat':f'mandat_{compare_year}'}),
                      on='parti',
                      how='left')
        
    else:
        # lägger till data från förra valet
        df_muni = df_muni.merge(df.loc[df['valår']==compare_year]\
                          .loc[:,['kommun','parti','procent','mandat']]\
                          .rename(columns={'procent':f'procent_{compare_year}',
                                          'mandat':f'mandat_{compare_year}'}),
                      on=['kommun','parti'],
                      how='left')
        
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']] = \
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']].fillna(0)
    
    
    # Beräknar skillnaden i procentenheter mellan valet och 
    # jämförelsevalet fyra år tidigare
    df_muni[f'förändring_procent_{elec_year}_{compare_year}'] = \
    df_muni['procent'] - df_muni[f'procent_{compare_year}']
    
    # se till att kolumnerna mandat och röster är integers
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']] = \
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']]\
                                            .fillna(0).astype('int')
    df_muni.rename(columns={'procent':f'procent_{elec_year}',
                           'mandat':f'mandat_{elec_year}'},inplace=True)
    
    return df_muni.loc[:,['kommun',
                          'beteckning',
                          'röster',
                          f'procent_{compare_year}',
                          f'procent_{elec_year}',
                          f'förändring_procent_{elec_year}_{compare_year}',
                          f'mandat_{compare_year}',                          
                          f'mandat_{elec_year}']]\
                    .sort_values(by=sort_variabel,
                                ascending=sorter)
    
def parti_till_grafik(df,elec_type,elec_year=2018,compare_year=2014,party='KD'):
    grafik = valanalys(df,query='valresultat',year=elec_year,elec_type=elec_type)[0]\
        .merge(valanalys(df,query='valresultat',year=compare_year,elec_type=elec_type)[0],
              on='parti',how='left')

    grafik.columns = ['parti',
                      f'procent_{elec_year}{elec_type}',
                      f'röster_{elec_year}{elec_type}',
                      f'procent_{compare_year}{elec_type}',
                      f'röster_{compare_year}{elec_type}']

    grafik = grafik.loc[grafik['parti']==party,['parti',
                                      f'procent_{elec_year}{elec_type}',
                                      f'procent_{compare_year}{elec_type}']]

    grafik.columns = [col.replace('procent_','').replace(f'{elec_type}','').replace('p','P') for col in grafik.columns]

    grafik['Differens, %'] = grafik[f'{elec_year}']-grafik[f'{compare_year}']

    grafik=grafik.set_index('Parti').T

    grafik[f'{party}']=grafik[f'{party}'].round(1)
    return grafik

def party_kommuner(df=all_elec_years('K'),elec_year=2018,sorter=False,party='KD'):
    grafik=muni_sorter(df,
                       elec_year=elec_year,
                       party=party).sort_values(by=f'förändring_procent_{elec_year}_{elec_year-4}',
                                               ascending=sorter).head(10)

    förändring = [col for col in grafik.columns if 'förändring' in col]

    grafik=grafik.loc[:,['kommun',f'procent_{elec_year-4}',f'procent_{elec_year}',förändring[0]]]

    grafik=grafik.rename(columns={f'procent_{elec_year}':f'Kommunvalet {elec_year}, %',
                           förändring[0]:'Differens',
                           f'procent_{elec_year-4}':f'Kommunvalet {elec_year-4}, %'})
    
    return grafik

def weakest_strongest_party(df,elec_year=2018,max_min='max',party=None,overview=False):
    
    max_min = max_min.lower()
    
    riksdagspartier = ['M','C','L','KD','S','V','MP','SD']
    
    df = df.loc[~df['parti'].isin(['OG','OGEJ'])]
    
    df.loc[~df['parti'].isin(riksdagspartier),'parti']='Övr'
    
    if max_min == 'min':
        df = df.loc[~df['mandat'].isnull()]
    
    df = df.loc[df['valår']==elec_year]
    
    df1 = df.groupby(['kommun','parti']).sum()
    
    df1 = df1.sort_values(by='procent',ascending=False).sort_index(level=[0],sort_remaining=False)
    
    if max_min == 'max':
        highest_values = df1.groupby(level=0)\
                            .procent.max()\
                            .reset_index(drop=True)
        highest_values_party = df1.groupby(level=0).idxmax()\
                                    .procent.apply(lambda x: x[-1])\
                                    .reset_index()\
                                    .rename(columns={'procent':'parti'})
    
    elif max_min == 'min':
        highest_values = df1.groupby(level=0)\
                            .procent.min()\
                            .reset_index(drop=True)
        highest_values_party = df1.groupby(level=0).idxmin()\
                                    .procent.apply(lambda x: x[-1])\
                                    .reset_index()\
                                    .rename(columns={'procent':'parti'})
    
    df1 = pd.concat([highest_values_party,highest_values],axis=1)
    if not overview:
        if party:
            return df1.loc[df1.parti==party]
        else:
            return df1
    else:
        return df1.parti.value_counts()


def riks_mot_kommun(df_riks,df_kommun,elec_year=2018,sorter=False):
    """Denna funktion sorterar fram de kommuner där partierna \
gick svagast/starkast jämfört riksdagsvalets resultat i samma \
kommun. Det är parametern sorter som bestämmer ifall man får \
fram starkaste (sorter=False)/svagaste (sorter=True) kommunen \
jämfört riksdagsvalet."""
    a_list=[]
    for party in ['M','L','C','KD','S','V','MP','SD']:
        
        riks = valanalys(df_riks,query='valresultat',year=elec_year,elec_type='R',sorter=sorter)[1][party]\
            .loc[:,['kommun','parti',f'valresultat_{elec_year}']]\
            .rename(columns={f'valresultat_{elec_year}':f'valresultat_{elec_year}R'})

        kommun = valanalys(df_kommun,query='valresultat',year=elec_year,elec_type='K',sorter=sorter)[1][party]\
                   .loc[:,['kommun','parti',f'valresultat_{elec_year}']]\
                   .rename(columns={f'valresultat_{elec_year}':f'valresultat_{elec_year}K'})

        totalt = riks.merge(kommun,on=['kommun','parti'],how='left')
        totalt['differens'] = totalt[f'valresultat_{elec_year}K']-totalt[f'valresultat_{elec_year}R']
        totalt = totalt.sort_values('differens',ascending=sorter).head(1)
        a_dict = {}
        a_dict['Parti'] = totalt.parti.iloc[0]
        a_dict['Kommun'] = totalt.kommun.iloc[0]
        a_dict['Riksdagsvalet, %'] = totalt[f'valresultat_{elec_year}R'].iloc[0].round(1)
        a_dict['Kommunvalet, %'] = totalt[f'valresultat_{elec_year}K'].iloc[0].round(1)
        a_dict['Differens'] = totalt.differens.iloc[0]
        a_list.append(a_dict)
    return pd.DataFrame(a_list).loc[:,['Parti',
                                       'Kommun',
                                       'Riksdagsvalet, %',
                                       'Kommunvalet, %',
                                       'Differens']]
    


def party_mandate_counter(df,\
                          years=[2006,
                                 2010,
                                 2014,
                                 2018],\
                          party='SD',\
                          compare_party='S',\
                          plot=False):
    
    def reformatter(df,party,year):
        df.loc[:,['mandat','summa_mandat']] = \
        df.loc[:,['mandat','summa_mandat']].fillna(0).astype('int')
        
        summa_mandat = df.loc[df['valår']==year,['kommun',
                                                 'summa_mandat']]\
                            .drop_duplicates().summa_mandat.sum()
        
        df = df.loc[(df.parti==party)&\
                     (df.valår==year),['kommun',
                                            'parti',
                                            'mandat',
                                            'summa_mandat']]
        

        df = df.loc[:,['mandat',
                       'summa_mandat']].sum()\
                .reset_index().rename(columns={'index':f'{party}',
                                               0:f'{year}'})\
                .set_index(f'{party}').T

        df.summa_mandat = summa_mandat
        
        df['andelar_mandat'] = ((df.mandat/df.summa_mandat)*100).round(1)
        return df
    
    placeholder = pd.DataFrame(columns=['mandat','summa_mandat','andelar_mandat'])
    
    for year in years:
        placeholder = pd.concat([placeholder,reformatter(df,party,year)])
    if plot:
        df = pd.concat([party_mandate_counter(df,party=compare_party).andelar_mandat,
                          party_mandate_counter(df,party=party).andelar_mandat],axis=1)
        
        df.columns = [compare_party,party]
        
        return df.plot(kind='bar',colormap='Paired',legend=True)
        
        
        
    else:
        return placeholder
    
def party_kommuner(df=all_elec_years('K'),elec_year=2018,sorter=False,party='SD'):
    grafik=muni_sorter(df,
                       elec_year=elec_year,
                       party=party).sort_values(by=f'förändring_procent_{elec_year}_{elec_year-4}',
                                               ascending=sorter).head(10)

    förändring = [col for col in grafik.columns if 'förändring' in col]

    grafik=grafik.loc[:,['kommun',f'procent_{elec_year-4}',f'procent_{elec_year}',förändring[0]]]

    grafik=grafik.rename(columns={f'procent_{elec_year}':f'Kommunvalet {elec_year}, %',
                           förändring[0]:'Differens',
                           f'procent_{elec_year-4}':f'Kommunvalet {elec_year-4}, %'})
    
    return grafik



def majority_counter(df,years=[2006,2010,2014,2018],operator='procent',table=False,plot=False):
    
    def reformatter(df,year,operator='procent',table=False):
        
        if operator == 'procent':
            df = df.loc[(df['procent']>50)&\
                        (df['valår']==year),['kommun',
                                             'parti',
                                             'procent']]
            
        elif operator == 'mandat':
            df = df.loc[(df['mandat']>(df['summa_mandat']/2))&\
                   (df['valår']==year),['kommun',
                                        'parti',
                                        'mandat']]
        
        if table:
            df['valår'] = int(year)
            return df
        
        df = df.parti.value_counts().reset_index()
        
        df['valår'] = year
        
        df = df.groupby(['valår']).sum()\
                    .reset_index()\
                    .rename(columns={'parti':'antal_med_majoritetsparti'})
        
        if len(df['antal_med_majoritetsparti'])<1:
            df = pd.DataFrame(index=[0])
            df['valår'] = year
            df['antal_med_majoritetsparti'] = 0
            
        return df
        
    
    
    if table:
        placeholder = pd.DataFrame(columns=['kommun','parti',f'{operator}'])
    else:
        placeholder = pd.DataFrame(columns=['valår','antal_med_majoritetsparti'])
    
    for year in years:
        placeholder = pd.concat([placeholder,reformatter(df,year,operator,table)])
    
    if plot and not table:

        return placeholder.set_index('valår').plot(kind='bar',
                                                   colormap='Paired',
                                                   legend=False)
    elif plot and table:
        
        df = placeholder.set_index('valår')
        df = df.reset_index().loc[:,['valår',
                                     'parti',
                                     'kommun']]\
                        .groupby(['valår',
                                  'parti']).count()
        
        return df.reset_index().pivot(index='valår',
                                      columns='parti',
                                      values='kommun')\
                                .plot(kind='bar',
                                      stacked=True,
                                      alpha=0.6)
    else:
        return placeholder
    
def got_in_gov(val='K',\
               elec_year=2018,\
               party='FI',
               results='in'):
    
    ##################
    
    def muni_sorter(df,\
                elec_year=2018,\
                muni=None,\
                sort_variabel='procent',\
                sorter=False,\
                party=False):
        """Den här funktionen är skapad för att se valresultat i en kommun. \
    Men den kan också användas för att kontrollera hur det gick \
    för ett särskilt parti i samtliga kommuner, jämfört med förra \
    valet.

    PARAMETRAR
    ----------

    df : formatterad valdata från funktionen all_elec_years().

    elec_year : det valåret man önskar kontrollera. jämförelse-\
    året är alltid det fyra år tidigare. Default=2018

    muni : den kommun man vill kontrollera med.

    sort_variabel : vilket mått man vill sortera efter. \
    Default='procent'. Tar också 'mandat'

    sorter : Bestämmer ifall man vill se bästa/sämsta kommuner.

    party : bestämmer vilket parti man vill kontrollera. Tar \
    partiförkortningar."""

        sort_variabel = sort_variabel + f'_{elec_year}'

        # Sortera bort ogiltiga röster
        df = df.loc[~df['parti'].isin(['OG','OGEJ'])]

        # jämför alltid med förra valet
        compare_year = elec_year-4

        if not party:
            # om party inte bestämts så ska all valdata från angiven
            # kommun hämtas
            df_muni = df.loc[(df['kommun']==muni)&(df['valår']==elec_year)]
        else:
            # sortera fram angivet partis alla kommuner under givna valåret
            df_muni = df.loc[(df['valår']==elec_year)&(df['parti']==party)]

        # path conversion
        path_partierna = Path('data/resultat/alla_partier.xlsx')

        # hämtar partibeteckningar
        partierna = pd.read_excel(path_partierna)
        partierna = partierna.loc[partierna['val']==f'{str(elec_year)}K',
                                  ['parti','beteckning']]

        df_muni = df_muni.merge(partierna,on='parti',how='left')

        df_muni = df_muni.sort_values(by='procent',ascending=False)


        if not party:
            # lägger till data från förra valet
            df_muni = df_muni.merge(df.loc[(df['kommun']==muni)&
                                 (df['valår']==compare_year)]\
                              .loc[:,['parti','procent','mandat']]\
                              .rename(columns={'procent':f'procent_{compare_year}',
                                              'mandat':f'mandat_{compare_year}'}),
                          on='parti',
                          how='left')

        else:
            # lägger till data från förra valet
            df_muni = df_muni.merge(df.loc[df['valår']==compare_year]\
                              .loc[:,['kommun','parti','procent','mandat']]\
                              .rename(columns={'procent':f'procent_{compare_year}',
                                              'mandat':f'mandat_{compare_year}'}),
                          on=['kommun','parti'],
                          how='left')

        df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']] = \
        df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']].fillna(0)


        # Beräknar skillnaden i procentenheter mellan valet och 
        # jämförelsevalet fyra år tidigare
        df_muni[f'förändring_procent_{elec_year}_{compare_year}'] = \
        df_muni['procent'] - df_muni[f'procent_{compare_year}']

        # se till att kolumnerna mandat och röster är integers
        df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']] = \
        df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']]\
                                                .fillna(0).astype('int')
        df_muni.rename(columns={'procent':f'procent_{elec_year}',
                               'mandat':f'mandat_{elec_year}'},inplace=True)

        return df_muni.loc[:,['kommun',
                              'beteckning',
                              'röster',
                              f'procent_{compare_year}',
                              f'procent_{elec_year}',
                              f'förändring_procent_{elec_year}_{compare_year}',
                              f'mandat_{compare_year}',                          
                              f'mandat_{elec_year}']]\
                        .sort_values(by=sort_variabel,
                                    ascending=sorter)

    ################
    
    
    compare_year = elec_year - 4
    
    df = all_elec_years(val)
    
    df = muni_sorter(df,
                     elec_year=elec_year,
                     party=party,
                     sort_variabel='procent')
    
    results = results.lower()
    
    if results == 'in':
        return df.loc[(df[f'mandat_{compare_year}']==0)&\
                      (df[f'mandat_{elec_year}']>0)]
    elif results == 'ut':
        return df.loc[(df[f'mandat_{compare_year}']>0)&\
                      (df[f'mandat_{elec_year}']==0)]
    
def representation_FI(df,elec_years=[2018],party='FI'):
    """Sorterar fram kommuner där FI är representerade."""
    return df.loc[(df['valår'].isin(elec_years))&\
                  (df['parti']==party)&\
                  (df['mandat']>0)]

def totalprocent_jämförare(df,elec_year=2018,elec_type='K'):
    """En liten funktion som concatinerar andelarna för \
det angivna valets resultat med valet innan. Använder \
sig av funktionen valanalys()."""
    
    compare_year = (elec_year-4)
    
    return pd.concat([valanalys(df,
                                query='valresultat',
                                year=elec_year,
                                elec_type=elec_type)[0].rename(columns={
                                    'procent':f'procent_{elec_year}',
                                    'röster':f'röster_{elec_year}'
                                    }),
                        valanalys(df,
                                  query='valresultat',
                                  year=compare_year,
                                  elec_type=elec_type)[0]\
                           .loc[:,[f'procent',
                                   f'röster']].rename(columns={
                                    'procent':f'procent_{compare_year}',
                                    'röster':f'röster_{compare_year}'
                                    })],axis=1)\
                .set_index('parti')

def local_parties(df, elec_year=2018,elec_type='K',sorter=False,bort=['K', 'LPo', 'MED', 'SPI']):
    partier = ['M','C','L','KD','S','V','MP',
               'SD','FI','OG','OGEJ','BLANK']
    
    path_beteckningar = Path('data/resultat/alla_partier.xlsx')
    
    beteckningar = pd.read_excel(path_beteckningar)
    
    beteckningar = beteckningar.loc[beteckningar['val']==f'{elec_year}{elec_type}']
    beteckningar.parti=beteckningar.parti.str.upper()
    df.parti=df.parti.str.upper()
    
    df = df.loc[(~df['parti'].isin(partier))&(df['valår']==elec_year)]
    df = df.loc[~df['parti'].isin([x.upper() for x in bort])]
    df = df.loc[df['mandat']>0]
    
    df = df.merge(beteckningar,on='parti',how='left')
    
    return df.loc[:,['kommun','beteckning','procent','mandat','summa_mandat']]\
                .rename(columns={'procent':f'procent_{elec_year}',
                                 'mandat':f'mandat_{elec_year}',
                                 'summa_mandat':'kommunmandat_totalt'})\
                .sort_values(by=f'procent_{elec_year}',ascending=sorter)#.head(15)


def particip_sorter(elec_year=2018,elec_type='K',value_sorter='förändring',sorter=False):
        
    compare_year = elec_year-4
    
    if value_sorter == 'förändring':
        value_sorter = f'förändring_{compare_year}-{elec_year}'
    elif value_sorter == 'valdeltagande':
        value_sorter = f'valdeltagande_{elec_year}'
    else:
        return """Fel typ i parameterinput. 'value_sorter' måste \
vara antingen 'förändring' (för att sortera efter valdeltagande-\
förändring) eller 'valdeltagande' (för att sortera efter vilken \
kommun som hade högst/lägst valdeltagande i det angivna valet)."""
    
    path_participation = Path(f'data/meta_filer/valdeltagande/\
valdeltagande_{elec_year}{elec_type}.xlsx')
    
    df = pd.read_excel(path_participation)
    
    df[f'förändring_{compare_year}-{elec_year}'] = \
    df['valdeltagande'] - df['valdeltagande_fgval']
    
    df.rename(columns={'valdeltagande':f'valdeltagande_{elec_year}',
                       'valdeltagande_fgval':f'valdeltagande_{compare_year}'},
                 inplace=True)

    return df.loc[:,['kommun',
                     f'valdeltagande_{compare_year}',
                     f'valdeltagande_{elec_year}',
                     f'förändring_{compare_year}-{elec_year}']]\
            .sort_values(f'{value_sorter}',
                        ascending=sorter)

def elec_particip(elec_type='K'):
    a_list=[]
    

    
    for year in [2006,2010,2014,2018]:
        if year==2006:
            summa_röster = "summa_röster_fgval"
            summa_röstberättigade = "summa_röstberättigade_fgval"
                
            path_2010 = Path(f'data/meta_filer/valdeltagande/\
valdeltagande_2010{elec_type}.xlsx')

            # 2006 data finns i xml-filerna från 2010
            df = pd.read_excel(path_2010)
        else:
            path = Path(f'data/meta_filer/valdeltagande/\
valdeltagande_{year}{elec_type}.xlsx')
            df = pd.read_excel(path)
            summa_röster = "summa_röster"
            summa_röstberättigade = "summa_röstberättigade"
        a_dict={}
        a_dict['Valår'] = year
        a_dict['Valdeltagande, %'] = \
        ((df[f'{summa_röster}'].sum()/df[f'{summa_röstberättigade}'].sum())*100).round(1)
        a_list.append(a_dict)
    return pd.DataFrame(a_list).loc[:,['Valår','Valdeltagande, %']]

def kommun_deltagande(elec_year=2018, elec_type='K',sorter=False):

    grafik=particip_sorter(elec_year=elec_year,elec_type=f'{elec_type}',
                           value_sorter='förändring',sorter=sorter).head(10)

    grafik=grafik.loc[:,['kommun',f'valdeltagande_{elec_year}',f'förändring_{elec_year-4}-{elec_year}']]

    return grafik.rename(columns={f'valdeltagande_{elec_year}':'Valdeltagande, %',
                          f'förändring_{elec_year-4}-{elec_year}':'Differens'})

def big_city_sort(cities=['Stockholm',
                          'Göteborg',
                          'Malmö'],\
                  elec_year=2018,\
                  elec_type='K',\
                  value='mandat'):
    """Denna funktion hämtar valresultatet och mandatförändring \
för angivna kommuner. Parametern 'cities' tar en lista på kommuner \
och återger en df på dessa för det givna valåret ('elec_year'). \
Default är Stockholm, Göteborg och Malmö."""
    
    path = Path(f'data/resultat/resultat_{elec_year}/\
valresultat_{elec_year}{elec_type}.xlsx')

    df = pd.read_excel(path)
    
    remove_these = ['OG',
                    'OGEJ',
                    'BLANK',
                    'övriga_mindre_partier_totalt']
    
    df = df.loc[(df['kommun'].isin(cities))&\
                (~df['parti'].isin(remove_these))]
    
    compare_year = elec_year-4
    
    path_descr = Path('data/resultat/alla_partier.xlsx')

    beteckningar = pd.read_excel(path_descr)
    
    beteckningar = beteckningar.loc[beteckningar['val'] == \
                                    f'{elec_year}{elec_type}']
    
    df[f'{value}förändring_{compare_year}-{elec_year}'] = \
    df[f'{value}'] - df[f'{value}_fgval']
    
    df = df.merge(beteckningar,on='parti',how='left')
    
    return df.loc[:,['kommun',
                     'parti',
                     'beteckning',
                     'röster',
                     'procent',
                     'mandat',
                     f'{value}förändring_{compare_year}-{elec_year}']]\
                .rename(columns={'procent':f'procent_{elec_year}'
                                 ,'mandat':f'mandat_{elec_year}',
                                 'summa_mandat':'kommunmandat_totalt'}).fillna(0)

def storstäderna_grafik(df,stad,elec_year=2018):

    df=df.loc[(df[f'mandat_{elec_year}']>0)&(df['kommun']==f'{stad}')]

    df=df.loc[:,['beteckning',f'mandat_{elec_year}', f'mandatförändring_{elec_year-4}-{elec_year}']]

    df[f'Mandat {elec_year-4}'] = df[f'mandat_{elec_year}']+(-1*df[f'mandatförändring_{elec_year-4}-{elec_year}'])

    df.rename(columns={f'mandat_{elec_year}':f'Mandat {elec_year}',
                      f'mandatförändring_{elec_year-4}-{elec_year}':'Differens',
                      'beteckning':'Parti'},inplace=True)

    return df.loc[:,['Parti',f'Mandat {elec_year-4}',f'Mandat {elec_year}','Differens']]

def looser_winner(df,\
                elec_year=2018,\
                sorter=False,\
                party=False,\
                stora_partier=False):
    
    
    # Sortera bort ogiltiga röster
    df = df.loc[~df['parti'].isin(['OG','OGEJ'])]
    if stora_partier:
        parties = ['M','C','L','KD','S','V','MP','SD','FI']
        df = df.loc[df['parti'].isin(parties)]
    
    # jämför alltid med förra valet
    compare_year = elec_year-4
    
    if not party:
        # om party inte bestämts så ska all valdata från angiven
        # kommun hämtas
        df_muni = df.loc[df['valår']==elec_year]
    else:
        # sortera fram angivet partis alla kommuner under givna valåret
        df_muni = df.loc[(df['valår']==elec_year)&(df['parti']==party)]
    
    # hämtar partibeteckningar
    path_partierna = Path('data/resultat/alla_partier.xlsx')
    partierna = pd.read_excel(path_partierna)
    partierna = partierna.loc[partierna['val']==f'{str(elec_year)}K',
                              ['parti','beteckning']]
    
    df_muni = df_muni.merge(partierna,on='parti',how='left')
    
    df_muni = df_muni.sort_values(by='procent',ascending=False)
    
    # lägger till data från förra valet
    df_muni = df_muni.merge(df.loc[df['valår']==compare_year]\
                     .loc[:,['kommun','parti','procent','mandat']]\
                     .rename(columns={'procent':f'procent_{compare_year}',
                                      'mandat':f'mandat_{compare_year}'}),
                            on=['kommun','parti'],
                            how='left')
        
    
        
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']] = \
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']].fillna(0)
    
    
    # Beräknar skillnaden i procentenheter mellan valet och 
    # jämförelsevalet fyra år tidigare
    df_muni[f'diff i procentenheter {elec_year}-{compare_year}'] = \
    df_muni['procent'] - df_muni[f'procent_{compare_year}']
    
    # se till att kolumnerna mandat och röster är integers
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']] = \
    df_muni.loc[:,['röster','mandat',f'mandat_{compare_year}']]\
                                            .fillna(0).astype('int')
    df_muni.rename(columns={'röster':f'röster_{elec_year}',
                            'procent':f'procent_{elec_year}',
                           'mandat':f'mandat_{elec_year}'},inplace=True)
    
    return df_muni.loc[:,['kommun',
                          'beteckning',
                          f'röster_{elec_year}',
                          f'procent_{compare_year}',
                          f'procent_{elec_year}',
                          f'diff i procentenheter {elec_year}-{compare_year}',
                          f'mandat_{compare_year}',                          
                          f'mandat_{elec_year}']]\
                    .sort_values(by=f'diff i procentenheter {elec_year}-{compare_year}',
                                ascending=sorter)

def local_magnates(elec_year=2018,elec_types=['K','R']):
    """Denna funktion hämtar valresultatet från olika val \
och återger hur skillnaden är i valresultat för partierna \
i kommunerna."""
    
    # Kolla endast dessa partier
    big_parties = ['M','C','L','KD','S','V','MP','SD','FI']
    
    # placeholder
    ph = {}
    
    # hämta de olika valresultaten och placera i ph
    for types in elec_types:
        df = all_elec_years(types)
        
        # lite df-formattering
        df = df.loc[(df['valår']==elec_year)&\
                    (df['parti'].isin(big_parties))]
        
        del df['valår']
        
        ph[types] = df.loc[:,['kommun','parti','röster','procent']]
    
    # Detta döper om kolumnerna
    for k,v in ph.items():
        for col in v.columns:
            if col not in ['kommun','parti']:
                v.rename(columns={f'{col}':f'{col}_{k}'},inplace=True)
    
    # if-statement 
    if len(elec_types)== 1:
        return ph[types]
    elif len(elec_types) == 2:
        df = ph[elec_types[0]].merge(ph[elec_types[1]],on=['kommun','parti'],how='left')
    elif len(elec_types) == 3:
        df = ph[elec_types[0]]
        for types in elec_types[1:]:
            df = df.merge(ph[types],on=['kommun','parti'],how='left')
    
    df['diff_K_jämf_R'] = df['procent_K']-df['procent_R']
    
    
    
    return df.sort_values(by='diff_K_jämf_R',ascending=False)

def elec_compare(elec_types=['K','R'],elec_year=2018):
    """Denna är det något vajsing med. Sket i den.."""
    
    return pd.concat([valanalys(all_elec_years(elec_types[0]),
                                query='valresultat',
                                year=elec_year,
                                elec_type=elec_types[0])[0].rename(columns={
                                    'procent':f'procent_{elec_year}{elec_types[0]}',
                                    'röster':f'röster_{elec_year}{elec_types[0]}'
                                    }),
                        valanalys(all_elec_years(elec_types[-1]),
                                  query='valresultat',
                                  year=elec_year,
                                  elec_type=elec_types[1])[0].rename(columns={
                                    'procent':f'procent_{elec_year}{elec_types[1]}',
                                    'röster':f'röster_{elec_year}{elec_types[1]}'
                                    })\
                           .loc[:,[f'procent_{elec_year}{elec_types[1]}',
                                   f'röster_{elec_year}{elec_types[1]}']]],axis=1)\
                .set_index('parti')

def elec_macro_fetcher(elec_type='L',\
                       elec_years=[2010,
                                   2014,
                                   2018],\
                       parties=['M',
                                'C',
                                'L',
                                'KD',
                                'S',
                                'V',
                                'MP',
                                'SD',
                                'FI'],\
                       grouping='parti',\
                       pivot_value='procent',\
                       all_parties=False):
    
    path = Path('data/resultat/alla_valresultat_2006_2018.xlsx')

    df = pd.read_excel(path)
    
    elec_years = [str(year)+elec_type for year in elec_years]
    
    if not all_parties:
        df.loc[~df['parti'].isin(parties),'beteckning'] = 'Övr'
        df.loc[~df['parti'].isin(parties),'parti'] = 'Övr'
        parties.append('Övr')      
    else:
        df = df.loc[df['parti']==party]
    
    df = df.loc[df['val'].isin(elec_years)]
    

    df = df.groupby([f'{grouping}','val']).sum().reset_index()


    
    df = df.pivot(index=f'{grouping}',columns='val',values=pivot_value)
    for col in df.columns:
        df.rename(columns={f'{col}':f'{pivot_value}_{col}'},inplace=True)
    return df
    
def till_datawrapper(elec_types=['K','R'],\
                     elec_years=[2014,2018],\
                     parties=['M',
                              'L',
                              'C',
                              'KD',
                              'S',
                              'V',
                              'MP',
                              'SD',
                              'FI',
                              'Övr']):
    parameter = f'Förändring jämfört {elec_years[0]}, %'
    val_kolumn_lokalt = f'procent_{elec_years[-1]}{elec_types[0]}'
    val_kolumn_riks = f'procent_{elec_years[-1]}{elec_types[-1]}'
    if elec_types[0] == 'K':
        column = 'Resultat kommunvalen, %'
    elif elec_types[0] == 'L':
        column = 'Resultat landstingsvalen, %'
    else:
        return 'Första "elec_types" måste vara "K" eller "L".'
    
    df = elec_macro_fetcher(elec_type=elec_types[0],
                       elec_years=elec_years,
                       parties=parties).reset_index()\
        .merge(\
    elec_macro_fetcher(elec_type=elec_types[1],
                       elec_years=elec_years,
                       parties=parties).reset_index(),
               on='parti',how='left')
    #print(df.columns)
    df[parameter] = df[val_kolumn_lokalt] - df[f'procent_{elec_years[0]}{elec_types[0]}']
    df = df.rename(columns={val_kolumn_lokalt:f'{column}',
                            val_kolumn_riks:'Resultat riksdagsvalet, %',
                           'parti':'Parti'})
    df = df.loc[:,['Parti',f'{column}',f'{parameter}','Resultat riksdagsvalet, %']]
    for col in [f'{column}',f'{parameter}','Resultat riksdagsvalet, %']:
        df[col] = df[col].round(1)
    return df





    