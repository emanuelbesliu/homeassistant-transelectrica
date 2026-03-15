# Transelectrica SEN - Integrare Home Assistant

Integrare pentru monitorizarea in timp real a **Sistemului Energetic National (SEN)** din Romania, folosind datele publice de la **Transelectrica**.

## Functionalitati

- Monitorizare in timp real: consum, productie, sold schimburi
- Generare pe surse: carbune, gaze, hidro, nuclear, eolian, solar, biomasa, acumulare
- Medii pe 15 minute pentru principalii indicatori
- Procent energie regenerabila (senzor calculat)
- Detalii interconexiuni transfrontaliere (atribute)
- Nu necesita autentificare - date publice nationale
- Actualizare automata la fiecare 60 secunde (configurabil)
- Traduceri complete romana/engleza

## Instalare

### HACS (Recomandat)

1. Deschide HACS in Home Assistant
2. Click pe "Integrations"
3. Click pe meniul cu 3 puncte -> "Custom repositories"
4. Adauga: `https://github.com/emanuelbesliu/homeassistant-transelectrica`
5. Categorie: "Integration"
6. Cauta "Transelectrica SEN" si instaleaza

### Manual

```bash
cd /config/custom_components
git clone https://github.com/emanuelbesliu/homeassistant-transelectrica.git transelectrica
mv transelectrica/custom_components/transelectrica/* transelectrica/
rm -rf transelectrica/custom_components
```

## Configurare

1. Reporniti Home Assistant
2. **Settings -> Devices & Services -> Add Integration**
3. Cautati "Transelectrica SEN"
4. Confirmati configurarea (nu necesita credentiale)
5. Optional: ajustati intervalul de actualizare din optiunile integrarii

## Documentatie Completa

Vezi [README complet](README.md) pentru:
- Lista completa a senzorilor
- Exemple de automatizari
- Configurare dashboard
- Troubleshooting

## Support

- [GitHub Issues](https://github.com/emanuelbesliu/homeassistant-transelectrica/issues)
- [Documentatie completa](README.md)
