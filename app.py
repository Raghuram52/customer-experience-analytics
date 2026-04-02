# CX Analytics Dashboard
# Built to analyze customer support trends, satisfaction scores, and account health
# across enterprise CX data. Uses Streamlit + Plotly for interactive reporting.

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="CX Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# basic styling - clean white background with some card separation
st.markdown("""
<style>
    .main { background-color: #f5f6fa; }
    .block-container { padding-top: 1.5rem; }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #dde1e7;
        border-radius: 6px;
        padding: 14px 18px;
    }
    div[data-testid="stSidebar"] { background-color: #1a2e4a; }
    div[data-testid="stSidebar"] * { color: #e8edf2 !important; }
    .chart-title {
        font-size: 14px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 6px;
        padding-bottom: 4px;
        border-bottom: 2px solid #2e75b6;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    customers = pd.read_csv(os.path.join(base, "data/customers.csv"))
    tickets = pd.read_csv(os.path.join(base, "data/tickets.csv"))
    surveys = pd.read_csv(os.path.join(base, "data/surveys.csv"))
    monthly_kpis = pd.read_csv(os.path.join(base, "data/monthly_kpis.csv"))

    tickets["created_date"] = pd.to_datetime(tickets["created_date"])
    surveys["survey_date"] = pd.to_datetime(surveys["survey_date"])
    customers["join_date"] = pd.to_datetime(customers["join_date"])

    return customers, tickets, surveys, monthly_kpis


customers, tickets, surveys, monthly_kpis = load_data()

with st.sidebar:
    st.markdown("## CX Analytics")
    st.markdown("---")
    st.markdown("**Filters**")

    segment_options = ["All"] + sorted(tickets["segment"].unique().tolist())
    selected_segment = st.selectbox("Segment", segment_options)

    region_options = ["All"] + sorted(tickets["region"].unique().tolist())
    selected_region = st.selectbox("Region", region_options)

    year_options = ["All", "2023", "2024"]
    selected_year = st.selectbox("Year", year_options)

    st.markdown("---")
    st.caption("Dataset: 300 customers, 1,200 tickets, 600 surveys (2023-2024)")


def apply_filters(tickets_df, surveys_df, customers_df):
    t = tickets_df.copy()
    s = surveys_df.copy()
    c = customers_df.copy()

    if selected_segment != "All":
        t = t[t["segment"] == selected_segment]
        s = s[s["segment"] == selected_segment]

    if selected_region != "All":
        t = t[t["region"] == selected_region]
        s = s[s["region"] == selected_region]
        c = c[c["region"] == selected_region]

    if selected_year != "All":
        t = t[t["created_date"].dt.year == int(selected_year)]
        s = s[s["survey_date"].dt.year == int(selected_year)]

    return t, s, c


ft, fs, fc = apply_filters(tickets, surveys, customers)

st.title("Customer Experience Analytics")
st.caption("Support ticket trends, satisfaction metrics, and customer health")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Ticket Analysis",
    "Satisfaction",
    "Customer Health"
])


def base_layout(fig, height=300):
    fig.update_layout(
        height=height,
        margin=dict(t=10, b=10, l=0, r=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(size=12),
        xaxis=dict(showgrid=False, linecolor="#dde1e7"),
        yaxis=dict(gridcolor="#f0f0f0", linecolor="#dde1e7"),
    )
    return fig


BLUE_PALETTE = ["#1a2e4a", "#2e75b6", "#5ba3d9", "#9dc3e6", "#bdd7ee"]
PRIORITY_COLORS = {
    "Critical": "#c0392b",
    "High": "#e67e22",
    "Medium": "#f1c40f",
    "Low": "#27ae60"
}
SEGMENT_COLORS = {
    "Enterprise": "#1a2e4a",
    "Mid-Market": "#2e75b6",
    "SMB": "#5ba3d9",
    "Startup": "#9dc3e6"
}


with tab1:
    total = len(ft)
    critical = len(ft[ft["priority"] == "Critical"])
    avg_csat = ft["csat_score"].mean()
    avg_nps = fs["nps_score"].mean()
    avg_res = ft["resolution_hours"].mean()
    mrr_risk = fc[fc["health_score"] < 50]["mrr"].sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Tickets", f"{total:,}")
    c2.metric("Critical", f"{critical:,}", delta=f"{critical/total*100:.1f}%", delta_color="inverse")
    c3.metric("Avg CSAT", f"{avg_csat:.2f} / 5")
    c4.metric("Avg NPS", f"{avg_nps:.1f} / 10")
    c5.metric("Avg Resolution", f"{avg_res:.1f} hrs")
    c6.metric("MRR at Risk", f"${mrr_risk:,.0f}", delta_color="inverse")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="chart-title">Monthly Ticket Volume</div>', unsafe_allow_html=True)
        vol = ft.groupby("created_month").size().reset_index(name="tickets")
        vol = vol.sort_values("created_month")
        fig = px.area(vol, x="created_month", y="tickets",
                      color_discrete_sequence=["#2e75b6"])
        fig.update_traces(line_width=2, fillcolor="rgba(46,117,182,0.12)")
        st.plotly_chart(base_layout(fig), use_container_width=True)

    with right:
        st.markdown('<div class="chart-title">Tickets by Category</div>', unsafe_allow_html=True)
        cats = ft["category"].value_counts().reset_index()
        cats.columns = ["category", "count"]
        fig = px.bar(cats, x="count", y="category", orientation="h",
                     color="count", color_continuous_scale="Blues")
        fig.update_layout(coloraxis_showscale=False,
                          yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(base_layout(fig), use_container_width=True)

    left2, right2 = st.columns(2)

    with left2:
        st.markdown('<div class="chart-title">Priority Breakdown</div>', unsafe_allow_html=True)
        pri = ft["priority"].value_counts().reset_index()
        pri.columns = ["priority", "count"]
        fig = px.pie(pri, values="count", names="priority",
                     color="priority", color_discrete_map=PRIORITY_COLORS, hole=0.4)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, height=300,
                          margin=dict(t=10, b=10), paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with right2:
        st.markdown('<div class="chart-title">Inbound Channel Mix</div>', unsafe_allow_html=True)
        ch = ft["channel"].value_counts().reset_index()
        ch.columns = ["channel", "count"]
        fig = px.bar(ch, x="channel", y="count",
                     color="channel", color_discrete_sequence=BLUE_PALETTE)
        fig.update_layout(showlegend=False)
        st.plotly_chart(base_layout(fig), use_container_width=True)


with tab2:
    resolved = ft[ft["status"].isin(["Resolved", "Closed"])]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tickets", f"{len(ft):,}")
    c2.metric("Resolution Rate", f"{len(resolved)/len(ft)*100:.1f}%")
    c3.metric("Avg CSAT", f"{ft['csat_score'].mean():.2f}")
    c4.metric("Avg Resolution", f"{ft['resolution_hours'].mean():.1f} hrs")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="chart-title">Volume by Segment</div>', unsafe_allow_html=True)
        seg = ft["segment"].value_counts().reset_index()
        seg.columns = ["segment", "count"]
        fig = px.bar(seg, x="segment", y="count",
                     color="segment", color_discrete_map=SEGMENT_COLORS)
        fig.update_layout(showlegend=False)
        st.plotly_chart(base_layout(fig), use_container_width=True)

    with right:
        st.markdown('<div class="chart-title">Avg Resolution Time by Priority</div>', unsafe_allow_html=True)
        res_p = ft.groupby("priority")["resolution_hours"].mean().reset_index()
        order = ["Critical", "High", "Medium", "Low"]
        res_p["priority"] = pd.Categorical(res_p["priority"], categories=order, ordered=True)
        res_p = res_p.sort_values("priority")
        fig = px.bar(res_p, x="priority", y="resolution_hours",
                     color="priority", color_discrete_map=PRIORITY_COLORS)
        fig.update_layout(showlegend=False)
        st.plotly_chart(base_layout(fig), use_container_width=True)

    st.markdown('<div class="chart-title">Agent Performance Summary</div>', unsafe_allow_html=True)
    agent = ft.groupby("assigned_agent").agg(
        tickets=("ticket_id", "count"),
        avg_resolution=("resolution_hours", "mean"),
        avg_csat=("csat_score", "mean")
    ).reset_index().sort_values("tickets", ascending=False)
    agent["avg_resolution"] = agent["avg_resolution"].round(1)
    agent["avg_csat"] = agent["avg_csat"].round(2)
    agent.columns = ["Agent", "Tickets", "Avg Resolution (hrs)", "Avg CSAT"]
    st.dataframe(agent, use_container_width=True, hide_index=True)


with tab3:
    total_s = len(fs)
    promoters = len(fs[fs["nps_category"] == "Promoter"])
    detractors = len(fs[fs["nps_category"] == "Detractor"])
    passives = len(fs[fs["nps_category"] == "Passive"])
    nps = round((promoters - detractors) / total_s * 100, 1) if total_s > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("NPS Score", f"{nps}")
    c2.metric("Promoters", f"{promoters}", f"{promoters/total_s*100:.1f}%")
    c3.metric("Passives", f"{passives}", f"{passives/total_s*100:.1f}%")
    c4.metric("Detractors", f"{detractors}", f"{detractors/total_s*100:.1f}%", delta_color="inverse")
    c5.metric("Avg CSAT", f"{fs['csat_score'].mean():.2f}")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="chart-title">NPS Trend by Month</div>', unsafe_allow_html=True)
        nps_m = fs.groupby("survey_month").apply(
            lambda x: round(
                ((x["nps_category"] == "Promoter").sum() - (x["nps_category"] == "Detractor").sum())
                / len(x) * 100, 1
            )
        ).reset_index()
        nps_m.columns = ["month", "nps"]
        nps_m = nps_m.sort_values("month")
        fig = px.line(nps_m, x="month", y="nps",
                      color_discrete_sequence=["#2e75b6"])
        fig.add_hline(y=0, line_dash="dash", line_color="#c0392b", opacity=0.4)
        fig.update_traces(line_width=2.5)
        st.plotly_chart(base_layout(fig), use_container_width=True)

    with right:
        st.markdown('<div class="chart-title">NPS by Segment</div>', unsafe_allow_html=True)
        nps_s = fs.groupby("segment").apply(
            lambda x: round(
                ((x["nps_category"] == "Promoter").sum() - (x["nps_category"] == "Detractor").sum())
                / len(x) * 100, 1
            )
        ).reset_index()
        nps_s.columns = ["segment", "nps"]
        fig = px.bar(nps_s, x="segment", y="nps",
                     color="nps", color_continuous_scale=["#c0392b", "#f1c40f", "#27ae60"])
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(base_layout(fig), use_container_width=True)

    st.markdown('<div class="chart-title">NPS Category by Region</div>', unsafe_allow_html=True)
    nps_r = fs.groupby(["region", "nps_category"]).size().reset_index(name="count")
    fig = px.bar(nps_r, x="region", y="count", color="nps_category",
                 color_discrete_map={
                     "Promoter": "#27ae60",
                     "Passive": "#f1c40f",
                     "Detractor": "#c0392b"
                 },
                 barmode="stack")
    st.plotly_chart(base_layout(fig, height=320), use_container_width=True)


with tab4:
    at_risk = len(fc[fc["health_score"] < 50])
    avg_h = fc["health_score"].mean()
    total_mrr = fc["mrr"].sum()
    risk_mrr = fc[fc["health_score"] < 50]["mrr"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Health Score", f"{avg_h:.1f} / 100")
    c2.metric("At-Risk Accounts", f"{at_risk}", f"{at_risk/len(fc)*100:.1f}% of base", delta_color="inverse")
    c3.metric("Total MRR", f"${total_mrr:,.0f}")
    c4.metric("MRR at Risk", f"${risk_mrr:,.0f}", f"{risk_mrr/total_mrr*100:.1f}%", delta_color="inverse")

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="chart-title">Health Score Distribution</div>', unsafe_allow_html=True)
        fig = px.histogram(fc, x="health_score", nbins=20,
                           color_discrete_sequence=["#2e75b6"])
        fig.add_vline(x=50, line_dash="dash", line_color="#c0392b",
                      annotation_text="At-Risk", annotation_position="top right")
        st.plotly_chart(base_layout(fig), use_container_width=True)

    with right:
        st.markdown('<div class="chart-title">MRR by Segment</div>', unsafe_allow_html=True)
        mrr_s = fc.groupby("segment")["mrr"].sum().reset_index()
        fig = px.bar(mrr_s, x="segment", y="mrr",
                     color="segment", color_discrete_map=SEGMENT_COLORS)
        fig.update_layout(showlegend=False)
        st.plotly_chart(base_layout(fig), use_container_width=True)

    st.markdown('<div class="chart-title">Health Score by Region and Segment</div>', unsafe_allow_html=True)
    hm = fc.groupby(["region", "segment"])["health_score"].mean().reset_index()
    fig = px.bar(hm, x="region", y="health_score", color="segment",
                 barmode="group", color_discrete_map=SEGMENT_COLORS)
    fig.add_hline(y=50, line_dash="dash", line_color="#c0392b", opacity=0.4,
                  annotation_text="At-Risk Threshold")
    st.plotly_chart(base_layout(fig, height=320), use_container_width=True)
