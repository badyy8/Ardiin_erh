import streamlit as st
from data_loader import (
    load_data, get_lookup,
    get_page5_bundle,   get_page5_loyal_normalized_profile
)
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots

@st.cache_data(show_spinner=False)
def load_base_data():
    df = load_data()
    lookup = get_lookup()
    return df, lookup

df, loyal_code_to_desc = load_base_data()

available_years = sorted(df["year"].dropna().unique())

selected_year = st.sidebar.selectbox(
    "Жил сонгох",
    available_years,
    index=len(available_years) - 1
)

st.sidebar.caption(f"Одоогийн сонголт: {selected_year}")

bundle = get_page5_bundle(df, selected_year)

df_year = bundle["df_year"]
monthly_customer_points = bundle["monthly_customer_points"]
users_agg_df = bundle["users_agg_df"]
thresholds = bundle["thresholds"]
reach_frequency = bundle["reach_frequency"]
user_month_profile = bundle["user_month_profile"]

tab3, tab4, tab5 = st.tabs([
    "1000 Хүрсэн Хэрэглэгчдийн Онооны Тархалт",
    "Зардал/Борлуулалт",
    "RDX Хөнгөлөлт",
])


with tab3:
    user_month_profile = get_page5_loyal_normalized_profile(df_year, users_agg_df)

    profile_wide = user_month_profile.pivot_table(
        index=["CUST_CODE", "MONTH_NUM"],
        columns="LOYAL_CODE",
        values="Normalized_Points",
        fill_value=0
    )

    avg_user_points = profile_wide.mean().reset_index()
    avg_user_points.columns = ["LOYAL_CODE", "Normalized_Points"]

    avg_user_points = avg_user_points.sort_values("Normalized_Points", ascending=False)
    avg_user_points["Normalized_Points"] = (
        avg_user_points["Normalized_Points"] / avg_user_points["Normalized_Points"].sum() * 1000
    )

    avg_user_points["DESC"] = avg_user_points["LOYAL_CODE"].map(loyal_code_to_desc)

    threshold = 50
    main = avg_user_points.copy()
    main.loc[main['Normalized_Points'] < threshold, 'DESC'] = 'Бусад урамшуулал'
    main.loc[main['DESC'].isna(), 'DESC'] = 'Бусад урамшуулал'
    other_sum = avg_user_points[avg_user_points['Normalized_Points'] < threshold]['Normalized_Points'].sum()

    avg_user_simple = (
        main.groupby('DESC',observed=True)['Normalized_Points']
        .sum()
        .reset_index()
        .sort_values('Normalized_Points', ascending=False)
    )
    
    fig = go.Figure()
    left_name = "1к эрхийн гүйлгээний"
    right_name = "Бусад урамшуулал"

    # 1) add the left piece FIRST
    left_df = avg_user_simple[avg_user_simple["DESC"] == left_name]
    right_df = avg_user_simple[avg_user_simple["DESC"] == right_name]

    middle_df = avg_user_simple[
        (avg_user_simple["DESC"] != left_name) &
        (avg_user_simple["DESC"] != right_name)
    ]

    # 1) LEFT ALWAYS FIRST
    for _, row in left_df.iterrows():
        fig.add_bar(
            y=["Дундаж хэрэглэгч = 1000 Оноо"],
            x=[row["Normalized_Points"]],
            name=row["DESC"],
            orientation="h",
            hovertemplate="%{x:.0f} оноог %{fullData.name}-аас авсан<extra></extra>",
        )

    # 2) MIDDLE
    for _, row in middle_df.iterrows():
        fig.add_bar(
            y=["Дундаж хэрэглэгч = 1000 Оноо"],
            x=[row["Normalized_Points"]],
            name=row["DESC"],
            orientation="h",
            hovertemplate="%{x:.0f} оноог %{fullData.name}-аас авсан<extra></extra>",
        )

    # 3) RIGHT ALWAYS LAST
    for _, row in right_df.iterrows():
        fig.add_bar(
            y=["Дундаж хэрэглэгч = 1000 Оноо"],
            x=[row["Normalized_Points"]],
            name=row["DESC"],
            orientation="h",
            hovertemplate="%{x:.0f} оноог %{fullData.name}-аас авсан<extra></extra>",
            marker_color="grey"
        )
        
    fig.update_layout(
        barmode="stack",
        title="Хэрэглэгч дунджаар хэрхэн 1000 оноонд хүрдэг вэ?",
        xaxis_title="Оноо",
        yaxis_title="",
        template="plotly_white",
        height=350,
        legend_title_text="урамшууллын төрөл",
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Даатгал авсны урамшууллын оноог оролцуулаагүй болно")


with tab4:
    st.markdown("## 1,000 оноонд хүрэх Зардал / Борлуулалт")
    st.info('**Зардлыг хэрхэн тооцсон бэ?**')
    st.markdown("""

    - Оноо цуглуулах хамгийн боломжит арга бол **дансандаа орлого хийх** юм
        - Хэрэглэгчид **цэнэглэсэн 100,000 төгрөг тутамд 50 оноо** авдаг (**1 оноо = 2,000 төгрөг**)
    """)

    # Base scenario assumptions
    dominant_points = 400
    remaining_points = 600

    mnt_per_block = 100_000
    points_per_block = 50
    cost_per_point = mnt_per_block / points_per_block  # 2,000 MNT

    remaining_cost = remaining_points * cost_per_point

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Үндсэн гүйлгээнээс авсан оноо",
        f"~{dominant_points} оноо"
    )

    col2.metric(
        "Данс цэнэглэлтээр авах оноо",
        f"{remaining_points} оноо"
    )

    col3.metric(
        "Шаардлагатай орлого хийх дүн",
        f"{remaining_cost:,.0f} төг"
    )


    st.divider()

    st.subheader("Хэрэв гүйлгээний урамшууллын оноог 300-аар хязгаарлавал:")
    capped_points = 300
    new_remaining_points = 1000 - capped_points
    new_required_cost = new_remaining_points * cost_per_point
    incremental_cost = new_required_cost - remaining_cost

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "10K_TRANSACTION-аас авах оноо",
        f"{capped_points} оноо",
        delta="-100 оноо"
    )

    col3.metric(
        "Үлдэгдэл оноонд шаардлагатай орлого",
        f"{new_required_cost:,.0f} ТӨГ",
        delta=f"+{incremental_cost:,.0f} ТӨГ"
    )

    col2.metric(
        "Данс цэнэглэлтээр авах оноо",
        f"{new_remaining_points} оноо",
        delta="+100 оноо"
    )

    st.markdown("""
    **Энэхүү өөрчлөлтийн нөлөө**

    - Хэрэглэгчид ижил хэмжээний урамшуулал авахын тулд **илүү их бодит мөнгө** төвлөрүүлэх шаардлагатай болно
    - Шаардлагатай орлого хийх дүн **1.2 сая -аас  1.4 сая төгрөг** болж нэмэгдэнэ
    - Ганцхан төрлийн гүйлгээний урамшууллаас хамааралтай байхыг бууруулна
    """)



with tab5:
    st.markdown("## Хөнгөлөлттэй Ардын Эрх")
    data = {
        "RDX reached": ["500 RDX", "600 RDX", "700 RDX", "800 RDX", "900 RDX", "1000 RDX"],
        "Discount": ["50%", "60%", "70%", "80%", "90%", "100%"],
        "ARDX received": ["250 ARDX", "360 ARDX", "490 ARDX", "640 ARDX", "810 ARDX", "1000 ARDX"]
    }

    df_table = pd.DataFrame(data)

    mcp = monthly_customer_points.rename(columns={"Total_Points": "Total_Points"}).copy()

    bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 
            mcp ['Total_Points'].max() + 1]
    labels = ['0-99', '100-199', '200-299', '300-399', '400-499', '500-599', 
            '600-699', '700-799', '800-899', '900-999', '1000+']

    # Create segments for ALL months (not filtered)
    mcp ['Segments'] = pd.cut(
        mcp ['Total_Points'], 
        bins=bins, 
        labels=labels, 
        right=False
    )

    # Aggregate across all months by counting customers in each segment
    segment_counts = (
        mcp 
        .groupby('Segments', observed=True)
        .size()
        .reset_index(name='Counts')
    )

    total_customers = segment_counts['Counts'].sum()
    segment_counts['Percentage'] = (segment_counts['Counts'] / total_customers * 100).round(1)
    segment_counts['Percentage'] = segment_counts['Percentage'].astype(str) + '%'

    withdrawal_map = {
        '0-99': 0, '100-199': 0, '200-299': 0, '300-399': 0, '400-499': 0,
        '500-599': 1, '600-699': 1, '700-799': 1, '800-899': 1, '900-999': 1, '1000+': 1,
    }

    segment_counts['Can_Withdraw_Discounted'] = (
        segment_counts['Segments']
        .astype(str)
        .map(withdrawal_map)
        .fillna(0)
        .astype(int)
    )

    segment_counts['Can_Withdraw_Current'] = (
        segment_counts['Segments'] == '1000+'
    ).astype(int)

    current_success = (
        segment_counts
        .loc[segment_counts['Can_Withdraw_Current'] == 1, 'Counts']
        .sum()
    )

    discounted_success = (
        segment_counts
        .loc[segment_counts['Can_Withdraw_Discounted'] == 1, 'Counts']
        .sum()
    )



    total_users = segment_counts['Counts'].sum()

    current_rate = current_success / total_users * 100
    discounted_rate = discounted_success / total_users * 100
    lift = discounted_rate - current_rate

    col1, col2, col3 = st.columns(3,gap='large')
    
    with col1:
        with st.container(border = True):
            st.metric(
                "Одоогийн амжилттай хэрэглэгчдийн тоо",
                f"{current_success:,}",
                help="≥ 1000 RDX оноотой хэрэглэгчид давтагдсан тоогоор",
            )

    with col2:
        with st.container(border = True):
            st.metric(
            "Хөнгөлөлтийн дараах амжилттай хэрэглэгчдийн тоо",
            f"{discounted_success:,}",
            delta=f"+{discounted_success - current_success:,} хэрэглэгч",
            help="≥ 500 RDX оноотой хэрэглэгчид",   
        )

    with col3:
        with st.container(border = True):
            st.metric(
                "Амжилтын хувийн өсөлт",
                f"{discounted_rate:.1f}%",
                delta=f"+{lift:.1f} %"
            )
    success_df = pd.DataFrame({
        "Хувилбар": ["Одоогийн (1000 RDX)", "Хөнгөлөлттэй (≥500 RDX)"],
        "Амжилттай хэрэглэгчид": [current_success, discounted_success]
    })

    # Calculate metrics for the title/labels
    increase = success_df.iloc[1]["Амжилттай хэрэглэгчид"] - success_df.iloc[0]["Амжилттай хэрэглэгчид"]
    increase_pct = (increase / success_df.iloc[0]["Амжилттай хэрэглэгчид"] * 100)

    # Create the figure
    fig = px.bar(
        success_df,
        x="Хувилбар",
        y="Амжилттай хэрэглэгчид",
        text="Амжилттай хэрэглэгчид",
        template="plotly_white",
        color="Хувилбар",
        # Grey for baseline, Brand Blue/Green for the 'Win'
        color_discrete_map={
            success_df.iloc[0]["Хувилбар"]: "#BDC3C7", 
            success_df.iloc[1]["Хувилбар"]: "#2ECC71"
        }
    )

    # Refine bar look and labels
    fig.update_traces(
        textposition="inside",
        texttemplate='<b>%{text:,}</b>',
        marker_line_width=0,
        width=0.6 # Thinner bars look more modern
    )

    fig.update_layout(
        height=600,
        title={
            'text': f"Амжилттай хэрэглэгчдийн өсөлт: <span style='color:#2ECC71'>+{increase_pct:.1f}%</span>",
            'y': 0.95,
            'x': 0.05,
            'xanchor': 'left',
            'yanchor': 'top'
        },
        xaxis_title="",
        yaxis_title="Хэрэглэгчдийн тоо",
        showlegend=False,
        margin=dict(t=80, b=20, l=50, r=20),
        yaxis=dict(showgrid=True, gridcolor='#F0F0F0', zeroline=False)
    )

    with st.expander(expanded=False,label='Хөнгөлөлтийн шатлал'):
        st.subheader("Хөнгөлөлтийн шатлал")

        st.table(df_table)

    st.divider()
    # Streamlit Layout
    col1, col2 = st.columns([0.5, 0.5], gap="large")

    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        ### Шинжилгээний дүгнэлт
        Нөхцөлийг хөнгөлснөөр нийт **{increase:,}** хэрэглэгч шинээр урамшуулал авах боломжтой болж байна.
        
        * **Хүртээмж:** 1,000 RDX-ээс бага оноотой хэрэглэгчид идэвхжих хөшүүрэг болно.
        * **Retention:** Зорилтдоо дөхсөн хэрэглэгчдийг "амжилттай" болгох нь системээс гарах магадлалыг бууруулна.
        """)
        lift_source = segment_counts[

            (segment_counts['Can_Withdraw_Discounted'] == 1) &

            (segment_counts['Can_Withdraw_Current'] == 0)

        ][['Segments', 'Counts']]
        # Clean up the dataframe view
        st.write("---")
        st.caption("Шинээр нэмэгдэж буй сегментүүд")
        st.dataframe(
            lift_source.style.background_gradient(cmap='Greens', subset=['Counts']),
            use_container_width=True,
            hide_index=True
        )