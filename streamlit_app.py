import streamlit as st
import pandas as pd
import requests

# Настройка страницы (Темная тема и мобильный вид)
st.set_page_config(page_title="Подвеска Voge DS900X", page_icon="🏍️", layout="centered")

# Стилизация интерфейса (Крупные индикаторы цифр, карточки, кастомные цвета)
st.markdown("""
    <style>
    .main { background-color: #121212; color: #FFFFFF; }
    .stApp { background-color: #121212; }
    
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

@st.cache_data(ttl=15)
def load_all_data():
    try:
        df_b = pd.read_csv(URL_BASE, dtype=str)
        df_b.columns = df_b.columns.str.strip()
        df_b['mode'] = df_b['mode'].astype(str).str.strip()
        
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
    st.caption("Данные синхронизируются с Google Таблицей клуба.")

    # Блок ввода параметров
    st.header("📋 Ваши параметры")
    user_weight = st.number_input("Вес в экипировке, кг", min_value=65, max_value=110, value=90, step=1)
    modes = df_base['mode'].unique().tolist()
    loading_mode = st.selectbox("Режим загрузки", modes)

    rounded_weight = int(round(user_weight / 5.0) * 5)
    rounded_weight = max(70, min(rounded_weight, 105))
    st.info(f"Ближайшая категория в базе: {rounded_weight} кг.")

    # Фильтруем строку из базы данных
    df_base['weight'] = pd.to_numeric(df_base['weight'], errors='coerce').fillna(0).astype(int)
    filtered_df = df_base[(df_base['weight'] == rounded_weight) & (df_base['mode'] == loading_mode)]

    # Извлекаем данные напрямую
    if not filtered_df.empty:
        vals = filtered_df.values.tolist()[0]
        b_p_szh = str(vals[2]).strip()
        b_p_otb = str(vals[3]).strip()
        b_p_tur = str(vals[4]).strip()
        b_z_pred = str(vals[5]).strip()
        b_z_otb = str(vals[6]).strip()
        b_notes = str(vals[7]).strip() if len(vals) > 7 else ""
        
        if b_p_tur.endswith('.0'): b_p_tur = b_p_tur[:-2]
        if b_p_szh.endswith('.0'): b_p_szh = b_p_szh[:-2]
        if b_p_otb.endswith('.0'): b_p_otb = b_p_otb[:-2]
        if b_z_pred.endswith('.0'): b_z_pred = b_z_pred[:-2]
        if b_z_otb.endswith('.0'): b_z_otb = b_z_otb[:-2]
    else:
        b_p_szh, b_p_otb, b_p_tur, b_z_pred, b_z_otb, b_notes = "12", "9", "3", "17", "17", ""

    st.header("🛠️ Рекомендуемые настройки")
    
    # Передняя вилка — компактный вид с переносом подсказок
    st.markdown(f"""
    <div class="fork-card">
        <div class="card-title">⚙️ Передняя вилка</div>
        <div class="value-container">
            <span class="value-label">• Преднатяг пружины<br><small style="color: #888888; font-style: italic;">(по рискам)</small></span>
            <span class="value-badge-blue">{b_p_tur} рис.</span>
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
    
    if b_notes and b_notes != "nan" and b_notes.strip() != "":
        st.warning(f"📝 **Памятка:** {b_notes}")

        # ==================== ВЫВОД ОТЗЫВОВ КЛУБА (КАРУСЕЛЬ С ЛАЙКОМ НАВЕРХУ) ====================
    st.header("👥 Живой опыт других владельцев")
    matching_reviews = df_reviews[(df_reviews['Вес'] == str(rounded_weight)) & (df_reviews['Загрузка'] == loading_mode)]
    
    if not matching_reviews.empty:
        total_reviews = len(matching_reviews)
        
        # Инициализируем индекс текущего отзыва в памяти приложения
        if 'review_index' not in st.session_state:
            st.session_state.review_index = 0
            
        if st.session_state.review_index >= total_reviews:
            st.session_state.review_index = 0

        r_row = matching_reviews.iloc[st.session_state.review_index]
        
        # Считываем количество лайков из 12-го столбца таблицы
        likes_count = r_row.get('Лайки', '0')
        if str(likes_count) == 'nan' or not str(likes_count).isdigit():
            likes_count = '0'

        # Уникальный суффикс для кнопок
        unique_suffix = f"{rounded_weight}_{loading_mode.replace(' ', '_')}"
        like_id = f"liked_{r_row['Имя']}_{unique_suffix}"
        has_liked = st.session_state.get(like_id, False)
        btn_text = f"❤️ Полезно ({likes_count})" if not has_liked else f"💖 Отменить лайк ({likes_count})"

        # 1. ПЕРВЫЙ УРОВЕНЬ: КНОПКА ЛАЙКА НА САМОМ ВЕРХУ (на всю ширину)
        like_btn_key = f"like_btn_{unique_suffix}_{st.session_state.review_index}_{likes_count}"
        if st.button(btn_text, key=like_btn_key, use_container_width=True):
            try:
                if not has_liked:
                    requests.post(WEB_APP_URL, json={"action": "like", "name": str(r_row['Имя']), "review_text": str(r_row['Причина_Текст'])})
                    st.session_state[like_id] = True
                    st.toast(f"Вы круты! Лайк для {r_row['Имя']} учтен 💥")
                else:
                    requests.post(WEB_APP_URL, json={"action": "unlike", "name": str(r_row['Имя']), "review_text": str(r_row['Причина_Текст'])})
                    st.session_state[like_id] = False
                    st.toast(f"Лайк для {r_row['Имя']} успешно отменен ↩️")
                st.cache_data.clear()
                st.rerun()
            except Exception:
                st.error("Ошибка связи с сервером таблицы.")

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
        p_s = r_row['Перед_Реальный_Сэг_мм'] if 'Перед_Реальный_Сэг_мм' in df_reviews.columns else "58"
        z_s = r_row['Зад_Реальный_Сэг_мм'] if 'Зад_Реальный_Сэг_мм' in df_reviews.columns else "60"
        
        st.markdown(f"""
        <div class="user-review" style="margin-top: 15px;">
            <div class="review-header" style="display: flex; justify-content: space-between;">
                <span>🏍️ Райдер: {r_row['Имя']} | {rounded_weight} кг | {loading_mode}</span>
                <span style="color: #FF9F1C; font-weight: bold;">Отзыв {st.session_state.review_index + 1} из {total_reviews}</span>
            </div>
            <p class="sub-text" style="line-height: 1.5;">
                <b>⚙️ Передняя вилка:</b>
                <br>• Преднатяг: {r_row['Перед_Преднатяг_Витков']} рис.
                <br>• Сжатие: {r_row['Перед_Сжатие']} щелч.
                <br>• Отбой: {r_row['Перед_Отбой']} щелч.
                <br><span style="color: #888888;">📊 Реальный Сэг переда: {p_s} мм</span>
                <br><br>
                <b>⚙️ Задний амортизатор:</b>
                <br>• Преднатяг: {r_row['Зад_Преднатяг']} щелч.
                <br>• Отбой: {r_row['Зад_Отбой']} щелч.
                <br><span style="color: #888888;">📊 Реальный Сэг зада: {z_s} мм</span>
            </p>
            <p style="margin-top: 12px; font-size: 0.9em; color: #FF9F1C; line-height: 1.3; border-top: 1px solid #2D2D2D; padding-top: 8px;">
                💬 <b>Почему изменил:</b> {r_row['Причина_Текст']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Альтернативных сетапов для этих параметров пока нет. Станьте первым!")

    # ==================== УМНАЯ ФОРМА ОТПРАВКИ ОТЗЫВА ====================
    if 'show_form' not in st.session_state: st.session_state.show_form = False
    if 'show_success' not in st.session_state: st.session_state.show_success = False

    if st.session_state.show_success:
        st.success("✅ Отзыв успешно опубликован! Сетап мгновенно добавлен в базу.")
        st.session_state.show_success = False

    form_label = "❌ Закрыть форму написания отзыва" if st.session_state.show_form else "✍️ Добавить свой вариант настройки / Предложить изменения"
    if st.button(form_label, key="toggle_form_btn"):
        st.session_state.show_form = not st.session_state.show_form
        st.rerun()

    if st.session_state.show_form:
        with st.container(border=True):
            user_name = st.text_input("Ваш ник в чате / Имя", placeholder="Например: Voge_Rider_77")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**⚙️ Ваша передняя вилка:**")
                u_p_tur = st.number_input("Преднатяг (риски)", value=float(b_p_tur) if b_p_tur.replace('.', '', 1).isdigit() else 3.0, step=0.5, key="up1")
                u_p_szh = st.number_input("Сжатие (щелчки)", value=int(b_p_szh) if b_p_szh.isdigit() else 12, step=1, key="up2")
                u_p_otb = st.number_input("Отбой (щелчки)", value=int(b_p_otb) if b_p_otb.isdigit() else 9, step=1, key="up3")
                u_p_seg = st.number_input("Реальный Сэг переда (мм)", value=58, step=1, key="up4")
            with col2:
                st.markdown("**⚙️ Ваш задний амортизатор:**")
                u_z_pred = st.number_input("Преднатяг (щелчки)", value=int(b_z_pred) if b_z_pred.isdigit() else 17, step=1, key="uz1")
                u_z_otb = st.number_input("Отбой (щелчки)", value=int(b_z_otb) if b_z_otb.isdigit() else 17, step=1, key="uz2")
                u_z_seg = st.number_input("Замеренный Сэг зада (мм)", value=60, step=1, key="uz3")
                
            user_comment = st.text_area("Почему вы выбрали такие настройки?", placeholder="Например: Базовый преднатяг вилки показался мягким...")
            
            if st.button("🚀 Опубликовать сетап в приложении", key="submit_review_btn"):
                if not user_name.strip() or not user_comment.strip():
                    st.error("Заполните ваше имя и причину изменений перед отправкой.")
                else:
                    payload = {
                        "name": str(user_name), "weight": str(rounded_weight), "mode": str(loading_mode),
                        "p_seg": str(u_p_tur), "p_szh": str(u_p_szh), "p_otb": str(u_p_otb),
                        "z_pred": str(u_z_pred), "z_otb": str(u_z_otb), 
                        "p_real_seg": str(u_p_seg), "z_seg": str(u_z_seg),
                        "text": str(user_comment)
                    }
                    try:
                        res = requests.post(WEB_APP_URL, json=payload)
                        if res.status_code == 200:
                            st.cache_data.clear()
                            st.session_state.show_form = False
                            st.session_state.show_success = True
                            st.rerun()
                        else:
                            st.error("Ошибка сервера при отправке.")
                    except Exception:
                        st.error("Не удалось связаться с базой данных.")

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

        with st.expander("🏍️ Шпаргалка: Как изменить поведение мотоцикла?"):
        st.markdown("### 🛠️ Рецепты быстрой настройки подвески")
        
        st.markdown("**Жестко на кочках (бьет в руки/руль)?**")
        st.write("• *Решение:* Открутите (против часовой стрелки в сторону **S**) винт **Сжатия** на передней вилке на 1–2 щелчка. Это сделает вилку мягче при обработке неровностей.")
        
        st.markdown("**Мотоцикл раскачивается как лодка (после прыжка или волны)?**")
        st.write("• *Решение:* Подвеске не хватает контроля возврата пружины. Закрутите (по часовой стрелке в сторону **H**) винты **Отбоя** на передней вилке и снизу заднего амортизатора на 1–2 щелчка.")
        
        st.markdown("**Задняя подвеска пробивает до упора (с пассажиром или багажом)?**")
        st.write("• *Решение:* Не хватает жесткости пружины. Накрутите черную выносную рукоятку **Преднатяга** сжатия задней пружины по часовой стрелке на 3–5 щелчков больше, чем выдает калькулятор.")
        
        st.markdown("**Морда мотоцикла задирается, руль пустой и легкий на скорости?**")
        st.write("• *Решение:* Мотоцикл слишком просел назад. Увеличьте **Преднатяг** задней пружины рукояткой на 2–3 щелчка, либо уменьшите **Преднатяг** передней вилки на 0.5–1 риску, чтобы опустить нос байка.")
        
        st.markdown("**Мотоцикл неохотно заходит в повороты (сопротивляется рулению)?**")
        st.write("• *Решение:* Перед завышен, а зад слишком занижен. Добавьте 2–3 щелчка **Преднатяга** сзади, чтобы приподнять хвост мотоцикла. Геометрия изменится, и байк станет рулиться намного острее.")

    with st.expander("📊 Теория сэга и ходов подвески"):
        st.write("• **Ход передней вилки:** 194 мм &nbsp;|&nbsp; **Ход заднего амортизатора:** 198 мм")
        st.write("• **Целевой рабочий Сэг (SAG):** спереди ~58 мм, сзади ~60 мм. Это 30% от полного хода подвески под нагрузкой.")
