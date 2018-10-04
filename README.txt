DAGENS SAMHÄLLES VALBEVAKNING 2018

Syftet med denna repo är att visa hur man som redaktion kan använda python inför (om möjligt) och under en större nyhetshändelse. Ett underliggande syfte är också att enskilda delar av koden kan vara användbara för de som i framtiden vill fördjupa sig i valdata från Valmyndigheten.

Denna repo innehåller majoriteten av databearbetningen som tidningen Dagens Samhälle gjorde i samband med publiceringen av artiklar veckan efter svenska valet den 9 september 2018. Artiklarna publicerades på webben under den efterföljande veckan och i tidningen -- nummer 31 2018.

Innehåll:

1. setup.py
Innehåller kod som skapar rätt mappstruktur för övriga programmet, samt hämtar korrekt data från Valmyndighetens grundfiler.

2. util.py
En fil som innehåller alla funktioner som utför det mesta av de beräkningar som sedan låg till grund för Dagens Samhälles valnummer 2018.

3. notebook.ipynb
Den Notebook som är tänkt att användas för att köra koden i. I denna finner man också löpandes text som förklarar bakgrunden till datakörningen, samt i vissa fall vad som i slutändan inte hamnade i tidningen/på sajten.

4. Pipfile & Pipfile.lock
Programmet är skrivet i en pipenv-miljö. Dessa filer är tänkta att kunna användas för att kunna få till samma utvecklarmiljö för användare.

Viktigaste moduler för detta projekt är:

- pandas
- os
- shutil
- zipfile
- io
- requests
- xml.etree.ElementTree
- warnings
- jupyter notebook
- matplotlib



Om man har frågor är man välkommen att kontakta mig på min mejl: johan.ekman@dagenssamhalle.se

