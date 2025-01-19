import pandas as pd
import plotly.graph_objects as go


class DashComponents:
    def __init__(self):
        pass

    def aggregate_by_period(self, df, date_column, period):
        df[date_column] = pd.to_datetime(df[date_column])
        df['year'] = df[date_column].dt.year

        if period == 'day':
            agg_df = df.groupby(date_column)['id'].count().reset_index(name='count')

        elif period == 'week':
            df['week'] = df[date_column].dt.isocalendar().week
            df['week_period'] = df['year'].astype(str) + '-W' + df['week'].astype(str)
            agg_df = df.groupby('week_period')['id'].count().reset_index(name='count')

        elif period == 'month':
            df['month'] = df[date_column].dt.strftime('%Y-%m')
            agg_df = df.groupby('month')['id'].count().reset_index(name='count')

        elif period == 'quarter':
            df['quarter'] = df[date_column].dt.to_period('Q').astype(str)
            agg_df = df.groupby('quarter')['id'].count().reset_index(name='count')

        elif period == 'year':
            agg_df = df.groupby('year')['id'].count().reset_index(name='count')

        else:
            raise ValueError(f"Unknown period: {period}")

        return agg_df

    def create_line_plot(self, aggregated_df):
        date_col = [x[1] for x in aggregated_df]  # first column is the date column

        fig_spark = go.Figure(
            data=go.Scatter(
                x=date_col,  # Ensure x-values are set
                y=[x[0] for x in aggregated_df],
                mode="lines",
                fill="tozeroy",
                line_color="red",
                fillcolor="pink",
                hovertemplate=(
                    '<b>%{x}</b><br>'  # Date
                    'Count: <b>%{y}<extra></extra></b>'  # Count value
                )
            ),
        )

        fig_spark.update_xaxes(visible=False, fixedrange=True)
        fig_spark.update_yaxes(visible=False, fixedrange=True)
        fig_spark.update_layout(
            showlegend=False,
            height=50,
            margin=dict(t=10, l=0, b=0, r=0, pad=0),
        )

        return fig_spark
    def get_metrices(self, aggregated_df):
        try:
            current_metrice = aggregated_df[-1][0]
        except:
            return 0,0
        try:
            previous_metrice = aggregated_df[-2][0]
        except:
            previous_metrice = 0

        percentage_change = ((current_metrice - previous_metrice) / (previous_metrice + 1)) * 100

        return current_metrice, percentage_change

    def map_plot(self, aggregated_df):
        col_2 = aggregated_df.columns[-1]  # This is the value for coloring the map
        col_1 = aggregated_df.columns[0]  # This is the location (e.g., country names)

        fig = go.Figure(data=go.Choropleth(
            locations=aggregated_df[col_1],
            z=aggregated_df[col_2],
            text=aggregated_df[col_1],  # Optional: add text to hover info
            hovertemplate=(
                f'Country: <b>%{{location}}</b><br>'  # Display the location
                f'{col_2}: <b>%{{z}}</b><extra></extra>'  # Display the value associated with the location
            ),
            autocolorscale=False,
            reversescale=False,
            marker_line_color='black',
            colorscale='Reds',
            marker_line_width=1,
            locationmode='country names',
        ))

        fig.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=350,
            geo=dict(
                showframe=False,  # Hide the map frame
                bgcolor=None,  # Set the background color to black
                landcolor='white',
            ),
            dragmode='pan',  # Enable panning but not zooming
        )

        return fig
    def line_plot_finances(self, user_wallet_df):
        # Group and sum the balances by updated_at
        wallet_data_formatted = user_wallet_df.groupby('updated_at')[
            ['total_balance', 'paid_balance']].sum().reset_index()

        fig = go.Figure()

        # Add Total Balance trace
        fig.add_trace(go.Scatter(
            x=wallet_data_formatted['updated_at'],
            y=wallet_data_formatted['total_balance'],
            mode='lines',
            name='Total Balance',
            hovertemplate='Date:<b> %{x}</b><br>Total Balance:<b> $%{y:.2f}</b><extra></extra>'
        ))

        # Add Paid Balance trace
        fig.add_trace(go.Scatter(
            x=wallet_data_formatted['updated_at'],
            y=wallet_data_formatted['paid_balance'],
            mode='lines',
            name='Paid Balance',
            hovertemplate='Date:<b> %{x}</b><br>Paid Amount:<b> $%{y:.2f}</b><extra></extra>'
        ))

        fig.update_layout(
        title={
            'text': 'Total Balance and Total Paid Amount Over Time',
            'font': {'size': 16},
            'x': 0.5,  # Center the title
            'xanchor': 'center'
        },
            yaxis_title='Amount',
            template='plotly_dark',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            margin=dict(l=0, r=0, t=20, b=20),
            height=300,
            xaxis_title_font=dict(size=16, family='Arial', color='white', weight='bold'),

        )

        return fig

    def bar_plot(self, aggregated_df, orientation='v'):
        fig = go.Figure()

        col2_name = aggregated_df.columns[1]
        sorted_df = aggregated_df.sort_values(by=aggregated_df.columns[1], ascending=True)

        counts = sorted_df[sorted_df.columns[1]]
        normalized_counts = (counts - counts.min()) / (counts.max() - counts.min())

        # Define a red colorscale
        red_colorscale = [
            [0, 'lightpink'],  # Start color (light red)
            [1, 'darkred']  # End color (dark red)
        ]


        x = sorted_df[sorted_df.columns[0]]
        y = sorted_df[sorted_df.columns[1]]

        # Add bar trace with custom hover information and colorscale
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            orientation=orientation,  # Set orientation based on the parameter
            marker=dict(
                color=normalized_counts,  # Apply the normalized counts to the color
                colorscale=red_colorscale,  # Use the red colorscale
                # colorbar=dict(title='Count')  # Optional: Add colorbar to show scale
            )
        ))

        fig.update_layout(
            xaxis=dict(showticklabels=False, showgrid=False) if orientation == 'h' else {},
            yaxis=dict(showticklabels=False, showgrid=False) if orientation == 'v' else {}
        )

        return fig