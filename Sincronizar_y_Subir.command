#!/bin/bash
cd "$(dirname "$0")"
echo "============================================="
echo " Sincronización del Dashboard del Comité"
echo "============================================="
python3 update_data.py
echo "============================================="
echo "Proceso completado. Presiona Enter para cerrar."
read
