import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import load_data,get_stat_monthly,get_lookup,get_users_agg_by_monthnum,get_page5_user_milestone_counts,add_year_columns

tab1,tab2 = st.tabs(['Хэрэглэгчдийн Онооны Тархалт', '1000 Хүрсэн Хэрэглэгчдийн Онооны Тархалт'])    

@st.cache_data(show_spinner=False)
def load_base():
    return load_data(), get_lookup()

df, loyal_code_to_desc = load_base()
df = add_year_columns(df)

available_years = sorted(df["year"].unique())

selected_year = st.sidebar.selectbox(
    "Жил сонгох",
    available_years,
    index=len(available_years) - 1
)
df_year = df[df["year"] == selected_year].copy()
user_level_stat_monthly, monthly_reward_stat = get_stat_monthly(df_year)
users_agg_df = get_users_agg_by_monthnum(df_year)

reach_frequency = get_page5_user_milestone_counts(users_agg_df)

st.sidebar.caption(f"Одоогийн сонголт: {selected_year}")

bucket_order = [
    '0-49','50-99','100-199','200-299','300-399',
    '400-499','500-599','600-699','700-799',
    '800-899','900-999','1000+'
]

with tab1:
    # ------------------------------------------------------------------
    # Prepare data
    # ------------------------------------------------------------------
    user_level_stat_monthly = user_level_stat_monthly.sort_values("year_month")

    counts = (
        user_level_stat_monthly
        .groupby(["year_month", "point_bucket"], observed=True)
        .size()
        .reset_index(name="Counts")
    )

    counts["Percent"] = (
        counts["Counts"]
        / counts.groupby("year_month")["Counts"].transform("sum")
        * 100
    )

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------
    fig = px.bar(
        counts,
        x="Counts",
        y="point_bucket",
        orientation="h",
        animation_frame="year_month",
        animation_group="point_bucket", 
        #color="Counts",
        #color_continuous_scale="Blues",
        category_orders={"point_bucket": bucket_order},
        template="plotly_white",
    )
    fig.update_traces(
        #texttemplate="%{customdata:.1f}%",
        customdata=counts["Percent"],
        #textposition="outside",
        marker_line_width=1,
        marker_line_color="white",
        opacity=0.9,
        hovertemplate=(
            "Онооны ангилал: %{y}<br>"
            "Хэрэглэгчдийн тоо: %{x}<br>"
            "Хувь: %{customdata:.1f}%"
            "<extra></extra>"
        ),
    )
    fig.update_layout(
        bargap=0.05,
        xaxis_title="<b>Хэрэглэгчдийн тоо</b>",
        yaxis_title="<b>Онооны ангилал</b>",
        height = 500,
        title=dict(
            text="<b>Хэрэглэгчдийн Онооны Тархалт (Сараар)</b>",
            x=0.5,
            y=0.95,
            xanchor="center",
            yanchor="top",
            font=dict(size=24),
        ),
        xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),
    )
    fig.update_xaxes(showgrid=True)

    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 300

    st.plotly_chart(fig, use_container_width=True)


    transaction_bar_plot_df = df.groupby('LOYAL_CODE').agg({
        'TXN_AMOUNT': 'sum',
        'JRNO': 'count'
    })
    transaction_bar_plot_df['AVG'] = (transaction_bar_plot_df['TXN_AMOUNT'] / transaction_bar_plot_df['JRNO']).round(2)
    transaction_bar_plot_df['PERCENTAGE'] =(( transaction_bar_plot_df['TXN_AMOUNT']/transaction_bar_plot_df['TXN_AMOUNT'].sum() )* 100).round(2)
    transaction_bar_plot_df = transaction_bar_plot_df[transaction_bar_plot_df['PERCENTAGE']>2].reset_index()
    transaction_bar_plot_df = transaction_bar_plot_df.sort_values(by='AVG')
    transaction_bar_plot_df['DESC'] = transaction_bar_plot_df['LOYAL_CODE'].map(loyal_code_to_desc)


    fig = px.bar(
        transaction_bar_plot_df,
        x='AVG',
        y='DESC',
        color = 'AVG',
        text = 'AVG',
        labels= {
            'DESC': 'ГҮЙЛГЭЭНИЙ НЭР',
            'AVG': 'ДУНДАЖ ОНОО',
            'PERCENTAGE': 'Эзлэх Хувь'
        }
    )

    fig.update_layout(
        title=dict(
            text = 'Нэгж гүйлгээний дундаж урамшууллын оноо',
            xanchor = 'center',
            x = 0.5
        ),
    )
    fig.update_traces(textposition='outside')

    with st.expander(expanded=False, label='Тайлбар:'):
        st.markdown(f"""
            #### Гүйлгээний шинжилгээ
            -	2025 онд **Топ 5** гүйлгээний төрөл нийлээд **65.6%** буюу нийт онооны талаас их хувийг бүрдүүлж байна.
            -	Бүх гүйлгээний төрлүүдийн **10%** (9/84) нь нийт онооны **80%** ийг бүрдүүлж байна.
                    
            #### 1к эрхийн гүйлгээний урамшуулал:  
            - 2025 оны бүх сард хамгийн өндөр урамшууллын оноо тараагдсан мөн хамгийн олон оролцогчид оролцсон төрөл.
            - 2025 онд нийт **{df[df['LOYAL_CODE'] == '10K_TRANSACTION']['CUST_CODE'].nunique():,}** хэрэглэгчдэд **{df[df['LOYAL_CODE'] == '10K_TRANSACTION']['TXN_AMOUNT'].sum():,.0f}** оноо тараагдсан.
        """)
    
    st.divider()

    st.subheader("Нэгж гүйлгээний дундаж урамшууллын онооны шинжилгээ")
    st.plotly_chart(fig)
    st.caption('Нийт оноонд 1% аас илүү хувь нэмэр оруулсан гүйлгээнүүдийг жагсаав.')
     
    with st.expander(expanded=False, label='Тайлбар:'):


        st.markdown("""
        ### Графикийн тайлбар
        -   Гүйлгээний төрлүүдийг **нэг гүйлгээнд ногдох дундаж урамшууллын оноогоор** харьцуулсан  
        -   **Багана:** Дундаж онооны хэмжээ
        -   **Баганан дээрх хувь:** Гүйлгээний нийт оноонд эзлэх хувь
        """)

        st.markdown("""
        ### Гол ажиглалтууд
        - **Даатгал, хадгаламж, тэтгэврийн хуримтлал** зэрэг гүйлгээнүүд:
        - Нэг удаад **өндөр оноо** олгодог
            - Нийт оноонд эзлэх хувь **харьцангуй бага**
        - **Ердийн гүйлгээ**:
            - Дундаж оноо **бага** харин нийт оноонд эзлэх хувь **хамгийн өндөр**
        """)

        st.markdown("""
        ### Зан төлөвийн ялгаа
        - **Дундаж оноо өндөр + эзлэх хувь бага**  
            -   Өндөр үнэ цэнтэй, ховор хийгддэг гүйлгээ  
        - **Дундаж оноо бага + эзлэх хувь өндөр**  
            -  Өдөр тутмын, олон давтамжтай гүйлгээ
        """)



with tab2:
    fig = px.bar(
        reach_frequency,
        x="Times_Reached_1000",
        y="Number_of_Users",
        text="Number_of_Users",
        title=f"{selected_year} онд давхардаагүй тоогоор хэрэглэгчид хэдэн удаа 1,000 онооны босго давсан бэ?",
        labels={"Times_Reached_1000": "Босгонд давсан удаа", "Number_of_Users": "Хэрэглэгчийн тоо"},
        template="plotly_white"
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(tickmode="linear")

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"""
        {selected_year} онд нийт давхардаагүй тоогоор **{reach_frequency['Number_of_Users'].sum():,}**
        давхардсан тоогоор **{reach_frequency['Total'].sum():,}** хэрэглэгч 1000 оноо давсан байна.
        """
    )
