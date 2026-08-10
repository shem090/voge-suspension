import streamlit as st
import pandas as pd
import requests

# Настройка страницы (Темная тема и мобильный вид)
st.set_page_config(page_title="Подвеска Voge DS900X", page_icon="🏍️", layout="centered")

# Стилизация интерфейса под современный Glide
st.markdown("""
    <style>
    .main { background-color: #121212; color: #FFFFFF; }
    .stApp { background-color: #121212; }
    .fork-card { background-color: #1A2332; padding: 15px; border-radius: 10px; border-left: 5px solid #3A86FF; margin-bottom: 15px; }
    .shock-card { background-color: #1A2E26; padding: 15px; border-radius: 10px; border-left: 5px solid #38B000; margin-bottom: 15px; }
    .user-review { background-color: #1E1E1E; border: 1px solid #2D2D2D; padding: 15px; border-radius: 8px; margin-bottom: 12px; }
    .review-header { color: #888888; font-size: 0.85em; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #2D2D2D; padding-bottom: 5px; }
    .orange-box { background-color: #2D2214; border: 1px solid #FF9F1C; padding: 15px; border-radius: 8px; color: #FF9F1C; margin: 10px 0; }
    .sub-text { font-size: 0.9em; color: #B0B0B0; margin: 2px 0; }
    </style>
""", unsafe_allow_html=True)

# Ссылки для чтения листов вашей таблицы
URL_BASE = st.secrets["URL_BASE"]
URL_REVIEWS = st.secrets["URL_REVIEWS"]

# Вставьте сюда вашу ссылку из Apps Script, полученную на Шаге 2
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwgYieaAX5vFI4rTiGGgv7Utng82NPqfKmXEWBwjyE_ji6HLSb_X41LcIUGtqwB-g8/exec"

@st.cache_data(ttl=15) # Уменьшил время кэша до 15 секунд для быстрых тестов
def load_all_data():
    try:
        # Принудительно читаем в кодировке UTF-8 и игнорируем мелкие ошибки строк
        df_b = pd.read_csv(URL_BASE, encoding='utf-8', on_bad_lines='skip')
        df_b.columns = df_b.columns.str.strip()
        df_b['Загрузка'] = df_b['Загрузка'].astype(str).str.strip()
        
        try:
            df_r = pd.read_csv(URL_REVIEWS, encoding='utf-8', on_bad_lines='skip')
            df_r.columns = df_r.columns.str.strip()
            if 'Загрузка' in df_r.columns:
                df_r['Загрузка'] = df_r['Загрузка'].astype(str).str.strip()
        except Exception:
            df_r = pd.DataFrame(columns=['Имя', 'Вес', 'Загрузка', 'Перед_Преднатяг_Витков', 'Перед_Сжатие', 'Перед_Отбой', 'Зад_Преднатяг', 'Зад_Отбой', 'Зад_Реальный_Сэг_мм', 'Причина_Текст'])
            
        return df_b, df_r
    except Exception as e:
        # Если снова будет ошибка, приложение выведет её точный технический текст на экран
        st.error(f"Техническая ошибка: {str(e)}")
        return None, None

df_base, df_reviews = load_all_data()

if df_base is not None:
    st.title("🏍️ Подвеска Voge DS900X")
    st.caption("Данные синхронизируются с Google Таблицей клуба.")

    # Блок ввода параметров
    st.header("📋 Ваши параметры")
    user_weight = st.number_input("Вес в экипировке, кг", min_value=65, max_value=110, value=90, step=1)
    modes = df_base['Загрузка'].unique().tolist()
    loading_mode = st.selectbox("Режим загрузки", modes)

    rounded_weight = int(round(user_weight / 5.0) * 5)
    rounded_weight = max(70, min(rounded_weight, 105))
    st.info(f"Ближайшая категория в базе: {rounded_weight} кг.")

    filtered_df = df_base[(df_base['Вес (кг)'] == rounded_weight) & (df_base['Загрузка'] == loading_mode)]

    b_p_szh, b_p_otb, b_p_tur = 12, 9, 3
    b_z_pred, b_z_otb = 17, 17

    if not filtered_df.empty:
        row = filtered_df.iloc[0]
        b_p_szh, b_p_otb = int(row['Перед: Сжатие']), int(row['Перед: Отбой'])
        b_p_tur = row['Перед: Преднатяг (витков)']
        b_z_pred, b_z_otb = int(row['Зад: Преднатяг']), int(row['Зад: Отбой'])

        st.header("🛠️ Рекомендуемые настройки")
        
        st.markdown(f"""
        <div class="fork-card">
            <h3>⚓ Передняя вилка</h3>
            <p><b>Преднатяг пружины:</b> {b_p_tur} витков/оборотов (от полностью распущенного)</p>
            <p><b>Гидравлика Сжатия:</b> {b_p_szh} кликов (от полностью закрученного)</p>
            <p><b>Гидравлика Отбоя:</b> {b_p_otb} кликов</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="shock-card">
            <h3>🪐 Задний амортизатор</h3>
            <p><b>Преднатяг пружины:</b> {b_z_pred} щелчков рукоятки</p>
            <p><b>Гидравлика Отбоя:</b> {b_z_otb} кликов (от полностью закрученного)</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 'Личные заметки' in df_base.columns and pd.notna(row['Личные заметки']):
            st.warning(f"📝 **Базовая памятка:** {row['Личные заметки']}")

    # ==================== ВЫВОД ОТЗЫВОВ КЛУБА ====================
    st.header("👥 Живой опыт других владельцев")
    
    matching_reviews = df_reviews[(df_reviews['Вес'] == rounded_weight) & (df_reviews['Загрузка'] == loading_mode)]
    
    if not matching_reviews.empty:
        for _, r_row in matching_reviews.iterrows():
            st.markdown(f"""
            <div class="user-review">
                <div class="review-header">🏍️ Райдер: {r_row['Имя']} | Категория: {rounded_weight} кг | {loading_mode}</div>
                <p class="sub-text">🔹 <b>Передняя вилка:</b> Преднатяг: {r_row['Перед_Преднатяг_Витков']} об. , Сжатие: {r_row['Перед_Сжатие']} кл. , Отбой: {r_row['Перед_Отбой']} кл.</p>
                <p class="sub-text">🔹 <b>Задний аморт:</b> Преднатяг: {r_row['Зад_Преднатяг']} кл. , Отбой: {r_row['Зад_Отбой']} кл. &nbsp;|&nbsp; 📊 Реальный Сэг: {r_row['Зад_Реальный_Сэг_мм']} мм</p>
                <p style="margin-top: 8px; color: #FF9F1C;">💬 <b>Почему изменил:</b> {r_row['Причина_Текст']}</p>
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
            u_p_tur = st.number_input("Преднатяг (обороты гайки)", value=float(b_p_tur), step=0.5, key="up1")
            u_p_szh = st.number_input("Сжатие (клики)", value=int(b_p_szh), step=1, key="up2")
            u_p_otb = st.number_input("Отбой (клики)", value=int(b_p_otb), step=1, key="up3")
        with col2:
            st.markdown("**🪐 Ваш задний амортизатор:**")
            u_z_pred = st.number_input("Преднатяг (щелчки)", value=int(b_z_pred), step=1, key="uz1")
            u_z_otb = st.number_input("Отбой (клики)", value=int(b_z_otb), step=1, key="uz2")
            u_z_seg = st.number_input("Замеренный Сэг (мм)", value=60, step=1, key="uz3")
            
        user_comment = st.text_area("Почему вы выбрали такие настройки?", placeholder="Например: Базовый преднатяг вилки показался мягким...")
        
        if st.button("🚀 Опубликовать сетап в приложении"):
            if not user_name.strip() or not user_comment.strip():
                st.error("Заполните ваше имя и причину изменений перед отправкой.")
            elif WEB_APP_URL == "ПОКА_ПУСТО_ЗАМЕНИМ_ПОСЛЕ_РАЗВЕРТЫВАНИЯ":
                st.error("Настройте скрипт отправки в Google Таблицу.")
            else:
                payload = {
                    "name": user_name, "weight": rounded_weight, "mode": loading_mode,
                    "p_seg": float(u_p_tur), "p_szh": int(u_p_szh), "p_otb": int(u_p_otb),
                    "z_pred": int(u_z_pred), "z_otb": int(u_z_otb), "z_seg": int(u_z_seg),
                    "text": user_comment
                }
                try:
                    res = requests.post(WEB_APP_URL, json=payload)
                    if res.status_code == 200:
                        st.success("✅ Отзыв успешно опубликован! Данные сохранены в базу клуба.")
                        st.cache_data.clear()
                    else:
                        st.error("Ошибка сервера при отправке.")
                except Exception:
                    st.error("Не удалось связаться с базой данных.")

    # Раздел стандартных шпаргалок
    st.header("📖 Теория и Шпаргалки")
    with st.expander("📊 Справочные данные ходов подвески Voge DS900X"):
        st.write("• **Ход передней вилки:** 194 мм &nbsp;|&nbsp; **Ход заднего амортизатора:** 198 мм")
        st.write("• **Целевой правильный Сэг (SAG):** спереди ~58 мм, сзади ~60 мм. Это 30% от полного хода.")
