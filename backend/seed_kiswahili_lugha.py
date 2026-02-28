#!/usr/bin/env python3
"""
Seed Kiswahili Lugha curriculum data from KICD PDF into MongoDB
This script adds Grade 10 Kiswahili Lugha curriculum data to the existing database.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Kiswahili Lugha curriculum data extracted from PDF
KISWAHILI_LUGHA_DATA = {
    "strands": [
        {
            "name": "Kusikiliza na Kuzungumza",
            "substrands": [
                {
                    "name": "Ufahamu wa Kusikiliza - Ujumbe na fani katika matini simulizi",
                    "slos": [
                        {"name": "Kueleza maana ya ujumbe na fani katika matini", "description": "Mwanafunzi aweze kueleza maana ya ujumbe na fani katika matini ili kuipambanua."},
                        {"name": "Kutabiri ujumbe wa matini simulizi", "description": "Mwanafunzi aweze kutabiri ujumbe wa matini simulizi kwa kuzingatia anwani."},
                        {"name": "Kutambua ujumbe katika matini simulizi", "description": "Mwanafunzi aweze kutambua ujumbe katika matini simulizi aliyosikiliza."},
                        {"name": "Kuchambua vipengele vya fani", "description": "Mwanafunzi aweze kuchambua vipengele vya fani katika matini simulizi aliyosikiliza."}
                    ]
                },
                {
                    "name": "Matamshi Bora - Sauti /b/, /mb/, /bw/, /mbw/",
                    "slos": [
                        {"name": "Kutambua sauti katika matini", "description": "Mwanafunzi aweze kutambua sauti /b/, /mb/, /bw/ na /mbw/ katika matini."},
                        {"name": "Kutamka sauti ipasavyo", "description": "Mwanafunzi aweze kutamka sauti /b/, /mb/, /bw/ na /mbw/ ipasavyo katika maneno."},
                        {"name": "Kutamka vitanzandimi", "description": "Mwanafunzi aweze kutamka vitanzandimi vyenye sauti /b/, /mb/, /bw/ na /mbw/ ipasavyo."},
                        {"name": "Kutunga vitanzandimi", "description": "Mwanafunzi aweze kutunga vitanzandimi vyenye maneno yaliyo na sauti /b/, /mb/, /bw/ na /mbw/."}
                    ]
                },
                {
                    "name": "Kuzungumza Kwa Kupasha Habari",
                    "slos": [
                        {"name": "Kueleza maana ya kuzungumza kwa kupasha habari", "description": "Mwanafunzi aweze kueleza maana ya kuzungumza kwa kupasha habari ili kukutofautisha na aina nyingine za uzungumzaji."},
                        {"name": "Kutambua aina za uzungumzaji wa kupasha habari", "description": "Mwanafunzi aweze kutambua aina za uzungumzaji wa kupasha habari ili kuzitofautisha."},
                        {"name": "Kujadili vipengele vya kuzingatia", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika kuzungumza kwa kupasha habari."},
                        {"name": "Kuwawasilisha mazungumzo ya kupasha habari", "description": "Mwanafunzi aweze kuwawasilisha mazungumzo ya kupasha habari kuhusu mambo mbalimbali."}
                    ]
                },
                {
                    "name": "Kusikiliza kwa Kupata Habari",
                    "slos": [
                        {"name": "Kutambua miktadha ya usikizaji", "description": "Mwanafunzi aweze kutambua miktadha ambapo usikizaji wa kupata habari hufanyika."},
                        {"name": "Kujadili vipengele vya kusikiliza", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika kusikiliza kwa kupata habari."},
                        {"name": "Kushiriki katika mazungumzo", "description": "Mwanafunzi aweze kushiriki katika mazungumzo akizingatia vipengele vya kusikiliza kwa kupata habari."},
                        {"name": "Kujadili ujumbe katika matini", "description": "Mwanafunzi aweze kujadili ujumbe katika matini aliyosikiliza ili kukuza umakinifu."}
                    ]
                },
                {
                    "name": "Kusikiliza kwa Kupambanua",
                    "slos": [
                        {"name": "Kueleza maana ya kusikiliza kwa kupambanua", "description": "Mwanafunzi aweze kueleza maana ya kusikiliza kwa kupambanua ili kukutofautisha na aina nyingine za kusikiliza."},
                        {"name": "Kutambua vipengele vya kuzingatia", "description": "Mwanafunzi aweze kutambua vipengele vya kuzingatia katika kusikiliza kwa kupambanua ili kufasiri maana."},
                        {"name": "Kujadili mielekeo kuhusu ujumbe", "description": "Mwanafunzi aweze kujadili mielekeo kuhusu ujumbe kutokana na msamiati, viziada lugha na kiimbo."},
                        {"name": "Kusikiliza matini", "description": "Mwanafunzi aweze kusikiliza matini ili kufanikisha ufasiri wa ujumbe na msamiati."}
                    ]
                },
                {
                    "name": "Uzungumzaji wa Papo kwa Hapo",
                    "slos": [
                        {"name": "Kueleza maana ya uzungumzaji wa papo kwa hapo", "description": "Mwanafunzi aweze kueleza maana ya uzungumzaji wa papo kwa hapo ili kuutofautisha na aina nyingine za mazungumzo."},
                        {"name": "Kueleza miktadha ya uzungumzaji", "description": "Mwanafunzi aweze kueleza miktadha ambapo uzungumzaji wa papo kwa hapo hutokea katika jamii yake."},
                        {"name": "Kujadili kanuni za uzungumzaji", "description": "Mwanafunzi aweze kujadili kanuni za uzungumzaji wa papo kwa hapo."},
                        {"name": "Kushiriki katika uzungumzaji", "description": "Mwanafunzi aweze kushiriki katika uzungumzaji wa papo kwa hapo akizingatia kanuni zifaazo."}
                    ]
                },
                {
                    "name": "Mjadala",
                    "slos": [
                        {"name": "Kueleza maana ya mjadala", "description": "Mwanafunzi aweze kueleza maana ya mjadala ili kuupambanua."},
                        {"name": "Kujadili sifa za mjadala", "description": "Mwanafunzi aweze kujadili sifa za mjadala ili kuzibainisha."},
                        {"name": "Kushiriki mjadala", "description": "Mwanafunzi aweze kushiriki mjadala kuhusu suala lengwa akizingatia kanuni za mjadala."},
                        {"name": "Kukuza mawasiliano kupitia mijadala", "description": "Mwanafunzi aweze kufurahia kushiriki katika mijadala ili kukuza mawasiliano."}
                    ]
                },
                {
                    "name": "Ushawishi kuhusu ukweli fulani",
                    "slos": [
                        {"name": "Kueleza maana ya uzungumzaji wa kushawishi", "description": "Mwanafunzi aweze kueleza maana ya uzungumzaji wa kushawishi."},
                        {"name": "Kutambua miktadha ya uzungumzaji wa kushawishi", "description": "Mwanafunzi aweze kutambua miktadha ambapo uzungumzaji wa kushawishi hufanyika."},
                        {"name": "Kujadili kanuni za uzungumzaji wa ushawishi", "description": "Mwanafunzi aweze kujadili kanuni za uzungumzaji wa ushawishi akishirikiana na wenzake."},
                        {"name": "Kukuza stadi ya kushawishi", "description": "Mwanafunzi aweze kuonea fahari uzungumzaji wa kushawishi katika miktadha mbalimbali."}
                    ]
                },
                {
                    "name": "Usikilizaji Husishi",
                    "slos": [
                        {"name": "Kueleza maana ya usikilizaji husishi", "description": "Mwanafunzi aweze kueleza maana ya usikilizaji husishi ili kuutofautisha na aina nyingine za usikilizaji."},
                        {"name": "Kujadili umuhimu wa usikilizaji husishi", "description": "Mwanafunzi aweze kujadili umuhimu wa usikilizaji husishi katika mawasiliano."},
                        {"name": "Kueleza miktadha ya usikilizaji husishi", "description": "Mwanafunzi aweze kueleza miktadha ambapo usikilizaji husishi hutokea."},
                        {"name": "Kushiriki mazungumzo", "description": "Mwanafunzi aweze kushiriki mazungumzo kwa kuzingatia kanuni za usikilizaji husishi."}
                    ]
                },
                {
                    "name": "Kuhakiki Matini ya Kusikiliza",
                    "slos": [
                        {"name": "Kueleza maana ya kusikiliza kwa kuhakiki", "description": "Mwanafunzi aweze kueleza maana ya kusikiliza kwa kuhakiki ili kukutofautisha na aina nyingine za kusikiliza."},
                        {"name": "Kujadili kanuni za kusikiliza kwa kuhakiki", "description": "Mwanafunzi aweze kujadili kanuni za kusikiliza kwa kuhakiki ili kuzipambanua."},
                        {"name": "Kusikiliza matini kwa kuzingatia kanuni", "description": "Mwanafunzi aweze kusikiliza matini kwa kuzingatia kanuni za kusikiliza kwa kuhakiki."},
                        {"name": "Kuhakiki matini aliyosikiliza", "description": "Mwanafunzi aweze kuhakiki matini aliyosikiliza kwa kuzingatia vipengele vifaavyo."}
                    ]
                }
            ]
        },
        {
            "name": "Kusoma",
            "substrands": [
                {
                    "name": "Kusoma kwa Ufasaha - Kifungu simulizi",
                    "slos": [
                        {"name": "Kujadili vipengele vya kusoma kwa ufasaha", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika kusoma kwa ufasaha."},
                        {"name": "Kusoma akizingatia matamshi bora", "description": "Mwanafunzi aweze kusoma kifungu simulizi akizingatia matamshi bora."},
                        {"name": "Kusoma akizingatia kasi ifaayo", "description": "Mwanafunzi aweze kusoma kifungu simulizi akizingatia kasi ifaayo."},
                        {"name": "Kusoma akizingatia kiimbo na kiwango cha sauti", "description": "Mwanafunzi aweze kusoma kifungu simulizi akizingatia kiimbo na kiwango kifaacho cha sauti."},
                        {"name": "Kusoma akizingatia viziada lugha", "description": "Mwanafunzi aweze kusoma kifungu simulizi akizingatia viziada lugha."}
                    ]
                },
                {
                    "name": "Kusoma kwa Ufahamu - Kifungu simulizi",
                    "slos": [
                        {"name": "Kudondoa habari mahususi", "description": "Mwanafunzi aweze kudondoa habari mahususi katika kifungu simulizi."},
                        {"name": "Kupanga matukio yanavyofuatana", "description": "Mwanafunzi aweze kupanga matukio yanavyofuatana katika kifungu simulizi alichosoma."},
                        {"name": "Kufanya utabiri na ufasiri", "description": "Mwanafunzi aweze kufanya utabiri na ufasiri kutokana na kifungu simulizi."},
                        {"name": "Kutumia msamiati ipasavyo", "description": "Mwanafunzi aweze kutumia msamiati katika kifungu simulizi ipasavyo."}
                    ]
                },
                {
                    "name": "Ufupisho - Kifungu cha kupasha habari",
                    "slos": [
                        {"name": "Kujadili vipengele vya kufupisha", "description": "Mwanafunzi aweze kujadili na wenzake vipengele vya kuzingatia katika kufupisha kifungu cha kupasha habari."},
                        {"name": "Kujadili umuhimu wa ufupisho", "description": "Mwanafunzi aweze kujadili na wenzake umuhimu wa ufupisho."},
                        {"name": "Kusoma vifungu vya kupasha habari", "description": "Mwanafunzi aweze kusoma vifungu vya kupasha habari kuhusu suala lengwa na kuvifupisha."},
                        {"name": "Kuwawasilisha ufupisho darasani", "description": "Mwanafunzi aweze kuwawasilisha ufupisho wake darasani ili wenzake wautolee maoni."}
                    ]
                },
                {
                    "name": "Kusoma kwa Mapana - Matini ya kujichagulia",
                    "slos": [
                        {"name": "Kueleza maana ya kusoma kwa mapana", "description": "Mwanafunzi aweze kueleza maana ya kusoma kwa mapana."},
                        {"name": "Kujadili vipengele vya kusoma kwa mapana", "description": "Mwanafunzi aweze kujadili vipengele mbalimbali vya kuzingatia katika kusoma kwa mapana."},
                        {"name": "Kutambua matini ya kujichagulia", "description": "Mwanafunzi aweze kutambua matini ya kujichagulia (andishi au ya kidijitali) na kuisoma."},
                        {"name": "Kutambua ujumbe katika matini", "description": "Mwanafunzi aweze kutambua ujumbe katika matini aliyoisoma."},
                        {"name": "Kuweka rekodi ya aliyosoma", "description": "Mwanafunzi aweze kuweka rekodi ya aliyosoma kwa kuyanakili katika kijitabu kwa marejeleo."}
                    ]
                },
                {
                    "name": "Kusoma kwa Kina - Usomaji wa kurashia",
                    "slos": [
                        {"name": "Kueleza maana ya kurashia", "description": "Mwanafunzi aweze kueleza maana ya kurashia katika usomaji wa kina."},
                        {"name": "Kujadili vipengele vya usomaji wa kurashia", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika usomaji wa kurashia."},
                        {"name": "Kusoma matini kwa mbinu ya kurashia", "description": "Mwanafunzi aweze kusoma matini kwa kutumia mbinu ya kurashia ili kupata ujumbe."},
                        {"name": "Kuthamini usomaji wa kina", "description": "Mwanafunzi aweze kuthamini usomaji wa kina ili kukuza stadi ya kusoma."}
                    ]
                },
                {
                    "name": "Kusoma kwa Ufasaha - Kifungu cha maelezo",
                    "slos": [
                        {"name": "Kujadili vipengele na umuhimu wake", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika kusoma kwa ufasaha na umuhimu wake."},
                        {"name": "Kusoma kifungu akizingatia matamshi", "description": "Mwanafunzi aweze kusoma kifungu cha maelezo akizingatia matamshi bora."},
                        {"name": "Kusoma akizingatia kasi na kiimbo", "description": "Mwanafunzi aweze kusoma kifungu cha maelezo akizingatia kasi ifaayo, kiimbo na kiwango cha sauti."},
                        {"name": "Kujenga mazoea ya kusoma kwa ufasaha", "description": "Mwanafunzi aweze kujenga mazoea ya kusoma kwa ufasaha kifungu cha maelezo."}
                    ]
                },
                {
                    "name": "Kusoma kwa Kina - Usomaji wa kuduhushi",
                    "slos": [
                        {"name": "Kueleza maana ya kuduhushi", "description": "Mwanafunzi aweze kueleza maana ya kuduhushi kama mbinu ya usomaji."},
                        {"name": "Kujadili uhusiano wa kuduhushi na kurashia", "description": "Mwanafunzi aweze kujadili uhusiano na tofauti kati ya mbinu ya kuduhushi na ya kurashia."},
                        {"name": "Kusoma kwa mbinu ya kuduhushi", "description": "Mwanafunzi aweze kusoma matini kwa kutumia mbinu ya kuduhushi akizingatia msamiati na matumizi ya lugha."},
                        {"name": "Kutafiti na kusoma matini mtandaoni", "description": "Mwanafunzi aweze kutafiti matini katika mtandao salama na kuzisoma kwa mbinu ya kuduhushi."}
                    ]
                }
            ]
        },
        {
            "name": "Kuandika",
            "substrands": [
                {
                    "name": "Viakifishi - Herufi kubwa, Nukta, Kipumuo, Alama za mtajo",
                    "slos": [
                        {"name": "Kueleza matumizi ya alama za uakifishi", "description": "Mwanafunzi aweze kueleza matumizi ya herufi kubwa, nukta, kipumuo na alama za mtajo katika matini."},
                        {"name": "Kutambua alama za uakifishi", "description": "Mwanafunzi aweze kutambua herufi kubwa, nukta, kipumuo na alama za mtajo katika matini."},
                        {"name": "Kutumia alama za uakifishi ipasavyo", "description": "Mwanafunzi aweze kutumia ipasavyo herufi kubwa, nukta, kipumuo na alama za mtajo katika matini."},
                        {"name": "Kufurahia matumizi yafaayo", "description": "Mwanafunzi aweze kufurahia matumizi yafaayo ya alama za uakifishi katika matini."}
                    ]
                },
                {
                    "name": "Barua ya Kirafiki",
                    "slos": [
                        {"name": "Kueleza maana ya barua ya kirafiki", "description": "Mwanafunzi aweze kueleza maana ya barua ya kirafiki."},
                        {"name": "Kutambua miktadha ya barua ya kirafiki", "description": "Mwanafunzi aweze kutambua miktadha ambapo barua ya kirafiki hutumika."},
                        {"name": "Kueleza umuhimu wa barua ya kirafiki", "description": "Mwanafunzi aweze kueleza umuhimu wa barua ya kirafiki."},
                        {"name": "Kujadili vipengele vya barua ya kirafiki", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika uandishi wa barua ya kirafiki."},
                        {"name": "Kuandika barua ya kirafiki", "description": "Mwanafunzi aweze kuandika barua ya kirafiki kwa kuzingatia vipengele vifaavyo."}
                    ]
                },
                {
                    "name": "Insha ya Wasifu",
                    "slos": [
                        {"name": "Kueleza maana ya insha ya wasifu", "description": "Mwanafunzi aweze kueleza maana ya insha ya wasifu ili kuipambanua."},
                        {"name": "Kujadili ujumbe wa insha ya wasifu", "description": "Mwanafunzi aweze kujadili ujumbe unaoafiki insha ya wasifu akishirikiana na wenzake."},
                        {"name": "Kujadili muundo wa insha ya wasifu", "description": "Mwanafunzi aweze kujadili muundo wa insha ya wasifu (utangulizi, mwili na hitimisho)."},
                        {"name": "Kuandika insha ya wasifu", "description": "Mwanafunzi aweze kuandika insha ya wasifu kuhusu suala lengwa akizingatia ujumbe, muundo na mtindo ufaao."}
                    ]
                },
                {
                    "name": "Ratiba",
                    "slos": [
                        {"name": "Kueleza maana ya ratiba", "description": "Mwanafunzi aweze kueleza maana ya ratiba ili kuipambanua."},
                        {"name": "Kujadili umuhimu wa ratiba", "description": "Mwanafunzi aweze kujadili umuhimu wa ratiba katika maisha ya kila siku."},
                        {"name": "Kujadili vipengele vya ratiba", "description": "Mwanafunzi aweze kujadili vipengele vya ratiba ili kuvibainisha."},
                        {"name": "Kuandika ratiba", "description": "Mwanafunzi aweze kuandika ratiba kwa kuzingatia vipengele vifaavyo."}
                    ]
                },
                {
                    "name": "Kuhariri Matini",
                    "slos": [
                        {"name": "Kueleza maana ya kuhariri", "description": "Mwanafunzi aweze kueleza maana ya kuhariri ili kuipambanua."},
                        {"name": "Kujadili hatua za uhariri", "description": "Mwanafunzi aweze kujadili hatua za kuzingatia katika uhariri wa matini."},
                        {"name": "Kujadili kanuni za kuhariri", "description": "Mwanafunzi aweze kujadili kanuni za kuhariri matini."},
                        {"name": "Kuhariri makala", "description": "Mwanafunzi aweze kuhariri makala akizingatia kanuni za uhariri wa matini."}
                    ]
                },
                {
                    "name": "Notisi",
                    "slos": [
                        {"name": "Kueleza maana ya notisi", "description": "Mwanafunzi aweze kueleza maana ya notisi ili kuipambanua."},
                        {"name": "Kueleza umuhimu wa notisi", "description": "Mwanafunzi aweze kueleza umuhimu wa notisi katika mawasiliano."},
                        {"name": "Kujadili vipengele vya notisi", "description": "Mwanafunzi aweze kujadili vipengele vya kuzingatia katika kuandika notisi."},
                        {"name": "Kuandika notisi", "description": "Mwanafunzi aweze kuandika notisi kwa kuzingatia vipengele vifaavyo."}
                    ]
                },
                {
                    "name": "Shajara",
                    "slos": [
                        {"name": "Kueleza maana ya shajara", "description": "Mwanafunzi aweze kueleza maana ya shajara ili kuibainisha."},
                        {"name": "Kujadili umuhimu wa shajara", "description": "Mwanafunzi aweze kujadili umuhimu wa shajara katika uandishi wa kiuamilifu."},
                        {"name": "Kueleza aina mbalimbali za shajara", "description": "Mwanafunzi aweze kueleza aina mbalimbali za shajara ili kuzipambanua."},
                        {"name": "Kuandika shajara", "description": "Mwanafunzi aweze kuandika shajara akizingatia vipengele vifaavyo vya uandishi wa shajara."}
                    ]
                },
                {
                    "name": "Insha ya Masimulizi - Picha",
                    "slos": [
                        {"name": "Kueleza maana ya insha ya masimulizi", "description": "Mwanafunzi aweze kueleza maana ya insha ya masimulizi kuhusu picha ili kuitofautisha na aina nyingine za insha."},
                        {"name": "Kujadili ujumbe kutokana na picha", "description": "Mwanafunzi aweze kujadili ujumbe kutokana na insha ya picha."},
                        {"name": "Kufafanua matukio ya insha", "description": "Mwanafunzi aweze kufafanua matukio ya insha ya masimulizi kutokana na picha."},
                        {"name": "Kuandika insha ya masimulizi", "description": "Mwanafunzi aweze kuandika insha ya masimulizi kutokana na picha akizingatia ujumbe, mtindo na muundo."}
                    ]
                },
                {
                    "name": "Insha fafanuzi - Matatizo na utatuzi",
                    "slos": [
                        {"name": "Kueleza maana ya insha fafanuzi", "description": "Mwanafunzi aweze kueleza maana ya insha fafanuzi ili kuibainisha."},
                        {"name": "Kujadili vipengele vya insha fafanuzi", "description": "Mwanafunzi aweze kujadili vipengele vya insha fafanuzi kuhusu matatizo na utatuzi."},
                        {"name": "Kuandika insha fafanuzi", "description": "Mwanafunzi aweze kuandika insha fafanuzi kuhusu matatizo na utatuzi akizingatia vipengele vifaavyo."},
                        {"name": "Kufurahia kuandika insha fafanuzi", "description": "Mwanafunzi aweze kufurahia kuandika insha fafanuzi ili kufanikisha mawasiliano."}
                    ]
                },
                {
                    "name": "Tafsiri",
                    "slos": [
                        {"name": "Kueleza maana ya tafsiri", "description": "Mwanafunzi aweze kueleza maana ya tafsiri ili kuipambanua."},
                        {"name": "Kujadili aina za tafsiri", "description": "Mwanafunzi aweze kujadili aina za tafsiri (neno kwa neno, kimaana, kimawasiliano)."},
                        {"name": "Kueleza umuhimu wa tafsiri", "description": "Mwanafunzi aweze kueleza umuhimu wa tafsiri (kusaidia kueneza dini, kufikisha sera za serikali, kukuza lugha na fasihi)."},
                        {"name": "Kuandika tafsiri", "description": "Mwanafunzi aweze kuandika tafsiri ya kiwango chao kwa kuzingatia mambo muhimu katika tafsiri."}
                    ]
                }
            ]
        },
        {
            "name": "Matumizi ya Lugha",
            "substrands": [
                {
                    "name": "Aina za Maneno - Nomino, Vitenzi, Viwakilishi, Vivumishi",
                    "slos": [
                        {"name": "Kueleza maana za aina za maneno", "description": "Mwanafunzi aweze kueleza maana za nomino, vitenzi, viwakilishi na vivumishi ili kuvibainisha."},
                        {"name": "Kutambua aina za maneno katika matini", "description": "Mwanafunzi aweze kutambua nomino, vitenzi, viwakilishi na vivumishi katika matini."},
                        {"name": "Kutumia aina za maneno katika matini", "description": "Mwanafunzi aweze kutumia nomino, vitenzi, viwakilishi na vivumishi katika matini."},
                        {"name": "Kujenga ufasaha wa lugha", "description": "Mwanafunzi aweze kuchangamkia matumizi ya nomino, vitenzi, viwakilishi na vivumishi ili kujenga ufasaha wa lugha."}
                    ]
                },
                {
                    "name": "Ngeli za Nomino - A-WA, U-I, KI-VI, I-ZI",
                    "slos": [
                        {"name": "Kutambua viambishi vya upatanisho", "description": "Mwanafunzi aweze kutambua viambishi vya upatanisho wa kisarufi wa ngeli ya A-WA, U-I, KI-VI na I-ZI."},
                        {"name": "Kutambua nomino za ngeli", "description": "Mwanafunzi aweze kutambua nomino za ngeli ya A-WA, U-I, KI-VI na I-ZI katika matini."},
                        {"name": "Kutumia nomino katika ngeli", "description": "Mwanafunzi aweze kutumia nomino katika ngeli ya A-WA, U-I, KI-VI na I-ZI kwa kuzingatia upatanisho ufaao."},
                        {"name": "Kuimarisha mawasiliano", "description": "Mwanafunzi aweze kuchangamkia kutumia nomino za ngeli ipasavyo katika sentensi na vifungu."}
                    ]
                },
                {
                    "name": "Nyakati na Hali - Wakati uliopo, uliopita, ujao",
                    "slos": [
                        {"name": "Kubainisha vitenzi vya nyakati", "description": "Mwanafunzi aweze kubainisha vitenzi vilivyo katika wakati uliopo, uliopita na ujao katika matini."},
                        {"name": "Kutumia wakati ifaavyo", "description": "Mwanafunzi aweze kutumia wakati uliopo, uliopita na ujao ifaavyo katika matini."},
                        {"name": "Kuchangamkia ufasaha wa lugha", "description": "Mwanafunzi aweze kuchangamkia ufasaha wa lugha kwa kutumia wakati uliopo, uliopita na ujao ifaavyo."}
                    ]
                },
                {
                    "name": "Mnyambuliko wa Vitenzi - kutenda, kutendea, kutendwa, kutendewa",
                    "slos": [
                        {"name": "Kutambua kauli za vitenzi", "description": "Mwanafunzi aweze kutambua kauli ya kutenda, kutendea, kutendwa na kutendewa katika vitenzi."},
                        {"name": "Kutumia vitenzi katika kauli mbalimbali", "description": "Mwanafunzi aweze kutumia vitenzi katika kauli ya kutenda, kutendea, kutendwa na kutendewa ipasavyo."},
                        {"name": "Kujenga ufasaha wa lugha", "description": "Mwanafunzi aweze kuchangamkia kutumia ipasavyo kauli ya kutenda, kutendea, kutendwa na kutendewa."}
                    ]
                },
                {
                    "name": "Ukanushaji - Wakati uliopo, uliopita, ujao",
                    "slos": [
                        {"name": "Kueleza maana ya ukanushaji", "description": "Mwanafunzi aweze kueleza maana ya ukanushaji ili kuupambanua."},
                        {"name": "Kutambua viambishi vya ukanushaji", "description": "Mwanafunzi aweze kutambua viambishi vya ukanushaji wa nyakati katika matini."},
                        {"name": "Kukanusha sentensi", "description": "Mwanafunzi aweze kukanusha sentensi kwa kuzingatia viambishi vya nyakati."},
                        {"name": "Kufurahia ukanushaji wa nyakati", "description": "Mwanafunzi aweze kufurahia ukanushaji wa nyakati ili kufanikisha mawasiliano."}
                    ]
                },
                {
                    "name": "Aina za Maneno - Vielezi, Viunganishi, Vihusishi, Vihisishi",
                    "slos": [
                        {"name": "Kueleza maana ya aina za maneno", "description": "Mwanafunzi aweze kueleza maana ya vielezi, viunganishi, vihusishi na vihisishi."},
                        {"name": "Kutumia aina za maneno ipasavyo", "description": "Mwanafunzi aweze kutumia ipasavyo aina za vielezi, viunganishi, vihusishi na vihisishi katika matini."},
                        {"name": "Kufurahia matumizi", "description": "Mwanafunzi aweze kufurahia matumizi ya vielezi, viunganishi, vihusishi na vihisishi katika sentensi."}
                    ]
                },
                {
                    "name": "Uundaji wa maneno - Maneno ya mkato, Nomino ambata, Uradidi",
                    "slos": [
                        {"name": "Kueleza dhana ya uundaji wa maneno", "description": "Mwanafunzi aweze kueleza dhana ya uundaji wa maneno."},
                        {"name": "Kujadili mbinu za uundaji wa maneno", "description": "Mwanafunzi aweze kujadili mbinu za uundaji wa maneno: maneno ya mkato, nomino ambata na uradidi."},
                        {"name": "Kutafiti maneno yaliyoundwa", "description": "Mwanafunzi aweze kutafiti vitabuni na mtandaoni kupata maneno yaliyoundwa kwa mbinu mbalimbali."},
                        {"name": "Kuunda maneno ya mkato", "description": "Mwanafunzi aweze kuunda maneno ya mkato akishirikiana na wenzake."}
                    ]
                },
                {
                    "name": "Kinyume - Nomino, Vitenzi, Vivumishi",
                    "slos": [
                        {"name": "Kueleza dhana ya kinyume", "description": "Mwanafunzi aweze kueleza dhana ya kinyume cha neno ili kuipambanua."},
                        {"name": "Kueleza maana ya kinyume", "description": "Mwanafunzi aweze kueleza maana ya kinyume cha nomino, vitenzi na vivumishi ili kuvitofautisha."},
                        {"name": "Kutumia vinyume ipasavyo", "description": "Mwanafunzi aweze kutumia vinyume vya nomino, vitenzi na vivumishi katika matini ipasavyo."},
                        {"name": "Kufurahia matumizi ya vinyume", "description": "Mwanafunzi aweze kufurahia matumizi yafaayo ya vinyume ili kufanikisha mawasiliano."}
                    ]
                },
                {
                    "name": "Isimujamii - Kaida za matumizi ya lugha, Sajili",
                    "slos": [
                        {"name": "Kueleza dhana ya isimujamii", "description": "Mwanafunzi aweze kueleza dhana ya isimujamii."},
                        {"name": "Kufanya utafiti kuhusu isimujamii", "description": "Mwanafunzi aweze kufanya utafiti vitabuni au mtandaoni kuhusu umuhimu wa isimujamii."},
                        {"name": "Kufafanua kaida za matumizi ya lugha", "description": "Mwanafunzi aweze kufafanua kaida za matumizi ya lugha (mada, umri na cheo)."},
                        {"name": "Kueleza dhana ya sajili", "description": "Mwanafunzi aweze kueleza dhana ya sajili (sajili ya shuleni, michezo, dini, biashara, hospitalini)."}
                    ]
                }
            ]
        }
    ]
}

async def seed_kiswahili_lugha():
    """Seed Kiswahili Lugha curriculum data into the database"""
    
    print("Starting Kiswahili Lugha curriculum seeding...")
    
    # First, check if Grade 10 exists
    grade = await db.grades.find_one({"name": {"$regex": "10|Ten", "$options": "i"}})
    if not grade:
        # Create Grade 10 if it doesn't exist
        grade_result = await db.grades.insert_one({
            "name": "Grade 10",
            "order": 10
        })
        grade_id = str(grade_result.inserted_id)
        print(f"Created Grade 10 with ID: {grade_id}")
    else:
        grade_id = str(grade["_id"])
        print(f"Found existing Grade 10 with ID: {grade_id}")
    
    # Check if Kiswahili Lugha subject exists
    subject = await db.subjects.find_one({"name": {"$regex": "Kiswahili Lugha", "$options": "i"}})
    if not subject:
        # Create Kiswahili Lugha subject
        subject_result = await db.subjects.insert_one({
            "name": "Kiswahili Lugha",
            "gradeIds": [grade_id]
        })
        subject_id = str(subject_result.inserted_id)
        print(f"Created Kiswahili Lugha subject with ID: {subject_id}")
    else:
        subject_id = str(subject["_id"])
        # Update gradeIds if needed
        if grade_id not in subject.get("gradeIds", []):
            await db.subjects.update_one(
                {"_id": subject["_id"]},
                {"$addToSet": {"gradeIds": grade_id}}
            )
        print(f"Found existing Kiswahili Lugha subject with ID: {subject_id}")
    
    # Now add strands, substrands, and SLOs
    strands_added = 0
    substrands_added = 0
    slos_added = 0
    
    for strand_data in KISWAHILI_LUGHA_DATA["strands"]:
        # Check if strand exists
        existing_strand = await db.strands.find_one({
            "name": strand_data["name"],
            "subjectId": subject_id
        })
        
        if not existing_strand:
            strand_result = await db.strands.insert_one({
                "name": strand_data["name"],
                "subjectId": subject_id
            })
            strand_id = str(strand_result.inserted_id)
            strands_added += 1
            print(f"  Created strand: {strand_data['name']}")
        else:
            strand_id = str(existing_strand["_id"])
            print(f"  Found existing strand: {strand_data['name']}")
        
        # Add substrands
        for substrand_data in strand_data["substrands"]:
            existing_substrand = await db.substrands.find_one({
                "name": substrand_data["name"],
                "strandId": strand_id
            })
            
            if not existing_substrand:
                substrand_result = await db.substrands.insert_one({
                    "name": substrand_data["name"],
                    "strandId": strand_id
                })
                substrand_id = str(substrand_result.inserted_id)
                substrands_added += 1
                print(f"    Created substrand: {substrand_data['name']}")
            else:
                substrand_id = str(existing_substrand["_id"])
                print(f"    Found existing substrand: {substrand_data['name']}")
            
            # Add SLOs
            for slo_data in substrand_data["slos"]:
                existing_slo = await db.slos.find_one({
                    "name": slo_data["name"],
                    "substrandId": substrand_id
                })
                
                if not existing_slo:
                    await db.slos.insert_one({
                        "name": slo_data["name"],
                        "description": slo_data["description"],
                        "substrandId": substrand_id
                    })
                    slos_added += 1
    
    print(f"\n=== Kiswahili Lugha Seeding Complete ===")
    print(f"Strands added: {strands_added}")
    print(f"Substrands added: {substrands_added}")
    print(f"SLOs added: {slos_added}")
    
    # Verify the data
    total_strands = await db.strands.count_documents({"subjectId": subject_id})
    total_substrands = await db.substrands.count_documents({})
    total_slos = await db.slos.count_documents({})
    
    print(f"\n=== Database Totals ===")
    print(f"Total Kiswahili Lugha strands: {total_strands}")
    print(f"Total substrands (all subjects): {total_substrands}")
    print(f"Total SLOs (all subjects): {total_slos}")

if __name__ == "__main__":
    asyncio.run(seed_kiswahili_lugha())
