import csv
import io
import json
import os
from datetime import datetime
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

CODIGOS_ACCESO = {
    "DEMO2026": {"plan": "DEMO", "limite": 1000},
    "VIP100": {"plan": "VIP", "limite": 5000},
    "CONTAB2026": {"plan": "PRO", "limite": 999999},
}

CUENTAS_VEN = [
    {"codigo": "1.1.01", "nombre": "Caja Chica", "grupo": "ACTIVO_CORRIENTE", "naturaleza": "DEUDORA"},
    {"codigo": "1.1.02", "nombre": "Banco Nacional", "grupo": "ACTIVO_CORRIENTE", "naturaleza": "DEUDORA"},
    {"codigo": "1.1.03", "nombre": "Cuentas por Cobrar Clientes", "grupo": "ACTIVO_CORRIENTE", "naturaleza": "DEUDORA"},
    {"codigo": "1.1.04", "nombre": "Inventario de Mercancías", "grupo": "ACTIVO_CORRIENTE", "naturaleza": "DEUDORA"},
    {"codigo": "1.1.05", "nombre": "Crédito Fiscal IVA", "grupo": "ACTIVO_CORRIENTE", "naturaleza": "DEUDORA"},
    {"codigo": "1.2.01", "nombre": "Propiedad, Planta y Equipo", "grupo": "ACTIVO_NO_CORRIENTE", "naturaleza": "DEUDORA"},
    {"codigo": "1.2.02", "nombre": "Depreciación Acumulada PPE", "grupo": "ACTIVO_NO_CORRIENTE", "naturaleza": "ACREEDORA"},
    {"codigo": "2.1.01", "nombre": "Cuentas por Pagar Proveedores", "grupo": "PASIVO_CORRIENTE", "naturaleza": "ACREEDORA"},
    {"codigo": "2.1.02", "nombre": "Débito Fiscal IVA", "grupo": "PASIVO_CORRIENTE", "naturaleza": "ACREEDORA"},
    {"codigo": "2.1.03", "nombre": "Retenciones de IVA por Pagar", "grupo": "PASIVO_CORRIENTE", "naturaleza": "ACREEDORA"},
    {"codigo": "2.1.04", "nombre": "Retenciones de ISLR por Pagar", "grupo": "PASIVO_CORRIENTE", "naturaleza": "ACREEDORA"},
    {"codigo": "2.2.01", "nombre": "Obligaciones a Largo Plazo", "grupo": "PASIVO_NO_CORRIENTE", "naturaleza": "ACREEDORA"},
    {"codigo": "3.1.01", "nombre": "Capital Social", "grupo": "PATRIMONIO", "naturaleza": "ACREEDORA"},
    {"codigo": "3.1.02", "nombre": "Utilidades / Pérdidas Acumuladas", "grupo": "PATRIMONIO", "naturaleza": "ACREEDORA"},
    {"codigo": "4.1.01", "nombre": "Ventas / Ingresos Operativos", "grupo": "INGRESO", "naturaleza": "ACREEDORA"},
    {"codigo": "5.1.01", "nombre": "Costo de Ventas", "grupo": "COSTO", "naturaleza": "DEUDORA"},
    {"codigo": "6.1.01", "nombre": "Gastos Administrativos y Operativos", "grupo": "GASTO", "naturaleza": "DEUDORA"},
]

RENGLONES_CONTAB = [
    {"id": "r01", "num": 1, "label": "Seleccionar y Ejecutar Archivo", "rama": "rama_directo", "ico": "ico-doc"},
    {"id": "r02", "num": 2, "label": "Destino del Archivo (BG / ER)", "rama": "rama_directo", "ico": "ico-doc"},
    {"id": "r03", "num": 3, "label": "Balance General VEN (Editable)", "rama": "rama_directo", "ico": "ico-chart"},
    {"id": "r04", "num": 4, "label": "Estado Resultados VEN (Editable)", "rama": "rama_directo", "ico": "ico-chart"},
    {"id": "r05", "num": 5, "label": "Activo Corriente", "rama": "rama_directo", "ico": "ico-coin"},
    {"id": "r06", "num": 6, "label": "Activo No Corriente", "rama": "rama_directo", "ico": "ico-coin"},
    {"id": "r07", "num": 7, "label": "Pasivo Corriente", "rama": "rama_directo", "ico": "ico-doc"},
    {"id": "r08", "num": 8, "label": "Pasivo No Corriente", "rama": "rama_directo", "ico": "ico-doc"},
    {"id": "r09", "num": 9, "label": "Patrimonio VEN", "rama": "rama_directo", "ico": "ico-chart"},
    {"id": "r10", "num": 10, "label": "Entradas y Salidas", "rama": "rama_libros", "ico": "ico-coin"},
    {"id": "r11", "num": 11, "label": "Libro Diario", "rama": "rama_libros", "ico": "ico-book"},
    {"id": "r12", "num": 12, "label": "Libro Mayor", "rama": "rama_libros", "ico": "ico-book"},
    {"id": "r13", "num": 13, "label": "Libro de Ventas IVA", "rama": "rama_libros", "ico": "ico-doc"},
    {"id": "r14", "num": 14, "label": "Libro de Compras IVA", "rama": "rama_libros", "ico": "ico-doc"},
    {"id": "r15", "num": 15, "label": "Retenciones IVA / ISLR", "rama": "rama_libros", "ico": "ico-coin"},
    {"id": "r16", "num": 16, "label": "Cuentas por Cobrar", "rama": "rama_libros", "ico": "ico-doc"},
    {"id": "r17", "num": 17, "label": "Cuentas por Pagar", "rama": "rama_libros", "ico": "ico-doc"},
    {"id": "r18", "num": 18, "label": "Cierre del Período", "rama": "rama_libros", "ico": "ico-book"},
    {"id": "r19", "num": 19, "label": "Ordenar y Exportar CSV", "rama": "rama_directo", "ico": "ico-doc"},
    {"id": "r20", "num": 20, "label": "Actualizaciones VEN", "rama": "rama_aprender", "ico": "ico-grad"},
    {"id": "r21", "num": 21, "label": "Cursos e Informes", "rama": "rama_aprender", "ico": "ico-grad"},
    {"id": "r22", "num": 22, "label": "Precios Actuales", "rama": "rama_aprender", "ico": "ico-coin"},
]

CURSOS_Y_ACTUALIZACIONES = [
    {
        "titulo": "Actualización · Enfoque Contable en Venezuela (VEN-NIF)",
        "detalle": "Presentación de estados financieros bajo lineamientos adaptados en Venezuela: separación de partidas corrientes y no corrientes, revelación de políticas contables y consistencia entre el Libro Diario, Libro Mayor y estados resumidos.",
    },
    {
        "titulo": "Actualización · Libros de Ventas y Compras, Control y Retenciones",
        "detalle": "Verificación de RIF, número de factura, número de control, base imponible, alícuotas de IVA (general, reducida o exenta) y porcentajes de retención de IVA e ISLR según el tipo de operación.",
    },
    {
        "titulo": "Curso · Cómo leer un Estado de Resultados venezolano paso a paso",
        "detalle": "1) Suma los ingresos operativos del período. 2) Resta el costo de ventas para obtener la utilidad bruta. 3) Resta los gastos administrativos y operativos para hallar la utilidad operativa. 4) Incorpora otros ingresos/egresos y estimaciones fiscales para llegar a la utilidad o pérdida neta.",
    },
    {
        "titulo": "Curso · Cómo leer un Balance General venezolano paso a paso",
        "detalle": "Clasifica el Activo en Corriente (efectivo, bancos, cuentas por cobrar) y No Corriente (propiedad, planta y equipo). Clasifica el Pasivo en Corriente y No Corriente, y contrasta el Patrimonio para comprobar el equilibrio contable.",
    },
    {
        "titulo": "Curso · Cierre contable e informes contables para clientes y gerencia",
        "detalle": "Antes del cierre: revisa movimientos pendientes, asientos descuadrados y facturas sin clasificar. Al cerrar: registra la observación del período y emite un informe claro con resultados, liquidez y cuentas pendientes.",
    },
]

HTML_CONTAB = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>C-CONTAB // Totalmente Contable · Venezuela</title>
  <style>
    :root {
      --bg-dark: #040711;
      --bg-navy: #091124;
      --panel: #0d1934;
      --panel-2: #132347;
      --border: #283f75;
      --text: #f8fafc;
      --muted: #a6bae0;
      --fucsia: {{ tono_fucsia }};
      --fucsia-2: #db2777;
      --fucsia-soft: rgba(236, 72, 153, 0.16);
      --ok: #10b981;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Inter", "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
      background:
        radial-gradient(circle at 90% 6%, rgba(236, 72, 153, 0.22), transparent 38%),
        radial-gradient(circle at 10% 14%, #162e66 0%, var(--bg-dark) 65%);
      color: var(--text);
      min-height: 100vh;
      font-size: 15px;
    }
    .corner-tag {
      position: fixed;
      top: 14px;
      right: 16px;
      z-index: 60;
      background: rgba(13, 25, 52, 0.96);
      border: 1.5px solid var(--fucsia);
      color: #f9a8d4;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 0.76rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      box-shadow: 0 0 20px rgba(236, 72, 153, 0.28);
    }
    .wrap { max-width: 1480px; margin: 0 auto; padding: 52px 24px 80px; }
    .login-box {
      max-width: 460px;
      margin: 68px auto;
      background: linear-gradient(165deg, var(--panel) 0%, var(--bg-navy) 100%);
      border: 1.5px solid var(--fucsia);
      box-shadow: 0 0 46px rgba(236, 72, 153, 0.24);
      border-radius: 12px;
      padding: 36px 30px;
      text-align: center;
    }
    .brand-title { margin: 0; font-size: 2.35rem; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; }
    .brand-title span { color: var(--fucsia); }
    .brand-sub { margin: 8px 0 24px; font-size: 0.8rem; color: var(--muted); letter-spacing: 0.2em; text-transform: uppercase; }

    label {
      display: block;
      text-align: left;
      font-size: 0.84rem;
      font-weight: 600;
      color: #cbd5e1;
      margin-bottom: 7px;
      letter-spacing: 0.03em;
    }
    input, select, textarea {
      width: 100%;
      background: var(--bg-dark);
      color: var(--text);
      border: 1.5px solid var(--border);
      border-radius: 8px;
      padding: 11px 14px;
      font-size: 0.94rem;
      margin-bottom: 16px;
    }
    .inp-inline {
      width: 150px;
      margin-bottom: 0;
      padding: 7px 10px;
      font-size: 0.88rem;
      display: inline-block;
    }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--fucsia); }

    button {
      cursor: pointer;
      border: none;
      border-radius: 8px;
      padding: 12px 18px;
      font-weight: 700;
      font-size: 0.9rem;
      letter-spacing: 0.04em;
    }
    .btn-fucsia {
      width: 100%;
      background: linear-gradient(90deg, var(--fucsia-2), var(--fucsia));
      color: #fff;
      padding: 13px 18px;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }
    .btn-navy {
      background: var(--panel-2);
      color: var(--text);
      border: 1.5px solid var(--border);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .btn-navy:hover { border-color: var(--fucsia); }

    .topbar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      background: var(--panel);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      padding: 16px 22px;
      margin-bottom: 20px;
    }
    .pill {
      display: inline-block;
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      background: var(--fucsia-soft);
      color: #f9a8d4;
      border: 1px solid rgba(236, 72, 153, 0.45);
    }

    .ramas-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      margin-bottom: 22px;
    }
    .rama-btn {
      background: var(--panel);
      border: 1.5px solid var(--border);
      color: var(--text);
      padding: 18px 20px;
      border-radius: 10px;
      text-align: left;
    }
    .rama-btn.active {
      background: linear-gradient(135deg, rgba(219,39,119,0.26), rgba(13,25,52,0.98));
      border-color: var(--fucsia);
      box-shadow: 0 0 24px rgba(236, 72, 153, 0.22);
    }
    .rama-title { font-size: 1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; display: block; }
    .rama-desc { font-size: 0.82rem; color: var(--muted); display: block; margin-top: 5px; line-height: 1.4; }

    .app-layout {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 22px;
      align-items: start;
    }
    @media (max-width: 980px) {
      .app-layout { grid-template-columns: 1fr; }
    }

    .fila-menu {
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: var(--panel);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      max-height: 82vh;
      overflow-y: auto;
    }
    .renglon-item {
      display: flex;
      align-items: center;
      gap: 12px;
      width: 100%;
      background: var(--panel-2);
      border: 1.5px solid transparent;
      color: var(--text);
      padding: 11px 12px;
      border-radius: 8px;
      text-align: left;
      font-size: 0.84rem;
      font-weight: 600;
    }
    .renglon-item:hover, .renglon-item.active {
      border-color: var(--fucsia);
      background: var(--fucsia-soft);
    }
    .thumb-box {
      width: 38px;
      height: 38px;
      min-width: 38px;
      border-radius: 7px;
      background: var(--bg-dark);
      border: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .main-stage {
      background: var(--panel);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      padding: 24px;
    }
    .hidden { display: none !important; }

    .split-directo {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(390px, 1fr));
      gap: 22px;
      margin-bottom: 24px;
    }
    .card {
      background: var(--panel-2);
      border: 1.5px solid var(--border);
      border-radius: 10px;
      padding: 22px;
      margin-bottom: 20px;
    }
    .card-bg { border-top: 3px solid var(--fucsia); }
    .card-file { border-top: 3px solid #f472b6; }
    .card-learn { border-left: 4px solid var(--fucsia); }

    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }

    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
      gap: 14px;
      margin: 14px 0 20px;
    }
    .kpi {
      background: var(--bg-dark);
      border: 1px solid var(--border);
      border-left: 3px solid var(--fucsia);
      border-radius: 8px;
      padding: 13px 14px;
    }
    .kpi-lbl { font-size: 0.76rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-val { font-size: 1.15rem; font-weight: 800; margin-top: 4px; }

    .table-wrap {
      overflow-x: auto;
      max-height: 380px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 18px;
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    th, td { border: 1px solid var(--border); padding: 9px 12px; text-align: left; }
    th { background: var(--panel); position: sticky; top: 0; z-index: 2; color: #f9a8d4; text-transform: uppercase; font-size: 0.76rem; letter-spacing: 0.05em; }

    .alert-err {
      background: rgba(239, 68, 68, 0.16);
      border: 1.5px solid #ef4444;
      color: #fecaca;
      padding: 13px 16px;
      border-radius: 8px;
      margin-bottom: 18px;
      font-size: 0.9rem;
    }
    .alert-ok {
      background: rgba(16, 185, 129, 0.15);
      border: 1.5px solid var(--ok);
      color: #a7f3d0;
      padding: 13px 16px;
      border-radius: 8px;
      margin-bottom: 18px;
      font-size: 0.9rem;
    }
    .curso-stream { display: flex; flex-direction: column; gap: 16px; }
    .renglon-banner {
      background: var(--fucsia-soft);
      border: 1px solid var(--fucsia);
      border-radius: 8px;
      padding: 12px 16px;
      margin-bottom: 18px;
      font-size: 0.88rem;
      color: #fbcfe8;
    }
    a { color: #f472b6; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<div class="corner-tag">Totalmente contable</div>

<svg width="0" height="0" style="position:absolute;">
  <defs>
    <g id="ico-doc">
      <rect x="6" y="4" width="12" height="16" rx="2" fill="none" stroke="#f472b6" stroke-width="1.8"/>
      <line x1="9" y1="9" x2="15" y2="9" stroke="#9fb3d9" stroke-width="1.6"/>
      <line x1="9" y1="13" x2="15" y2="13" stroke="#9fb3d9" stroke-width="1.6"/>
    </g>
    <g id="ico-chart">
      <rect x="4" y="12" width="3.5" height="7" fill="#ec4899"/>
      <rect x="10" y="8" width="3.5" height="11" fill="#f472b6"/>
      <rect x="16" y="5" width="3.5" height="14" fill="#10b981"/>
    </g>
    <g id="ico-book">
      <path d="M4 6h6a2 2 0 0 1 2 2v10a2 2 0 0 0-2-2H4z" fill="none" stroke="#ec4899" stroke-width="1.7"/>
      <path d="M20 6h-6a2 2 0 0 0-2 2v10a2 2 0 0 1 2-2h6z" fill="none" stroke="#9fb3d9" stroke-width="1.7"/>
    </g>
    <g id="ico-coin">
      <circle cx="12" cy="12" r="7" fill="none" stroke="#f472b6" stroke-width="1.8"/>
      <line x1="12" y1="7" x2="12" y2="17" stroke="#10b981" stroke-width="1.6"/>
    </g>
    <g id="ico-grad">
      <polygon points="12,5 21,10 12,15 3,10" fill="none" stroke="#ec4899" stroke-width="1.7"/>
      <path d="M7 12.5v4.5c0 1.5 2.2 2.5 5 2.5s5-1 5-2.5v-4.5" fill="none" stroke="#9fb3d9" stroke-width="1.6"/>
    </g>
  </defs>
</svg>

<div class="wrap">
  {% if not autorizado %}
    <div class="login-box">
      <div class="thumb-box" style="width:58px;height:58px;margin:0 auto 14px;border-radius:10px;">
        <svg viewBox="0 0 24 24" width="34" height="34"><use href="#ico-chart"/></svg>
      </div>
      <h1 class="brand-title">C-<span>CONTAB</span></h1>
      <p class="brand-sub">CONTABILIDAD VENEZUELA // ACCESO</p>
      {% if error %}<div class="alert-err">{{ error }}</div>{% endif %}
      <form method="POST">
        <label for="codigo">Clave / Código de acceso</label>
        <input id="codigo" name="codigo" type="text" placeholder="DEMO2026, VIP100 o CONTAB2026" required />
        <button class="btn-fucsia" type="submit">Entrar a C-CONTAB</button>
      </form>
    </div>
  {% else %}
    <div class="topbar">
      <div>
        <strong style="font-size:1.15rem;letter-spacing:0.08em;">C-<span style="color:var(--fucsia)">CONTAB</span></strong>
        <span class="pill">{{ codigo }} · {{ plan }}</span>
        {% if estado_cierre == 'CERRADO' %}
          <span class="pill" style="background:rgba(16,185,129,0.16);color:#6ee7b7;border-color:#10b981;">PERÍODO CERRADO</span>
        {% else %}
          <span class="pill">PERÍODO ABIERTO</span>
        {% endif %}
      </div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <span class="pill">Tasa: {{ tasa_ref }} Bs</span>
        <span class="pill">Uso: {{ uso }} / {{ limite }}</span>
        <a class="btn-navy" style="padding:8px 14px;border-radius:8px;" href="/">Salir</a>
      </div>
    </div>

    {% if error %}<div class="alert-err">{{ error }}</div>{% endif %}
    {% if aviso %}<div class="alert-ok">{{ aviso }}</div>{% endif %}

    <div class="ramas-bar">
      <button type="button" class="rama-btn {% if active_rama == 'rama_directo' %}active{% endif %}" onclick="openRama('rama_directo', this)">
        <span class="rama-title">Rama 1 · Flujo Directo &amp; Estados VEN</span>
        <span class="rama-desc">Balance General y Estado de Resultados editables en blanco + Seleccionar y Ejecutar Archivo</span>
      </button>
      <button type="button" class="rama-btn {% if active_rama == 'rama_libros' %}active{% endif %}" onclick="openRama('rama_libros', this)">
        <span class="rama-title">Rama 2 · Libros, Tributos y Cierre</span>
        <span class="rama-desc">Entradas/Salidas, Libro Diario, Mayor, Ventas/Compras IVA/ISLR, CxC/CxP y Cierre</span>
      </button>
      <button type="button" class="rama-btn {% if active_rama == 'rama_aprender' %}active{% endif %}" onclick="openRama('rama_aprender', this)">
        <span class="rama-title">Rama 3 · Actualizaciones y Cursos</span>
        <span class="rama-desc">Novedades contables Venezuela, cursos de lectura vertical y precios actuales</span>
      </button>
    </div>

    <div class="app-layout">
      <aside class="fila-menu" aria-label="Menú vertical por renglones">
        {% for item in renglones_menu %}
          <button type="button" class="renglon-item {% if active_renglon == item.id %}active{% endif %}" onclick="openRenglon('{{ item.id }}', '{{ item.label }}', '{{ item.rama }}', this)">
            <span class="thumb-box">
              <svg viewBox="0 0 24 24" width="20" height="20"><use href="#{{ item.ico }}"/></svg>
            </span>
            <span>{{ item.label }}</span>
          </button>
        {% endfor %}
      </aside>

      <main class="main-stage">
        <div id="renglon_banner" class="renglon-banner">
          Renglón activo: <strong id="renglon_activo_txt">{{ active_renglon_label }}</strong> · Inicia en blanco, escribe directo en los estados o selecciona y ejecuta un archivo.
        </div>

        <div id="rama_directo" class="rama-sec {% if active_rama != 'rama_directo' %}hidden{% endif %}">
          <div class="split-directo">
            <!-- ESTADOS EDITABLES DIRECTAMENTE EN BLANCO -->
            <div class="card card-bg">
              <h2 style="margin-top:0;color:#f9a8d4;text-transform:uppercase;letter-spacing:0.05em;">Estados Financieros · Venezuela (Editable)</h2>
              <div class="kpi-row">
                <div class="kpi"><div class="kpi-lbl">Activo Total</div><div class="kpi-val" style="color:var(--ok)">{{ bg.activo_total }}</div></div>
                <div class="kpi"><div class="kpi-lbl">Pasivo Total</div><div class="kpi-val" style="color:#f472b6">{{ bg.pasivo_total }}</div></div>
                <div class="kpi"><div class="kpi-lbl">Patrimonio Total</div><div class="kpi-val">{{ bg.patrimonio_total }}</div></div>
                <div class="kpi"><div class="kpi-lbl">Utilidad / Pérdida Neta</div><div class="kpi-val" style="color:var(--ok)">{{ er.utilidad_neta }}</div></div>
              </div>

              <form method="POST">
                <input type="hidden" name="codigo" value="{{ codigo }}" />
                <input type="hidden" name="active_rama" value="rama_directo" />
                <input type="hidden" name="accion" value="guardar_estados_editables" />

                <h3 style="color:#f9a8d4;margin:14px 0 10px;">Estado de Resultados (Escribe y edita directo)</h3>
                <div class="table-wrap">
                  <table>
                    <thead><tr><th>Renglón del Estado de Resultados</th><th>Valor</th></tr></thead>
                    <tbody>
                      <tr><td>Ingresos Operativos</td><td><input class="inp-inline" type="number" step="any" name="er_ingresos" value="{{ raw_est.er_ingresos }}" /></td></tr>
                      <tr><td>(-) Costo de Ventas</td><td><input class="inp-inline" type="number" step="any" name="er_costos" value="{{ raw_est.er_costos }}" /></td></tr>
                      <tr><td><strong>Utilidad Bruta (Calculado)</strong></td><td><strong>{{ er.utilidad_bruta }}</strong></td></tr>
                      <tr><td>(-) Gastos Administrativos y Operativos</td><td><input class="inp-inline" type="number" step="any" name="er_gastos" value="{{ raw_est.er_gastos }}" /></td></tr>
                      <tr><td><strong>Utilidad / (Pérdida) Operativa (Calculado)</strong></td><td><strong>{{ er.utilidad_operativa }}</strong></td></tr>
                      <tr><td>(+/-) Otros Ingresos / Egresos</td><td><input class="inp-inline" type="number" step="any" name="er_otros" value="{{ raw_est.er_otros }}" /></td></tr>
                      <tr><td>(-) Estimación ISLR</td><td><input class="inp-inline" type="number" step="any" name="er_islr" value="{{ raw_est.er_islr }}" /></td></tr>
                      <tr><td><strong>Utilidad / (Pérdida) Neta (Calculado)</strong></td><td><strong>{{ er.utilidad_neta }}</strong></td></tr>
                    </tbody>
                  </table>
                </div>

                <h3 style="color:#f9a8d4;margin:16px 0 10px;">Balance General (Escribe y edita directo)</h3>
                <div class="table-wrap">
                  <table>
                    <thead><tr><th>Partida del Balance General</th><th>Valor</th></tr></thead>
                    <tbody>
                      <tr><td><strong>ACTIVO CORRIENTE</strong></td><td><strong>{{ bg.activo_corriente }}</strong></td></tr>
                      <tr><td>· Efectivo, Caja y Bancos</td><td><input class="inp-inline" type="number" step="any" name="bg_efectivo" value="{{ raw_est.bg_efectivo }}" /></td></tr>
                      <tr><td>· Cuentas por Cobrar</td><td><input class="inp-inline" type="number" step="any" name="bg_cxc" value="{{ raw_est.bg_cxc }}" /></td></tr>
                      <tr><td>· Inventario</td><td><input class="inp-inline" type="number" step="any" name="bg_inv" value="{{ raw_est.bg_inv }}" /></td></tr>
                      <tr><td><strong>ACTIVO NO CORRIENTE</strong></td><td><strong>{{ bg.activo_no_corriente }}</strong></td></tr>
                      <tr><td>· Propiedad, Planta y Equipo (Neto)</td><td><input class="inp-inline" type="number" step="any" name="bg_ppe" value="{{ raw_est.bg_ppe }}" /></td></tr>
                      <tr><td><strong>TOTAL ACTIVO (Calculado)</strong></td><td><strong>{{ bg.activo_total }}</strong></td></tr>
                      <tr><td><strong>PASIVO CORRIENTE</strong></td><td><strong>{{ bg.pasivo_corriente }}</strong></td></tr>
                      <tr><td>· Cuentas por Pagar / Retenciones</td><td><input class="inp-inline" type="number" step="any" name="bg_cxp" value="{{ raw_est.bg_cxp }}" /></td></tr>
                      <tr><td><strong>PASIVO NO CORRIENTE</strong></td><td><strong>{{ bg.pasivo_no_corriente }}</strong></td></tr>
                      <tr><td>· Obligaciones a Largo Plazo</td><td><input class="inp-inline" type="number" step="any" name="bg_pas_lp" value="{{ raw_est.bg_pas_lp }}" /></td></tr>
                      <tr><td><strong>TOTAL PASIVO (Calculado)</strong></td><td><strong>{{ bg.pasivo_total }}</strong></td></tr>
                      <tr><td><strong>PATRIMONIO</strong></td><td><strong>{{ bg.patrimonio_total }}</strong></td></tr>
                      <tr><td>· Capital Social</td><td><input class="inp-inline" type="number" step="any" name="bg_capital" value="{{ raw_est.bg_capital }}" /></td></tr>
                      <tr><td>· Utilidades / Resultados Acumulados</td><td><input class="inp-inline" type="number" step="any" name="bg_util_ac" value="{{ raw_est.bg_util_ac }}" /></td></tr>
                      <tr><td><strong>TOTAL PASIVO + PATRIMONIO</strong></td><td><strong>{{ bg.pasivo_mas_patrimonio }}</strong></td></tr>
                    </tbody>
                  </table>
                </div>

                <button type="submit" class="btn-fucsia">Guardar cambios directos en Estados</button>
              </form>
            </div>

            <!-- SELECCIONAR Y EJECUTAR ARCHIVO -->
            <div class="card card-file">
              <h2 style="margin-top:0;color:#f9a8d4;text-transform:uppercase;letter-spacing:0.05em;">Seleccionar y Ejecutar Archivo</h2>
              <p style="color:var(--muted);font-size:0.88rem;line-height:1.5;margin-bottom:18px;">
                Selecciona un archivo o escribe/pega tus líneas y ejecútalo para sumarlas directo al Balance General, Estado de Resultados o libros.
              </p>

              <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="codigo" value="{{ codigo }}" />
                <input type="hidden" name="active_rama" value="rama_directo" />
                <input type="hidden" name="accion" value="ejecutar_archivo_directo" />

                <label for="dir_archivo">Seleccionar un archivo (.csv, .txt, .json)</label>
                <input id="dir_archivo" name="dir_archivo" type="file" accept=".csv,.txt,.json" />

                <label for="dir_texto">O escribir / pegar líneas (Fecha, Tipo, Cuenta, Concepto, Monto)</label>
                <textarea id="dir_texto" name="dir_texto" rows="5" placeholder=""></textarea>

                <label for="dir_destino">¿Dónde meter esta información al ejecutar?</label>
                <select id="dir_destino" name="dir_destino">
                  <option value="balance_general">Balance General y Estado de Resultados (Directo)</option>
                  <option value="diario">Libro Diario (Debe / Haber)</option>
                  <option value="ventas">Libro de Ventas IVA</option>
                  <option value="compras">Libro de Compras IVA</option>
                  <option value="cxc">Cuentas por Cobrar</option>
                  <option value="cxp">Cuentas por Pagar</option>
                </select>

                <button type="submit" class="btn-fucsia">Ejecutar archivo</button>
              </form>

              <form method="POST" style="margin-top:22px;border-top:1px solid var(--border);padding-top:18px;">
                <input type="hidden" name="codigo" value="{{ codigo }}" />
                <input type="hidden" name="active_rama" value="rama_directo" />
                <input type="hidden" name="accion" value="ordenar_movs" />
                <div class="grid-2">
                  <div>
                    <label for="ord_c">Ordenar por</label>
                    <select id="ord_c" name="orden_campo">
                      <option value="fecha" {% if orden_campo == 'fecha' %}selected{% endif %}>Fecha</option>
                      <option value="monto" {% if orden_campo == 'monto' %}selected{% endif %}>Monto</option>
                      <option value="tipo" {% if orden_campo == 'tipo' %}selected{% endif %}>Tipo</option>
                      <option value="cuenta" {% if orden_campo == 'cuenta' %}selected{% endif %}>Cuenta</option>
                    </select>
                  </div>
                  <div>
                    <label for="ord_d">Dirección</label>
                    <select id="ord_d" name="orden_dir">
                      <option value="desc" {% if orden_dir == 'desc' %}selected{% endif %}>Descendente</option>
                      <option value="asc" {% if orden_dir == 'asc' %}selected{% endif %}>Ascendente</option>
                    </select>
                  </div>
                </div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;">
                  <button type="submit" class="btn-navy" style="flex:1;">Ordenar registros</button>
                  <a class="btn-navy" style="padding:12px 16px;border-radius:8px;" href="/descargar-contable?codigo={{ codigo }}">Exportar CSV</a>
                </div>
              </form>
            </div>
          </div>

          <div class="card">
            <h3 style="margin-top:0;color:#f9a8d4;">Movimientos registrados</h3>
            <div class="table-wrap">
              <table>
                <thead><tr><th>#</th><th>Fecha</th><th>Tipo</th><th>Cuenta</th><th>Concepto</th><th>Monto</th></tr></thead>
                <tbody>
                  {% for m in movimientos %}
                    <tr>
                      <td>{{ loop.index }}</td>
                      <td>{{ m.fecha }}</td>
                      <td>{{ m.tipo }}</td>
                      <td>{{ m.cuenta }}</td>
                      <td>{{ m.concepto }}</td>
                      <td>{{ m.monto }}</td>
                    </tr>
                  {% else %}
                    <tr><td colspan="6" style="color:var(--muted)">Sin movimientos todavía. Escribe arriba o ejecuta un archivo.</td></tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div id="rama_libros" class="rama-sec {% if active_rama != 'rama_libros' %}hidden{% endif %}">
          <h2 style="margin-top:0;color:#f9a8d4;text-transform:uppercase;letter-spacing:0.05em;">Libros, Tributos, Cuentas y Cierre</h2>

          <div class="grid-2">
            <form method="POST" class="card">
              <h3 style="margin-top:0;color:#f9a8d4;">Entrada / Salida</h3>
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_libros" />
              <input type="hidden" name="accion" value="agregar_mov" />
              <label for="m_tipo">Tipo</label>
              <select id="m_tipo" name="mov_tipo">
                <option value="ENTRADA">ENTRADA (Ingreso / Cobro)</option>
                <option value="SALIDA">SALIDA (Egreso / Pago)</option>
              </select>
              <label for="m_cta">Cuenta</label>
              <select id="m_cta" name="mov_cuenta">
                {% for c in cuentas_ven %}
                  <option value="{{ c.nombre }}">{{ c.codigo }} · {{ c.nombre }}</option>
                {% endfor %}
              </select>
              <label for="m_desc">Concepto</label>
              <input id="m_desc" name="mov_desc" type="text" required />
              <label for="m_monto">Monto</label>
              <input id="m_monto" name="mov_monto" type="number" step="any" required />
              <button type="submit" class="btn-fucsia">Guardar movimiento</button>
            </form>

            <form method="POST" class="card">
              <h3 style="margin-top:0;color:#f9a8d4;">Asiento en Libro Diario</h3>
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_libros" />
              <input type="hidden" name="accion" value="agregar_asiento" />
              <label for="a_cta">Cuenta</label>
              <input id="a_cta" name="as_cuenta" type="text" required />
              <label for="a_ref">Referencia</label>
              <input id="a_ref" name="as_ref" type="text" required />
              <div class="grid-2">
                <div><label for="a_d">Debe</label><input id="a_d" name="as_debe" type="number" step="any" value="0" /></div>
                <div><label for="a_h">Haber</label><input id="a_h" name="as_haber" type="number" step="any" value="0" /></div>
              </div>
              <button type="submit" class="btn-fucsia">Registrar asiento</button>
            </form>
          </div>

          <div class="card">
            <h3 style="margin-top:0;color:#f9a8d4;">Libro Mayor (Saldo por cuenta)</h3>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Cuenta</th><th>Debe</th><th>Haber</th><th>Saldo</th></tr></thead>
                <tbody>
                  {% for r in libro_mayor %}
                    <tr><td><strong>{{ r.cuenta }}</strong></td><td>{{ r.debe }}</td><td>{{ r.haber }}</td><td>{{ r.saldo }}</td></tr>
                  {% else %}
                    <tr><td colspan="4" style="color:var(--muted)">Sin asientos registrados todavía.</td></tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>
          </div>

          <div class="grid-2">
            <form method="POST" class="card">
              <h3 style="margin-top:0;color:#f9a8d4;">Libro de Ventas / Compras (IVA e ISLR)</h3>
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_libros" />
              <input type="hidden" name="accion" value="agregar_factura" />
              <label for="f_lib">Libro</label>
              <select id="f_lib" name="fac_libro">
                <option value="VENTA">VENTA (Débito Fiscal)</option>
                <option value="COMPRA">COMPRA (Crédito Fiscal)</option>
              </select>
              <label for="f_rif">RIF</label>
              <input id="f_rif" name="fac_rif" type="text" required />
              <label for="f_ctrl">N.º Control</label>
              <input id="f_ctrl" name="fac_control" type="text" />
              <label for="f_base">Base imponible</label>
              <input id="f_base" name="fac_base" type="number" step="any" required />
              <div class="grid-3">
                <div>
                  <label for="f_iva">IVA %</label>
                  <select id="f_iva" name="fac_iva_pct">
                    <option value="16">16%</option>
                    <option value="8">8%</option>
                    <option value="0">0%</option>
                  </select>
                </div>
                <div>
                  <label for="f_riva">Ret. IVA %</label>
                  <select id="f_riva" name="fac_ret_iva_pct">
                    <option value="75">75%</option>
                    <option value="100">100%</option>
                    <option value="0">0%</option>
                  </select>
                </div>
                <div>
                  <label for="f_rislr">Ret. ISLR %</label>
                  <input id="f_rislr" name="fac_ret_islr_pct" type="number" step="any" value="0" />
                </div>
              </div>
              <button type="submit" class="btn-fucsia">Guardar factura</button>
            </form>

            <form method="POST" class="card">
              <h3 style="margin-top:0;color:#f9a8d4;">Cuentas por Cobrar / Pagar</h3>
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_libros" />
              <input type="hidden" name="accion" value="agregar_cxc_cxp" />
              <label for="c_tipo">Tipo</label>
              <select id="c_tipo" name="cx_tipo">
                <option value="COBRAR">Por Cobrar (Cliente)</option>
                <option value="PAGAR">Por Pagar (Proveedor)</option>
              </select>
              <label for="c_ter">Cliente / Proveedor</label>
              <input id="c_ter" name="cx_tercero" type="text" required />
              <label for="c_doc">Documento</label>
              <input id="c_doc" name="cx_doc" type="text" />
              <label for="c_mon">Monto</label>
              <input id="c_mon" name="cx_monto" type="number" step="any" required />
              <button type="submit" class="btn-fucsia">Agregar cuenta</button>
            </form>
          </div>

          <div class="grid-2">
            <form method="POST" class="card">
              <h3 style="margin-top:0;color:#f9a8d4;">Cierre del período</h3>
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_libros" />
              <input type="hidden" name="accion" value="ejecutar_cierre" />
              <label for="c_obs">Observación</label>
              <input id="c_obs" name="cierre_obs" type="text" value="{{ cierre_obs }}" />
              <button type="submit" class="btn-fucsia">
                {% if estado_cierre == 'CERRADO' %}Reabrir período{% else %}Ejecutar cierre del período{% endif %}
              </button>
            </form>

            <form method="POST" class="card">
              <h3 style="margin-top:0;color:#f9a8d4;">Tasa y Estilo Fucsia</h3>
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_libros" />
              <input type="hidden" name="accion" value="guardar_tasa_y_tono" />
              <label for="t_ref">Tasa referencial</label>
              <input id="t_ref" name="tasa_ref_inp" type="number" step="any" value="{{ tasa_ref }}" />
              <label for="t_tono">Tono fucsia</label>
              <select id="t_tono" name="tono_fucsia">
                <option value="#ec4899" {% if tono_fucsia == '#ec4899' %}selected{% endif %}>Fucsia vibrante</option>
                <option value="#f43f5e" {% if tono_fucsia == '#f43f5e' %}selected{% endif %}>Rosa fucsia intenso</option>
                <option value="#d946ef" {% if tono_fucsia == '#d946ef' %}selected{% endif %}>Fucsia magenta</option>
              </select>
              <button type="submit" class="btn-fucsia">Guardar tasa y estilo</button>
            </form>
          </div>
        </div>

        <div id="rama_aprender" class="rama-sec {% if active_rama != 'rama_aprender' %}hidden{% endif %}">
          <h2 style="margin-top:0;color:#f9a8d4;text-transform:uppercase;letter-spacing:0.05em;">Actualizaciones, Cursos y Precios Actuales</h2>

          <div class="curso-stream">
            {% for modulo in cursos_y_actualizaciones %}
              <article class="card card-learn">
                <h3 style="margin-top:0;color:#f9a8d4;">{{ modulo.titulo }}</h3>
                <p style="margin:0;color:var(--text);font-size:0.9rem;line-height:1.6;">{{ modulo.detalle }}</p>
              </article>
            {% endfor %}
          </div>

          <div class="card" style="margin-top:20px;">
            <h3 style="margin-top:0;color:#f9a8d4;">Precios y Referencias Actuales</h3>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Concepto</th><th>Valor Actual</th><th>Nota</th></tr></thead>
                <tbody>
                  {% for p in precios_actuales %}
                    <tr><td><strong>{{ p.concepto }}</strong></td><td>{{ p.valor }}</td><td>{{ p.nota }}</td></tr>
                  {% else %}
                    <tr><td colspan="3" style="color:var(--muted)">Sin precios cargados todavía. Agrega el tuyo abajo.</td></tr>
                  {% endfor %}
                </tbody>
              </table>
            </div>

            <form method="POST" class="grid-3" style="align-items:end;">
              <input type="hidden" name="codigo" value="{{ codigo }}" />
              <input type="hidden" name="active_rama" value="rama_aprender" />
              <input type="hidden" name="accion" value="agregar_precio_actual" />
              <div>
                <label for="p_con">Concepto / Precio</label>
                <input id="p_con" name="p_concepto" type="text" required />
              </div>
              <div>
                <label for="p_val">Valor</label>
                <input id="p_val" name="p_valor" type="text" required />
              </div>
              <div>
                <label for="p_nota">Nota</label>
                <input id="p_nota" name="p_nota" type="text" />
              </div>
              <div style="grid-column:1/-1;">
                <button type="submit" class="btn-fucsia">Agregar a Precios Actuales</button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  {% endif %}
</div>

<script>
  function openRama(ramaId, btn) {
    document.querySelectorAll('.rama-sec').forEach(s => s.classList.add('hidden'));
    document.querySelectorAll('.rama-btn').forEach(b => b.classList.remove('active'));
    const sec = document.getElementById(ramaId);
    if (sec) sec.classList.remove('hidden');
    if (btn) btn.classList.add('active');
    document.querySelectorAll('input[name="active_rama"]').forEach(i => i.value = ramaId);
  }

  function openRenglon(renglonId, renglonLabel, ramaId, btn) {
    document.querySelectorAll('.renglon-item').forEach(r => r.classList.remove('active'));
    if (btn) btn.classList.add('active');
    document.querySelectorAll('.rama-sec').forEach(s => s.classList.add('hidden'));
    const sec = document.getElementById(ramaId);
    if (sec) sec.classList.remove('hidden');
    document.querySelectorAll('input[name="active_rama"]').forEach(i => i.value = ramaId);
    const bannerTxt = document.getElementById('renglon_activo_txt');
    if (bannerTxt) bannerTxt.textContent = renglonLabel;
    if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
</script>
</body>
</html>
"""

SESIONES_CONTAB = {}


def fmt_num(valor):
    try:
        num = float(valor)
        if num.is_integer():
            return str(int(num))
        return f"{round(num, 2):.2f}"
    except (TypeError, ValueError):
        return "0"


def ordenar_movimientos(movimientos, campo="fecha", direccion="desc"):
    reversa = (direccion == "desc")
    if campo == "monto":
        return sorted(movimientos, key=lambda x: float(x.get("monto", 0) or 0), reverse=reversa)
    if campo == "tipo":
        return sorted(movimientos, key=lambda x: str(x.get("tipo", "")).lower(), reverse=reversa)
    if campo == "cuenta":
        return sorted(movimientos, key=lambda x: str(x.get("cuenta", "")).lower(), reverse=reversa)
    return sorted(movimientos, key=lambda x: str(x.get("fecha", "")), reverse=reversa)


def calcular_libro_mayor(asientos):
    acumulado = {}
    for a in asientos:
        cuenta = str(a.get("cuenta") or "Cuenta General").strip()
        debe = float(a.get("debe", 0) or 0)
        haber = float(a.get("haber", 0) or 0)
        if cuenta not in acumulado:
            acumulado[cuenta] = {"debe": 0.0, "haber": 0.0}
        acumulado[cuenta]["debe"] += debe
        acumulado[cuenta]["haber"] += haber

    return [
        {
            "cuenta": cuenta,
            "debe": fmt_num(vals["debe"]),
            "haber": fmt_num(vals["haber"]),
            "saldo": fmt_num(vals["debe"] - vals["haber"]),
        }
        for cuenta, vals in acumulado.items()
    ]


def _f(val):
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def calcular_estados_venezuela(sesion, movimientos):
    raw = sesion["raw_est"]

    mov_ing = sum(_f(m.get("monto")) for m in movimientos if m.get("tipo") == "ENTRADA" and "CAPITAL" not in str(m.get("cuenta", "")).upper())
    mov_cos = sum(_f(m.get("monto")) for m in movimientos if m.get("tipo") == "SALIDA" and ("COSTO" in str(m.get("cuenta", "")).upper() or "COMPRA" in str(m.get("cuenta", "")).upper()))
    mov_gas = sum(_f(m.get("monto")) for m in movimientos if m.get("tipo") == "SALIDA" and ("COSTO" not in str(m.get("cuenta", "")).upper() and "COMPRA" not in str(m.get("cuenta", "")).upper()))
    mov_cap = sum(_f(m.get("monto")) for m in movimientos if "CAPITAL" in str(m.get("cuenta", "")).upper())

    cxc_pend = sum(_f(c.get("monto")) for c in sesion["cuentas_cx"] if c.get("tipo") == "COBRAR" and c.get("estado") == "PENDIENTE")
    cxp_pend = sum(_f(c.get("monto")) for c in sesion["cuentas_cx"] if c.get("tipo") == "PAGAR" and c.get("estado") == "PENDIENTE")

    ingresos = _f(raw["er_ingresos"]) + mov_ing
    costos = _f(raw["er_costos"]) + mov_cos
    utilidad_bruta = ingresos - costos
    gastos = _f(raw["er_gastos"]) + mov_gas
    utilidad_operativa = utilidad_bruta - gastos
    otros = _f(raw["er_otros"])
    islr = _f(raw["er_islr"])
    utilidad_neta = utilidad_operativa + otros - islr

    efectivo = _f(raw["bg_efectivo"]) + sum(_f(m.get("monto")) for m in movimientos if m.get("tipo") == "ENTRADA") - sum(_f(m.get("monto")) for m in movimientos if m.get("tipo") == "SALIDA")
    cxc = _f(raw["bg_cxc"]) + cxc_pend
    inv = _f(raw["bg_inv"])
    activo_corriente = efectivo + cxc + inv

    ppe = _f(raw["bg_ppe"])
    activo_no_corriente = ppe
    activo_total = activo_corriente + activo_no_corriente

    cxp = _f(raw["bg_cxp"]) + cxp_pend
    pasivo_corriente = cxp
    pas_lp = _f(raw["bg_pas_lp"])
    pasivo_no_corriente = pas_lp
    pasivo_total = pasivo_corriente + pasivo_no_corriente

    capital = _f(raw["bg_capital"]) + mov_cap
    util_ac = _f(raw["bg_util_ac"]) + utilidad_neta
    patrimonio_total = capital + util_ac

    er = {
        "ingresos_operativos": fmt_num(ingresos),
        "costo_ventas": fmt_num(costos),
        "utilidad_bruta": fmt_num(utilidad_bruta),
        "gastos_operativos": fmt_num(gastos),
        "utilidad_operativa": fmt_num(utilidad_operativa),
        "otros_neto": fmt_num(otros),
        "islr_est": fmt_num(islr),
        "utilidad_neta": fmt_num(utilidad_neta),
    }
    bg = {
        "activo_corriente": fmt_num(activo_corriente),
        "efectivo_bancos": fmt_num(efectivo),
        "cxc_total": fmt_num(cxc),
        "activo_no_corriente": fmt_num(activo_no_corriente),
        "ppe_neto": fmt_num(ppe),
        "activo_total": fmt_num(activo_total),
        "pasivo_corriente": fmt_num(pasivo_corriente),
        "cxp_total": fmt_num(cxp),
        "pasivo_no_corriente": fmt_num(pasivo_no_corriente),
        "pasivo_total": fmt_num(pasivo_total),
        "patrimonio_total": fmt_num(patrimonio_total),
        "capital_social": fmt_num(capital),
        "resultado_patrimonio": fmt_num(util_ac),
        "pasivo_mas_patrimonio": fmt_num(pasivo_total + patrimonio_total),
    }
    raw_fmt = {k: fmt_num(v) for k, v in raw.items()}
    return er, bg, raw_fmt


def parsear_lineas_contables(texto):
    filas = []
    hoy = datetime.now().strftime("%Y-%m-%d")
    for linea in (texto or "").splitlines():
        linea = linea.strip()
        if not linea:
            continue
        partes = [p.strip() for p in linea.split(",")]
        fecha = partes[0] if len(partes) > 0 and partes[0] else hoy
        tipo_raw = (partes[1] if len(partes) > 1 else "ENTRADA").upper()
        tipo = "SALIDA" if "SAL" in tipo_raw or "EGR" in tipo_raw else "ENTRADA"
        cuenta = partes[2] if len(partes) > 2 and partes[2] else "Banco Nacional"
        concepto = partes[3] if len(partes) > 3 and partes[3] else "Movimiento directo"
        try:
            monto = abs(float(partes[4])) if len(partes) > 4 else 0.0
        except ValueError:
            monto = 0.0
        filas.append({
            "fecha": fecha,
            "tipo": tipo,
            "cuenta": cuenta,
            "concepto": concepto,
            "monto": monto,
        })
    return filas


def obtener_sesion(codigo):
    code = (codigo or "").strip().upper()
    if code not in CODIGOS_ACCESO:
        return None
    if code not in SESIONES_CONTAB:
        SESIONES_CONTAB[code] = {
            "uso": 0,
            "active_rama": "rama_directo",
            "active_renglon": "r01",
            "active_renglon_label": "Seleccionar y Ejecutar Archivo",
            "tono_fucsia": "#ec4899",
            "estado_cierre": "ABIERTO",
            "cierre_obs": "",
            "orden_campo": "fecha",
            "orden_dir": "desc",
            "tasa_ref": 0.0,
            "raw_est": {
                "er_ingresos": 0.0,
                "er_costos": 0.0,
                "er_gastos": 0.0,
                "er_otros": 0.0,
                "er_islr": 0.0,
                "bg_efectivo": 0.0,
                "bg_cxc": 0.0,
                "bg_inv": 0.0,
                "bg_ppe": 0.0,
                "bg_cxp": 0.0,
                "bg_pas_lp": 0.0,
                "bg_capital": 0.0,
                "bg_util_ac": 0.0,
            },
            "movimientos": [],
            "asientos": [],
            "facturas": [],
            "cuentas_cx": [],
            "precios_actuales": [],
        }
    return SESIONES_CONTAB[code]


def render_contab(codigo, sesion, error_msg=None, aviso_msg=None):
    info = CODIGOS_ACCESO[codigo]
    movs_ord = ordenar_movimientos(sesion["movimientos"], sesion["orden_campo"], sesion["orden_dir"])
    er, bg, raw_fmt = calcular_estados_venezuela(sesion, movs_ord)
    return render_template_string(
        HTML_CONTAB,
        autorizado=True,
        error=error_msg,
        aviso=aviso_msg,
        codigo=codigo,
        plan=info["plan"],
        limite=info["limite"],
        uso=sesion["uso"],
        active_rama=sesion.get("active_rama", "rama_directo"),
        active_renglon=sesion.get("active_renglon", "r01"),
        active_renglon_label=sesion.get("active_renglon_label", "Seleccionar y Ejecutar Archivo"),
        tono_fucsia=sesion.get("tono_fucsia", "#ec4899"),
        estado_cierre=sesion.get("estado_cierre", "ABIERTO"),
        cierre_obs=sesion.get("cierre_obs", ""),
        orden_campo=sesion.get("orden_campo", "fecha"),
        orden_dir=sesion.get("orden_dir", "desc"),
        tasa_ref=fmt_num(sesion.get("tasa_ref", 0.0)),
        cuentas_ven=CUENTAS_VEN,
        renglones_menu=RENGLONES_CONTAB,
        cursos_y_actualizaciones=CURSOS_Y_ACTUALIZACIONES,
        precios_actuales=sesion["precios_actuales"],
        movimientos=movs_ord,
        libro_mayor=calcular_libro_mayor(sesion["asientos"]),
        er=er,
        bg=bg,
        raw_est=raw_fmt,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        codigo = (request.form.get("codigo") or "").strip().upper()
        sesion = obtener_sesion(codigo)
        if not sesion:
            return render_template_string(
                HTML_CONTAB,
                autorizado=False,
                tono_fucsia="#ec4899",
                error="Código no válido. Usa DEMO2026, VIP100 o CONTAB2026.",
            )

        rama_sel = request.form.get("active_rama")
        if rama_sel in ("rama_directo", "rama_libros", "rama_aprender"):
            sesion["active_rama"] = rama_sel

        limite = CODIGOS_ACCESO[codigo]["limite"]
        accion = request.form.get("accion")
        aviso = None
        error = None

        if accion:
            if sesion["uso"] >= limite:
                return render_contab(codigo, sesion, error_msg="Límite de uso alcanzado.")
            sesion["uso"] += 1

        if accion == "guardar_estados_editables":
            if sesion["estado_cierre"] == "CERRADO":
                error = "El período está CERRADO. Reábrelo para editar."
            else:
                for k in sesion["raw_est"]:
                    if k in request.form:
                        sesion["raw_est"][k] = _f(request.form.get(k))
                aviso = "Valores del Balance General y Estado de Resultados actualizados."
            sesion["active_rama"] = "rama_directo"

        elif accion == "ejecutar_archivo_directo":
            if sesion["estado_cierre"] == "CERRADO":
                error = "El período está CERRADO. Reábrelo para cargar datos."
            else:
                filas = []
                arch = request.files.get("dir_archivo")
                if arch and arch.filename:
                    raw = arch.read().decode("utf-8", errors="ignore").strip()
                    if arch.filename.lower().endswith(".json") or raw.startswith("["):
                        data = json.loads(raw)
                        if isinstance(data, list):
                            for it in data:
                                if isinstance(it, dict):
                                    filas.append({
                                        "fecha": str(it.get("fecha") or datetime.now().strftime("%Y-%m-%d")),
                                        "tipo": "SALIDA" if str(it.get("tipo", "")).upper() == "SALIDA" else "ENTRADA",
                                        "cuenta": str(it.get("cuenta") or "Banco Nacional"),
                                        "concepto": str(it.get("concepto") or "Importado"),
                                        "monto": abs(_f(it.get("monto"))),
                                    })
                    else:
                        filas.extend(parsear_lineas_contables(raw))
                pegar = request.form.get("dir_texto") or ""
                if pegar.strip():
                    filas.extend(parsear_lineas_contables(pegar))

                destino = request.form.get("dir_destino") or "balance_general"
                if not filas:
                    error = "No se encontraron filas válidas en el archivo o texto."
                elif destino == "balance_general":
                    sesion["movimientos"].extend(filas)
                    aviso = f"Archivo ejecutado: {len(filas)} fila(s) incorporadas al Balance General y Estado de Resultados."
                elif destino == "diario":
                    for f in filas:
                        d = f["monto"] if f["tipo"] == "ENTRADA" else 0.0
                        h = f["monto"] if f["tipo"] == "SALIDA" else 0.0
                        sesion["asientos"].append({"cuenta": f["cuenta"], "ref": f["concepto"], "debe": d, "haber": h})
                    aviso = f"Archivo ejecutado: {len(filas)} asiento(s) registrados en el Libro Diario."
                elif destino in ("ventas", "compras"):
                    lib = "VENTA" if destino == "ventas" else "COMPRA"
                    for f in filas:
                        iva_m = f["monto"] * 0.16
                        sesion["facturas"].append({
                            "libro": lib,
                            "rif": f["cuenta"],
                            "control": f["fecha"],
                            "base": fmt_num(f["monto"]),
                            "iva": fmt_num(iva_m),
                            "ret_iva": fmt_num(iva_m * 0.75),
                            "ret_islr": "0",
                            "total": fmt_num(f["monto"] + iva_m),
                        })
                    aviso = f"Archivo ejecutado: {len(filas)} factura(s) cargadas en {lib}."
                elif destino in ("cxc", "cxp"):
                    t_cx = "COBRAR" if destino == "cxc" else "PAGAR"
                    for f in filas:
                        sesion["cuentas_cx"].append({
                            "tipo": t_cx,
                            "tercero": f["cuenta"],
                            "doc": f["concepto"],
                            "monto": f["monto"],
                            "estado": "PENDIENTE",
                        })
                    aviso = f"Archivo ejecutado: {len(filas)} cuenta(s) por {t_cx.lower()} agregadas."
            sesion["active_rama"] = "rama_directo"

        elif accion == "ordenar_movs":
            sesion["orden_campo"] = request.form.get("orden_campo") or "fecha"
            sesion["orden_dir"] = request.form.get("orden_dir") or "desc"
            aviso = "Registros ordenados."
            sesion["active_rama"] = "rama_directo"

        elif accion == "agregar_mov":
            if sesion["estado_cierre"] == "CERRADO":
                error = "Período CERRADO."
            else:
                tipo = request.form.get("mov_tipo") or "ENTRADA"
                cta = request.form.get("mov_cuenta") or "Banco Nacional"
                desc = (request.form.get("mov_desc") or "").strip()
                monto = abs(_f(request.form.get("mov_monto")))
                if desc and monto > 0:
                    sesion["movimientos"].append({
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "tipo": tipo,
                        "cuenta": cta,
                        "concepto": desc,
                        "monto": monto,
                    })
                    aviso = "Movimiento registrado."
                else:
                    error = "Indica concepto y monto válido."
            sesion["active_rama"] = "rama_libros"

        elif accion == "agregar_asiento":
            if sesion["estado_cierre"] == "CERRADO":
                error = "Período CERRADO."
            else:
                cta = (request.form.get("as_cuenta") or "").strip()
                ref = (request.form.get("as_ref") or "").strip()
                d = abs(_f(request.form.get("as_debe")))
                h = abs(_f(request.form.get("as_haber")))
                if cta and ref and (d > 0 or h > 0):
                    sesion["asientos"].append({"cuenta": cta, "ref": ref, "debe": d, "haber": h})
                    aviso = "Asiento registrado."
                else:
                    error = "Completa cuenta, referencia y Debe o Haber."
            sesion["active_rama"] = "rama_libros"

        elif accion == "agregar_factura":
            lib = request.form.get("fac_libro") or "VENTA"
            rif = (request.form.get("fac_rif") or "").strip().upper()
            ctrl = (request.form.get("fac_control") or "S/N").strip()
            base = abs(_f(request.form.get("fac_base")))
            iva_p = abs(_f(request.form.get("fac_iva_pct")))
            riva_p = abs(_f(request.form.get("fac_ret_iva_pct")))
            rislr_p = abs(_f(request.form.get("fac_ret_islr_pct")))
            if rif and base > 0:
                iva_m = base * (iva_p / 100.0)
                riva_m = iva_m * (riva_p / 100.0)
                rislr_m = base * (rislr_p / 100.0)
                sesion["facturas"].append({
                    "libro": lib,
                    "rif": rif,
                    "control": ctrl,
                    "base": fmt_num(base),
                    "iva": fmt_num(iva_m),
                    "ret_iva": fmt_num(riva_m),
                    "ret_islr": fmt_num(rislr_m),
                    "total": fmt_num(base + iva_m),
                })
                aviso = f"Factura registrada en {lib}."
            else:
                error = "Indica RIF y base mayor a cero."
            sesion["active_rama"] = "rama_libros"

        elif accion == "agregar_cxc_cxp":
            t_cx = request.form.get("cx_tipo") or "COBRAR"
            ter = (request.form.get("cx_tercero") or "").strip()
            doc = (request.form.get("cx_doc") or "S/N").strip()
            mon = abs(_f(request.form.get("cx_monto")))
            if ter and mon > 0:
                sesion["cuentas_cx"].append({"tipo": t_cx, "tercero": ter, "doc": doc, "monto": mon, "estado": "PENDIENTE"})
                aviso = "Cuenta agregada."
            else:
                error = "Completa tercero y monto."
            sesion["active_rama"] = "rama_libros"

        elif accion == "ejecutar_cierre":
            obs = (request.form.get("cierre_obs") or "").strip()
            if obs:
                sesion["cierre_obs"] = obs
            sesion["estado_cierre"] = "ABIERTO" if sesion["estado_cierre"] == "CERRADO" else "CERRADO"
            aviso = f"Período ahora está {sesion['estado_cierre']}."
            sesion["active_rama"] = "rama_libros"

        elif accion == "guardar_tasa_y_tono":
            t_v = abs(_f(request.form.get("tasa_ref_inp")))
            if t_v > 0:
                sesion["tasa_ref"] = t_v
            tono = (request.form.get("tono_fucsia") or "#ec4899").strip()
            if tono in ("#ec4899", "#f43f5e", "#d946ef"):
                sesion["tono_fucsia"] = tono
            aviso = "Tasa y tono actualizados."
            sesion["active_rama"] = "rama_libros"

        elif accion == "agregar_precio_actual":
            con = (request.form.get("p_concepto") or "").strip()
            val = (request.form.get("p_valor") or "").strip()
            nota = (request.form.get("p_nota") or "Actualizado").strip()
            if con and val:
                sesion["precios_actuales"].append({"concepto": con, "valor": val, "nota": nota})
                aviso = "Precio/referencia agregado."
            else:
                error = "Indica concepto y valor."
            sesion["active_rama"] = "rama_aprender"

        return render_contab(codigo, sesion, error_msg=error, aviso_msg=aviso)

    return render_template_string(HTML_CONTAB, autorizado=False, tono_fucsia="#ec4899", error=None)


@app.route("/descargar-contable")
def descargar_contable():
    codigo = (request.args.get("codigo") or "").strip().upper()
    sesion = obtener_sesion(codigo)
    if not sesion:
        return "Código no autorizado", 403
    movs_ord = ordenar_movimientos(sesion["movimientos"], sesion["orden_campo"], sesion["orden_dir"])
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Fecha", "Tipo", "Cuenta", "Concepto", "Monto"])
    for m in movs_ord:
        writer.writerow([m["fecha"], m["tipo"], m["cuenta"], m["concepto"], m["monto"]])
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=c_contab_movimientos.csv"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
