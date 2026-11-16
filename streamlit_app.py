import streamlit as st
import pandas as pd
import requests
import math
import re
from html import escape

# Настройка страницы (Темная тема и мобильный вид)
st.set_page_config(page_title="Подвеска Voge DS900X", page_icon="🏍️", layout="centered")

st.markdown("""
<style>
.stApp {
    --moto-bg: #13171c;
    --moto-card: #1b2027;
    --moto-line: #353d47;
    --moto-text: #f0f2f5;
    --moto-muted: #b0bac6;
    --moto-accent: #ffd27f;
    background: var(--moto-bg);
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
.moto-panel { padding: .85rem .9rem; border: 1px solid var(--moto-line); border-radius: .85rem; background: var(--moto-card); }
.moto-panel-head { display: flex; justify-content: space-between; align-items: baseline; gap: .65rem; margin-bottom: .7rem; }
.moto-panel-title { font-size: .94rem; font-weight: 700; line-height: 1.2; }
.moto-panel-meta { color: var(--moto-muted); font-size: .73rem; line-height: 1.25; }
.moto-setup-grid { display: grid; grid-template-columns: 1.25fr 1fr; gap: .55rem; padding-bottom: .625rem; }
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
.moto-pressure-reference { margin-top: .65rem; padding-top: .6rem; border-top: 1px solid var(--moto-line); }
.moto-pressure-reference p { margin: .25rem 0 0; font-size: .85rem; }
.moto-load { border-top: 1px solid var(--moto-line); padding-top: .6rem; margin-top: .65rem; }
.moto-review-head { display: flex; justify-content: space-between; align-items: baseline; gap: .75rem; }
.moto-review-name { font-size: .98rem; font-weight: 700; overflow-wrap: anywhere; min-width: 0; }
.moto-review-count { color: var(--moto-accent); font-size: .76rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
.moto-review-rows { display: grid; gap: .45rem; margin-top: .65rem; }
.moto-review-line { display: grid; grid-template-columns: minmax(3.1rem, .6fr) 2fr; gap: .45rem; border-top: 1px solid var(--moto-line); padding-top: .45rem; }
.moto-review-line span, .moto-review-sag { font-size: .77rem; color: var(--moto-muted); }
.moto-review-sag { margin-top: .4rem; }
.moto-review-comment { line-height: 1.45; border-top: 1px solid var(--moto-line); margin-top: .6rem; padding-top: .55rem; overflow-wrap: anywhere; }
.stApp [data-testid="stExpander"] details { border-color: var(--moto-line); border-radius: .7rem; }
.stApp [data-testid="stExpander"] summary { min-height: 2.55rem; }
.stApp [data-baseweb="input"], .stApp [data-baseweb="select"] > div, .stApp [data-baseweb="textarea"] {
    background: var(--moto-card); border-color: var(--moto-line); color: var(--moto-text);
}
.stApp :is(input, textarea, [data-baseweb="select"] button) { color: var(--moto-text); }
.stApp [data-baseweb="select"] :is(span, svg) { color: var(--moto-text); fill: currentColor; }
.stApp [data-testid="stNumberInput"] button { color: var(--moto-text); background: var(--moto-card); }
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
REFERENCE_RIDER_KG = 75
REFERENCE_PASSENGER_KG = 55
REFERENCE_CARGO_KG = 25


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
        settings[column] = round(float(value), 2) if column == "preload_f" else math.floor(value + 0.5)

    limited = settings["preload_r"] > REAR_PRELOAD_CAP
    settings["preload_r"] = min(settings["preload_r"], REAR_PRELOAD_CAP)
    notes = left.get("notes", "") if status == "table" else ""
    if pd.isna(notes):
        notes = ""
    return settings, status, int(left["weight"]), int(right["weight"]), limited, str(notes).strip()


def rear_lookup_weight(rider_weight, passenger_weight, cargo_weight, has_passenger, has_cases):
    # Режим таблицы уже учитывает опорную загрузку. Пересчитываем только разницу.
    reference_passenger = REFERENCE_PASSENGER_KG if has_passenger else 0
    reference_cargo = REFERENCE_CARGO_KG if has_cases else 0
    passenger_delta = 0 if passenger_weight is None else passenger_weight - reference_passenger
    cargo_delta = 0 if cargo_weight is None else cargo_weight - reference_cargo
    return rider_weight + passenger_delta * (0.8 / 0.6) + cargo_delta * (0.9 / 0.6)


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
            "Райдер, кг", min_value=60, max_value=150, value=90, step=1,
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
            min_value=0, max_value=250, value=None if has_cases else 0, step=1,
            key=f"cargo_weight_{loading_mode}",
        )
        st.caption(f"Допустимая нагрузка мотоцикла по руководству Voge — {MAX_PAYLOAD_KG} кг.")
    counted_load = user_weight + (passenger_weight or 0) + (cargo_weight or 0)
    load_complete = passenger_weight is not None and cargo_weight is not None
    load_remaining = MAX_PAYLOAD_KG - counted_load
    overloaded = load_remaining < 0
    if overloaded:
        st.error(f"Введённая нагрузка {counted_load} кг превышает предел Voge на {-load_remaining} кг. "
                 "Уменьшите загрузку.")

    result = suspension_setting(df_base, user_weight, loading_mode)
    status = None
    b_notes = ""
    b_p_szh = b_p_otb = b_p_tur = b_z_pred = b_z_otb = None
    if result is None:
        st.info("В таблице клуба пока нет полной строки для этого режима. Запишите свой замер сэга.")
    elif not overloaded:
        values, status, low, high, _, b_notes = result
        b_p_szh = values["comp_f"]
        b_p_otb = values["reb_f"]
        b_p_tur = values["preload_f"]
        b_z_pred = values["preload_r"]
        b_z_otb = values["reb_r"]
        rear_weight = rear_lookup_weight(user_weight, passenger_weight, cargo_weight,
                                         has_passenger, has_cases)
        if rear_weight != user_weight:
            rear_result = suspension_setting(df_base, rear_weight, loading_mode)
            if rear_result is not None:
                rear_values = rear_result[0]
                b_z_pred, b_z_otb = rear_values["preload_r"], rear_values["reb_r"]
                b_notes = ""
        if status == "table":
            st.subheader("Стартовые настройки")
        elif status == "interpolated":
            st.subheader("Стартовые настройки")
            st.caption(f"Расчёт между точками {low} и {high} кг.")
        else:
            st.subheader("Ближайшие настройки")
            st.info(f"Для {user_weight} кг показана ближайшая точка {low} кг. Проверьте сэг под нагрузкой.")
        if b_z_pred >= REAR_PRELOAD_CAP:
            st.warning(f"Задний преднатяг достиг принятой границы {REAR_PRELOAD_CAP} щелчков. "
                       "Проверьте сэг с выбранной загрузкой и предел регулятора на своём мотоцикле.")

        front_preload = f"{b_p_tur:g}".replace(".", ",")
        st.markdown(f"""
        <div class="moto-setup-grid">
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
        if rear_weight != user_weight:
            st.caption("Задние настройки учитывают введённую загрузку. "
                       f"Опорные массы режима: пассажир {REFERENCE_PASSENGER_KG if has_passenger else 0} кг, "
                       f"багаж с кофрами {REFERENCE_CARGO_KG if has_cases else 0} кг.")
        with st.expander("Как выставить щелчки"):
            st.markdown("**Вилка:** сжатие — правое перо, отбой — левое. Преднатяг выставляется по рискам на обоих перьях.")
            st.markdown("**Амортизатор:** отбой — винт снизу. Преднатяг — ручка справа, щелчки по часовой от полностью распущенного положения.")
            st.caption("Для сжатия и отбоя аккуратно закройте регулировку по часовой и отсчитайте щелчки против часовой. "
                       "К H — сильнее, к S — слабее. Проверьте сэг под нагрузкой и меняйте по одному щелчку за раз.")
            if b_notes:
                st.caption(b_notes)

    pressure_title = "Оценка давления"
    pressure_content = ""
    load_summary = ""
    if overloaded:
        pressure_title = "Давление в шинах"
        pressure_content = '<div class="moto-panel-meta">Уменьшите загрузку до допустимой.</div>'
    else:
        if has_passenger:
            pressure_title = "Давление в шинах"
            pressure_content = '<div class="moto-panel-meta">С пассажиром используйте значения Voge ниже.</div>'
        elif load_complete:
            front, rear = (f"{value:.2f}".rstrip("0").replace(".", ",")
                           for value in estimated_pressure_by_payload(counted_load))
            pressure_content = (
                f'<div class="moto-pressure-line" aria-label="Расчётная оценка по весу {counted_load} кг">'
                f'<div><span class="moto-label">Перед</span><strong class="moto-value">{front}</strong></div>'
                f'<div><span class="moto-label">Зад</span><strong class="moto-value">{rear}</strong></div></div>'
            )
        else:
            pressure_content = '<div class="moto-panel-meta">Введите вес багажа, чтобы увидеть оценку.</div>'
        if load_complete:
            load_summary = f"Загрузка {counted_load} / {MAX_PAYLOAD_KG} кг · запас {load_remaining} кг"
        else:
            load_summary = f"Учтено {counted_load} кг · заполните оставшиеся поля загрузки"
        pressure_content += (
            '<div class="moto-pressure-reference">'
            '<div class="moto-panel-meta">Для накачки по мануалу Voge · перед / зад</div>'
            '<p>Один — 2,2 / 2,5 бар<br>Вдвоём — 2,5 / 2,9 бар</p></div>'
        )
    st.markdown(
        f'<section class="moto-panel" aria-label="{pressure_title}">'
        f'<div class="moto-panel-head"><b class="moto-panel-title">{pressure_title}</b>'
        '<span class="moto-panel-meta">бар · на холодную</span></div>'
        f'{pressure_content}'
        + (f'<div class="moto-panel-meta moto-load">{load_summary}</div>' if load_summary else "")
        + '</section>', unsafe_allow_html=True,
    )
    st.caption(f"[Руководство Voge · стр. 4 и 78]({MANUAL_URL})")

    if not overloaded and not has_passenger:
        with st.expander("Как считается оценка"):
            st.caption(f"Линейная шкала по общей загрузке. До {REFERENCE_RIDER_KG} кг — 2,2 / 2,5 бар, "
                       f"при {MAX_PAYLOAD_KG} кг — 2,5 / 2,9 бар. "
                       "Весовые точки выбраны для калькулятора. Voge указывает давление по режимам поездки.")
            if has_cases or cargo_weight:
                st.caption("Для соло с багажом отдельного значения в мануале Voge нет.")

    with st.expander("Проверить рабочий сэг", expanded=(status == "reference" or result is None
                                                        or b_z_pred == REAR_PRELOAD_CAP)):
        st.caption("Ориентир клуба — 58 мм спереди и 60 мм сзади, около 30% хода. "
                   "Сэг — разница между полностью разгруженной подвеской и положением "
                   "мотоцикла с райдером и выбранной загрузкой.")
        st.caption("Если сэг больше ориентира, добавьте преднатяг и повторите замер. "
                   "Если меньше — уменьшите. На вилке выставляйте одинаковый преднатяг на обоих перьях.")
        for axle, target, travel in (("Перед", 58, 194), ("Зад", 60, 198)):
            measured = st.number_input(
                f"{axle} · замер, мм", min_value=1, max_value=travel, value=None, step=1,
                key=f"sag_{axle}_{user_weight}_{loading_mode}",
            )
            if measured is not None:
                difference = measured - target
                st.caption(f"{measured / travel:.0%} хода · "
                           + (f"{difference:+d} мм от ориентира" if difference else "совпадает с ориентиром"))

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
            <div class="moto-panel-meta">{review_weight:g} кг · {html_text(loading_mode)}</div>
            <div class="moto-review-rows">
                <div class="moto-review-line"><b>Перед</b><span>Преднатяг {html_text(r_row['Перед_Преднатяг_Витков'])} рис. · Сжатие {html_text(r_row['Перед_Сжатие'])} · Отбой {html_text(r_row['Перед_Отбой'])}</span></div>
                <div class="moto-review-line"><b>Зад</b><span>Преднатяг {html_text(r_row['Зад_Преднатяг'])} щелч. · Отбой {html_text(r_row['Зад_Отбой'])}</span></div>
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

    # Раздел стандартных шпаргалок и руководств
    st.header("Руководство")
    
    with st.expander("Передняя вилка"):
        st.markdown("### ⚙️ Регулировка вилки Voge DS900X")
        st.write("🛑 **ПРАВИЛО ОТСЧЕТА ГИДРАВЛИКИ:** Все клики гидравлики (Сжатие и Отбой) считаются **ОТ ПОЛНОСТЬЮ ЗАКРУЧЕННОГО** состояния!")
        st.markdown("""
        1. **Шаг 1:** Аккуратно закрутите винт отверткой по часовой стрелке до упора (в сторону **H - Hard**). *В конце не давите сильно, чтобы не погнуть иглу клапана!*
        2. **Шаг 2:** Отсчитайте против часовой стрелки (в сторону **S - Soft**) нужное количество щелчков из калькулятора.
        """)
        st.write("🌀 **ПРЕДНАТЯГ ВИЛКИ (Риски):** Регулируется большой гайкой под ключ сверху пера.")
        st.write("• Отсчет идет по физическим насечкам (рискам) на гайке регулятора.")

    with st.expander("Задний амортизатор"):
        st.markdown("### ⚙️ Регулировка заднего амортизатора")
        st.write("🌀 **ПРЕДНАТЯГ ПРУЖИНЫ (Щелчки):** Регулируется большой выносной пластиковой рукояткой на правом боку мотоцикла.")
        st.write("• Отсчет идет **от полностью распущенного состояния** (крутить против часовой стрелки до упора, когда крутилка станет идти совсем легко).")
        st.write("• Чтобы настроить под вес, крутите рукоятку по часовой стрелке, считая каждый отчетливый щелчок.")
        st.write("🛑 **ОТБОЙ АМОРТИЗАТОРA (Клики):** Регулируется маленьким винтом под шлицевую отвертку в самой нижней части амортизатора (около прогрессии).")
        st.write("• Закрутите винт по часовой стрелке до упора (в сторону **H**).")
        st.write("• Открутите против часовой стрелки (в сторону **S**) на нужное количество кликов из калькулятора.")

        # ==================== БЛОК ДИАГНОСТИКИ ПО ДИНАМИКЕ ====================
    st.header("Диагностика на дороге")
    
    with st.expander("Раскачка после кочек"):
        st.error("**Симптом:** Корма или перед долго совершают колебания вверх-вниз, мотоцикл «плывет» в повороте.")
        st.success("**Решение (Слишком мягкий ОТБОЙ):** Подвеске не хватает контроля возврата пружины. Закрутите регулятор **Отбоя (Rebound)** на вилке или заднем амортизаторе по часовой стрелке на 1-2 клика (в сторону **H / Hard**).")

    with st.expander("Жёсткость на мелких неровностях"):
        st.error("**Симптом:** Каждый стык, мелкий камушек или трещина на асфальте бьют в руль или по позвоночнику.")
        st.success("**Решение (Слишком жесткое СЖАТИЕ):** Открутите регулятор **Сжатия (Compression)** против часовой стрелки на 1-2 клика (в сторону **S / Soft**).")

    with st.expander("Клевок при торможении"):
        st.error("**Симптом:** При нажатии на передний тормоз мотоцикл слишком резко и глубоко проседает вперед.")
        st.success("**Решение (Слишком мягкое СЖАТИЕ спереди):** Закрутите регулятор **Сжатия (Comp)** на передней вилке по часовой стрелке на 2 клика (в сторону **H / Hard**).")

    with st.expander("Колёса скачут в повороте"):
        st.error("**Симптом:** На неровном асфальте или «стиральной доске» колеса будто теряют зацеп и прыгают.")
        st.success("**Решение (Слишком жесткий ОТБОЙ):** Подвеска зажимается внизу и не успевает возвращаться обратно. Открутите регулятор **Отбоя (Rebound)** на 1-2 клика против часовой стрелки (в сторону **S / Soft**).")

    with st.expander("Переднее колесо разгружено"):
        st.error("**Симптом:** Из-за пассажира или багажа корма сильно просела, разгрузив переднее колесо. Теряется стабильность.")
        st.success("**Решение (Мало преднатяга сзади):** Мотоцикл слишком просел назад. Накрутите черную выносную рукоятку **Преднатяга задней пружины** по часовой стрелке на 2–3 щелчка больше, чтобы вернуть правильную геометрию.")
