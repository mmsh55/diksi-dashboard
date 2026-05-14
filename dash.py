import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import random

st.set_page_config(layout="wide")
st.title("📊 Дашборд «Индекс привлекательности магазинов Дикси для молодёжи»")

@st.cache_data
def load_data():
    df = pd.read_csv('stores_data.csv')
    color_map = {
        'green': 'зелёный',
        'yellow': 'жёлтый',
        'orange': 'оранжевый',
        'red': 'красный'
    }
    df['color_rus'] = df['color'].map(color_map)
    return df

df = load_data()

# функция для разнообразных рекомендаций
def get_diverse_recommendations(store):
    recs = []
    if store['university']:
        options = [
            "🎓 **Рядом вуз/колледж** → предложите скидку по студенческому билету",
            "🎓 **Рядом вуз** → разместите QR-коды со скидкой в студенческих чатах",
            "🎓 **Рядом вуз** → запустите акцию «Перекус между парами»"
        ]
        recs.append(random.choice(options))
    if store['dormitory']:
        options = [
            "🏠 **Рядом общежитие** → добавьте стойку с зарядками и микроволновку",
            "🏠 **Рядом общежитие** → предложите наборы для студента: лапша + печенье + сок",
            "🏠 **Рядом общежитие** → сделайте полку с товарами «Готовим в общаге»"
        ]
        recs.append(random.choice(options))
    if store['competitor']:
        options = [
            "🏪 **Рядом конкурент** → увеличьте долю снеков и готовой еды",
            "🏪 **Рядом конкурент** → сделайте цену на хлеб и молоко ниже, чем у них",
            "🏪 **Рядом конкурент** → выделите стеллаж «Товары за 50₽»"
        ]
        recs.append(random.choice(options))
    else:
        options = [
            "🏪 **Нет конкурентов рядом** → используйте это в рекламе: «У нас дешевле!»",
            "🏪 **Нет конкурентов** → добавьте табличку «Единственный магазин в районе»"
        ]
        recs.append(random.choice(options))
    if store['cinema']:
        recs.append("🎬 **Рядом кинотеатр** → предложите набор «На попкорн» со скидкой")
    if store['park']:
        recs.append("🌳 **Рядом парк** → предложите набор для пикника, рекламу на входе в парк")
    if store['transport']:
        recs.append("🚌 **Хорошая транспортная доступность** → разместите рекламу на остановках")
    if store['index'] < 50:
        options = [
            "⚠️ **Низкий индекс** → проверьте чистоту и освещение в магазине",
            "⚠️ **Требуется внимание** → обновите ассортимент снеков и напитков"
        ]
        recs.append(random.choice(options))
    if len(recs) < 2:
        recs.append("✅ Добавьте полку с товарами «Студенческий набор»")
    return recs[:4]

# боковая панель
st.sidebar.header("🎛️ Фильтры")
color_order = ['зелёный', 'жёлтый', 'оранжевый', 'красный']
color_filter = st.sidebar.multiselect("Выберите цвет магазина", options=color_order, default=color_order)
filtered_df = df[df['color_rus'].isin(color_filter)]

# легенда
st.sidebar.markdown("""
### 📖 Легенда (индекс от 0 до 100)
- 🟢 **зелёный** (80–100): отлично для молодёжи
- 🟡 **жёлтый** (50–79): есть потенциал
- 🟠 **оранжевый** (30–49): нужны изменения
- 🔴 **красный** (0–29): критично
""")

# ФОРМУЛА ИНДЕКСА (вернули на боковую панель)
st.sidebar.markdown("### ⚙️ Формула индекса")
st.sidebar.info("""
- Вуз/колледж в 500м: **+20**
- Общежитие в 500м: **+15**
- Транспорт (300м): **+10**
- Отсутствие конкурента: **+15**
- Кинотеатр в 500м: **+5**
- Парк/сквер в 500м: **+5**

**Максимум: 70 баллов → нормируется до 100**
""")

# два столбца: карта + карточка
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Карта магазинов")
    if not filtered_df.empty:
        center_lat = filtered_df['lat'].mean()
        center_lon = filtered_df['lon'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
        
        for _, row in filtered_df.iterrows():
            # правильное соответствие цветов для карты
            color_map_folium = {
                'зелёный': 'green',
                'жёлтый': 'yellow',
                'оранжевый': 'orange',
                'красный': 'red'
            }
            folium_color = color_map_folium.get(row['color_rus'], 'gray')
            
            popup_text = f"""
            <b>{row['address']}</b><br>
            Индекс: {row['index']} / 100<br>
            Рейтинг: {row['rating']}<br>
            Цвет: {row['color_rus']}
            """
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=popup_text,
                icon=folium.Icon(color=folium_color, icon='shop', prefix='fa')
            ).add_to(m)
        
        st_folium(m, width=700, height=500)
    else:
        st.warning("Нет магазинов с выбранными фильтрами")

with col2:
    st.subheader("🏪 Карточка магазина")
    if not filtered_df.empty:
        selected_address = st.selectbox("Выберите магазин", filtered_df['address'].tolist())
        store = filtered_df[filtered_df['address'] == selected_address].iloc[0]
        
        if store['index'] >= 80:
            st.success(f"**Индекс:** {store['index']} / 100 🟢")
        elif store['index'] >= 50:
            st.info(f"**Индекс:** {store['index']} / 100 🟡")
        elif store['index'] >= 30:
            st.warning(f"**Индекс:** {store['index']} / 100 🟠")
        else:
            st.error(f"**Индекс:** {store['index']} / 100 🔴")
        
        st.markdown(f"**📍 Адрес:** {store['address']}")
        st.markdown(f"**⭐ Рейтинг:** {store['rating']}")
        
        # ПОЛНАЯ ТАБЛИЦА РАЗБОРА ПО ФАКТОРАМ (вернули)
        st.markdown("### 🔍 Разбор по факторам")
        col_factors1, col_factors2 = st.columns(2)
        with col_factors1:
            st.write(f"🎓 Вуз/колледж: {'✅ да' if store['university'] else '❌ нет'}")
            st.write(f"🏠 Общежитие: {'✅ да' if store['dormitory'] else '❌ нет'}")
            st.write(f"🚌 Транспорт: {'✅ да' if store['transport'] else '❌ нет'}")
        with col_factors2:
            st.write(f"🏪 Конкурент: {'⚠️ да' if store['competitor'] else '✅ нет'}")
            st.write(f"🎬 Кинотеатр: {'✅ да' if store['cinema'] else '❌ нет'}")
            st.write(f"🌳 Парк/сквер: {'✅ да' if store['park'] else '❌ нет'}")
        
        st.markdown("### 💡 Рекомендации")
        for rec in get_diverse_recommendations(store):
            st.write(f"- {rec}")
    else:
        st.warning("Нет магазинов для отображения")

# сводная аналитика
st.header("📈 Сводная аналитика")

col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 Распределение по цветам")
    if not filtered_df.empty:
        color_counts = filtered_df['color_rus'].value_counts()
        color_counts = color_counts.reindex(color_order, fill_value=0)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(color_counts.index, color_counts.values,
                      color=['green', 'gold', 'orange', 'red'])
        ax.set_xlabel("Цветовая категория")
        ax.set_ylabel("Количество магазинов")
        ax.set_title("Сколько магазинов в каждой категории")
        for bar, val in zip(bars, color_counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(val), ha='center', va='bottom')
        st.pyplot(fig)
    else:
        st.info("Нет данных")

with col4:
    st.subheader("🏆 Топ-5 лучших магазинов")
    if not filtered_df.empty:
        st.dataframe(filtered_df.nlargest(5, 'index')[['address', 'index', 'rating', 'color_rus']])
    else:
        st.info("Нет данных")
    
    st.subheader("📉 Топ-5 худших магазинов")
    if not filtered_df.empty:
        st.dataframe(filtered_df.nsmallest(5, 'index')[['address', 'index', 'rating', 'color_rus']])
    else:
        st.info("Нет данных")
