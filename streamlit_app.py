import streamlit as st
import pandas as pd
import requests
import math
import re
from bisect import bisect_left
from html import escape
from pathlib import Path

# Настройка страницы (Темная тема и мобильный вид)
st.set_page_config(page_title="Подвеска Voge DS900X", page_icon="🏍️", layout="centered")

st.markdown("""
<style>
:root {
    --moto-bg: #13171c;
    --moto-card: #1d242d;
    --moto-section-head: #232b35;
    --moto-line: #353d47;
    --moto-text: #f0f2f5;
    --moto-muted: #b0bac6;
    --moto-accent: #ffd27f;
    --moto-shadow: 0 3px 10px #0004, inset 0 1px #ffffff0b;
}
.stApp {
    background: var(--moto-bg);
}
.stApp :is(.moto-hero, .moto-panel, .moto-advice, [data-testid="stExpander"] summary) {
    color: var(--moto-text);
}
.stApp :is(h1, h2, h3, label, [data-testid="stMarkdownContainer"] p) { color: var(--moto-text); }
.stApp [data-testid="stCaptionContainer"] p { color: var(--moto-muted); }
.stApp [data-testid="stMarkdownContainer"] a { color: var(--moto-accent); }
[data-testid="stHeader"] { background: transparent; height: auto; }
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
.block-container { max-width: 46rem; padding: 2rem 1rem 4rem; }
[data-testid="stVerticalBlock"] { gap: .72rem; }
.moto-hero { border-top: 2px solid var(--moto-accent); padding: .88rem 0 .25rem; }
.moto-hero .model {
    color: var(--moto-accent); font-size: .74rem; font-weight: 700; letter-spacing: .14em;
}
.moto-hero h1 { margin: .2rem 0 0; padding: 0; font-size: clamp(2rem, 7vw, 3.15rem); line-height: 1.05; letter-spacing: -.045em; }
.stApp h2, .stApp h3 { font-size: 1.22rem; line-height: 1.25; margin: 0; padding: .4rem 0 .15rem; }
.moto-panel {
    padding: .85rem .9rem;
    border: 1px solid var(--moto-line);
    border-radius: .85rem;
    background: var(--moto-card);
    box-shadow: var(--moto-shadow);
}
.moto-panel-head { display: flex; justify-content: space-between; align-items: baseline; gap: .65rem; margin-bottom: .7rem; }
.moto-panel-title { font-size: .94rem; font-weight: 700; line-height: 1.2; }
.moto-panel-meta { color: var(--moto-muted); font-size: .73rem; line-height: 1.25; }
.moto-setup-grid { display: grid; grid-template-columns: 1.25fr 1fr; gap: .55rem; padding-bottom: .625rem; }
.moto-setup-overload .moto-panel, .moto-panel-overload { background: #2b2025; border-color: #a34f59; }
.moto-metrics { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); }
.moto-metric { min-width: 0; padding: .48rem .45rem 0; border-top: 1px solid var(--moto-line); }
.moto-metric:first-child { padding-left: 0; }
.moto-metric + .moto-metric { border-left: 1px solid var(--moto-line); }
.moto-label { display: block; color: var(--moto-muted); font-size: .74rem; line-height: 1.15; }
.moto-value {
    display: block; margin-top: .25rem; color: var(--moto-text); font-size: 1.52rem;
    line-height: 1; font-weight: 700; font-variant-numeric: tabular-nums; letter-spacing: -.04em;
}
.moto-unit { color: var(--moto-muted); font-size: .67rem; }
.moto-pressure-line { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; }
.moto-pressure-line .moto-value { color: var(--moto-accent); }
.moto-setup-overload .moto-value, .moto-panel-overload .moto-value { color: #ff9ca5; }
.moto-pressure-reference { margin-top: .65rem; padding-top: .6rem; border-top: 1px solid var(--moto-line); }
.moto-pressure-reference p { margin: .25rem 0 0; font-size: .85rem; }
.moto-load { border-top: 1px solid var(--moto-line); padding-top: .6rem; margin-top: .65rem; }
.moto-review-head { display: flex; justify-content: space-between; align-items: baseline; gap: .75rem; }
.moto-review-name { font-size: .98rem; font-weight: 700; overflow-wrap: anywhere; min-width: 0; }
.moto-review-count { color: var(--moto-accent); font-size: .76rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
.moto-review-rows { display: grid; gap: .45rem; margin-top: .65rem; }
.moto-review-line { display: grid; grid-template-columns: minmax(3.1rem, .6fr) 2fr; gap: .45rem; border-top: 1px solid var(--moto-line); padding-top: .45rem; }
.moto-review-line span, .moto-review-sag { font-size: .77rem; color: var(--moto-muted); }
.moto-review-context { color: #b5d7f5; font-weight: 650; }
.moto-review-value { color: var(--moto-accent); font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
.moto-review-sag { margin-top: .4rem; }
.moto-review-comment { line-height: 1.45; border-top: 1px solid var(--moto-line); margin-top: .6rem; padding-top: .55rem; overflow-wrap: anywhere; }
.stApp [data-testid="stExpander"] details {
    background: var(--moto-card);
    border-color: var(--moto-line);
    border-radius: .7rem;
    box-shadow: var(--moto-shadow);
}
.stApp [data-testid="stExpander"] summary { min-height: 2.55rem; }
.stApp [data-testid="stExpander"] details[open] > summary {
    background: var(--moto-section-head);
    border-radius: .7rem .7rem 0 0;
}
.stApp [data-testid="stExpander"] [data-testid="stImage"] img { border-radius: .55rem; }
.moto-advice { display: grid; gap: .55rem; }
.moto-advice-card {
    --moto-advice-accent: #accced;
    background: #29465e;
    border-inline-start: 2px solid var(--moto-advice-accent);
    border-radius: .55rem;
    padding: .68rem .8rem;
}
.moto-advice-card:not(.moto-advice-action) { box-shadow: inset 0 0 0 1px #44627d; }
.moto-advice-action { --moto-advice-accent: var(--moto-accent); background: #2c261c; }
.moto-advice-label {
    display: block;
    color: var(--moto-advice-accent);
    font-size: .85rem;
    margin-bottom: .2rem;
}
.moto-advice .moto-advice-card p { margin: 0; line-height: 1.5; }
.stApp .moto-sag-guide p {
    color: #dce4ed;
    font-size: 1rem;
    line-height: 1.6;
    margin: 0 0 .65rem;
}
.stApp .moto-sag-guide p:last-child { margin-bottom: 0; }
.stApp .moto-sag-guide .moto-sag-target { color: var(--moto-text); font-weight: 600; }
.moto-sag-target strong { color: var(--moto-accent); font-variant-numeric: tabular-nums; }
/* Поля и выпадающие списки используют согласованные цвета темы Streamlit. */
.stApp [data-testid="stButton"] button { background: var(--moto-card); color: var(--moto-text); border-color: var(--moto-line); }
.stApp [data-testid="stButton"] button:hover { border-color: var(--moto-accent); color: var(--moto-accent); }
.stApp [data-testid="stButton"] button:focus-visible { outline: 2px solid var(--moto-accent); }
.st-key-ride_inputs [data-testid="stHorizontalBlock"], .st-key-review_navigation [data-testid="stHorizontalBlock"] {
    display: grid; gap: .5rem;
}
.st-key-ride_inputs [data-testid="stHorizontalBlock"] { grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr); }
.st-key-review_navigation { padding-top: .625rem; }
.st-key-review_navigation [data-testid="stHorizontalBlock"] { grid-template-columns: minmax(0, .55fr) minmax(0, .55fr) minmax(0, 2fr); }
:is(.st-key-ride_inputs, .st-key-review_navigation) [data-testid="stColumn"] { width: 100% !important; min-width: 0 !important; }
.st-key-review_navigation button { min-height: 2.75rem; }
@media (max-width: 560px) {
    .block-container { padding: .8rem .85rem 3.25rem; }
    .moto-setup-grid { grid-template-columns: 1fr; }
    .moto-hero { padding-top: .7rem; }
}
@media (max-width: 345px) {
    .st-key-ride_inputs [data-testid="stHorizontalBlock"] { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# Ссылки из Секретов Streamlit
URL_BASE = st.secrets["URL_BASE"]
URL_REVIEWS = st.secrets["URL_REVIEWS"]

# Вставьте вашу сохраненную ссылку из Apps Script
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyT_0f2fr52rkOA5Z7EsGjDqa8axAOxZNqHaEY8lx-o9n3KJQAOgup0sMfwtwsS9_pR/exec"

SETTING_COLUMNS = ("comp_f", "reb_f", "preload_f", "preload_r", "reb_r")
REAR_PRELOAD_CAP = 25  # Наблюдение Shem090, а не подтверждённый предел для всех экземпляров.
MAX_PAYLOAD_KG = 205
MANUAL_URL = "https://voge.gr/wp-content/uploads/2021/09/DS900X-user-manual-.pdf"
FORK_GUIDE_PHOTO = Path(__file__).resolve().parent / "assets" / "fork-adjusters.jpg"
REFERENCE_RIDER_KG = 75
REFERENCE_PASSENGER_KG = 55
REFERENCE_CARGO_KG = 24


def number(value):
    try:
        parsed = float(str(value).strip().replace(",", "."))
    except (ValueError, TypeError):
        return None
    return parsed if math.isfinite(parsed) else None


def suspension_setting(base, weight, mode):
    rows = base.loc[base["mode"] == mode].copy()
    for column in ("weight", *SETTING_COLUMNS):
        rows[column] = rows[column].map(number)
    rows = rows.dropna(subset=["weight", *SETTING_COLUMNS])
    rows = rows.loc[(rows[list(SETTING_COLUMNS)] >= 0).all(axis=1)]
    rows = rows.sort_values("weight", kind="stable").drop_duplicates("weight", keep="first")
    if rows.empty:
        return None

    lower = rows.loc[rows["weight"] <= weight]
    upper = rows.loc[rows["weight"] >= weight]
    if lower.empty or upper.empty:
        edge = rows.iloc[0] if lower.empty else rows.iloc[-1]
        left = right = edge
        status = "reference"
    else:
        left, right = lower.iloc[-1], upper.iloc[0]
        status = "table" if left["weight"] == right["weight"] else "interpolated"

    fraction = 0 if left["weight"] == right["weight"] else (
        (weight - left["weight"]) / (right["weight"] - left["weight"])
    )
    settings = {}
    for column in SETTING_COLUMNS:
        value = left[column] + (right[column] - left[column]) * fraction
        step = 0.5 if column == "preload_f" else 1
        settings[column] = math.floor(value / step + 0.5) * step

    limited = settings["preload_r"] > REAR_PRELOAD_CAP
    settings["preload_r"] = min(settings["preload_r"], REAR_PRELOAD_CAP)
    notes = left.get("notes", "") if status == "table" else ""
    if pd.isna(notes):
        notes = ""
    return settings, status, int(left["weight"]), int(right["weight"]), limited, str(notes).strip()


def rear_setting(base, modes, rider_weight, passenger_weight, cargo_weight):
    # Доли веса на задней оси — допущения модели.
    passenger_share, cargo_share, rider_share = 0.8, 0.9, 0.6
    passenger_reference = REFERENCE_PASSENGER_KG * passenger_share
    cargo_reference = REFERENCE_CARGO_KG * cargo_share
    anchor_loads = (0, cargo_reference, passenger_reference, passenger_reference + cargo_reference)
    mode_names = {mode.casefold().replace("ё", "е"): mode for mode in modes}
    mode_keys = ("один", "один + кофры", "вдвоем", "вдвоем + кофры")
    anchor_modes = tuple(mode_names.get(key) for key in mode_keys)

    rear_load = passenger_weight * passenger_share + cargo_weight * cargo_share
    index = bisect_left(anchor_loads, rear_load)
    rear_columns = ("preload_r", "reb_r")
    last_load = anchor_loads[-1]
    if rear_load >= last_load:
        lookup_weight = rider_weight + (rear_load - last_load) / rider_share
        result = suspension_setting(base, lookup_weight, anchor_modes[-1])
        return (result[0], result[1] == "reference") if result else None

    upper = suspension_setting(base, rider_weight, anchor_modes[index])
    if upper is None:
        return None
    if rear_load == anchor_loads[index]:
        return upper[0], upper[1] == "reference"
    lower = suspension_setting(base, rider_weight, anchor_modes[index - 1])
    if lower is None:
        return None
    lower_load, upper_load = anchor_loads[index - 1:index + 1]
    fraction = (rear_load - lower_load) / (upper_load - lower_load)
    values = {
        column: math.floor(lower[0][column] + (upper[0][column] - lower[0][column]) * fraction + 0.5)
        for column in rear_columns
    }
    return values, lower[1] == "reference" or upper[1] == "reference"


def estimated_pressure_by_payload(payload):
    progress = (payload - REFERENCE_RIDER_KG) / (MAX_PAYLOAD_KG - REFERENCE_RIDER_KG)
    progress = min(1, max(0, progress))
    return 2.2 + 0.3 * progress, 2.5 + 0.4 * progress


def sag_text(value):
    measured = number(value)
    return f"{measured:g} мм" if measured is not None and measured > 0 else "—"


def html_text(value):
    return "" if pd.isna(value) else escape(str(value))


def review_text_html(value):
    if pd.isna(value):
        return ""
    lines = re.split(r"<br\s*/?>|\r?\n", str(value), flags=re.IGNORECASE)
    return "<br>".join(escape(line) for line in lines)


def post_review_action(payload):
    response = requests.post(WEB_APP_URL, json=payload, timeout=12)
    response.raise_for_status()
    if response.text.strip() != "Success":
        raise ValueError("Unexpected Apps Script response")


@st.cache_data(ttl=15)
def load_all_data():
    try:
        df_b = pd.read_csv(URL_BASE, dtype=str)
        df_b.columns = df_b.columns.str.strip()
        df_b["mode"] = df_b["mode"].str.strip().replace("", pd.NA)
        missing_columns = {"weight", "mode", *SETTING_COLUMNS} - set(df_b.columns)
        if missing_columns:
            raise ValueError("Нет столбцов: " + ", ".join(sorted(missing_columns)))
        
        try:
            df_r = pd.read_csv(URL_REVIEWS, dtype=str)
            df_r.columns = df_r.columns.str.strip()
            df_r['Загрузка'] = df_r['Загрузка'].astype(str).str.strip()
        except Exception:
            df_r = pd.DataFrame(columns=['Имя', 'Вес', 'Загрузка', 'Перед_Преднатяг_Витков', 'Перед_Сжатие', 'Перед_Отбой', 'Зад_Преднатяг', 'Зад_Отбой', 'Перед_Реальный_Сэг_мм', 'Зад_Реальный_Сэг_мм', 'Причина_Текст', 'Лайки'])
            
        return df_b, df_r
    except Exception as e:
        st.error(f"Ошибка синхронизации: {str(e)}")
        return None, None

df_base, df_reviews = load_all_data()

if df_base is not None:
    st.markdown('<div class="moto-hero"><span class="model">VOGE DS900X</span>'
                '<h1>Подвеска</h1></div>', unsafe_allow_html=True)

    modes = df_base["mode"].dropna().unique().tolist()
    if not modes:
        st.error("В таблице клуба нет режимов загрузки.")
        st.stop()
    with st.container(key="ride_inputs"):
        weight_column, mode_column = st.columns([1, 1.25])
        user_weight = weight_column.number_input(
            "Райдер, кг", min_value=50, max_value=150, value=90, step=1,
            help="Введите вес в экипировке.",
        )
        loading_mode = mode_column.selectbox("Загрузка", modes)
    mode_slug = loading_mode.casefold().replace("ё", "е")

    has_passenger = "вдвоем" in mode_slug
    has_cases = "кофры" in mode_slug
    with st.expander("Вес пассажира и багажа", expanded=has_passenger or has_cases):
        passenger_weight = st.number_input(
            "Пассажир в экипировке, кг", min_value=1, max_value=250,
            value=REFERENCE_PASSENGER_KG, step=1,
            help="По умолчанию 55 кг. Укажите фактический вес, если он известен.",
        ) if has_passenger else 0
        cargo_weight = st.number_input(
            "Кофры, багаж и дополнительные аксессуары, кг",
            min_value=0, max_value=250, value=REFERENCE_CARGO_KG if has_cases else 0, step=1,
            key=f"cargo_weight_{loading_mode}",
        )
        st.caption(f"Допустимая нагрузка мотоцикла по руководству Voge — {MAX_PAYLOAD_KG} кг.")
        counted_load = user_weight + (passenger_weight or 0) + (cargo_weight or 0)
        load_complete = passenger_weight is not None and cargo_weight is not None
        load_remaining = MAX_PAYLOAD_KG - counted_load
        overloaded = load_remaining < 0
        if overloaded:
            load_summary = f"Загрузка {counted_load} / {MAX_PAYLOAD_KG} кг · превышение {-load_remaining} кг"
        elif load_complete:
            load_summary = f"Загрузка {counted_load} / {MAX_PAYLOAD_KG} кг · запас {load_remaining} кг"
        else:
            load_summary = f"Учтено {counted_load} кг · заполните оставшиеся поля загрузки"
        st.caption(load_summary)
    setup_passenger_weight, setup_cargo_weight = passenger_weight, cargo_weight
    if overloaded:
        st.error(f"Введённая нагрузка {counted_load} кг превышает предел Voge на {-load_remaining} кг. "
                 "Уменьшите загрузку.")
        available_weight = MAX_PAYLOAD_KG - user_weight
        setup_passenger_weight = min(passenger_weight or 0, available_weight)
        setup_cargo_weight = available_weight - setup_passenger_weight

    result = suspension_setting(df_base, user_weight, loading_mode)
    status = None
    b_p_szh = b_p_otb = b_p_tur = b_z_pred = b_z_otb = None
    if result is None:
        st.info("Для выбранной загрузки пока нет настроек.")
    else:
        values, status, lower_weight, upper_weight, _, _ = result
        b_p_szh = values["comp_f"]
        b_p_otb = values["reb_f"]
        b_p_tur = values["preload_f"]
        b_z_pred = values["preload_r"]
        b_z_otb = values["reb_r"]
        rear_outside_range = False
        rear_adjusted = False
        reference_passenger = REFERENCE_PASSENGER_KG if has_passenger else 0
        reference_cargo = REFERENCE_CARGO_KG if has_cases else 0
        rear_passenger = reference_passenger if setup_passenger_weight is None else setup_passenger_weight
        rear_cargo = reference_cargo if setup_cargo_weight is None else setup_cargo_weight
        if (rear_passenger, rear_cargo) != (reference_passenger, reference_cargo):
            rear_result = rear_setting(df_base, modes, user_weight, rear_passenger, rear_cargo)
            if rear_result is not None:
                rear_values, rear_outside_range = rear_result
                b_z_pred, b_z_otb = rear_values["preload_r"], rear_values["reb_r"]
                rear_adjusted = True
        if overloaded:
            st.subheader(f"Справочные настройки при {MAX_PAYLOAD_KG} кг")
            st.caption(f"В расчёте: райдер {user_weight} кг, пассажир {setup_passenger_weight} кг, "
                       f"кофры и багаж {setup_cargo_weight} кг.")
            st.caption("Перед поездкой уменьшите фактическую загрузку до допустимой и пересчитайте настройки.")
        elif status == "reference":
            st.subheader("Ближайшие настройки")
            st.info(f"Для {user_weight} кг использованы настройки для {lower_weight} кг. Проверьте сэг под нагрузкой.")
        else:
            st.subheader("Стартовые настройки")
        if not overloaded and b_z_pred >= REAR_PRELOAD_CAP:
            st.warning(f"Расчёт заднего преднатяга достиг верхней границы — {REAR_PRELOAD_CAP} щелчков. "
                       "Проверьте сэг под выбранной нагрузкой и фактический ход регулятора.")

        front_preload = f"{b_p_tur:g}".replace(".", ",")
        setup_style = " moto-setup-overload" if overloaded else ""
        st.markdown(f"""
        <div class="moto-setup-grid{setup_style}">
          <section class="moto-panel" id="perednyaya-vilka" aria-label="Передняя вилка">
            <div class="moto-panel-head"><b class="moto-panel-title">Передняя вилка</b></div>
            <div class="moto-metrics">
              <div class="moto-metric"><span class="moto-label">Преднатяг</span><strong class="moto-value">{front_preload}</strong><span class="moto-unit">рис.</span></div>
              <div class="moto-metric"><span class="moto-label">Сжатие</span><strong class="moto-value">{b_p_szh}</strong><span class="moto-unit">щелч.</span></div>
              <div class="moto-metric"><span class="moto-label">Отбой</span><strong class="moto-value">{b_p_otb}</strong><span class="moto-unit">щелч.</span></div>
            </div>
          </section>
          <section class="moto-panel" aria-label="Задний амортизатор">
            <div class="moto-panel-head"><b class="moto-panel-title">Задний амортизатор</b></div>
            <div class="moto-metrics">
              <div class="moto-metric"><span class="moto-label">Преднатяг</span><strong class="moto-value">{b_z_pred}</strong><span class="moto-unit">щелч.</span></div>
              <div class="moto-metric"><span class="moto-label">Отбой</span><strong class="moto-value">{b_z_otb}</strong><span class="moto-unit">щелч.</span></div>
            </div>
          </section>
        </div>
        """, unsafe_allow_html=True)
        if rear_outside_range and not overloaded:
            st.caption("Нагрузка на заднюю подвеску вышла за диапазон расчёта. "
                       "Показаны ближайшие настройки. Проверьте сэг под нагрузкой.")
        with st.expander("Как выставить щелчки"):
            st.markdown("**Вилка:** сжатие — правое перо, отбой — левое. Преднатяг выставляется по рискам на обоих перьях.")
            if FORK_GUIDE_PHOTO.is_file():
                st.image(str(FORK_GUIDE_PHOTO), width=480)
                st.caption("Зелёная стрелка — винт сжатия или отбоя, в зависимости от пера. "
                           "Красная — винт регулировки преднатяга. Синяя — риски преднатяга.")
            st.markdown("**Амортизатор:** отбой — винт снизу. Преднатяг — ручка справа, щелчки по часовой от полностью распущенного положения.")
            st.caption("Для сжатия и отбоя аккуратно закройте регулировку по часовой и отсчитайте щелчки против часовой. "
                       "Первый ощутимый щелчок после упора — позиция 1. К H — сильнее, к S — слабее. "
                       "Для настройки заднего преднатяга разгрузите амортизатор на центральной подставке.")
        if not overloaded and (status == "interpolated" or rear_adjusted):
            with st.expander("Как рассчитаны настройки"):
                if status == "interpolated":
                    st.caption(f"Для {user_weight} кг калькулятор берёт промежуточные значения "
                               f"между настройками для {lower_weight} и {upper_weight} кг.")
                if rear_adjusted:
                    st.caption("Для заднего преднатяга и отбоя используется единая шкала нагрузки. "
                               "Модель относит к задней оси примерно 80% веса пассажира и 90% веса багажа.")

    pressure_title = "Оценка давления"
    pressure_style = " moto-panel-overload" if overloaded else ""
    pressure_load = MAX_PAYLOAD_KG if overloaded else counted_load
    if overloaded:
        pressure_title = "Давление в шинах"
        pressure_caption = f"Справочно по шкале калькулятора при {MAX_PAYLOAD_KG} кг. Уменьшите загрузку до допустимой."
    elif has_passenger:
        pressure_title = "Давление в шинах"
        pressure_caption = "С пассажиром используйте значения Voge ниже."
    elif not load_complete:
        pressure_caption = "Введите вес багажа, чтобы увидеть оценку."
    else:
        pressure_caption = ""
    pressure_content = ""
    if overloaded or (load_complete and not has_passenger):
        front, rear = (f"{value:.2f}".rstrip("0").replace(".", ",")
                       for value in estimated_pressure_by_payload(pressure_load))
        pressure_content = (
            f'<div class="moto-pressure-line" aria-label="Расчётная оценка по весу {pressure_load} кг">'
            f'<div><span class="moto-label">Перед</span><strong class="moto-value">{front}</strong></div>'
            f'<div><span class="moto-label">Зад</span><strong class="moto-value">{rear}</strong></div></div>'
        )
    if pressure_caption:
        caption_style = " moto-load" if overloaded else ""
        pressure_content += f'<div class="moto-panel-meta{caption_style}">{pressure_caption}</div>'
    if not overloaded:
        pressure_content += (
            '<div class="moto-pressure-reference">'
            '<div class="moto-panel-meta">Для накачки по мануалу Voge · перед / зад</div>'
            '<p>Один — 2,2 / 2,5 бар<br>Вдвоём — 2,5 / 2,9 бар</p></div>'
        )
    st.markdown(
        f'<section class="moto-panel{pressure_style}" aria-label="{pressure_title}">'
        f'<div class="moto-panel-head"><b class="moto-panel-title">{pressure_title}</b>'
        '<span class="moto-panel-meta">бар · на холодную</span></div>'
        f'{pressure_content}'
        + (f'<div class="moto-panel-meta moto-load">{load_summary}</div>' if not overloaded else "")
        + '</section>', unsafe_allow_html=True,
    )
    st.caption(f"[Руководство Voge · стр. 4 и 78]({MANUAL_URL})")

    if not overloaded and not has_passenger:
        with st.expander("Как считается оценка"):
            st.caption(f"Линейная шкала по общей загрузке. До {REFERENCE_RIDER_KG} кг — 2,2 / 2,5 бар, "
                       f"при {MAX_PAYLOAD_KG} кг — 2,5 / 2,9 бар. "
                       "Это шкала калькулятора. Давление по Voge указано выше.")
            if has_cases or cargo_weight:
                st.caption("Для соло с багажом отдельного значения в мануале Voge нет.")

    with st.expander("Проверить рабочий сэг", expanded=not overloaded and (
        status == "reference" or result is None or b_z_pred == REAR_PRELOAD_CAP
    )):
        st.markdown(
            '<div class="moto-sag-guide">'
            '<p class="moto-sag-target">Целевое значение СЭГ — <strong>58 мм</strong> спереди '
            'и <strong>60 мм</strong> сзади (около 30% хода).</p>'
            "<p>На ровной площадке замерьте расстояние с полностью вывешенной подвеской, "
            "затем между теми же точками с райдером и выбранной загрузкой. "
            "Сзади меряйте от оси колеса до метки на мотоцикле. Разница двух замеров — рабочий сэг.</p>"
            "<p>Если сэг больше целевого значения, добавьте преднатяг и повторите замер. "
            "Если меньше — уменьшите. На вилке выставляйте одинаковый преднатяг на обоих перьях.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        for axle, target, travel in (("Перед", 58, 194), ("Зад", 60, 198)):
            measured = st.number_input(
                f"{axle} · замер, мм", min_value=0, max_value=travel, value=0, step=1,
                key=f"sag_{axle}_{user_weight}_{loading_mode}",
            )
            if measured:
                difference = measured - target
                st.markdown(
                    f"{measured / travel:.0%} хода · "
                    + (f"**{difference:+d} мм** от целевого значения" if difference else "совпадает с целевым значением")
                )

    st.subheader("Отзывы владельцев")
    review_weights = pd.to_numeric(df_reviews["Вес"].map(number), errors="coerce")
    weight_distance = review_weights.sub(user_weight).abs()
    matching_reviews = df_reviews.assign(_distance=weight_distance)
    matching_reviews = matching_reviews.loc[
        (matching_reviews["Загрузка"] == loading_mode) & (matching_reviews["_distance"] <= 5)
    ].sort_values("_distance", kind="stable")

    if not matching_reviews.empty:
        total_reviews = len(matching_reviews)
        
        context = (user_weight, loading_mode)
        if st.session_state.get("review_context") != context:
            st.session_state.review_context = context
            st.session_state.review_index = 0
        st.session_state.review_index %= total_reviews
        r_row = matching_reviews.iloc[st.session_state.review_index]
        review_name = str(r_row["Имя"])
        review_text = str(r_row["Причина_Текст"])
        review_weight = number(r_row["Вес"])
        likes_count = max(0, int(number(r_row.get("Лайки")) or 0))

        # Apps Script identifies reviews by the exact name and review text.
        liked_reviews = st.session_state.setdefault("liked_reviews", {})
        like_id = (review_name, review_text)
        has_liked = liked_reviews.get(like_id, False)
        btn_text = f"♥ Полезно · {likes_count}" if has_liked else f"♡ Полезно · {likes_count}"
        unique_suffix = f"{user_weight}_{loading_mode}"
        front_sag = sag_text(r_row.get("Перед_Реальный_Сэг_мм"))
        rear_sag = sag_text(r_row.get("Зад_Реальный_Сэг_мм"))
        axle_note = (
            '<div class="moto-review-sag">Замер сэга взят для справки. '
            '1 щелчок сжатия — личная настройка Акселя.</div>'
            if review_name.strip().casefold().replace("ё", "е") == "аксель" else ""
        )

        st.markdown(f"""
        <section class="moto-panel">
            <div class="moto-review-head">
                <strong class="moto-review-name">{html_text(review_name)}</strong>
                <span class="moto-review-count">{st.session_state.review_index + 1} / {total_reviews}</span>
            </div>
            <div class="moto-panel-meta"><strong class="moto-review-context">{review_weight:g} кг · {html_text(loading_mode)}</strong></div>
            <div class="moto-review-rows">
                <div class="moto-review-line">
                    <b>Перед</b>
                    <span>Преднатяг <strong class="moto-review-value">{html_text(r_row['Перед_Преднатяг_Витков'])} рис.</strong>
                    · Сжатие <strong class="moto-review-value">{html_text(r_row['Перед_Сжатие'])}</strong>
                    · Отбой <strong class="moto-review-value">{html_text(r_row['Перед_Отбой'])}</strong></span>
                </div>
                <div class="moto-review-line">
                    <b>Зад</b>
                    <span>Преднатяг <strong class="moto-review-value">{html_text(r_row['Зад_Преднатяг'])} щелч.</strong>
                    · Отбой <strong class="moto-review-value">{html_text(r_row['Зад_Отбой'])}</strong></span>
                </div>
            </div>
            <div class="moto-review-sag">Сэг · перед {front_sag} · зад {rear_sag}</div>
            <div class="moto-review-comment">{review_text_html(r_row["Причина_Текст"])}</div>
            {axle_note}
        </section>
        """, unsafe_allow_html=True)
        with st.container(key="review_navigation"):
            if total_reviews > 1:
                previous_col, next_col, like_col = st.columns([.55, .55, 2])
                if previous_col.button("←", key=f"prev_{unique_suffix}", help="Предыдущий отзыв", use_container_width=True):
                    st.session_state.review_index = (st.session_state.review_index - 1) % total_reviews
                    st.rerun()
                if next_col.button("→", key=f"next_{unique_suffix}", help="Следующий отзыв", use_container_width=True):
                    st.session_state.review_index = (st.session_state.review_index + 1) % total_reviews
                    st.rerun()
            else:
                like_col = st
            if like_col.button(btn_text, key=f"like_{unique_suffix}", use_container_width=True,
                               help="Отменить лайк" if has_liked else "Отметить отзыв как полезный"):
                try:
                    post_review_action({"action": "unlike" if has_liked else "like",
                                        "name": review_name, "review_text": review_text})
                    liked_reviews[like_id] = not has_liked
                    load_all_data.clear()
                    st.rerun()
                except (requests.RequestException, ValueError):
                    st.error("Таблица не подтвердила обновление лайка.")
    else:
        st.caption("Для этой загрузки пока нет отзывов в пределах ±5 кг.")

    # ==================== УМНАЯ ФОРМА ОТПРАВКИ ОТЗЫВА ====================
    if 'show_form' not in st.session_state: st.session_state.show_form = False
    if 'show_success' not in st.session_state: st.session_state.show_success = False

    if st.session_state.show_success:
        st.success("Отзыв опубликован.")
        st.session_state.show_success = False

    form_label = "Закрыть форму" if st.session_state.show_form else "Добавить свой сетап"
    if st.button(form_label, key="toggle_form_btn"):
        st.session_state.show_form = not st.session_state.show_form
        st.rerun()

    if st.session_state.show_form:
        form_key = f"review_{user_weight}_{loading_mode}"
        use_defaults = status in ("table", "interpolated")
        with st.form(key=form_key):
            user_name = st.text_input("Ваш ник или имя")
            st.markdown("**Передняя вилка**")
            u_p_tur = st.number_input("Преднатяг вилки, риски", min_value=0.0,
                                      value=b_p_tur if use_defaults else None,
                                      step=0.25, format="%.2f")
            u_p_szh = st.number_input("Сжатие вилки, щелчки", min_value=0,
                                      value=b_p_szh if use_defaults else None, step=1)
            u_p_otb = st.number_input("Отбой вилки, щелчки", min_value=0,
                                      value=b_p_otb if use_defaults else None, step=1)
            u_p_seg = st.number_input("Измеренный сэг вилки, мм", min_value=1, max_value=194,
                                      value=st.session_state.get(f"sag_Перед_{user_weight}_{loading_mode}"),
                                      step=1)
            st.markdown("**Задний амортизатор**")
            u_z_pred = st.number_input("Преднатяг амортизатора, щелчки", min_value=0,
                                       value=b_z_pred if use_defaults else None, step=1)
            u_z_otb = st.number_input("Отбой амортизатора, щелчки", min_value=0,
                                      value=b_z_otb if use_defaults else None, step=1)
            u_z_seg = st.number_input("Измеренный задний сэг, мм", min_value=1, max_value=198,
                                      value=st.session_state.get(f"sag_Зад_{user_weight}_{loading_mode}"),
                                      step=1)
            st.caption("Если сэг не измеряли, оставьте поля пустыми.")
            user_comment = st.text_area("Почему выбрали эти настройки?")
            if st.form_submit_button("Опубликовать", use_container_width=True):
                if not user_name.strip() or not user_comment.strip():
                    st.error("Заполните имя и причину выбора настроек.")
                elif None in (u_p_tur, u_p_szh, u_p_otb, u_z_pred, u_z_otb):
                    st.error("Укажите все пять фактических регулировок.")
                else:
                    payload = {
                        "name": user_name.strip(), "weight": str(user_weight), "mode": loading_mode,
                        "p_seg": str(u_p_tur), "p_szh": str(u_p_szh), "p_otb": str(u_p_otb),
                        "z_pred": str(u_z_pred), "z_otb": str(u_z_otb),
                        "p_real_seg": str(u_p_seg or 0), "z_seg": str(u_z_seg or 0),
                        "text": user_comment.strip(),
                    }
                    try:
                        post_review_action(payload)
                        load_all_data.clear()
                        st.session_state.show_form = False
                        st.session_state.show_success = True
                        st.rerun()
                    except (requests.RequestException, ValueError):
                        st.error("Таблица не подтвердила публикацию отзыва.")

    st.header("Руководство")
    with st.expander("Заводские настройки Voge"):
        st.markdown(
            "**Передняя вилка:** сжатие — позиция **12** справа, отбой — **8** слева. "
            "Преднатяг — **13 мм** по рисунку Voge, диапазон **4–19 мм**. "
            "Значения в рисках в карточке — клубная шкала. Выставляйте оба пера одинаково."
        )
        st.markdown(
            "**Задний амортизатор, преднатяг / отбой:**  "
            "\n• Соло — **6 / 18**.  "
            "\n• Соло с тремя кофрами — **16 ± 1 / 16 ± 1**.  "
            "\n• Вдвоём с тремя кофрами — **21 ± 1 / 14 ± 1**."
        )
        st.caption("Заводские позиции приведены как ориентир. Таблица приложения даёт "
                   "стартовые настройки по весу. Для заднего преднатяга Voge предписывает "
                   "разгрузить подвеску на центральной подставке.")
        st.markdown(f"[Руководство Voge · стр. 58–59]({MANUAL_URL})")

    st.header("Проблемы и решения")
    st.caption("Начните с давления на холодных шинах по инструкции Voge и сэга под реальной загрузкой. "
               "Запишите исходные настройки. Меняйте одну регулировку за раз, по одному щелчку, "
               "и сравнивайте на том же участке при умеренной скорости.")

    advice = (
        (
            "Раскачивается после одной кочки",
            "Какая часть мотоцикла продолжает качаться после одиночной неровности — вилка или корма?",
            "Добавить отбой именно там. Поверните регулятор к <strong>H</strong> на 1 щелчок: "
            "число в настройке уменьшится, например <strong>15 → 14</strong>.",
        ),
        (
            "Дубеет на серии кочек",
            "Подвеска проседает всё глубже с каждой кочкой и не успевает распрямиться между ними?",
            "Ослабить отбой на проблемной оси. Поверните к <strong>S</strong> на 1 щелчок: "
            "число в настройке увеличится, например <strong>15 → 16</strong>.",
        ),
        (
            "Отдельные стыки бьют в руль",
            "Давление холодной передней шины и сэг вилки. "
            "Если жёсткость нарастает именно на серии кочек, начните с проверки отбоя.",
            "Если вилка жёстко встречает одиночный стык, откройте сжатие "
            "на правом пере на 1 щелчок к <strong>S</strong>, например <strong>12 → 13</strong>.",
        ),
        (
            "Вилка резко клюёт при торможении",
            "Рабочий сэг и запас хода вилки. Если сэг слишком большой, сначала поправьте преднатяг.",
            "При нормальном сэге и слишком быстром уходе вилки вниз "
            "добавьте сжатие на правом пере на 1 щелчок к <strong>H</strong>, например <strong>12 → 11</strong>.",
        ),
        (
            "Корма сильно проседает с пассажиром или кофрами",
            "Массу и размещение багажа. Замерьте задний сэг с пассажиром и кофрами.",
            "Если задний сэг слишком большой, добавьте задний преднатяг и повторите замер. "
            "Если регулятор уже на пределе, уменьшите загрузку или подберите пружину под свой вес.",
        ),
    )
    for symptom, check, action in advice:
        with st.expander(symptom):
            st.markdown(
                '<div class="moto-advice">'
                '<div class="moto-advice-card">'
                f'<strong class="moto-advice-label">Проверьте</strong><p>{check}</p></div>'
                '<div class="moto-advice-card moto-advice-action">'
                f'<strong class="moto-advice-label">Попробуйте</strong><p>{action}</p></div>'
                '</div>',
                unsafe_allow_html=True,
            )
