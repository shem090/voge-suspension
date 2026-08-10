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
    .fork-card { background-color: #1A2332; padding: 20px; border-radius: 12px; border-left: 5px solid #3A86FF; margin-bottom: 20px; }
    .shock-card { background-color: #1A2E26; padding: 20px; border-radius: 12px; border-left: 5px solid #38B000; margin-bottom: 20px; }
    .user-review { background-color: #1E1E1E; border: 1px solid #2D2D2D; padding: 15px; border-radius: 8px; margin-bottom: 12px; }
    .review-header { color: #888888; font-size: 0.85em; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #2D2D2D; padding-bottom: 5px; }
    .orange-box { background-color: #2D2214; border: 1px solid #FF9F1C; padding: 15px; border-radius: 8px; color: #FF9F1C; margin: 10px 0; }
    .sub-text { font-size: 0.9em; color: #B0B0B0; margin: 2px 0; }
    
    /* Стили для новых информативных блоков цифр */
    .value-container { display: flex; align-items: center; margin: 12px 0; }
    .value-label { flex-grow: 1; font-size: 1.1em; color: #E0E0E0; }
    .value-badge-blue { background-color: #3A86FF; color: #FFFFFF; font-size: 1.2em; font-weight: bold; padding: 4px 14px; border-radius: 6px; min-width: 90px; text-align: center; }
    .value-badge-green { background-color: #38B000; color: #FFFFFF; font-size: 1.2em; font-weight: bold; padding: 4px 14px; border-radius: 6px; min-width: 90px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Ссылки из Секретов Streamlit
URL_BASE = st.secrets["URL_BASE"]
URL_REVIEWS = st.secrets["URL_REVIEWS"]

# Вставьте сюда вашу сохраненную ссылку из Apps Script
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwqvbMw4s9OdMgdnNZUJNl8oVKvLIYijh65FzU-5DGkTAHjVNPYkTYV5_oYtHF6Rhmq/exec"

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
            df_r = pd.DataFrame(columns=['Имя', 'Вес', 'Загрузка', 'Перед_Преднатяг_Витков', 'Перед_Сжатие', 'Перед_Отбой', 'Зад_Преднатяг', 'Зад_Отбой', 'Перед_Реальный_Сэг_мм', 'Зад_Реальный_Сэг_мм', 'Причина_Текст'])
            
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
    
    # Передняя вилка с новыми блоками вывода цифр
    st.markdown(f"""
    <div class="fork-card">
        <h3>⚙️ Передняя вилка</h3>
        <div class="value-container">
            <span class="value-label">🔹 Преднатяг пружины (по рискам)</span>
            <span class="value-badge-blue">{b_p_tur} рис.</span>
        </div>
        <div class="value-container">
            <span class="value-label">🔹 Гидравлика Сжатия (от полностью закрученного)</span>
            <span class="value-badge-blue">{b_p_szh} щелч.</span>
        </div>
        <div class="value-container">
            <span class="value-label">🔹 Гидравлика Отбоя (от полностью закрученного)</span>
            <span class="value-badge-blue">{b_p_otb} щелч.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Задний амортизатор с новыми блоками вывода цифр
    st.markdown(f"""
    <div class="shock-card">
        <h3>⚙️ Задний амортизатор</h3>
        <div class="value-container">
            <span class="value-label">🔹 Преднатяг пружины (от полностью открученного)</span>
            <span class="value-badge-green">{b_z_pred} щелч.</span>
        </div>
        <div class="value-container">
            <span class="value-label">🔹 Гидравлика Отбоя (от полностью закрученного)</span>
            <span class="value-badge-green">{b_z_otb} щелч.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if b_notes and b_notes != "nan" and b_notes.strip() != "":
        st.warning(f"📝 **Базовая памятка:** {b_notes}")

        # ==================== ВЫВОД ОТЗЫВОВ КЛУБА ====================
    st.header("👥 Живой опыт других владельцев")
    matching_reviews = df_reviews[(df_reviews['Вес'] == str(rounded_weight)) & (df_reviews['Загрузка'] == loading_mode)]
    
    if not matching_reviews.empty:
        for _, r_row in matching_reviews.iterrows():
            # Защита от сдвигов: проверяем наличие колонок сэга
            p_s = r_row['Перед_Реальный_Сэг_мм'] if 'Перед_Реальный_Сэг_мм' in df_reviews.columns else "58"
            z_s = r_row['Зад_Реальный_Сэг_мм'] if 'Зад_Реальный_Сэг_мм' in df_reviews.columns else "60"
            
            st.markdown(f"""
            <div class="user-review">
                <div class="review-header">🏍️ Райдер: {r_row['Имя']} | {rounded_weight} кг | {loading_mode}</div>
                <p class="sub-text">
                    <b>⚓ Вилка:</b> Пр: {r_row['Перед_Преднатяг_Витков']} рис. | Сж: {r_row['Перед_Сжатие']} щелч. | Отб: {r_row['Перед_Отбой']} щелч. <span style="color: #888888;">(Сэг: {p_s} мм)</span>
                    <br>
                    <b>🪐 Аморт:</b> Пр: {r_row['Зад_Преднатяг']} щелч. | Отб: {r_row['Зад_Отбой']} щелч. <span style="color: #888888;">(Сэг: {z_s} мм)</span>
                </p>
                <p style="margin-top: 8px; font-size: 0.9em; color: #FF9F1C; line-height: 1.3;">
                    💬 <b>Почему изменил:</b> {r_row['Причина_Текст']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Альтернативных сетапов для этих параметров пока нет. Станьте первым!")

    # ==================== УМНАЯ ФОРМА ОТПРАВКИ ОТЗЫВА ====================
    with st.expander("✍️ Добавить свой вариант настройки / Предложить изменения"):
        user_name = st.text_input("Ваш ник в чате / Имя", placeholder="Например: Voge_Rider_77")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**⚓ Ваша передняя вилка:**")
            u_p_tur = st.number_input("Преднатяг (риски)", value=float(b_p_tur) if b_p_tur.replace('.', '', 1).isdigit() else 3.0, step=0.5, key="up1")
            u_p_szh = st.number_input("Сжатие (щелчки)", value=int(b_p_szh) if b_p_szh.isdigit() else 12, step=1, key="up2")
            u_p_otb = st.number_input("Отбой (щелчки)", value=int(b_p_otb) if b_p_otb.isdigit() else 9, step=1, key="up3")
            u_p_seg = st.number_input("Реальный Сэг переда (мм)", value=58, step=1, key="up4")
        with col2:
            st.markdown("**🪐 Ваш задний амортизатор:**")
            u_z_pred = st.number_input("Преднатяг (щелчки)", value=int(b_z_pred) if b_z_pred.isdigit() else 17, step=1, key="uz1")
            u_z_otb = st.number_input("Отбой (щелчки)", value=int(b_z_otb) if b_z_otb.isdigit() else 17, step=1, key="uz2")
            u_z_seg = st.number_input("Замеренный Сэг зада (мм)", value=60, step=1, key="uz3")
            
        user_comment = st.text_area("Почему вы выбрали такие настройки?", placeholder="Например: Базовый преднатяг вилки показался мягким...")
        
        if st.button("🚀 Опубликовать сетап в приложении"):
            if not user_name.strip() or not user_comment.strip():
                st.error("Заполните ваше имя и причину изменений перед отправкой.")
            elif WEB_APP_URL == "СЮДА_ВСТАВЬТЕ_ВАШУ_ССЫЛКУ_ИЗ_APPS_SCRIPT":
                st.error("Настройте скрипт отправки в Google Таблицу.")
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
                        st.success("✅ Отзыв успешно опубликован! Сетап мгновенно добавлен в базу.")
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

    with st.expander("📊 Теория сэга и ходов подвески"):
        st.write("• **Ход передней вилки:** 194 мм &nbsp;|&nbsp; **Ход заднего амортизатора:** 198 мм")
        st.write("• **Целевой рабочий Сэг (SAG):** спереди ~58 мм, сзади ~60 мм. Это 30% от полного хода подвески под нагрузкой.")
