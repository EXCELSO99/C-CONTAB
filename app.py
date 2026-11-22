import csv
import io
import json
import os
from datetime import datetime
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

CODIGOS_ACCESO = {
    "DEMO2026": {"plan": "DEMO", "limite": 500},
    "VIP100": {"plan": "VIP", "limite": 2000},
    "CONTAB2026": {"plan": "PRO", "limite": 999999},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>C-CONTAB // Contabilidad Venezuela</title>
  <style>
    :root {
      --bg-dark: #060b19;
      --bg-navy: #0b132b;
      --panel: #0f1b38;
      --panel-2: #15254b;
      --border: #263b6e;
      --text: #f8fafc;
      --muted: #9fb3d9;
      --fucsia: {{ tono_fucsia }};
      --fucsia-2: #db2777;
      --fucsia-soft: rgba(236, 72, 153, 0.16);
      --ok: #10b981;
      --warn: #f59e0b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at top right, rgba(236, 72, 153, 0.16), transparent 42%),
                  radial-gradient(circle at top left, #13295c 0%, var(--bg-dark) 65%);
      color: var(--text);
      min-height: 100vh;
    }
    .corner-tag {
      position: fixed;
      top: 10px;
      right: 12px;
      z-index: 50;
      background: rgba(15, 27, 56, 0.92);
      border: 1px solid var(--fucsia);
      color: #f9a8d4;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }
    .wrap { max-width: 1220px; margin: 0 auto; padding: 38px 14px 56px; }
    .login-box {
      max-width: 420px;
      margin: 56px auto;
      background: linear-gradient(160deg, var(--panel) 0%, var(--bg-navy) 100%);
      border: 1px solid var(--fucsia);
      box-shadow: 0 0 36px rgba(236, 72, 153, 0.24);
      border-radius: 18px;
      padding: 26px 24px;
      text-align: center;
    }
    .brand-title {
      margin: 0;
      font-size: 2rem;
      letter-spacing: 0.08em;
      color: #fff;
    }
    .brand-title span { color: var(--fucsia); }
    .brand-sub {
      margin: 6px 0 18px;
      font-size: 0.8rem;
      color: var(--muted);
      letter-spacing: 0.12em;
    }
    label { display: block; text-align: left; font-size: 0.82rem; color: var(--muted); margin-bottom: 5px; }
    input, select, textarea {
      width: 100%;
      background: var(--bg-dark);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 11px;
      font-size: 0.9rem;
      margin-bottom: 10px;
    }
    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: var(--fucsia);
    }
    button {
      cursor: pointer;
      border: none;
      border-radius: 10px;
      padding: 9px 13px;
      font-weight: 600;
      font-size: 0.84rem;
    }
    .btn-fucsia {
      width: 100%;
      background: linear-gradient(90deg, var(--fucsia-2), var(--fucsia));
      color: #fff;
      padding: 10px 14px;
    }
    .btn-navy {
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--border);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-navy:hover { border-color: var(--fucsia); }
    .btn-small { padding: 5px 9px; font-size: 0.76rem; border-radius: 8px; }
    .topbar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 16px;
      margin-bottom: 12px;
    }
    .pill {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.74rem;
      background: var(--fucsia-soft);
      color: #f9a8d4;
      border: 1px solid rgba(236, 72, 153, 0.45);
    }
    .seg-nav {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
      gap: 8px;
      margin-bottom: 14px;
    }
    .seg-btn {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      text-align: left;
      padding: 10px 12px;
      font-size: 0.83rem;
    }
    .seg-btn.active {
      background: var(--fucsia-soft);
      border-color: var(--fucsia);
      color: #fff;
    }
    .seg-panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }
    .hidden { display: none !important; }
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 14px; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .card {
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
    }
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
      gap: 10px;
      margin: 12px 0;
    }
    .kpi {
      background: var(--bg-dark);
      border: 1px solid var(--border);
      border-left: 3px solid var(--fucsia);
      border-radius: 10px;
      padding: 10px 12px;
    }
    .kpi-lbl { font-size: 0.74rem; color: var(--muted); }
    .kpi-val { font-size: 1.1rem; font-weight: 700; margin-top: 3px; }
    .table-wrap {
      overflow-x: auto;
      max-height: 390px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 10px;
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.81rem; }
    th, td { border: 1px solid var(--border); padding: 7px 8px; text-align: left; }
    th { background: var(--panel-2); position: sticky; top: 0; z-index: 2; color: #f9a8d4; }
    .alert-err {
      background: rgba(239, 68, 68, 0.16);
      border: 1px solid #ef4444;
      color: #fecaca;
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.85rem;
    }
    .alert-ok {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid var(--ok);
      color: #a7f3d0;
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.85rem;
    }
    a { color: #f472b6; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<div class="corner-tag">Totalmente contable</div>

<div class="wrap">
  {% if not autorizado %}
    <div class="login-box">
      <h1 class="brand-title">C-<span>CONTAB</span></h1>
      <p class="brand-sub">CONTABILIDAD VENEZUELA // ACCESO</p>
      {% if error %}
        <div class="alert-err">{{ error }}</div>
      {% endif %}
      <form method="POST">
        <label for="codigo">Clave / Código de acceso</label>
        <input id="codigo" name="codigo" type="text" placeholder="DEMO2026, VIP100 o CONTAB2026" required />
        <button class="btn-fucsia" type="submit">ENTRAR A C-CONTAB</button>
      </form>
    </div>
  {% else %}
    <div class="topbar">
      <div>
        <strong>C-<span style="color:var(--fucsia)">CONTAB</span></strong>
        <span class="pill">{{ codigo }} · {{ plan }}</span>
        {% if estado_cierre == 'CERRADO' %}
          <span class="pill" style="background:rgba(16,185,129,0.16); color:#6ee7b7; border-color:#10b981;">PERÍODO CERRADO</span>
        {% else %}
          <span class="pill">PERÍODO ABIERTO</span>
        {% endif %}
      </div>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span class="pill">Tasa ref: {{ tasa_ref }} Bs</span>
        <span class="pill">Uso: {{ uso }} / {{ limite }}</span>
        <a class="btn-navy" style="padding:7px 11px; border-radius:10px;" href="/">Salir</a>
      </div>
    </div>

    {% if error %}
      <div class="alert-err">{{ error }}</div>
    {% endif %}
    {% if aviso %}
      <div class="alert-ok">{{ aviso }}</div>
    {% endif %}

    <div class="seg-nav">
      <button type="button" class="seg-btn {% if active_seg == 's1' %}active{% endif %}" onclick="openSeg('s1', this)">1. Entradas y Salidas</button>
      <button type="button" class="seg-btn {% if active_seg == 's2' %}active{% endif %}" onclick="openSeg('s2', this)">2. Diario, Mayor y Cierre</button>
      <button type="button" class="seg-btn {% if active_seg == 's3' %}active{% endif %}" onclick="openSeg('s3', this)">3. Ventas, Compras y IVA</button>
      <button type="button" class="seg-btn {% if active_seg == 's4' %}active{% endif %}" onclick="openSeg('s4', this)">4. Cuentas Cobrar/Pagar</button>
      <button type="button" class="seg-btn {% if active_seg == 's5' %}active{% endif %}" onclick="openSeg('s5', this)">5. Balances y Divisas</button>
      <button type="button" class="seg-btn {% if active_seg == 's6' %}active{% endif %}" onclick="openSeg('s6', this)">6. Archivos y Ajustes</button>
    </div>

    <!-- SEGMENTO 1: ENTRADAS Y SALIDAS -->
    <section id="s1" class="seg-panel {% if active_seg != 's1' %}hidden{% endif %}">
      <h2 style="margin-top:0">Segmento 1 · Entradas y Salidas</h2>
      <p style="color:var(--muted)">Control de entradas (cobros/ingresos) y salidas (pagos/egresos) de caja y bancos.</p>

      <div class="grid-2">
        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Registrar movimiento</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s1" />
          <input type="hidden" name="accion" value="agregar_mov" />

          <label for="mov_tipo">Tipo</label>
          <select id="mov_tipo" name="mov_tipo">
            <option value="ENTRADA">Entrada (Ingreso / Cobro)</option>
            <option value="SALIDA">Salida (Egreso / Pago)</option>
          </select>

          <label for="mov_cuenta">Cuenta contable</label>
          <select id="mov_cuenta" name="mov_cuenta">
            <option value="Banco Nacional">Banco Nacional</option>
            <option value="Caja Chica">Caja Chica</option>
            <option value="Ventas / Ingresos">Ventas / Ingresos</option>
            <option value="Compras / Costos">Compras / Costos</option>
            <option value="Gastos Administrativos">Gastos Administrativos</option>
          </select>

          <label for="mov_desc">Concepto / Detalle</label>
          <input id="mov_desc" name="mov_desc" type="text" placeholder="Ej: Cobro factura o Pago proveedor" required />

          <label for="mov_monto">Monto</label>
          <input id="mov_monto" name="mov_monto" type="number" step="any" placeholder="Ej: 1500.00" required />

          <label for="mov_fecha">Fecha</label>
          <input id="mov_fecha" name="mov_fecha" type="date" />

          <button type="submit" class="btn-fucsia">Guardar movimiento</button>
        </form>

        <div class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Resumen de flujo</h3>
          <div class="kpi-row">
            <div class="kpi"><div class="kpi-lbl">Entradas</div><div class="kpi-val" style="color:var(--ok)">{{ resumen.entradas }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Salidas</div><div class="kpi-val" style="color:#f472b6">{{ resumen.salidas }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Saldo Neto</div><div class="kpi-val">{{ resumen.saldo }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Registros</div><div class="kpi-val">{{ resumen.cantidad }}</div></div>
          </div>
          <p style="color:var(--muted); font-size:0.84rem;">
            Equivalente referencial del saldo neto a tasa {{ tasa_ref }}: <strong>{{ saldo_ref_equiv }}</strong>.
          </p>
        </div>
      </div>

      <div class="table-wrap" style="margin-top:14px;">
        <table>
          <thead>
            <tr><th>#</th><th>Fecha</th><th>Tipo</th><th>Cuenta</th><th>Concepto</th><th>Monto</th><th>Acción</th></tr>
          </thead>
          <tbody>
            {% for m in movimientos %}
              <tr>
                <td>{{ loop.index }}</td>
                <td>{{ m.fecha }}</td>
                <td>
                  {% if m.tipo == 'ENTRADA' %}
                    <span style="color:var(--ok); font-weight:700;">ENTRADA</span>
                  {% else %}
                    <span style="color:#f472b6; font-weight:700;">SALIDA</span>
                  {% endif %}
                </td>
                <td>{{ m.cuenta }}</td>
                <td>{{ m.concepto }}</td>
                <td>{{ m.monto }}</td>
                <td>
                  <form method="POST" style="display:inline; margin:0;">
                    <input type="hidden" name="codigo" value="{{ codigo }}" />
                    <input type="hidden" name="active_seg" value="s1" />
                    <input type="hidden" name="accion" value="borrar_mov" />
                    <input type="hidden" name="mov_idx" value="{{ loop.index0 }}" />
                    <button type="submit" class="btn-navy btn-small">Quitar</button>
                  </form>
                </td>
              </tr>
            {% else %}
              <tr><td colspan="7" style="color:var(--muted)">Sin movimientos registrados.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- SEGMENTO 2: LIBRO DIARIO, LIBRO MAYOR Y CIERRE -->
    <section id="s2" class="seg-panel {% if active_seg != 's2' %}hidden{% endif %}">
      <h2 style="margin-top:0">Segmento 2 · Libro Diario, Libro Mayor y Cierre</h2>
      <p style="color:var(--muted)">Asientos de partida doble, saldo acumulado por cuenta en el Libro Mayor y cierre del período.</p>

      <div class="grid-2">
        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Nuevo asiento (Libro Diario)</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s2" />
          <input type="hidden" name="accion" value="agregar_asiento" />

          <label for="as_cuenta">Cuenta contable</label>
          <input id="as_cuenta" name="as_cuenta" type="text" placeholder="Ej: Banco Nacional / Ingresos" required />

          <label for="as_ref">Referencia / Concepto</label>
          <input id="as_ref" name="as_ref" type="text" placeholder="Ej: Factura #0010" required />

          <div class="grid-2">
            <div>
              <label for="as_debe">Debe</label>
              <input id="as_debe" name="as_debe" type="number" step="any" value="0" />
            </div>
            <div>
              <label for="as_haber">Haber</label>
              <input id="as_haber" name="as_haber" type="number" step="any" value="0" />
            </div>
          </div>
          <button type="submit" class="btn-fucsia">Registrar asiento</button>
        </form>

        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Cierre contable del período</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s2" />
          <input type="hidden" name="accion" value="ejecutar_cierre" />

          <div class="kpi-row">
            <div class="kpi"><div class="kpi-lbl">Total Debe</div><div class="kpi-val">{{ diario_res.debe }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Total Haber</div><div class="kpi-val">{{ diario_res.haber }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Diferencia</div><div class="kpi-val">{{ diario_res.dif }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Estado</div><div class="kpi-val">{{ estado_cierre }}</div></div>
          </div>

          <label for="cierre_obs">Observación de cierre</label>
          <input id="cierre_obs" name="cierre_obs" type="text" value="{{ cierre_obs }}" />

          <button type="submit" class="btn-fucsia">
            {% if estado_cierre == 'CERRADO' %}Reabrir período contable{% else %}Ejecutar cierre del período{% endif %}
          </button>
        </form>
      </div>

      <h3 style="color:#f9a8d4; margin-top:16px;">Libro Mayor (Saldo acumulado por cuenta)</h3>
      <div class="table-wrap" style="margin-bottom:14px;">
        <table>
          <thead>
            <tr><th>Cuenta</th><th>Total Debe</th><th>Total Haber</th><th>Saldo Neto</th></tr>
          </thead>
          <tbody>
            {% for row_m in libro_mayor %}
              <tr>
                <td><strong>{{ row_m.cuenta }}</strong></td>
                <td>{{ row_m.debe }}</td>
                <td>{{ row_m.haber }}</td>
                <td>{{ row_m.saldo }}</td>
              </tr>
            {% else %}
              <tr><td colspan="4" style="color:var(--muted)">Sin cuentas mayorizadas.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>

      <h3 style="color:#f9a8d4;">Libro Diario</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>#</th><th>Cuenta</th><th>Referencia</th><th>Debe</th><th>Haber</th></tr>
          </thead>
          <tbody>
            {% for a in asientos %}
              <tr>
                <td>{{ loop.index }}</td>
                <td>{{ a.cuenta }}</td>
                <td>{{ a.ref }}</td>
                <td>{{ a.debe }}</td>
                <td>{{ a.haber }}</td>
              </tr>
            {% else %}
              <tr><td colspan="5" style="color:var(--muted)">Sin asientos.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- SEGMENTO 3: LIBROS DE VENTAS, COMPRAS Y TRIBUTOS (IVA / ISLR) -->
    <section id="s3" class="seg-panel {% if active_seg != 's3' %}hidden{% endif %}">
      <h2 style="margin-top:0">Segmento 3 · Libros de Ventas, Compras y Tributos</h2>
      <p style="color:var(--muted)">Registro de facturas con RIF, N.º de Control, IVA, retenciones de IVA e ISLR.</p>

      <div class="grid-2">
        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Registrar factura (Libro Venta / Compra)</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s3" />
          <input type="hidden" name="accion" value="agregar_factura" />

          <label for="fac_libro">Libro</label>
          <select id="fac_libro" name="fac_libro">
            <option value="VENTA">Libro de Ventas (Débito Fiscal)</option>
            <option value="COMPRA">Libro de Compras (Crédito Fiscal)</option>
          </select>

          <div class="grid-2">
            <div>
              <label for="fac_rif">RIF</label>
              <input id="fac_rif" name="fac_rif" type="text" placeholder="Ej: J-12345678-9" required />
            </div>
            <div>
              <label for="fac_control">N.º de Control</label>
              <input id="fac_control" name="fac_control" type="text" placeholder="Ej: 00-001245" />
            </div>
          </div>

          <label for="fac_base">Base imponible</label>
          <input id="fac_base" name="fac_base" type="number" step="any" placeholder="Ej: 1000" required />

          <div class="grid-2">
            <div>
              <label for="fac_iva_pct">Alícuota IVA (%)</label>
              <select id="fac_iva_pct" name="fac_iva_pct">
                <option value="16">16% (General)</option>
                <option value="8">8% (Reducida)</option>
                <option value="0">0% (Exento)</option>
              </select>
            </div>
            <div>
              <label for="fac_ret_iva_pct">Retención IVA (%)</label>
              <select id="fac_ret_iva_pct" name="fac_ret_iva_pct">
                <option value="75">75%</option>
                <option value="100">100%</option>
                <option value="0">0%</option>
              </select>
            </div>
          </div>

          <label for="fac_ret_islr_pct">Retención ISLR (%)</label>
          <input id="fac_ret_islr_pct" name="fac_ret_islr_pct" type="number" step="any" value="0" />

          <button type="submit" class="btn-fucsia">Guardar factura</button>
        </form>

        <div class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Resumen fiscal (IVA e ISLR)</h3>
          <div class="kpi-row">
            <div class="kpi"><div class="kpi-lbl">Débito Fiscal (Ventas)</div><div class="kpi-val">{{ fisc.debito_iva }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Crédito Fiscal (Compras)</div><div class="kpi-val">{{ fisc.credito_iva }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Cuota IVA Neta</div><div class="kpi-val" style="color:var(--ok)">{{ fisc.iva_neto }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Ret. IVA Total</div><div class="kpi-val" style="color:#f472b6">{{ fisc.ret_iva_total }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Ret. ISLR Total</div><div class="kpi-val" style="color:#f472b6">{{ fisc.ret_islr_total }}</div></div>
          </div>
          <p style="color:var(--muted); font-size:0.83rem;">
            El débito fiscal proviene de las facturas registradas en Ventas y el crédito fiscal de las registradas en Compras.
          </p>
        </div>
      </div>

      <div class="table-wrap" style="margin-top:14px;">
        <table>
          <thead>
            <tr><th>Libro</th><th>RIF</th><th>Control</th><th>Base</th><th>IVA</th><th>Ret. IVA</th><th>Ret. ISLR</th><th>Total</th></tr>
          </thead>
          <tbody>
            {% for f in facturas %}
              <tr>
                <td><strong>{{ f.libro }}</strong></td>
                <td>{{ f.rif }}</td>
                <td>{{ f.control }}</td>
                <td>{{ f.base }}</td>
                <td>{{ f.iva }}</td>
                <td>{{ f.ret_iva }}</td>
                <td>{{ f.ret_islr }}</td>
                <td>{{ f.total }}</td>
              </tr>
            {% else %}
              <tr><td colspan="8" style="color:var(--muted)">Sin facturas registradas.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- SEGMENTO 4: CUENTAS POR COBRAR Y POR PAGAR -->
    <section id="s4" class="seg-panel {% if active_seg != 's4' %}hidden{% endif %}">
      <h2 style="margin-top:0">Segmento 4 · Cuentas por Cobrar y por Pagar</h2>
      <p style="color:var(--muted)">Seguimiento de saldos pendientes con clientes y proveedores.</p>

      <div class="grid-2">
        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Nueva cuenta pendiente</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s4" />
          <input type="hidden" name="accion" value="agregar_cxc_cxp" />

          <label for="cx_tipo">Tipo</label>
          <select id="cx_tipo" name="cx_tipo">
            <option value="COBRAR">Cuenta por Cobrar (Cliente)</option>
            <option value="PAGAR">Cuenta por Pagar (Proveedor)</option>
          </select>

          <label for="cx_tercero">Cliente / Proveedor</label>
          <input id="cx_tercero" name="cx_tercero" type="text" placeholder="Ej: Comercializadora Oriente C.A." required />

          <label for="cx_doc">Documento / Factura</label>
          <input id="cx_doc" name="cx_doc" type="text" placeholder="Ej: Factura #0089" />

          <label for="cx_monto">Monto pendiente</label>
          <input id="cx_monto" name="cx_monto" type="number" step="any" placeholder="Ej: 850.00" required />

          <button type="submit" class="btn-fucsia">Agregar cuenta</button>
        </form>

        <div class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Totales pendientes</h3>
          <div class="kpi-row">
            <div class="kpi"><div class="kpi-lbl">Por Cobrar</div><div class="kpi-val" style="color:var(--ok)">{{ cx_res.cobrar }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Por Pagar</div><div class="kpi-val" style="color:#f472b6">{{ cx_res.pagar }}</div></div>
            <div class="kpi"><div class="kpi-lbl">Posición Neta</div><div class="kpi-val">{{ cx_res.neto }}</div></div>
          </div>
        </div>
      </div>

      <div class="table-wrap" style="margin-top:14px;">
        <table>
          <thead>
            <tr><th>#</th><th>Tipo</th><th>Tercero</th><th>Documento</th><th>Monto</th><th>Estado</th><th>Acción</th></tr>
          </thead>
          <tbody>
            {% for c in cuentas_cx %}
              <tr>
                <td>{{ loop.index }}</td>
                <td>{{ c.tipo }}</td>
                <td>{{ c.tercero }}</td>
                <td>{{ c.doc }}</td>
                <td>{{ c.monto }}</td>
                <td>{{ c.estado }}</td>
                <td>
                  <form method="POST" style="display:inline; margin:0;">
                    <input type="hidden" name="codigo" value="{{ codigo }}" />
                    <input type="hidden" name="active_seg" value="s4" />
                    <input type="hidden" name="accion" value="alternar_estado_cx" />
                    <input type="hidden" name="cx_idx" value="{{ loop.index0 }}" />
                    <button type="submit" class="btn-navy btn-small">Cambiar estado</button>
                  </form>
                </td>
              </tr>
            {% else %}
              <tr><td colspan="7" style="color:var(--muted)">Sin cuentas registradas.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- SEGMENTO 5: BALANCES, ESTADOS Y DIVISAS -->
    <section id="s5" class="seg-panel {% if active_seg != 's5' %}hidden{% endif %}">
      <h2 style="margin-top:0">Segmento 5 · Balances, Estados y Divisas</h2>
      <p style="color:var(--muted)">Estado de resultados, balance general resumido y tasa referencial.</p>

      <div class="kpi-row">
        <div class="kpi"><div class="kpi-lbl">Ingresos (Entradas)</div><div class="kpi-val" style="color:var(--ok)">{{ resumen.entradas }}</div></div>
        <div class="kpi"><div class="kpi-lbl">Egresos (Salidas)</div><div class="kpi-val" style="color:#f472b6">{{ resumen.salidas }}</div></div>
        <div class="kpi"><div class="kpi-lbl">Resultado Neto</div><div class="kpi-val">{{ resumen.saldo }}</div></div>
        <div class="kpi"><div class="kpi-lbl">Cuentas por Cobrar</div><div class="kpi-val">{{ cx_res.cobrar }}</div></div>
        <div class="kpi"><div class="kpi-lbl">Cuentas por Pagar</div><div class="kpi-val">{{ cx_res.pagar }}</div></div>
      </div>

      <form method="POST" class="card" style="max-width:460px;">
        <h3 style="margin-top:0; color:#f9a8d4;">Actualizar tasa referencial</h3>
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_seg" value="s5" />
        <input type="hidden" name="accion" value="guardar_tasa" />
        <label for="tasa_ref_inp">Tasa de cambio referencial</label>
        <input id="tasa_ref_inp" name="tasa_ref_inp" type="number" step="any" value="{{ tasa_ref }}" required />
        <button type="submit" class="btn-fucsia">Guardar tasa</button>
      </form>
    </section>

    <!-- SEGMENTO 6: ARCHIVOS, ORDEN Y AJUSTES -->
    <section id="s6" class="seg-panel {% if active_seg != 's6' %}hidden{% endif %}">
      <h2 style="margin-top:0">Segmento 6 · Archivos, Orden y Ajustes</h2>
      <p style="color:var(--muted)">Importa archivos (.csv, .txt, .json), pega movimientos, ordénalos, exporta CSV y ajusta el fucsia.</p>

      <div class="grid-3">
        <form method="POST" enctype="multipart/form-data" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Importar / Pegar</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s6" />
          <input type="hidden" name="accion" value="importar_contable" />

          <label for="archivo_cont">Archivo (.csv, .txt, .json)</label>
          <input id="archivo_cont" name="archivo_cont" type="file" accept=".csv,.txt,.json" />

          <label for="texto_cont">Líneas (Fecha, Tipo, Cuenta, Concepto, Monto)</label>
          <textarea id="texto_cont" name="texto_cont" rows="3" placeholder="2026-11-22, ENTRADA, Banco Nacional, Cobro, 400"></textarea>

          <button type="submit" class="btn-fucsia">Cargar datos</button>
        </form>

        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Ordenar y Exportar</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s6" />
          <input type="hidden" name="accion" value="ordenar_movs" />

          <label for="orden_campo">Campo</label>
          <select id="orden_campo" name="orden_campo">
            <option value="fecha" {% if orden_campo == 'fecha' %}selected{% endif %}>Fecha</option>
            <option value="monto" {% if orden_campo == 'monto' %}selected{% endif %}>Monto</option>
            <option value="tipo" {% if orden_campo == 'tipo' %}selected{% endif %}>Tipo</option>
            <option value="cuenta" {% if orden_campo == 'cuenta' %}selected{% endif %}>Cuenta</option>
          </select>

          <label for="orden_dir">Orden</label>
          <select id="orden_dir" name="orden_dir">
            <option value="desc" {% if orden_dir == 'desc' %}selected{% endif %}>Descendente</option>
            <option value="asc" {% if orden_dir == 'asc' %}selected{% endif %}>Ascendente</option>
          </select>

          <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:6px;">
            <button type="submit" class="btn-fucsia" style="flex:1;">Ordenar</button>
            <a class="btn-navy" style="padding:10px 12px; border-radius:10px;" href="/descargar-contable?codigo={{ codigo }}">CSV</a>
          </div>
        </form>

        <form method="POST" class="card">
          <h3 style="margin-top:0; color:#f9a8d4;">Estilo fucsia</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_seg" value="s6" />
          <input type="hidden" name="accion" value="guardar_ajustes_contab" />

          <label for="tono_fucsia">Tono</label>
          <select id="tono_fucsia" name="tono_fucsia">
            <option value="#ec4899" {% if tono_fucsia == '#ec4899' %}selected{% endif %}>Fucsia vibrante</option>
            <option value="#f43f5e" {% if tono_fucsia == '#f43f5e' %}selected{% endif %}>Rosa fucsia intenso</option>
            <option value="#d946ef" {% if tono_fucsia == '#d946ef' %}selected{% endif %}>Fucsia magenta</option>
          </select>

          <button type="submit" class="btn-fucsia" style="margin-top:26px;">Guardar estilo</button>
        </form>
      </div>
    </section>
  {% endif %}
</div>

<script>
  function openSeg(id, btn) {
    document.querySelectorAll('.seg-panel').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(id);
    if (panel) panel.classList.remove('hidden');
    if (btn) btn.classList.add('active');
    document.querySelectorAll('input[name="active_seg"]').forEach(inp => inp.value = id);
  }
</script>
</body>
</html>
"""

SESIONES_CONTAB = {}


def _fmt_num(v):
    try:
        num = float(v)
        if num.is_integer():
            return str(int(num))
        return f"{round(num, 2):.2f}"
    except (TypeError, ValueError):
        return "0"


def obtener_sesion(codigo):
    code = (codigo or "").strip().upper()
    if code not in CODIGOS_ACCESO:
        return None
    if code not in SESIONES_CONTAB:
        SESIONES_CONTAB[code] = {
            "uso": 0,
            "active_seg": "s1",
            "tono_fucsia": "#ec4899",
            "estado_cierre": "ABIERTO",
            "cierre_obs": "Período activo listo para operar",
            "orden_campo": "fecha",
            "orden_dir": "desc",
            "tasa_ref": 45.0,
            "movimientos": [
                {"fecha": "2026-11-20", "tipo": "ENTRADA", "cuenta": "Banco Nacional", "concepto": "Cobro cliente inicial", "monto": 1200.0},
                {"fecha": "2026-11-21", "tipo": "SALIDA", "cuenta": "Gastos Administrativos", "concepto": "Servicio de internet y oficina", "monto": 180.0},
            ],
            "asientos": [
                {"cuenta": "Banco Nacional", "ref": "Apertura / Cobro cliente", "debe": 1200.0, "haber": 0.0},
                {"cuenta": "Ingresos por Servicios", "ref": "Apertura / Cobro cliente", "debe": 0.0, "haber": 1200.0},
            ],
            "facturas": [
                {"libro": "VENTA", "rif": "J-30123456-7", "control": "00-000101", "base": "1000.00", "iva": "160.00", "ret_iva": "120.00", "ret_islr": "20.00", "total": "1160.00"},
            ],
            "cuentas_cx": [
                {"tipo": "COBRAR", "tercero": "Cliente Ejemplo C.A.", "doc": "Fact-001", "monto": 500.0, "estado": "PENDIENTE"},
                {"tipo": "PAGAR", "tercero": "Proveedor Servicios", "doc": "Fact-209", "monto": 220.0, "estado": "PENDIENTE"},
            ],
        }
    return SESIONES_CONTAB[code]


def _ordenar_movs(movs, campo="fecha", direccion="desc"):
    rev = (direccion == "desc")
    if campo == "monto":
        return sorted(movs, key=lambda x: float(x.get("monto", 0) or 0), reverse=rev)
    if campo == "tipo":
        return sorted(movs, key=lambda x: str(x.get("tipo", "")).lower(), reverse=rev)
    if campo == "cuenta":
        return sorted(movs, key=lambda x: str(x.get("cuenta", "")).lower(), reverse=rev)
    return sorted(movs, key=lambda x: str(x.get("fecha", "")), reverse=rev)


def _calcular_resumen(movs):
    entradas = sum(float(m.get("monto", 0) or 0) for m in movs if m.get("tipo") == "ENTRADA")
    salidas = sum(float(m.get("monto", 0) or 0) for m in movs if m.get("tipo") == "SALIDA")
    saldo = entradas - salidas
    return {
        "entradas": _fmt_num(entradas),
        "salidas": _fmt_num(salidas),
        "saldo": _fmt_num(saldo),
        "saldo_raw": saldo,
        "cantidad": len(movs),
    }


def _calcular_diario_y_mayor(asientos):
    debe_tot = sum(float(a.get("debe", 0) or 0) for a in asientos)
    haber_tot = sum(float(a.get("haber", 0) or 0) for a in asientos)
    acum = {}
    for a in asientos:
        cta = str(a.get("cuenta") or "Cuenta General").strip()
        d = float(a.get("debe", 0) or 0)
        h = float(a.get("haber", 0) or 0)
        if cta not in acum:
            acum[cta] = {"debe": 0.0, "haber": 0.0}
        acum[cta]["debe"] += d
        acum[cta]["haber"] += h
    mayor_rows = []
    for cta, vals in acum.items():
        mayor_rows.append({
            "cuenta": cta,
            "debe": _fmt_num(vals["debe"]),
            "haber": _fmt_num(vals["haber"]),
            "saldo": _fmt_num(vals["debe"] - vals["haber"]),
        })
    return (
        {
            "debe": _fmt_num(debe_tot),
            "haber": _fmt_num(haber_tot),
            "dif": _fmt_num(debe_tot - haber_tot),
        },
        mayor_rows,
    )


def _calcular_fiscal(facturas):
    debito = sum(float(f.get("iva", 0) or 0) for f in facturas if f.get("libro") == "VENTA")
    credito = sum(float(f.get("iva", 0) or 0) for f in facturas if f.get("libro") == "COMPRA")
    ret_iva = sum(float(f.get("ret_iva", 0) or 0) for f in facturas)
    ret_islr = sum(float(f.get("ret_islr", 0) or 0) for f in facturas)
    return {
        "debito_iva": _fmt_num(debito),
        "credito_iva": _fmt_num(credito),
        "iva_neto": _fmt_num(debito - credito),
        "ret_iva_total": _fmt_num(ret_iva),
        "ret_islr_total": _fmt_num(ret_islr),
    }


def _calcular_cx(cuentas):
    cobrar = sum(float(c.get("monto", 0) or 0) for c in cuentas if c.get("tipo") == "COBRAR" and c.get("estado") == "PENDIENTE")
    pagar = sum(float(c.get("monto", 0) or 0) for c in cuentas if c.get("tipo") == "PAGAR" and c.get("estado") == "PENDIENTE")
    return {
        "cobrar": _fmt_num(cobrar),
        "pagar": _fmt_num(pagar),
        "neto": _fmt_num(cobrar - pagar),
    }


def _parsear_movimientos_texto(texto):
    nuevos = []
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
        concepto = partes[3] if len(partes) > 3 and partes[3] else "Movimiento importado"
        try:
            monto = abs(float(partes[4])) if len(partes) > 4 else 0.0
        except ValueError:
            monto = 0.0
        nuevos.append({
            "fecha": fecha,
            "tipo": tipo,
            "cuenta": cuenta,
            "concepto": concepto,
            "monto": monto,
        })
    return nuevos


def render_contap(codigo, sesion, error_msg=None, aviso_msg=None):
    info = CODIGOS_ACCESO[codigo]
    movs_ord = _ordenar_movs(sesion["movimientos"], sesion["orden_campo"], sesion["orden_dir"])
    resumen = _calcular_resumen(movs_ord)
    diario_res, libro_mayor = _calcular_diario_y_mayor(sesion["asientos"])
    tasa = float(sesion.get("tasa_ref", 45.0) or 45.0)
    saldo_equiv = _fmt_num(resumen["saldo_raw"] * tasa)

    return render_template_string(
        HTML_TEMPLATE,
        autorizado=True,
        error=error_msg,
        aviso=aviso_msg,
        codigo=codigo,
        plan=info["plan"],
        limite=info["limite"],
        uso=sesion["uso"],
        active_seg=sesion.get("active_seg", "s1"),
        tono_fucsia=sesion.get("tono_fucsia", "#ec4899"),
        estado_cierre=sesion.get("estado_cierre", "ABIERTO"),
        cierre_obs=sesion.get("cierre_obs", ""),
        orden_campo=sesion.get("orden_campo", "fecha"),
        orden_dir=sesion.get("orden_dir", "desc"),
        tasa_ref=_fmt_num(tasa),
        saldo_ref_equiv=saldo_equiv,
        movimientos=movs_ord,
        resumen=resumen,
        asientos=sesion["asientos"],
        diario_res=diario_res,
        libro_mayor=libro_mayor,
        facturas=sesion["facturas"],
        fisc=_calcular_fiscal(sesion["facturas"]),
        cuentas_cx=sesion["cuentas_cx"],
        cx_res=_calcular_cx(sesion["cuentas_cx"]),
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        codigo = (request.form.get("codigo") or "").strip().upper()
        sesion = obtener_sesion(codigo)
        if not sesion:
            return render_template_string(
                HTML_TEMPLATE,
                autorizado=False,
                tono_fucsia="#ec4899",
                error="Código no válido. Usa DEMO2026, VIP100 o CONTAB2026.",
            )

        seg_sel = request.form.get("active_seg")
        if seg_sel in ("s1", "s2", "s3", "s4", "s5", "s6"):
            sesion["active_seg"] = seg_sel

        limite = CODIGOS_ACCESO[codigo]["limite"]
        accion = request.form.get("accion")
        aviso = None
        error = None

        if accion:
            if sesion["uso"] >= limite:
                return render_contap(codigo, sesion, error_msg="Límite de uso alcanzado.")
            sesion["uso"] += 1

        if accion == "agregar_mov":
            if sesion["estado_cierre"] == "CERRADO":
                error = "El período está CERRADO. Reábrelo en '2. Diario, Mayor y Cierre'."
            else:
                tipo = request.form.get("mov_tipo") or "ENTRADA"
                cuenta = request.form.get("mov_cuenta") or "Banco Nacional"
                concepto = (request.form.get("mov_desc") or "").strip()
                fecha = (request.form.get("mov_fecha") or "").strip() or datetime.now().strftime("%Y-%m-%d")
                try:
                    monto = abs(float(request.form.get("mov_monto", 0)))
                    if concepto and monto > 0:
                        sesion["movimientos"].append({
                            "fecha": fecha,
                            "tipo": tipo,
                            "cuenta": cuenta,
                            "concepto": concepto,
                            "monto": monto,
                        })
                        aviso = f"{tipo} registrada."
                    else:
                        error = "Completa el concepto y un monto mayor a cero."
                except ValueError:
                    error = "Monto inválido."
            sesion["active_seg"] = "s1"

        elif accion == "borrar_mov":
            if sesion["estado_cierre"] == "CERRADO":
                error = "No puedes eliminar movimientos mientras el período esté CERRADO."
            else:
                try:
                    idx = int(request.form.get("mov_idx", -1))
                    movs_ord = _ordenar_movs(sesion["movimientos"], sesion["orden_campo"], sesion["orden_dir"])
                    if 0 <= idx < len(movs_ord):
                        sesion["movimientos"].remove(movs_ord[idx])
                        aviso = "Movimiento eliminado."
                except Exception:
                    error = "No se pudo eliminar el movimiento."
            sesion["active_seg"] = "s1"

        elif accion == "agregar_asiento":
            if sesion["estado_cierre"] == "CERRADO":
                error = "El período está CERRADO. Reábrelo para registrar asientos."
            else:
                cuenta = (request.form.get("as_cuenta") or "").strip()
                ref = (request.form.get("as_ref") or "").strip()
                try:
                    debe = abs(float(request.form.get("as_debe", 0) or 0))
                    haber = abs(float(request.form.get("as_haber", 0) or 0))
                    if cuenta and ref and (debe > 0 or haber > 0):
                        sesion["asientos"].append({"cuenta": cuenta, "ref": ref, "debe": debe, "haber": haber})
                        aviso = "Asiento registrado."
                    else:
                        error = "Indica cuenta, referencia y monto en Debe o Haber."
                except ValueError:
                    error = "Valores inválidos."
            sesion["active_seg"] = "s2"

        elif accion == "ejecutar_cierre":
            obs = (request.form.get("cierre_obs") or "").strip()
            if obs:
                sesion["cierre_obs"] = obs
            if sesion["estado_cierre"] == "CERRADO":
                sesion["estado_cierre"] = "ABIERTO"
                aviso = "Período reabierto."
            else:
                sesion["estado_cierre"] = "CERRADO"
                aviso = "Cierre contable ejecutado."
            sesion["active_seg"] = "s2"

        elif accion == "agregar_factura":
            libro = request.form.get("fac_libro") or "VENTA"
            rif = (request.form.get("fac_rif") or "").strip().upper()
            control = (request.form.get("fac_control") or "N/A").strip()
            try:
                base = abs(float(request.form.get("fac_base", 0) or 0))
                iva_pct = abs(float(request.form.get("fac_iva_pct", 16) or 0))
                ret_iva_pct = abs(float(request.form.get("fac_ret_iva_pct", 75) or 0))
                ret_islr_pct = abs(float(request.form.get("fac_ret_islr_pct", 0) or 0))
                if rif and base > 0:
                    iva_m = base * (iva_pct / 100.0)
                    ret_iva_m = iva_m * (ret_iva_pct / 100.0)
                    ret_islr_m = base * (ret_islr_pct / 100.0)
                    tot_m = base + iva_m
                    sesion["facturas"].append({
                        "libro": libro,
                        "rif": rif,
                        "control": control,
                        "base": _fmt_num(base),
                        "iva": _fmt_num(iva_m),
                        "ret_iva": _fmt_num(ret_iva_m),
                        "ret_islr": _fmt_num(ret_islr_m),
                        "total": _fmt_num(tot_m),
                    })
                    aviso = f"Factura agregada al libro de {libro.lower()}."
                else:
                    error = "Indica RIF y base imponible mayor a cero."
            except ValueError:
                error = "Revisa los montos de la factura."
            sesion["active_seg"] = "s3"

        elif accion == "agregar_cxc_cxp":
            tipo_cx = request.form.get("cx_tipo") or "COBRAR"
            tercero = (request.form.get("cx_tercero") or "").strip()
            doc = (request.form.get("cx_doc") or "S/N").strip()
            try:
                monto_cx = abs(float(request.form.get("cx_monto", 0) or 0))
                if tercero and monto_cx > 0:
                    sesion["cuentas_cx"].append({
                        "tipo": tipo_cx,
                        "tercero": tercero,
                        "doc": doc,
                        "monto": monto_cx,
                        "estado": "PENDIENTE",
                    })
                    aviso = "Cuenta agregada."
                else:
                    error = "Indica tercero y monto mayor a cero."
            except ValueError:
                error = "Monto inválido."
            sesion["active_seg"] = "s4"

        elif accion == "alternar_estado_cx":
            try:
                idx = int(request.form.get("cx_idx", -1))
                if 0 <= idx < len(sesion["cuentas_cx"]):
                    actual = sesion["cuentas_cx"][idx]["estado"]
                    sesion["cuentas_cx"][idx]["estado"] = "SALDADA" if actual == "PENDIENTE" else "PENDIENTE"
                    aviso = "Estado de cuenta actualizado."
            except Exception:
                error = "No se pudo actualizar el estado."
            sesion["active_seg"] = "s4"

        elif accion == "guardar_tasa":
            try:
                t_val = abs(float(request.form.get("tasa_ref_inp", 45) or 45))
                if t_val > 0:
                    sesion["tasa_ref"] = t_val
                    aviso = "Tasa referencial actualizada."
            except ValueError:
                error = "Tasa inválida."
            sesion["active_seg"] = "s5"

        elif accion == "importar_contable":
            nuevos = []
            arch = request.files.get("archivo_cont")
            if arch and arch.filename:
                raw_txt = arch.read().decode("utf-8", errors="ignore").strip()
                if arch.filename.lower().endswith(".json") or raw_txt.startswith("["):
                    data = json.loads(raw_txt)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                nuevos.append({
                                    "fecha": str(item.get("fecha") or datetime.now().strftime("%Y-%m-%d")),
                                    "tipo": "SALIDA" if str(item.get("tipo", "")).upper() == "SALIDA" else "ENTRADA",
                                    "cuenta": str(item.get("cuenta") or "Banco Nacional"),
                                    "concepto": str(item.get("concepto") or "Importado JSON"),
                                    "monto": abs(float(item.get("monto", 0) or 0)),
                                })
                else:
                    nuevos.extend(_parsear_movimientos_texto(raw_txt))

            pegar_txt = request.form.get("texto_cont") or ""
            if pegar_txt.strip():
                nuevos.extend(_parsear_movimientos_texto(pegar_txt))

            if nuevos:
                sesion["movimientos"].extend(nuevos)
                aviso = f"Se cargaron {len(nuevos)} movimiento(s)."
            else:
                error = "No se detectaron filas válidas."
            sesion["active_seg"] = "s6"

        elif accion == "ordenar_movs":
            sesion["orden_campo"] = request.form.get("orden_campo") or "fecha"
            sesion["orden_dir"] = request.form.get("orden_dir") or "desc"
            aviso = "Movimientos ordenados."
            sesion["active_seg"] = "s6"

        elif accion == "guardar_ajustes_contab":
            tono = (request.form.get("tono_fucsia") or "#ec4899").strip()
            if tono in ("#ec4899", "#f43f5e", "#d946ef"):
                sesion["tono_fucsia"] = tono
            aviso = "Estilo fucsia guardado."
            sesion["active_seg"] = "s6"

        return render_contap(codigo, sesion, error_msg=error, aviso_msg=aviso)

    return render_template_string(HTML_TEMPLATE, autorizado=False, tono_fucsia="#ec4899", error=None)


@app.route("/descargar-contable")
def descargar_contable():
    codigo = (request.args.get("codigo") or "").strip().upper()
    sesion = obtener_sesion(codigo)
    if not sesion:
        return "Código no autorizado", 403
    movs_ord = _ordenar_movs(sesion["movimientos"], sesion["orden_campo"], sesion["orden_dir"])
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
