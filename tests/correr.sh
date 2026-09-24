#!/bin/sh
# Regenera calculadora/ (los 4 archivos) y corre las pruebas en CPython
# y en MicroPython 1.11 con heap limitado (como la calculadora).
# Uso: sh tests/correr.sh        (desde cualquier carpeta)
cd "$(dirname "$0")/.." || exit 1
MP=.tools/micropython/ports/unix/micropython
MALOS=0

python3 build.py || exit 1

corre() {
    # corre <interprete...> -- <archivo> <entradas> <esperado>...
    arch=$1; ent=$2; shift 2
    for interp in py mp; do
        if [ $interp = py ]; then
            out=$(printf "$ent" | python3 "$arch" 2>&1)
        else
            [ -x "$MP" ] || continue
            out=$(printf "$ent" | "$MP" -X heapsize=1M "$arch" 2>&1)
        fi
        for e in "$@"; do
            case "$out" in
                *"$e"*) ;;
                *) echo "FALLA $arch ($interp): falta '$e'"; MALOS=$((MALOS+1)) ;;
            esac
        done
    done
}

echo "--- bateria (general + sat) ---"
printf '0\n0\n' | python3 tests/pruebas.py | tail -n 12
if [ -x "$MP" ]; then
    echo "--- bateria en MicroPython 1.11, heap 1M (la Nspire tiene ~2 MB) ---"
    printf '0\n0\n' | "$MP" -X heapsize=1M tests/pruebas.py | tail -n 12
else
    echo "(sin MicroPython 1.11 en .tools/: solo se probo en CPython)"
fi

echo "--- los 4 archivos sueltos, como se instalan ---"
corre calculadora/ap.py '2\n-x^2+4*x\n0\n5\n\n0\n' "mas alto: y=4 en x=2"
corre calculadora/ai.py '0\n' "IA: REGRESION LINEAL"
corre calculadora/fisica.py '8\n7\n4\n1.5\n0\n\n0\n' \
    ">>> FISICA v7" "t total = 1.616 s" "Saliste de FISICA"
corre calculadora/general.py \
    '1\n2\n-x^2+4*x\n0\n5\n\n0\n2\n0\n3\n8\n7\n2\n0.4\n0\n\n0\n0\n' \
    "elige materia" "mas alto: y=4 en x=2" "IA: REGRESION LINEAL" \
    "subiendo: v = +2.801 m/s" "Para abrir otra vez: general()"
if [ $MALOS = 0 ]; then echo "4 archivos sueltos: TODO OK"; fi
