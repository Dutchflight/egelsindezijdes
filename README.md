# Egels in de Zijdes

Website van het bewonersinitiatief Egels in de Zijdes (Leiden), gehost via GitHub Pages.

## Hoe video's op de site komen

1. Paul uploadt een video naar de Google Drive-map **Egels in de Zijdes – video's** (besloten).
2. Een dagelijkse taak van Claude kijkt welke video's minstens 24 uur in de map staan en nog niet op de site staan.
3. Die video's worden gedownload, met `scripts/add_video.py` gecomprimeerd (max. 720p) en in `videos/` gezet; `videos.json` wordt bijgewerkt.
4. De wijziging wordt naar `main` gepusht; GitHub Pages publiceert de site.

Titel van de video = bestandsnaam in Drive (zonder extensie), tenzij die een standaard cameranaam is.

## Eigen domein

Zodra egelsindezijdes.nl geregistreerd is: zet het domein in een bestand `CNAME` en stel bij de domeinregistrar de DNS-records voor GitHub Pages in.
