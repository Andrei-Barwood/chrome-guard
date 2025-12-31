# Uso de ChromeGuard

Escaneo básico:
```bash
chromeguard scan --browser chrome --output report.json --csv report.csv
```

Check puntual:
```bash
chromeguard check cjpalhdlnbpafiamejdnhcphjbkeiagm
```

Monitoreo:
```bash
chromeguard watch --browser edge --interval 120 --iterations 3
```

Actualizar firmas:
```bash
chromeguard update
python scripts/update_signatures.py
```

