"""gera o calendario de contribuicoes do perfil em svg, nas cores da capa"""
import datetime
import re
import sys
import urllib.request

USUARIO = sys.argv[1]
SAIDA = sys.argv[2]
ORIGEM = sys.argv[3] if len(sys.argv) > 3 else None

CORES = ["#161b22", "#0E2A66", "#1B4AA8", "#2F6BE0", "#8DB6FF"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DIAS = {1: "seg", 3: "qua", 5: "sex"}
CELULA, PASSO, MARGEM_X, MARGEM_Y = 12, 15, 40, 24
FONTE = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def baixar_html():
    if ORIGEM:
        return open(ORIGEM, encoding="utf-8").read()
    pedido = urllib.request.Request(
        f"https://github.com/users/{USUARIO}/contributions",
        headers={"x-requested-with": "XMLHttpRequest", "user-agent": "calendario-readme"},
    )
    return urllib.request.urlopen(pedido, timeout=30).read().decode("utf-8")


def ler_dias(html):
    pares = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html)
    return sorted((datetime.date.fromisoformat(data), int(nivel)) for data, nivel in pares)


def linha_do_dia(data):
    return (data.weekday() + 1) % 7


def montar_svg(dias, total):
    primeiro_domingo = dias[0][0] - datetime.timedelta(days=linha_do_dia(dias[0][0]))
    partes, mes_anterior, ultima_coluna = [], None, 0
    for data, nivel in dias:
        coluna = (data - primeiro_domingo).days // 7
        ultima_coluna = max(ultima_coluna, coluna)
        x = MARGEM_X + coluna * PASSO
        y = MARGEM_Y + linha_do_dia(data) * PASSO
        partes.append(f'<rect x="{x}" y="{y}" width="{CELULA}" height="{CELULA}" rx="2" fill="{CORES[nivel]}"/>')
        if linha_do_dia(data) == 0 and data.month != mes_anterior:
            partes.append(f'<text x="{x}" y="14">{MESES[data.month - 1]}</text>')
            mes_anterior = data.month
    for linha, nome in DIAS.items():
        partes.append(f'<text x="0" y="{MARGEM_Y + linha * PASSO + 10}">{nome}</text>')

    largura = MARGEM_X + (ultima_coluna + 1) * PASSO
    base = MARGEM_Y + 7 * PASSO + 22
    partes.append(f'<text x="{MARGEM_X}" y="{base}">{total} contribuições no último ano</text>')
    legenda_x = largura - 5 * PASSO - 78
    partes.append(f'<text x="{legenda_x}" y="{base}">menos</text>')
    for nivel, cor in enumerate(CORES):
        x = legenda_x + 44 + nivel * PASSO
        partes.append(f'<rect x="{x}" y="{base - 10}" width="{CELULA}" height="{CELULA}" rx="2" fill="{cor}"/>')
    partes.append(f'<text x="{legenda_x + 44 + 5 * PASSO + 4}" y="{base}">mais</text>')

    altura = base + 8
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" width="{largura}" height="{altura}" '
        f'role="img" aria-label="Calendário de contribuições no GitHub, {total} no último ano">'
        f'<g font-family="{FONTE}" font-size="11" fill="#8b949e">{"".join(partes)}</g></svg>'
    )


html = baixar_html()
dias = ler_dias(html)
if not dias:
    sys.exit("nenhum dia encontrado no html de contribuicoes")
achado = re.search(r"([\d,]+)\s+contributions", html)
total = achado.group(1).replace(",", ".") if achado else ""
open(SAIDA, "w", encoding="utf-8").write(montar_svg(dias, total))
