import streamlit as st
import pandas as pd
import requests
import math
import re
from html import escape

# Настройка страницы (Темная тема и мобильный вид)
st.set_page_config(page_title="Подвеска Voge DS900X", page_icon="🏍️", layout="centered")

# Стилизация интерфейса (Крупные индикаторы цифр, карточки, кастомные цвета)
st.markdown("""
    <style>
    .main { background-color: #121212; color: #FFFFFF; }
    .stApp { background-color: #121212; }
    .block-container { max-width: 44rem; padding: 2.2rem 1rem 2.5rem; }
    .fork-card, .shock-card, .tire-card { color: #F1F5FA; }
    .tire-card { background: #202632; border: 1px solid #455371; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
    .pressure-line { display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap; margin: 7px 0; }
    .pressure-line b { color: #DCE8FF; }
    @media (max-width: 480px) { .block-container { padding-top: 1.6rem; } }
    
    /* Компактные карточки подвески */
    .fork-card { background-color: #1A2332; padding: 14px; border-radius: 10px; border-left: 5px solid #3A86FF; margin-bottom: 12px; }
    .shock-card { background-color: #1A2E26; padding: 14px; border-radius: 10px; border-left: 5px solid #38B000; margin-bottom: 12px; }
    
    /* Уменьшенные шрифты заголовков в карточках */
    .card-title { font-size: 1.15em; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
    
    .user-review { background-color: #1E1E1E; border: 1px solid #2D2D2D; padding: 15px; border-radius: 8px; margin-bottom: 12px; }
    .review-header { color: #888888; font-size: 0.85em; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #2D2D2D; padding-bottom: 5px; }
    .orange-box { background-color: #2D2214; border: 1px solid #FF9F1C; padding: 15px; border-radius: 8px; color: #FF9F1C; margin: 10px 0; }
    .sub-text { font-size: 0.9em; color: #B0B0B0; margin: 2px 0; }
    
    /* Оптимизированные контейнеры цифр для мобилок */
    .value-container { display: flex; align-items: center; justify-content: space-between; margin: 8px 0; min-height: 36px; }
    .value-label { font-size: 0.95em; color: #E0E0E0; padding-right: 10px; line-height: 1.2; }
    .value-badge-blue { background-color: #3A86FF; color: #FFFFFF; font-size: 1.05em; font-weight: bold; padding: 6px 12px; border-radius: 6px; min-width: 80px; text-align: center; white-space: nowrap; }
    .value-badge-green { background-color: #38B000; color: #FFFFFF; font-size: 1.05em; font-weight: bold; padding: 6px 12px; border-radius: 6px; min-width: 80px; text-align: center; white-space: nowrap; }
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


def tire_pressures(mode):
    mode = mode.casefold().replace("ё", "е")
    if "вдвоем" in mode:
        return (("С пассажиром", "2,5", "2,9"),)
    if "кофры" in mode:
        return (("Соло", "2,2", "2,5"), ("С пассажиром", "2,5", "2,9"))
    return (("Соло", "2,2", "2,5"),)


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
    st.title("🏍️ Подвеска Voge DS900X")

    user_weight = st.number_input(
        "Вес райдера в экипировке, кг", min_value=60, max_value=150, value=90, step=1
    )
    modes = df_base["mode"].dropna().unique().tolist()
    if not modes:
        st.error("В таблице клуба нет режимов загрузки.")
        st.stop()
    loading_mode = st.selectbox("Режим загрузки", modes)
    mode_slug = loading_mode.casefold().replace("ё", "е")

    overloaded = False
    if "вдвоем" in mode_slug or "кофры" in mode_slug or user_weight >= 140:
        with st.expander("Проверить полную загрузку"):
            extra_load = st.number_input(
                "Пассажир в экипировке, кофры, багаж и аксессуары вместе, кг",
                min_value=0, max_value=250, value=None, step=1,
            )
            st.caption(f"Допустимая нагрузка по руководству Voge — {MAX_PAYLOAD_KG} кг.")
        if extra_load is not None:
            total_load = user_weight + extra_load
            overloaded = total_load > MAX_PAYLOAD_KG
            if overloaded:
                st.error(f"Полная загрузка {total_load} кг превышает предел Voge на {total_load - MAX_PAYLOAD_KG} кг.")
            else:
                st.caption(f"Полная загрузка {total_load} кг из {MAX_PAYLOAD_KG} кг.")

    result = suspension_setting(df_base, user_weight, loading_mode)
    status = None
    b_notes = ""
    b_p_szh = b_p_otb = b_p_tur = b_z_pred = b_z_otb = None
    if result is None:
        st.info("В таблице клуба пока нет полной строки для этого режима. Запишите свой замер сэга.")
    elif not overloaded:
        values, status, low, high, limited, b_notes = result
        b_p_szh = values["comp_f"]
        b_p_otb = values["reb_f"]
        b_p_tur = values["preload_f"]
        b_z_pred = values["preload_r"]
        b_z_otb = values["reb_r"]
        if status == "table":
            st.subheader("Стартовый сетап клуба")
            st.caption(f"Строка таблицы для {low} кг.")
        elif status == "interpolated":
            st.subheader("Стартовый сетап клуба")
            st.caption(f"Расчёт между строками {low} и {high} кг для выбранной загрузки.")
        else:
            st.subheader("Ближайший сетап в таблице")
            st.info(f"Данных для {user_weight} кг пока нет. Показана справка для {low} кг. "
                    "Для своего веса начните с замера сэга при выбранной загрузке.")
        if limited:
            st.caption("В исходной строке или расчёте задний преднатяг выше 25 щелчков. "
                       "Показано 25 по принятой клубной границе; проверьте положение регулятора и сэг.")

        # Передняя вилка — компактный вид с переносом подсказок
        st.markdown(f"""
        <div class="fork-card">
            <div class="card-title">⚙️ Передняя вилка</div>
            <div class="value-container">
                <span class="value-label">• Преднатяг пружины<br><small style="color: #888888; font-style: italic;">(по рискам)</small></span>
                <span class="value-badge-blue">{b_p_tur:g} рис.</span>
            </div>
            <div class="value-container">
                <span class="value-label">• <i>Гидравлика Сжатия</i><br><small style="color: #888888; font-style: italic;">(от полностью закрученного)</small></span>
                <span class="value-badge-blue">{b_p_szh} щелч.</span>
            </div>
            <div class="value-container">
                <span class="value-label">• <i>Гидравлика Отбоя</i><br><small style="color: #888888; font-style: italic;">(от полностью закрученного)</small></span>
                <span class="value-badge-blue">{b_p_otb} щелч.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Задний амортизатор — компактный вид с переносом подсказок
        st.markdown(f"""
        <div class="shock-card">
            <div class="card-title">⚙️ Задний амортизатор</div>
            <div class="value-container">
                <span class="value-label">• Преднатяг пружины<br><small style="color: #888888; font-style: italic;">(от полностью распущенного)</small></span>
                <span class="value-badge-green">{b_z_pred} щелч.</span>
            </div>
            <div class="value-container">
                <span class="value-label">• <i>Гидравлика Отбоя</i><br><small style="color: #888888; font-style: italic;">(от полностью закрученного)</small></span>
                <span class="value-badge-green">{b_z_otb} щелч.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    if b_notes:
        st.warning(b_notes)

    pressure_rows = "".join(
        f'<div class="pressure-line"><span>{label}</span>'
        f'<b>Перед {front} · Зад {rear} бар</b></div>'
        for label, front, rear in tire_pressures(loading_mode)
    )
    st.markdown(
        f'<div class="tire-card"><div class="card-title">Давление на холодных шинах</div>'
        f'{pressure_rows}</div>', unsafe_allow_html=True,
    )
    if "кофры" in mode_slug:
        st.caption("В руководстве есть две пары давления — соло и с пассажиром. "
                   "Отдельной нормы для кофров нет.")
    st.markdown(f"[Руководство Voge, стр. 78]({MANUAL_URL})")

    with st.expander("Проверить рабочий сэг", expanded=status == "reference" or result is None):
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
        btn_text = f"Отменить лайк ({likes_count})" if has_liked else f"♡ Полезно ({likes_count})"
        unique_suffix = f"{user_weight}_{loading_mode}"
        if st.button(btn_text, key=f"like_{unique_suffix}", use_container_width=True):
            try:
                post_review_action({"action": "unlike" if has_liked else "like",
                                    "name": review_name, "review_text": review_text})
                liked_reviews[like_id] = not has_liked
                load_all_data.clear()
                st.rerun()
            except (requests.RequestException, ValueError):
                st.error("Таблица не подтвердила обновление лайка.")

        # 2. ВТОРОЙ УРОВЕНЬ: КНОПКИ ЛИСТАНИЯ (Создаем две колонки в один ряд)
        col_nav1, col_nav2 = st.columns(2)
        
        # Кнопка НАЗАД рендерится строго в левой колонке
        if col_nav1.button("⬅️ Назад", key=f"btn_prev_{unique_suffix}_{st.session_state.review_index}", use_container_width=True):
            st.session_state.review_index = (st.session_state.review_index - 1) % total_reviews
            st.rerun()
                
        # Кнопка ВПЕРЕД рендерится строго в правой колонке
        if col_nav2.button("Вперед ➡️", key=f"btn_next_{unique_suffix}_{st.session_state.review_index}", use_container_width=True):
            st.session_state.review_index = (st.session_state.review_index + 1) % total_reviews
            st.rerun()

        # 3. ТРЕТИЙ УРОВЕНЬ: САМА КАРТОЧКА ОТЗЫВА
        p_s = sag_text(r_row.get("Перед_Реальный_Сэг_мм"))
        z_s = sag_text(r_row.get("Зад_Реальный_Сэг_мм"))
        axle_note = (
            "<p class='sub-text'>Замер сэга взят для справки. "
            "1 щелчок сжатия — личная настройка Акселя.</p>"
            if review_name.strip().casefold().replace("ё", "е") == "аксель" else ""
        )
        
        st.markdown(f"""
        <div class="user-review" style="margin-top: 15px;">
            <div class="review-header" style="display: flex; justify-content: space-between;">
                <span>🏍️ Райдер: {html_text(review_name)} | {review_weight:g} кг | {html_text(loading_mode)}</span>
                <span style="color: #FF9F1C; font-weight: bold;">Отзыв {st.session_state.review_index + 1} из {total_reviews}</span>
            </div>
            <p class="sub-text" style="line-height: 1.5;">
                <b>⚙️ Передняя вилка:</b>
                <br>• Преднатяг: {html_text(r_row['Перед_Преднатяг_Витков'])} рис.
                <br>• Сжатие: {html_text(r_row['Перед_Сжатие'])} щелч.
                <br>• Отбой: {html_text(r_row['Перед_Отбой'])} щелч.
                <br><span style="color: #888888;">📊 Реальный Сэг переда: {p_s}</span>
                <br><br>
                <b>⚙️ Задний амортизатор:</b>
                <br>• Преднатяг: {html_text(r_row['Зад_Преднатяг'])} щелч.
                <br>• Отбой: {html_text(r_row['Зад_Отбой'])} щелч.
                <br><span style="color: #888888;">📊 Реальный Сэг зада: {z_s}</span>
            </p>
            <p style="margin-top: 12px; font-size: 0.9em; color: #FF9F1C; line-height: 1.3; border-top: 1px solid #2D2D2D; padding-top: 8px;">
                💬 <b>Почему изменил:</b> {review_text_html(r_row["Причина_Текст"])}
            </p>
            {axle_note}
        </div>
        """, unsafe_allow_html=True)
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
    st.header("📖 Руководство: Как правильно крутить?")
    
    with st.expander("🛠️ ИНСТРУКЦИЯ ДЛЯ ПЕРЕДНЕЙ ВИЛКИ"):
        st.markdown("### ⚙️ Регулировка вилки Voge DS900X")
        st.write("🛑 **ПРАВИЛО ОТСЧЕТА ГИДРАВЛИКИ:** Все клики гидравлики (Сжатие и Отбой) считаются **ОТ ПОЛНОСТЬЮ ЗАКРУЧЕННОГО** состояния!")
        st.markdown("""
        1. **Шаг 1:** Аккуратно закрутите винт отверткой по часовой стрелке до упора (в сторону **H - Hard**). *В конце не давите сильно, чтобы не погнуть иглу клапана!*
        2. **Шаг 2:** Отсчитайте против часовой стрелки (в сторону **S - Soft**) нужное количество щелчков из калькулятора.
        """)
        st.write("🌀 **ПРЕДНАТЯГ ВИЛКИ (Риски):** Регулируется большой гайкой под ключ сверху пера.")
        st.write("• Отсчет идет по физическим насечкам (рискам) на гайке регулятора.")

    with st.expander("🛠️ ИНСТРУКЦИЯ ДЛЯ ЗАДНЕГО АМОРТИЗАТОРА"):
        st.markdown("### ⚙️ Регулировка заднего амортизатора")
        st.write("🌀 **ПРЕДНАТЯГ ПРУЖИНЫ (Щелчки):** Регулируется большой выносной пластиковой рукояткой на правом боку мотоцикла.")
        st.write("• Отсчет идет **от полностью распущенного состояния** (крутить против часовой стрелки до упора, когда крутилка станет идти совсем легко).")
        st.write("• Чтобы настроить под вес, крутите рукоятку по часовой стрелке, считая каждый отчетливый щелчок.")
        st.write("🛑 **ОТБОЙ АМОРТИЗАТОРA (Клики):** Регулируется маленьким винтом под шлицевую отвертку в самой нижней части амортизатора (около прогрессии).")
        st.write("• Закрутите винт по часовой стрелке до упора (в сторону **H**).")
        st.write("• Открутите против часовой стрелки (в сторону **S**) на нужное количество кликов из калькулятора.")

        # ==================== БЛОК ДИАГНОСТИКИ ПО ДИНАМИКЕ ====================
    st.header("🛠️ Диагностика поведения (Что крутить, если...)")
    
    with st.expander("❌ Мотоцикл раскачивается как лодка (после кочек или волн на асфальте)"):
        st.error("**Симптом:** Корма или перед долго совершают колебания вверх-вниз, мотоцикл «плывет» в повороте.")
        st.success("**Решение (Слишком мягкий ОТБОЙ):** Подвеске не хватает контроля возврата пружины. Закрутите регулятор **Отбоя (Rebound)** на вилке или заднем амортизаторе по часовой стрелке на 1-2 клика (в сторону **H / Hard**).")

    with st.expander("❌ Мотоцикл слишком жесткий на мелких неровностях"):
        st.error("**Симптом:** Каждый стык, мелкий камушек или трещина на асфальте бьют в руль или по позвоночнику.")
        st.success("**Решение (Слишком жесткое СЖАТИЕ):** Открутите регулятор **Сжатия (Compression)** против часовой стрелки на 1-2 клика (в сторону **S / Soft**).")

    with st.expander("❌ Вилка слишком сильно «клюет» при торможении"):
        st.error("**Симптом:** При нажатии на передний тормоз мотоцикл слишком резко и глубоко проседает вперед.")
        st.success("**Решение (Слишком мягкое СЖАТИЕ спереди):** Закрутите регулятор **Сжатия (Comp)** на передней вилке по часовой стрелке на 2 клика (в сторону **H / Hard**).")

    with st.expander("❌ Мотоцикл плохо держит траекторию (колеса «скачут» в повороте)"):
        st.error("**Симптом:** На неровном асфальте или «стиральной доске» колеса будто теряют зацеп и прыгают.")
        st.success("**Решение (Слишком жесткий ОТБОЙ):** Подвеска зажимается внизу и не успевает возвращаться обратно. Открутите регулятор **Отбоя (Rebound)** на 1-2 клика против часовой стрелки (в сторону **S / Soft**).")

    with st.expander("❌ Морда мотоцикла задирается, руль пустой и легкий на скорости"):
        st.error("**Симптом:** Из-за пассажира или багажа корма сильно просела, разгрузив переднее колесо. Теряется стабильность.")
        st.success("**Решение (Мало преднатяга сзади):** Мотоцикл слишком просел назад. Накрутите черную выносную рукоятку **Преднатяга задней пружины** по часовой стрелке на 2–3 щелчка больше, чтобы вернуть правильную геометрию.")
