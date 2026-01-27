import streamlit as st
from data_loader import (
    load_data,
    get_lookup,
    get_most_growing_loyal_code,
    get_page2_data
)
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np  
import math

@st.cache_data(show_spinner=False)
def load_base():
    df = load_data()
    lookup = get_lookup()
    return df, lookup

df, loyal_code_to_desc = load_base()

page2 = get_page2_data(df, loyal_code_to_desc)
grouped_reward = page2["grouped_reward"]
transaction_summary = page2["transaction_summary"]
transaction_summary_with_pad = page2["transaction_summary_with_pad"]

available_years = sorted(transaction_summary["year"].unique())

tab1, tab2, tab3, tab4 = st.tabs(["METHODOLOGY", "ГҮЙЛГЭЭНИЙ ОНООНЫ ТАРХАЦ", 'ГҮЙЛГЭЭНИЙ ТӨРЛИЙН ШИНЖИЛГЭЭ (БҮЛЭГЛЭСЭН)', 'ГҮЙЛГЭЭНИЙ ШИНЖИЛГЭЭ'])



@st.cache_data(show_spinner=False)
def build_animation_fig(transaction_summary):
    all_groups = sorted(transaction_summary["GROUP"].unique())
    fig = px.scatter(
        transaction_summary,
        x='Total_Users',
        y='Total_Amount',
        size='Transaction_Freq',
        color='GROUP',
        animation_frame='year_month',
        animation_group='LOYAL_CODE',
        log_x=True,
        log_y=True,
        size_max=55,
        color_discrete_sequence=px.colors.qualitative.Vivid,
        category_orders={"GROUP": all_groups},
        custom_data=['year_month', 'DESC',],
        hover_name = 'DESC'
    )
    return fig


def donut_plot(df, labels_col, values_col, title_text=""):
    fig = go.Figure(data=[go.Pie(
        labels=df[labels_col], 
        values=df[values_col], 
        hole=.6,              
        marker=dict(line=dict(color='#FFFFFF', width=2)), # White borders between slices
        hoverinfo='label+percent+value',
        textinfo='percent',    
        textfont_size=16,
    )])

    fig.update_layout(
        title=dict(
            text=f"<b>{title_text}</b>",
            #x=0.5,            
            font=dict(size=24)
        ),
        height=500,            
        width=800,             
        
        # CLEANING UP
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",   
            yanchor="bottom",
            y=-0.2,            
            xanchor="center",
            x=0.5,
            font=dict(size=14)
        ),
        #"Donut Hole" text
        annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig

with tab1:
    with st.expander("Гүйлгээний ангиллын аргачлал", expanded=True):
        st.markdown(
            """
            ### Гүйлгээний ангиллын тайлбар

            Энэхүү хуудсанд харуулах гүйлгээнүүдийн ангилалыг датасетын **`LOYAL_CODE`** дээр үндэслэн бизнесийн утга агуулгаар нь бүлэглэн ангилав.
            Ангиллын зорилго нь хэрэглэгчдийн оноо цуглуулах үйл ажиллагааг **товчоор, ойлгомжтой** байдлаар нэгтгэхэд оршино.

            #### Ангиллын үндсэн зарчим

            **1. Санхүүгийн гүйлгээ (Financial Transactions)**  
            Мөнгө шилжүүлэлт, төлбөр, зээлийн эргэн төлөлт болон картын гүйлгээнүүд.  

            **2. Данс нээлт (Account Opening)**  
            Хадгаламж, үнэт цаас, тэтгэврийн болон бусад данс нээхтэй холбоотой урамшууллууд.  

            **3. Хөрөнгө оруулалт ба үнэт цаас (Investments & Securities)**  
            Хувьцаа, crypto, арилжаа, 1072 хувьцаа болон хөрөнгө оруулалтын гүйлгээнүүд.  

            **4. Худалдаа, өдөр тутмын хэрэглээ (Merchant & Lifestyle)**  
            Худалдааны түнш, сугалаа, бараа үйлчилгээтэй холбоотой гүйлгээнүүд.  

            **5. Даатгал (Insurance)**  
            Даатгалын бүтээгдэхүүн болон даатгалтай холбоотой урамшуулалууд.  

            **6. Урамшуулалын аян, арга хэмжээ (Campaigns & Events)**  
            Маркетингийн кампанит ажил, Investor Week, сургалт, эвентүүд.  

            **7. Social оролцоо (Social & Engagement)**  
            Сошиал идэвхжил, мэдээлэл унших, селфи, контент хуваалцах үйлдлүүд.  

            **8. Бүс нутгийн аян (Geographic Campaigns)**  
            Тодорхой аймаг, хотод чиглэсэн кампанит ажлууд.
            """,
    )
        st.dataframe(df.groupby('CODE_GROUP',observed=True)['LOYAL_CODE'].unique(), use_container_width=True)
    
with tab2:

    x_limit = np.log10(transaction_summary_with_pad["Total_Users"].max()) + 0.5
    y_limit = np.log10(transaction_summary_with_pad["Total_Amount"].max()) + 0.7
    max_freq = transaction_summary_with_pad["Transaction_Freq"].max()

    fig = build_animation_fig(transaction_summary_with_pad)

    fig.update_traces(
        marker=dict(
            sizemode="area",
            sizeref=2.0 * max_freq / (55 ** 2),
            sizemin=6,
            opacity=0.65,
        ),
        hoverlabel=dict(bgcolor="white", font_size=13),
        hovertemplate="<br>".join([
            "<b>%{customdata[1]}</b>",
            "Он Сар: %{customdata[0]}",
            "Хэрэглэгч: %{x:,.0f}",
            "Оноо: %{y:,.0f}",
            "<extra></extra>"
        ])
    )

    fig.update_layout(
        height=600,
        template="plotly_white",
        margin=dict(r=100, t=80, b=80),
        title=dict(text="<b>Сарын Гүйлгээний Онооны Тархац</b>", x=0.5, xanchor="center"),
        xaxis=dict(
            title_text="<b>Нийт давтагдаагүй хэрэглэгчдийн тоо</b>",
            range=[0, x_limit],
            dtick=1,
            gridcolor="#F0F0F0",
            tickformat=".1s"
        ),
        yaxis=dict(
            title_text="<b>Нийт цуглуулсан оноо</b>",
            range=[3, y_limit],
            dtick=1,
            gridcolor="#F0F0F0",
            tickformat=".1s"
        ),
        legend=dict(
            title="<b>Гүйлгээний бүлэг</b>",
            yanchor="top", y=1,
            xanchor="left", x=1.02
        ),
    )
    # Animation Controls Styling 
    updatemenus=[{ 
        "buttons": [ 
            {
                "args": [None, {
                    "frame": {"duration": 3000, "redraw": False}, 
                    "fromcurrent": True, 
                    "transition": {"duration": 1500, "easing": "quadratic-in-out"} 
                }], 
                "label": "▶ Play", 
                "method": "animate"
            }, 
            {
                "args": [[None], {
                    "frame": {"duration": 0, "redraw": False}, 
                    "mode": "immediate", 
                    "transition": {"duration": 0}
                }], 
                "label": "|| Pause", 
                "method": "animate"
            } 
        ], 
        "direction": "left", 
        "pad": {"r": 10, "t": 40}, 
        "showactive": False, 
        "type": "buttons", 
        "x": 0.1, 
        "xanchor": "right", 
        "y": 0, 
        "yanchor": "top" 
    }]

    fig.update_xaxes(minor_showgrid=False, showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(minor_showgrid=False, showline=True, linewidth=1, linecolor="black", mirror=True)

    st.plotly_chart(fig, use_container_width=True)
    

        
    #st.dataframe(transaction_summary)
    with st.expander(expanded=True, label = 'Тайлбар:'):
        col1, col2 = st.columns([0.4,0.6])  
        with col1:
            st.subheader('Графикыг тайлбар:')
            st.markdown("""
                - **X axis (log)** – Хэрэглэгчийн тоо 
                - **Y axis (log)** – Нийт мөнгөн дүн 
                - **Bubble хэмжээ** – Гүйлгээний давтамж
                - **Өнгө** – Урамшууллын бүлэг 
                - **Animation** – Сарын өөрчлөлт 
                        
                | Харагдац | Утга |
                |---------|------|
                | Баруун дээд, том bubble | Үндсэн орлогын эх үүсвэр |
                | Дээд, зүүн хэсэг | Өндөр дүн, цөөн хэрэглэгч |
                | Дунд бүс | Оролцоо нэмэгч урамшууллууд |
                | Түр гарч ирэх | Кампанит ажил |
            """) 
        
        with col2:
            st.subheader("Ерөнхий тойм")
            
            st.markdown(f"""
                - 2025 оны **1–12** дугаар саруудад нийт **{df['LOYAL_CODE'].nunique()}** төрлийн урамшуулал олгогдсон байна.
                - 2025 оны 4-р сард **54** төрлийн урамшуулал олгогдсон нь хамгийн олон төрлийн урамшуулал олгосон сар болсон байна.
                - Графикийн баруун дээд хэсэгт дараах урамшууллууд тогтвортой байрлаж байна:
                    -   **1к эрхийн гүйлгээний**
                    -   **Тэтгэврийн хуримтлал цэнэглэлтийн**
                    -   **Хугацаатай хадгаламж / Итгэлцэл нээсэн**
                    -   Эдгээр нь олон хэрэглэгчтэй, нийт дүн өндөр, давтамж өндөр урамшууллуудыг илтгэнэ.
                -   2025 оны 6-р сард **1к эрхийн гүйлгээний** урамшуулалд хамгийн их оноо тараагдсан **(1,283,002)** мөн хамгийн олон оролцогчид оролцсон **(16,022)** байна.  
            """)
            st.caption('Үндсэн, тогтмол орлого бүрдүүлэгч урамшуулал гэж дүгнэж болно.')

    with st.expander(expanded=False, label = 'Өндөр өсөлттэй урамшууллууд:'):
        

        selected_year = st.selectbox(
            "Set Year to analyze",
            options=available_years,
            index=len(available_years) - 1
        )
        
        df_year = df[df["year"] == selected_year]
    
        movers, movers_df = get_most_growing_loyal_code(df_year)

        current_movers_list = movers.tolist()

        # 4. Filter visualization dataset
        movers_df = (
            transaction_summary[(
                (transaction_summary["LOYAL_CODE"].isin(current_movers_list)) &
                (transaction_summary['year'] == selected_year)
            )]
            .sort_values(["DESC", "year_month"])
        )
 
        fig = px.scatter(
            movers_df,
            x='Total_Users', 
            y='Total_Amount', 
            size='Transaction_Freq',
            color='DESC',
            size_max=30, 
            hover_name='LOYAL_CODE',
            hover_data=['year_month'],
            
        )
        fig.update_traces(
            marker=dict(sizemode='area',
                #sizeref=2. * max_freq / (30 ** 2),  # lock size scaling
                sizemin=6,
                opacity=0.65,            
            )
        )
        fig.update_layout(
            legend = dict(
                orientation = 'h',
                yanchor="top",
                y = 1.1,
                xanchor = 'right',
                x=0.99,
                title = None
            )
        )

        for desc in movers_df['DESC'].unique():
            df_sub = movers_df[movers_df['DESC'] == desc]
            n = len(df_sub) - 1

            for i in range(n):
                alpha = 0.05 + (0.8 * (i / n))

                fig.add_annotation(
                    x=df_sub.iloc[i+1]['Total_Users'],  # Arrow head x
                    y=df_sub.iloc[i+1]['Total_Amount'], # Arrow head y
                    ax=df_sub.iloc[i]['Total_Users'],   # Arrow tail x
                    ay=df_sub.iloc[i]['Total_Amount'],  # Arrow tail y
                    xref="x", yref="y",
                    axref="x", ayref="y",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=f"rgba(34,139,34 {alpha})"
                )

        st.subheader(f"Өндөр өсөлттэй урамшууллууд — {selected_year} он")
        st.plotly_chart(fig,use_container_width=True)

        summary = movers_df.groupby("DESC").agg(
            users_start=("Total_Users", "first"),
            users_end=("Total_Users", "last"),
            amount_start=("Total_Amount", "first"),
            amount_end=("Total_Amount", "last")
        ).reset_index()

        summary["user_growth"] = summary["users_end"] / summary["users_start"]
        summary["amount_growth"] = summary["amount_end"] / summary["amount_start"]
        
        st.caption('Онооны Өсөлт:')
        cols_amount = st.columns(4)

        for i, (_, row) in enumerate(summary.iterrows()):
            delta_pct = (
                (row["amount_end"] - row["amount_start"]) / row["amount_start"] * 100
                if row["amount_start"] != 0 else 0
            )

            with cols_amount[i % 4].container(border=True):
                st.metric(
                    label=row["DESC"],
                    value=f"{row['amount_end']:,.0f}",
                    delta=f"{delta_pct:.1f}%",
                    help=f"Эхлэл оноо: {row['amount_start']:,}"
                )

        st.caption('Хэрэглэгчдийн Өсөлт:')
        cols_users = st.columns(4)
        for i, (_, row) in enumerate(summary.iterrows()):
            delta_pct = (
                (row["users_end"] - row["users_start"]) / row["users_start"] * 100
                if row["users_start"] != 0 else 0
            )

            with cols_users[i % 4].container(border=True):
                st.metric(
                    label=row["DESC"],
                    value=f"{row['users_end']:,.0f}",
                    delta=f"{delta_pct:.1f}%",
                    help=f"Эхлэл хэрэглэгч: {row['users_start']:,}"
                )

    with st.expander(expanded=False, label = 'Хүснэгт харах:'):
        st.dataframe(transaction_summary, use_container_width=True)


with tab3:
  
    line_chart_df = grouped_reward[['CODE_GROUP', 'year_month', 'TOTAL_AMOUNT']]
    line_chart_df = line_chart_df.sort_values('year_month')

    line_chart_fig = px.line(line_chart_df, 
            x = 'year_month', 
            y = 'TOTAL_AMOUNT', 
            color = 'CODE_GROUP',
            markers=True,
            title='Урамшууллын Бүлгийн Чиг Хандлага Сараар',
            labels={'year_month': 'Сар', 'TOTAL_AMOUNT': 'Нийт Оноо'}
    )
    line_chart_fig.update_layout( 
        title=dict(
            xanchor = 'center',
            x = 0.5
        ),    
        hovermode= 'x unified' 
    )
    line_chart_fig.update_traces(
        mode="lines+markers",
        hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Total: %{y:,.0f}<extra></extra>"
    )
    
    st.plotly_chart(line_chart_fig, use_container_width=True)

    with st.expander(expanded=True, label= 'Тайлбар:'):

        st.markdown("""
            #### 2025 оны хэрэглэгчдийн бүлэглэсэн гүйлгээний шинжилгээ
            -   Сар бүр **"Гүйлгээний Урамшуулал"** нь хамгийн өндөр хувийг эзэлсэн байна
                -   8-р сард нийт олгогдсон урамшууллын онооны **92.5%-ыг** эзэлсэн нь хамгийн өндөр хувь эзэлсэн сар болсон. 
                -   Харин эсрэгээрээ 4-р сард нийт олгогдсон урамшууллын онооны **49.3%-ыг** эзэлсэн нь энэ бүлгийн хамгийн бага хувь эзэлсэн сар болсон байна
            -   4,5 -р сар хамгийн олон урамшууллын  бүлгүүд ашиглагдсан сар байсан буюу урамшууллын 8 ангиллаас **7** нь ашиглагдсан байна
            -   **"Орон Нутгийн"** урамшууллын гүйлгээ зөвхөн 6-р сард олгогдсон ч тухайн сарын нийт онооны **6.2%** ийг эзэлсэн нь орон нутаг руу чиглэсэн кампанит ажлууд амжилттай байсныг илтгэж байна     
            -   **Мерчантын** урамшууллын оноо эхний 5 сар **240,000-аас 270,000** хооронд байсан бол 8 сар хүртэл тогтмол унасаар **170,000** болсон байна
            -   **Данс Нээсний** урамшууллын оноо мөн адил эхний 5 сар өсөлттэй байсан ч 6,7-р сард унаснаар **5,000** хүрэн үүнээс хойш данс нээсний урамшуулал олгогдоогүй байна                 
            -   **Даатгалын** урамшуулал 4-р сард хамгийн өндөр үзүүлэлттэй байсан буюу тухайн сарын бүх онооны **13.9%** ийг эзэлж, нийт оноо нь өмнө сараас **34%** өссөн байна
                -   Үүнээс хойш тогтмол унасаар **Данс Нээсний** урамшуулалтай адил 7-р сар хүрээд дахиж оноо тараагдаагүй байна     
        """)
        
    with st.expander('Сар тус бүрээр харах:', expanded=False):
        available_months = sorted(grouped_reward['year_month'].unique())
        selected_month = st.selectbox(
            'Choose a month to analyze',
            options=available_months,
        )
        monthly_grouped_reward = grouped_reward[grouped_reward['year_month'] == selected_month]

        fig = donut_plot(
            monthly_grouped_reward, 
            'CODE_GROUP', 
            'TOTAL_AMOUNT',
            f'Percentage of Total Points by Transaction Group in {selected_month}'
        )

        st.plotly_chart(fig, use_container_width=True)


    
    with st.expander("Хүснэгт харах:", expanded=False):
        st.dataframe(monthly_grouped_reward, use_container_width=True)


with tab4:

    transaction_summary = transaction_summary[transaction_summary.LOYAL_CODE != 'None']

    # 2. Year Selection UI
    selected_year = st.selectbox("Select year to analyze:", options=available_years)

    # 3. Filter data for the selected year
    ts_filtered = transaction_summary[transaction_summary['year'] == selected_year]

    # 4. Aggregate data for the Top 5 + Others logic
    ts_agg = ts_filtered.groupby('LOYAL_CODE')['Total_Amount'].sum().reset_index()

    # Separate Top 5
    top5 = ts_agg.nlargest(5, columns='Total_Amount')
    other_total = ts_agg['Total_Amount'].sum() - top5['Total_Amount'].sum()

    # Create 'Others' row
    other_row = pd.DataFrame({'LOYAL_CODE': ['Бусад'], 'Total_Amount': [other_total]})

    # Combine and Map Descriptions
    ts_final = pd.concat([top5, other_row], ignore_index=True)
    ts_final['DESC'] = ts_final['LOYAL_CODE'].map(loyal_code_to_desc).fillna('Бусад')

    # 5. Create the Plot
    fig = donut_plot(
        ts_final,
        labels_col='DESC',
        values_col='Total_Amount',
        title_text=f'{selected_year} Оны Урамшууллын Бүтэц (Топ 5 болон Бусад)'
    )

    # 6. Final Polish
    fig.update_traces(
        customdata=ts_final[['DESC']],
        hovertemplate="<b>%{label}</b><br>Дүн: %{value:,.0f}<br>Хувь: %{percent}<extra></extra>"
    )

    fig.update_layout(
        title=dict(font=dict(size=18), x=0.5, xanchor='center', y=0.95),
        margin=dict(t=80, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    

    with st.expander(expanded=False, label=('Хүснэгт харах:')):
        st.dataframe(ts_final,use_container_width=True)