#!/bin/sh
# Regenera estudio.py/.tns y corre la bateria en CPython y en
# MicroPython 1.11 con heap limitado (como la calculadora).
# Uso: sh tests/correr.sh        (desde cualquier carpeta)
cd "$(dirname "$0")/.." || exit 1
MP=.tools/micropython/ports/unix/micropython

python3 build.py || exit 1

echo "--- CPython ---"
printf '0\n' | python3 tests/pruebas.py | tail -n 12

if [ -x "$MP" ]; then
    echo "--- MicroPython 1.11, heap 1M (la Nspire tiene ~2 MB) ---"
    printf '0\n' | "$MP" -X heapsize=1M tests/pruebas.py | tail -n 12
else
    echo "(sin MicroPython 1.11 en .tools/: solo se probo en CPython)"
fi
