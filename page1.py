import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_loader import load_data,get_stat_monthly,load_segment_counts_cutoff_fast,get_page1_bundle

color_2025 = '#3498DB' 

df = load_data()

bundle = get_page1_bundle()
df = bundle["df"]
user_level_stat_monthly = bundle["user_level_stat_monthly"]
monthly_reward_stat = bundle["monthly_reward_stat"]


tab1, tab2, tab3 = st.tabs(['САР БҮРИЙН ОНООНЫ ТАРХАЛТ', "ХЭРЭГЛЭГЧДИЙН ОНООНЫ БҮЛЭГ", "1000 ОНООНЫ БОСГО ДАВСАН ХЭРЭГЛЭГЧИД",])

with tab3:

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=monthly_reward_stat["year_month"],
            y=monthly_reward_stat["num_user_fail_1000"],
            name="1000 хүрээгүй",
            marker_color="lightgrey",
            visible="legendonly",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            x=monthly_reward_stat["year_month"],
            y=monthly_reward_stat["num_user_passed_1000"],
            name="1000 хүрсэн",
            marker_color=color_2025,
            hovertemplate="<b>1000 давсан:</b> %{y:,.0f}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_reward_stat["year_month"],
            y=monthly_reward_stat["percentage"],
            name="Амжилтын хувь (%)",
            line=dict(color="#F75A5A", width=3),
            mode="lines+markers",
            hovertemplate="<b>амжилтын хувь:</b> %{y}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title_text="Сар бүрийн хэрэглэгчдийн онооны гүйцэтгэл (1000 онооны босго)",
        barmode="stack",
        height=450,
        xaxis_title="Сар",
        hovermode="x unified",
        template="plotly_white",
        title={"xanchor": "center", "x": 0.5},
        legend=dict(orientation="h", yanchor="top", xanchor="right", y=1.1, x=0.94),
    )

    fig.update_xaxes(type="category")

    fig.update_yaxes(title_text="Хэрэглэгчийн тоо", secondary_y=False)
    max_pct = monthly_reward_stat["percentage"].max()
    fig.update_yaxes(secondary_y=True, range=[0, max_pct * 1.2])

    st.plotly_chart(fig, use_container_width=True)

    with st.expander(expanded=True,label= 'Тайлбар:'):

        st.subheader("Ерөнхий тойм")

        st.markdown(f"""
        - Сард дунджаар **{monthly_reward_stat['num_user_passed_1000'].mean():,.0f}** хэрэглэгч 1000 онооны босгыг давсан нь,
        сарын нийт оролцогчдын **{monthly_reward_stat['percentage'].mean():.2f}%**-ийг эзэлж байна.
        """)

    with st.expander(expanded=False,label= '2025 он үзүүлэлт:'):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Хамгийн өндөр идэвхтэй сар: 4-р сар")

            st.markdown("""
            - **1000 оноо давсан хэрэглэгч:** 1,432  
            - **Амжилтын хувь:** 6.89%  
            - **Нийт оролцогчид:** 20,778 (2025 оны хамгийн өндөр)
            """)

            st.info(
                "Энэхүү өсөлт нь 4–5-р сард зохион байгуулагдсан "
                "**“Investor Week”** зэрэг маркетингийн ажлуудтай "
                "холбоотой байх магадлалтай."
            )

        with col2:
            st.subheader("Хамгийн бага амжилттай сар: 8-р сар")

            st.markdown("""
            - **1000 оноо давсан хэрэглэгч:** 219  
            - **Амжилтын хувь:** 4.48% (жилийн хамгийн доод)  
            - **Нийт оролцогчид:** 13,607
            """)

            st.info(
                "Энэ нь данс нээсний болон даатгалтай холбоотой оноо өгөхийг зогсоосонтой "
                "холбоотой байх магадлалтай."
            )

        st.divider()

        st.subheader("Амжилтын хувийн онцгой үзүүлэлт: 12-р сар")

        st.markdown("""
        - **Нийт оролцогчид:** 15,204  
        - **1000 оноо давсан хэрэглэгч:** 1,535
        - **Амжилтын хувь:** **10.1%** (2025 оны хамгийн өндөр)
        """)

        st.info(
            "Нийт хэрэглэгчийн тоо харьцангуй бага байсан хэдий ч "
            "зорилтот хэрэглэгчдэд чиглэсэн илүү үр дүнтэй урамшуулал "
            "хэрэгжсэн байж болзошгүйг харуулж байна."
        )

        st.divider()

        st.subheader("Дүгнэлт")

        st.markdown("""
        - **Хэлбэлзэл:** Сар бүрийн нийт оролцогчдын тоо харьцангуй тогтвортой
        **(13,000 – 20,000)** боловч 1000 оноо давсан хэрэглэгчдийн тоо
        **600 – 1,535** хүртэл хэлбэлзэж байна.

        - **Боломж:** **7–8-р сарууд** амжилтын хувь хамгийн бага байгаа тул
        эдгээр саруудад зориулсан тусгай урамшуулал, богино хугацааны
        идэвхжүүлэлтийн аян хэрэгжүүлэх нь үр дүнтэй байх боломжтой.
        """)


    with st.expander(label='Хүснэгт харах:', expanded=False):
        st.dataframe(monthly_reward_stat, hide_index=True, use_container_width=True)


with tab2:

    cutoffs = [400, 500, 600, 700, 800, 900]

    segment_counts_all = load_segment_counts_cutoff_fast(user_level_stat_monthly, cutoffs)

    fig = px.line(
        segment_counts_all,
        x="year_month",
        y="Counts",
        color="cutoff",
        markers=True,
        template="plotly_white",
    )

    fig.update_layout(template="plotly_white")
    fig.update_xaxes(type="category")
    fig.update_yaxes(range=[0, segment_counts_all["Counts"].max() * 1.05])

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Тайлбар", expanded=True):

        st.subheader("2025 ОНЫ ХЭРЭГЛЭГЧДИЙН ОНООНЫ CUT-OFF СЕГМЕНТИЙН ШИНЖИЛГЭЭ")
        st.caption("Онооны босго (cumulative): 400+ | 500+ | 600+ | 700+ | 800+ | 900+")

        st.divider()

        # Зорилго
        st.markdown("#### Зорилго")
        st.write(
            "2024–2025 оны хугацаанд хэрэглэгчдийн урамшууллын онооны "
            "**босго давсан (cutoff-based)** сегментүүдийг шинжилж, "
            "**идэвхжил, улирлын хэлбэлзэл болон ахицын хандлагыг** тодорхойлох."
        )

        st.divider()

        # Гол ажиглалт
        st.markdown("#### Гол ажиглалт")
        st.markdown(
            """
            - Бүх босго сегментүүд **жил бүрийн 4-р сар болон 12-р сард өсөж**, 
            **7–8-р сард хамгийн доод түвшинд** хүрж байна  
            - **800+ ба 900+ сегментүүд** нь нийт хэмжээгээр цөөн боловч 
            **харьцангуй тогтвортой хэлбэлзэлтэй**  
            - Жилийн төгсгөлд (Q4) бүх босго дээр, хэрэглэгчдийн ахиц тодорхой ажиглагдана
            """
        )


with tab1:
    df_2024 = monthly_reward_stat[monthly_reward_stat["year_month"].str.startswith("2024")]
    df_2025 = monthly_reward_stat[monthly_reward_stat["year_month"].str.startswith("2025")]

    color_2024 = "#5D6D7E"
    color_2025 = "#3498DB"

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df_2024["year_month"],
            y=df_2024["total_points"],
            name="2024 Нийт Оноо",
            marker_color=color_2024,
            text=df_2024["total_points"],
            texttemplate="%{y:,.0f}",
            textposition="outside",
            hovertemplate="<b>Нийт оноо:</b> %{y:,.0f}<extra></extra>",
            legendgroup="2024",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            x=df_2025["year_month"],
            y=df_2025["total_points"],
            name="2025 Нийт Оноо",
            marker_color=color_2025,
            text=df_2025["total_points"],
            texttemplate="%{y:,.0f}",
            textposition="outside",
            hovertemplate="<b>Нийт оноо:</b> %{y:,.0f}<extra></extra>",
            legendgroup="2025",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_reward_stat["year_month"],
            y=monthly_reward_stat["total_users"],
            name="Хэрэглэгчдийн тоо",
            mode="lines+markers",
            line=dict(width=3),
            hovertemplate="<b>Оролцогчид (unique):</b> %{y}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        height=500,
        title={"text": "RDX Цуглуулалтын Тренд", "xanchor": "center", "x": 0.5},
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", xanchor="right", y=0.99, x=0.99),
    )

    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Нийт Оноо", secondary_y=False)
    fig.update_yaxes(title_text="Нийт Оролцогчид", secondary_y=True, rangemode="tozero")

    st.plotly_chart(fig, use_container_width=True)

    
    with st.expander(expanded=True, label='Тайлбар:'):

        st.subheader("Ерөнхий тойм")

        st.markdown(f"""
        - **2024-2025** онуудад нийт **{df['CUST_CODE'].nunique():,}** хэрэглэгч урамшууллын хөтөлбөрт хамрагдсан байна.
            - 2024 онд: **{df_2024['total_new_users'].sum():,}** хэрэглэгч
            - 2025 онд: **56,267** хэрэглэгч. (29,995 хэрэглэгчид бүх жилд ороролцсон)
        - Сард дунджаар **{df.groupby('MONTH_NUM')['CUST_CODE'].nunique().mean():,.0f}** хэрэглэгч урамшуулалд оролцсон байна.
        """)

        st.divider()


    with st.expander(expanded=False, label= '2025 он үзүүлэлт:'):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Хамгийн өндөр үзүүлэлттэй сар: 4-р сар")

            st.markdown("""
            - **Нийт тараагдсан оноо:** 3,449,918 (2025 оны хамгийн өндөр)
            - **Нэгж хүнд оногдох оноо:** 166.03  
            - **Нийт оролцогчид:** 20,778 (2025 оны хамгийн өндөр)
            """)

            st.info(
                "Энэхүү өсөлт нь 4–5-р сард зохион байгуулагдсан "
                "**“Investor Week”** зэрэг маркетингийн ажлуудтай "
                "холбоотой байх магадлалтай."
            )

        with col2:
            st.subheader("Хамгийн бага идэвхтэй сар: 8-р сар")

            st.markdown("""
            - **Нийт тараагдсан оноо:** 1,598,666 (2025 оны хамгийн бага)
            - **Нэгж хүнд оногдох оноо:** 117.49  
            - **Нийт оролцогчид:** 13,607
            """)

            st.info(
                "Энэ нь данс нээсний болон даатгалтай холбоотой оноо өгөхийг зогсоосонтой "
                "холбоотой байх магадлалтай."
            )

        st.divider()

        st.subheader("Нэг оролцогчид оногдох онооны онцгой үзүүлэлт: 12-р сар")

        st.markdown("""
            - **Нийт тараагдсан оноо:** 3,345,187 
            - **Нэгж хүнд оногдох оноо:** 245.84  (2025 оны хамгийн өндөр)
            - **Нийт оролцсон хэрэглэгчид:** 15,204
        """)

        st.divider()

    with st.expander(expanded=False, label = 'Хүснэгт харах:'):
        #monthly_reward_stat.columns = ['Сар','Нийт Оноо', 'Нийт Оролцогчид', 'Нэг Хэрэглэгчид оногдох оноо']
        st.dataframe(monthly_reward_stat, use_container_width=True, hide_index=True)



    