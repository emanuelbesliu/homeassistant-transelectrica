# Transelectrica SEN - Integrare Home Assistant pentru Sistemul Energetic National

[![GitHub Release](https://img.shields.io/github/v/release/emanuelbesliu/homeassistant-transelectrica)](https://github.com/emanuelbesliu/homeassistant-transelectrica/releases/latest)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/github/license/emanuelbesliu/homeassistant-transelectrica)](LICENSE)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/emanuelbesliu)

Integrare Home Assistant pentru monitorizarea in timp real a **Sistemului Energetic National (SEN)** din Romania, folosind datele publice de la [Transelectrica](https://www.transelectrica.ro).

Datele sunt furnizate de operatorul national de transport al energiei electrice si reflecta starea in timp real a retelei electrice nationale.

## Functionalitati

### Monitorizare in Timp Real
- **Consum national** - Consumul total al SEN (MW)
- **Productie nationala** - Productia totala a SEN (MW)
- **Sold schimburi** - Balanta import/export energie (MW)

### Generare pe Surse
- **Carbune** - Generare din termocentrale pe carbune
- **Hidrocarburi** - Generare din gaze naturale
- **Hidro** - Generare hidroelectrica
- **Nuclear** - Generare nucleara (Cernavoda)
- **Eolian** - Generare din parcuri eoliene
- **Solar** - Generare fotovoltaica
- **Biomasa** - Generare din biomasa
- **Acumulare** - Stocare/pompare (ISPOZ)

### Senzori Suplimentari
- **Procent Energie Regenerabila** - Senzor calculat: (Hidro + Eolian + Solar + Biomasa) / Productie totala

### Atribute Extra
- **Medii pe 15 minute** - Disponibile ca atribute pe senzorii principali
- **Interconexiuni transfrontaliere** - Detalii pe fiecare linie de interconexiune (Ungaria, Serbia, Bulgaria, Ucraina, Moldova)

## Instalare

### Metoda 1: HACS (Recomandat)

1. Deschide HACS in Home Assistant
2. Click pe "Integrations"
3. Click pe meniul cu 3 puncte -> "Custom repositories"
4. Adauga: `https://github.com/emanuelbesliu/homeassistant-transelectrica`
5. Categorie: "Integration"
6. Cauta "Transelectrica SEN" si instaleaza
7. Reporneste Home Assistant

### Metoda 2: Manual

```bash
cd /config
mkdir -p custom_components
cd custom_components
git clone https://github.com/emanuelbesliu/homeassistant-transelectrica.git transelectrica_tmp
mv transelectrica_tmp/custom_components/transelectrica .
rm -rf transelectrica_tmp
```

Reporneste Home Assistant.

## Configurare

### Pas 1: Adauga Integrarea

1. In Home Assistant, mergi la **Settings -> Devices & Services**
2. Click pe **+ Add Integration**
3. Cauta "**Transelectrica SEN**"
4. Confirma configurarea (nu necesita credentiale - datele sunt publice)

### Pas 2: Configureaza Intervalul de Actualizare (Optional)

1. Mergi la **Settings -> Devices & Services -> Transelectrica SEN -> Configure**
2. Seteaza intervalul de actualizare (implicit: 60 secunde, minim: 30 secunde)

### Pas 3: Verifica Senzorii Creati

Dupa configurare, vei avea urmatorii senzori:

| Senzor | Descriere | Unitate |
|--------|-----------|---------|
| `sensor.transelectrica_grid_consumption` | Consum total SEN | MW |
| `sensor.transelectrica_grid_production` | Productie totala SEN | MW |
| `sensor.transelectrica_exchange_balance` | Sold schimburi (import/export) | MW |
| `sensor.transelectrica_coal_generation` | Generare carbune | MW |
| `sensor.transelectrica_hydrocarbon_generation` | Generare hidrocarburi/gaze | MW |
| `sensor.transelectrica_hydro_generation` | Generare hidroelectrica | MW |
| `sensor.transelectrica_nuclear_generation` | Generare nucleara | MW |
| `sensor.transelectrica_wind_generation` | Generare eoliana | MW |
| `sensor.transelectrica_solar_generation` | Generare solara | MW |
| `sensor.transelectrica_biomass_generation` | Generare biomasa | MW |
| `sensor.transelectrica_storage` | Stocare/pompare | MW |
| `sensor.transelectrica_renewable_percentage` | Procent energie regenerabila | % |

## Utilizare

### Atribute Disponibile

Fiecare senzor de generare expune atribute suplimentare:

```yaml
# Exemplu: sensor.transelectrica_grid_consumption
attributes:
  avg_15min: 6150.0      # Media pe 15 minute
  timestamp: "2024-01-15 14:30:00"  # Timestamp-ul datelor
```

Senzorul de productie include si distributia pe surse:

```yaml
# sensor.transelectrica_grid_production
attributes:
  coal_mw: 1200.0
  hydrocarbons_mw: 800.0
  hydro_mw: 1500.0
  nuclear_mw: 1400.0
  wind_mw: 900.0
  solar_mw: 400.0
  biomass_mw: 50.0
  storage_mw: 30.0
```

Senzorul de sold schimburi include detalii interconexiuni:

```yaml
# sensor.transelectrica_exchange_balance
attributes:
  bekescsaba_1: -50.0
  sandorfalva: -30.0
  kozlodui_1: 100.0
  # ... etc.
```

### Exemple Automatizari

#### Notificare Consum Ridicat

```yaml
alias: "Notificare Consum SEN Ridicat"
description: "Trimite notificare cand consumul national depaseste 9000 MW"
mode: single

triggers:
  - entity_id: sensor.transelectrica_grid_consumption
    above: 9000
    trigger: numeric_state

actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "Consum SEN Ridicat"
      message: >-
        Consumul national a depasit 9000 MW:
        {{ states('sensor.transelectrica_grid_consumption') }} MW
```

#### Notificare Energie Regenerabila Sub Prag

```yaml
alias: "Notificare Regenerabile Scazute"
description: "Alerta cand procentul de energie regenerabila scade sub 20%"
mode: single

triggers:
  - entity_id: sensor.transelectrica_renewable_percentage
    below: 20
    trigger: numeric_state

actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "Energie Regenerabila Scazuta"
      message: >-
        Doar {{ states('sensor.transelectrica_renewable_percentage') }}%
        din energie provine din surse regenerabile.
```

### Exemple Dashboard

#### Card Rezumat SEN

```yaml
type: entities
title: Sistem Energetic National
entities:
  - entity: sensor.transelectrica_grid_consumption
    name: Consum Total
  - entity: sensor.transelectrica_grid_production
    name: Productie Totala
  - entity: sensor.transelectrica_exchange_balance
    name: Sold Schimburi
  - entity: sensor.transelectrica_renewable_percentage
    name: Regenerabile
```

#### Card Generare pe Surse

```yaml
type: custom:bar-card
title: Generare pe Surse (MW)
entities:
  - entity: sensor.transelectrica_nuclear_generation
    name: Nuclear
    color: orange
  - entity: sensor.transelectrica_hydro_generation
    name: Hidro
    color: blue
  - entity: sensor.transelectrica_wind_generation
    name: Eolian
    color: teal
  - entity: sensor.transelectrica_solar_generation
    name: Solar
    color: yellow
  - entity: sensor.transelectrica_coal_generation
    name: Carbune
    color: grey
  - entity: sensor.transelectrica_hydrocarbon_generation
    name: Gaze
    color: red
  - entity: sensor.transelectrica_biomass_generation
    name: Biomasa
    color: green
```

## Despre Date

### Sursa Datelor

Datele provin de la [Transelectrica](https://www.transelectrica.ro), operatorul national de transport al energiei electrice din Romania. Endpoint-ul `/sen-filter` furnizeaza date in timp real despre starea SEN.

### Frecventa Actualizare

- API-ul Transelectrica se actualizeaza la fiecare ~10 secunde
- Integrarea actualizeaza implicit la fiecare 60 de secunde (configurabil: 30s - 3600s)
- Valorile pe 15 minute sunt medii calculate de Transelectrica

### Limitari

- Datele sunt la nivel national (nu exista detaliere regionala)
- O singura instanta a integrarii este permisa (datele sunt identice pentru toti utilizatorii)
- Site-ul Transelectrica foloseste Cloudflare; in cazuri rare, request-urile pot fi blocate temporar

## Troubleshooting

### Senzorii arata "unavailable"

1. Verificati conexiunea la internet
2. Verificati logurile: **Settings -> System -> Logs**, cautati "transelectrica"
3. Posibil ca site-ul Transelectrica sa fie temporar indisponibil
4. Reincarcati integrarea: **Settings -> Devices & Services -> Transelectrica SEN -> Reload**

### Valorile nu se actualizeaza

1. Verificati intervalul de actualizare configurat
2. API-ul poate returna date identice daca SEN-ul este stabil
3. Verificati atributul `timestamp` pe senzori pentru a vedea cat de recente sunt datele

### Eroare la configurare

1. Verificati ca aveti acces la `https://www.transelectrica.ro`
2. Unele retele corporative pot bloca accesul la site
3. Verificati ca nu aveti deja o instanta configurata (o singura instanta permisa)

## Structura Fisierelor

```
custom_components/transelectrica/
  __init__.py           # Entry point
  manifest.json         # Metadata integrare
  const.py              # Constante si definitii senzori
  api.py                # Client API Transelectrica
  coordinator.py        # Data Update Coordinator
  config_flow.py        # Configurare UI
  sensor.py             # Entitati senzor
  strings.json          # Stringuri traducere (EN)
  translations/
    en.json             # Traduceri engleza
    ro.json             # Traduceri romana
```

## Contributii

Contributiile sunt binevenite! Pentru bug-uri sau feature requests, deschideti un issue pe GitHub.

## Licenta

MIT License - Vezi [LICENSE](LICENSE) pentru detalii.

## Support

- **GitHub Issues**: [Raportati probleme](https://github.com/emanuelbesliu/homeassistant-transelectrica/issues)
- **Home Assistant Community**: [Forum discutii](https://community.home-assistant.io/)

---

## ☕ Support the Developer

If you find this project useful, consider buying me a coffee!

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/emanuelbesliu)

---

*Aceasta integrare nu este afiliata oficial cu Transelectrica SA.*
*Datele sunt furnizate public de catre Transelectrica pentru informarea populatiei.*
