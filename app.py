import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import text

from dash_components.components import DashComponents
from utils.config import dest_db_config
from utils.general import connect

# Streamlit page configuration
st.set_page_config(page_title="DLsurf Dashboard", layout="wide")

# Connect to the database
engine = connect(dest_db_config)
component = DashComponents()

# Load CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Dashboard `v1`")
time_period = st.sidebar.selectbox(
    "Choose a time period:",
    ("day", "week", "month", "quarter", "year"),
    index=1
)


# Function to fetch data from a table
def get_tables(table_name, engine):
    with engine.connect() as conn:
        query = text(f"SELECT * FROM {table_name}")
        return pd.read_sql(query, conn)


# Function to join user data with another DataFrame
def join_on_user(df_user, df_2):
    return pd.merge(df_user[['id', 'country']], df_2, left_on='id', right_on='user_id', how='inner')


# Function to create metric cards
def create_cards(position, name, table_name, date_column, time_period, engine):
    with position:
        data = get_tables(table_name, engine)
        agg_df = component.aggregate_by_period(data, date_column, time_period)
        del (data)
        fig = component.create_line_plot(agg_df)
        metrices = component.get_metrices(agg_df)
        del (agg_df)

        with st.container(border=True):
            st.html(f'<span class="watchlist_card"></span>')

            tl, tr = st.columns([2, 1])
            bottom = st.container()

            with tl:
                st.html(f'<span class="watchlist_symbol_name"></span>')
                st.markdown(f"{name} ")
                negative_gradient = float(metrices[1]) < 0
                st.html(f'<span class="watchlist_ticker"></span>')
                st.markdown(
                    f"<span style='color:{'red' if negative_gradient else 'green'};'>"
                    f"{'▼' if negative_gradient else '▲'} {metrices[1]:.2f}%</span>",
                    unsafe_allow_html=True
                )

            with tr:
                st.html(f'<span class="watchlist_price_value"></span>')
                st.markdown(f"Count: {metrices[0]}")

            with bottom:
                st.plotly_chart(
                    fig, config=dict(displayModeBar=False), use_container_width=True
                )

###1St column###
queries = {
    "user_count": '''SELECT COUNT(id) FROM public.account_management_user''',
    "total_views": '''SELECT COUNT(id) FROM public.file_management_fileviewstransaction''',
    "total_uploads": '''SELECT COUNT(id) FROM public.file_management_userfile''',
    "total_subscribed": '''SELECT COUNT(id) FROM public.subscription_management_subscriptiontransaction WHERE is_active IS TRUE'''
}

col1, col2, col3, col4 = st.columns(4)
for col, (key, query) in zip([col1, col2, col3, col4], queries.items()):
    with col:
        with st.container():
            with engine.connect() as connection:
                # Use the text function to safely execute raw SQL queries
                result = connection.execute(text(query))
                count = result.scalar()
                st.markdown(f"""
                <div class="custom-metric">
                    {count}
                    <div class="custom-label">{key.replace('_', ' ').title()}</div>
                </div>
            """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

###2nd column###
query2 = {
    "users_active(7_days)": """SELECT COUNT(id) FROM public.account_management_user WHERE last_login >= NOW() - INTERVAL '7 days'""",
    "users_active(30_days)": """SELECT COUNT(id) FROM public.account_management_user WHERE last_login >= NOW() - INTERVAL '30 days'""",
    "total_balance": """SELECT SUM(total_balance + paid_balance) AS total_sum FROM public.finance_management_userwallet""",
    "total_paid_out": """SELECT SUM(paid_balance) AS total_sum FROM public.finance_management_userwallet"""
}

for col, (key, query) in zip([col1, col2, col3, col4], query2.items()):
    with col:
        with st.container():
            with engine.connect() as connection:
                # Use the text function to safely execute raw SQL queries
                result = connection.execute(text(query))
                count = result.scalar()
                if "total_balance" in key or "total_paid_out" in key:
                    count = f"${count:,.2f}"
            st.markdown(f"""
                <div class="custom-metric">
                    {count}
                    <div class="custom-label">{key.replace('_', ' ').title()}</div>
                </div>
            """, unsafe_allow_html=True)

# Spacing between metrics and plots
st.markdown("<br>", unsafe_allow_html=True)

# Plotting
col1_row1, col2_row1, col3_row1 = st.columns(3)
col1_row2, col2_row2, col3_row2 = st.columns(3)

create_cards(col1_row1, 'User', 'account_management_user', 'created_at', time_period, engine)
create_cards(col2_row1, 'Referrals', 'account_management_referraltransaction', 'created_at', time_period, engine)
create_cards(col3_row1, 'Followers', 'account_management_followerstransaction', 'updated_at', time_period, engine)
create_cards(col1_row2, 'Uploads', 'file_management_userfile', 'created_at', time_period, engine)
create_cards(col2_row2, 'Downloads', 'file_management_filedownloadtransaction', 'created_at', time_period, engine)
create_cards(col3_row2, 'Views', 'file_management_fileviewstransaction', 'created_at', time_period, engine)

# Map Plot
metric = st.sidebar.selectbox(
    "Choose a map metric",
    ("Balance", "Users", "File Uploads", "Earning Rate"),
    index=0
)


def create_map_plot(metric):
    plot = None

    if metric == 'File Uploads':
        file_uploads_by_country_query = '''SELECT u.country, COUNT(*) AS File_Count
                                            FROM file_management_userfile f
                                            JOIN account_management_user u ON f.user_id = u.id
                                            GROUP BY u.country'''
        file_country_data = pd.read_sql(file_uploads_by_country_query, engine)
        plot = component.map_plot(file_country_data)
        del file_country_data

    elif metric == 'Balance':
        balance_by_country_query = '''SELECT u.country,SUM(uw.total_balance) as Total_Balance FROM public.account_management_user u 
                                    JOIN finance_management_userwallet uw
                                ON u.id = uw.user_id 
                                GROUP BY 
                                1'''
        wallet_country_data = pd.read_sql(balance_by_country_query, engine)
        plot = component.map_plot(wallet_country_data)
        del wallet_country_data

    elif metric == 'Users':
        user_by_country_query = '''SELECT country, COUNT(id) as Total_Users FROM account_management_user GROUP BY 1'''
        user_by_country = pd.read_sql(user_by_country_query, engine)
        plot = component.map_plot(user_by_country)

    elif metric == 'Earning Rate':
        earning_rate_data = get_tables('finance_management_countrywiseearning', engine)
        plot = component.map_plot(earning_rate_data[['country_name', 'earning_rate']])
        del earning_rate_data  # Clean up

    return plot


plt = create_map_plot(metric)

st.plotly_chart(plt, config={'scrollZoom': False})
st.markdown("<br>", unsafe_allow_html=True)

# Balance Plot
wallet_df = get_tables('finance_management_userwallet', engine)
balance_plot = component.line_plot_finances(wallet_df)
del (wallet_df)
st.plotly_chart(balance_plot)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
st.markdown("<br><br>", unsafe_allow_html=True)

##### Categorial Views and uploads #####
with col1:
    file_category_distribution_query = '''
    SELECT fc.category_name, COUNT(uf.id) AS upload_count 
    FROM file_management_category fc 
    JOIN file_management_userfile uf ON fc.id = uf.category_id_id 
    GROUP BY fc.category_name;
    '''
    upload_df = pd.read_sql(file_category_distribution_query, engine)

    categorical_view_query = '''
    SELECT ct.category_name, COUNT(v.id) AS view_count 
    FROM public.file_management_userfile u 
    JOIN public.file_management_fileviewstransaction v ON u.id = v.file_id 
    JOIN public.file_management_category ct ON u.category_id_id = ct.id 
    GROUP BY ct.category_name;
    '''
    view_df = pd.read_sql(categorical_view_query, engine)

    # Merge the two DataFrames on the category_name
    merged_df = pd.merge(upload_df, view_df, on='category_name', how='outer').fillna(0)

    # Calculate percentage for uploads and views
    merged_df['upload_percentage'] = (merged_df['upload_count'] / merged_df['upload_count'].sum()) * 100
    merged_df['view_percentage'] = (merged_df['view_count'] / merged_df['view_count'].sum()) * 100

    # Create a new figure
    fig = go.Figure()

    # Bar plot for upload counts
    fig.add_trace(go.Bar(
        x=merged_df['category_name'],
        y=merged_df['upload_count'],
        name='Uploads',
        marker_color='rgba(110, 110, 255, 0.7)',  # Red for uploads
        text=merged_df['upload_count'],  # Show y (upload count) as text
        textposition='inside',  # Display text inside the bars
        hovertemplate='Category: <b>%{x}</b><br>Uploads: <b>%{y}</b><br>Percentage: <b>%{customdata:.1f}%</b><extra></extra>',
        customdata=merged_df['upload_percentage']  # Percentage in hover tooltip
    ))

    # Bar plot for view counts
    fig.add_trace(go.Bar(
        x=merged_df['category_name'],
        y=merged_df['view_count'],
        name='Views',
        marker_color='rgba(255, 0, 0, 0.7)',  # Light red for views
        text=merged_df['view_count'],  # Show y (view count) as text
        textposition='inside',  # Display text inside the bars
        hovertemplate='Category: <b>%{x}</b><br>Views: <b>%{y}</b><br>Percentage: <b>%{customdata:.1f}%</b><extra></extra>',
        customdata=merged_df['view_percentage']  # Percentage in hover tooltip
    ))

    # Update layout to customize the merged plot
    fig.update_layout(
        title='Categories: Uploads and Views',
        title_font=dict(size=16),
        barmode='group',  # Place bars for uploads and views side by side
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=20),
        yaxis=dict(showticklabels=False, showgrid=False),
        height=400
    )

    # Display the merged plot in Streamlit
    st.plotly_chart(fig)
### Withdraaw method and amount #####
with col2:
    withdraw_amount_by_different_method_query = '''SELECT wm.method_name,SUM(wt.amount)
    	FROM finance_management_withdrawmethod wm
    	JOIN finance_management_withdrawrequesttransaction wt
    	ON wm.id = wt.withdraw_method_id GROUP BY 
    1
    '''
    result_df = pd.read_sql(withdraw_amount_by_different_method_query, engine)
    payout_method_plot = component.bar_plot(result_df)
    payout_method_plot.update_layout(
        title='Withdraw method and amounts',
        title_font=dict(size=16),
        xaxis_title_font=dict(size=16, family='Arial', color='white', weight='bold'),
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=20),
        height=400,
    )
    payout_method_plot.update_traces(
        text=result_df['sum'].apply(lambda x: f'${x:,.2f}'),  # Format text inside the bars
        textposition='inside',  # Position the text inside the bars
        hovertemplate='Method: <b>%{x}</b><br>Amount: <b>$%{y:,.2f}<b><extra></extra>'  # Hover info
    )
    del result_df
    st.plotly_chart(payout_method_plot)

col1, col2, col3 = st.columns(3)
##### SunBrust ####
with col1:
    query = """
    SELECT 
        u.id AS user_id,
        s.id AS subscription_id,
        s.subscription_name AS subscription_name
    FROM 
        public.account_management_user u
    LEFT JOIN 
        public.subscription_management_subscriptiontransaction st
    ON 
        u.id = st.user_id
    LEFT JOIN 
        public.subscription_management_subscription s
    ON 
        st.subscription_id = s.id
    """
    df = pd.read_sql(query, engine)

    df['status'] = df['subscription_id'].apply(lambda x: 'Subscribed' if pd.notna(x) else 'Unsubscribed')

    subscribed_counts = df[df['status'] == 'Subscribed'].groupby('subscription_name').size().reset_index(name='values')

    subscribed_counts['parent'] = 'Subscribed'
    subscribed_counts.rename(columns={'subscription_name': 'label'}, inplace=True)

    unsubscribed_count = len(df[df['status'] == 'Unsubscribed'])

    unsubscribed_entry = pd.DataFrame({
        'label': ['Unsubscribed'],
        'parent': ['All Users'],
        'values': [unsubscribed_count]
    })

    subscribed_entry = pd.DataFrame({
        'label': ['Subscribed'],
        'parent': ['All Users'],
        'values': [subscribed_counts['values'].sum()]
    })

    root = pd.DataFrame({'label': ['All Users'], 'parent': [''], 'values': [df.shape[0]]})

    sunburst_data = pd.concat([root, subscribed_entry, subscribed_counts, unsubscribed_entry], ignore_index=True)
    del df, subscribed_counts, unsubscribed_entry, subscribed_entry, root  # Clean up
    total_value = sunburst_data.iloc[0]['values']
    sunburst_data['percentage'] = [(value / total_value) * 100 for value in sunburst_data['values']]

    # Create the sunburst chart with a red-to-pink color scale and custom hover info
    fig = go.Figure(
        go.Sunburst(
            labels=sunburst_data['label'],
            parents=sunburst_data['parent'],
            values=sunburst_data['values'],
            hovertemplate=(
                    '<b>%{label}</b><br>' +
                    'Users: <b>%{value}</b><br>' +
                    'Percentage: <b>%{customdata:.1f}</b>%<extra></extra>'
            ),
            customdata=sunburst_data['percentage'],  # Pass the percentage data for hover
            marker=dict(
                colors=sunburst_data['values'],  # Base the color on the values
                colorscale=[
                    [0, 'rgb(255,0,0)'],  # Dark red
                    [0.5, 'rgb(255,102,102)'],  # Light red
                    [1, 'rgb(255,182,193)']  # Light pink
                ],
            )
        )
    )

    # Update layout with the title
    fig.update_layout(
        title='User Subscription Status',
        margin=dict(t=50, l=0, r=0, b=0)
    )

    # Display the figure
    st.plotly_chart(fig)
    del sunburst_data
#### Browser Distribution Plot ####
with col2:
    browser_info_query = '''SELECT browser_name,count(id) FROM public.file_management_filedownloadtransaction 
                                GROUP BY browser_name ORDER BY 
                                2 DESC'''
    browser_info_df = pd.read_sql(browser_info_query, engine)
    browser_info_plot = component.bar_plot(browser_info_df)
    browser_info_plot.update_layout(
        title='Downloads By Browser ',
        title_font=dict(size=16),
        xaxis_title_font=dict(size=16, family='Arial', color='white', weight='bold'),
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=20),
        height=400,
    )
    browser_info_plot.update_traces(
        text=browser_info_df['count'],
        textposition='inside',  # Position the text inside the bars
        hovertemplate='Browser: <b>%{x}</b><br>Count: <b>%{y}<b><extra></extra>'  # Hover info
    )
    del browser_info_df
    st.plotly_chart(browser_info_plot)
#### Device Distribution Plot ####
with col3:
    browser_info_query = '''SELECT device_name,count(id) FROM public.file_management_filedownloadtransaction 
                                    GROUP BY 1 ORDER BY 
                                    2 DESC'''
    device_info_df = pd.read_sql(browser_info_query, engine)
    device_info_plot = component.bar_plot(device_info_df)
    device_info_plot.update_layout(
        title='Downloads By Device',
        title_font=dict(size=16),
        xaxis_title_font=dict(size=16, family='Arial', color='white', weight='bold'),
        template='plotly_dark',
        margin=dict(l=0, r=0, t=40, b=20),
        height=400,
    )
    device_info_plot.update_traces(
        text=device_info_df['count'],
        textposition='inside',  # Position the text inside the bars
        hovertemplate='Device: <b>%{x}</b><br>Count: <b>%{y}<b><extra></extra>'  # Hover info
    )
    del device_info_df
    st.plotly_chart(device_info_plot)

#### User Info DF ######
user_id = st.text_input("Enter User ID", "1")

col1,col2 = st.columns(2)
with col1:
    def get_user_data(user_id, engine):
        user_info_query = f'''SELECT 
                                COALESCE(v.created_at, u.created_at) AS created_at,
                                COALESCE(views_count, 0) AS views_count,
                                COALESCE(uploads_count, 0) AS uploads_count
                            FROM (
                                SELECT v.created_at, COUNT(v.id) AS views_count
                                FROM public.file_management_fileviewstransaction v
                                JOIN public.file_management_userfile f ON v.file_id = f.id
                                WHERE f.user_id = {user_id}
                                GROUP BY v.created_at
                            ) v
                            FULL OUTER JOIN (
                                SELECT f.created_at, COUNT(f.id) AS uploads_count
                                FROM public.file_management_userfile f
                                WHERE f.user_id = {user_id}
                                GROUP BY f.created_at
                            ) u
                            ON v.created_at = u.created_at
                            ORDER BY created_at;'''

        user_df = pd.read_sql(user_info_query, engine)
        today = pd.to_datetime('today').normalize()
        date_range = pd.date_range(end=today, periods=30)
        user_df.set_index('created_at', inplace=True)
        user_df = user_df.reindex(date_range, fill_value=0).reset_index()
        user_df.columns = ['date', 'views', 'uploads']
        fig = go.Figure()

        # Area for views
        fig.add_trace(go.Scatter(
            x=user_df['date'],
            y=user_df['views'],
            mode='lines',
            name='Views',
            line=dict(color='red')
        ))

        # Area for uploads
        fig.add_trace(go.Scatter(
            x=user_df['date'],
            y=user_df['uploads'],
            mode='lines',
            name='Uploads',
            line=dict(color='royalblue')
        ))

        # Update layout
        fig.update_layout(
            title=f"User Views and Uploads in Last 30 Days for User ID: {user_id}",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode="x unified"
        )

        # Display the Plotly chart in Streamlit
        return fig


    fig = get_user_data(user_id, engine)
    st.plotly_chart(fig)
with col2:

    downloads_by_country_query = f"""SELECT dt.country_name,COUNT(dt.id) FROM public.file_management_filedownloadtransaction dt JOIN public.file_management_userfile uf
ON dt.file_id = uf.id WHERE 
uf.user_id = {user_id}
GROUP BY 1"""

    downloads_by_country_df = pd.read_sql(downloads_by_country_query,engine)
    downloads_by_country_plot = component.map_plot(downloads_by_country_df)
    downloads_by_country_plot.update_layout(title=f'Downloads for user {user_id}',
                                            margin=dict(l=0, r=0, t=40, b=0),
                                            )


    st.plotly_chart(downloads_by_country_plot, config={'scrollZoom': False})
