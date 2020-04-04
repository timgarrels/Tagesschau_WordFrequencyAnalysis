# Tagesschau Untertitel Crawlen & Worthäufigkeit

Inspiration vom 36C3:
```
"https://media.ccc.de/v/36c3-10993-vom_ich_zum_wir",  Vom Ich zum Wir
Gesellschaftlicher Wandel in den Reden im Bundestag

maha and Kai Biermann 
```
Tl;dw: Worthäufigkeits-Analyse der Gesprächsprotokolle des Bundestags


Eigene Idee: Worthäufigkeits-Analyse der Tagesschau

Schritte:
1. Transcripte der Tagesschau finden --> Es gibt Untertitel --> Jede Tagesschaustream-Seite enthält ein Element `<a class="track" type="application/ttaf+xml" href="/multimedia/untertitel-40731.xml" data-enabled="enabled" lang="de">EBUTT/ttml file</a>`. Unter `/multimedia/untertitel-xxx.xml` liegt die Untertiteldatei im [EBU-TT-D-Basic](https://www.irt.de/fileadmin/media/Neue_Downloads/Publikationen/Technische_Richtlinien/EBU-TT-D-Basic-DE-Untertitelformat_fuer_die_ARD_Mediatheken-v1.2.pdf)-Format.  
Witzig: Tageschauseiten debuggen um Untertitel zu finden, externe Firma beauftragt, deutsche Kommentare im Code :D
2. Transcripte crawlen --> Sendungsarchiv `https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-yyyymmdd.html`, crawlen des Archivs, sammeln der Links und Contenttitel, jüngster Eintrag wohl vom 01.04.2007, da `yyyyymmdd < 20070401` immer trotzdem den 01.04.2007 zeigt --> Gecrawlte Links aufrufen, Untertitellink rausparsen --> Untertitel runterladen
3. Transcripte zu Datenbank parsen (am besten direkt mit maha & Kai Biermanns Tool nutzbar, Mail an die? Tool der Zeit, evtl. von Zeit bezahlt, Copyright...)
4. ???
5. Profit


Ideas:  
- Data Science on Raw HTML of archive-sites/tagesschau-sites: Since when thumbnails, when did url schema change, when which show format?
