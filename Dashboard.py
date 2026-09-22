import streamlit as st
import mysql.connector
import plotly.express as px


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

    /* Main App Background */
    .stApp {
        background-color: #0E1117;
    }

    /* Main Title */
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #AAB2C0;
        font-size: 17px;
        margin-bottom: 35px;
    }

    /* Section Heading */
    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    /* KPI Card */
    .kpi-card {
        background: linear-gradient(
            135deg,
            #1B1F2A,
            #252A36
        );

        border: 1px solid #343A46;
        border-radius: 16px;

        padding: 22px 15px;

        text-align: center;

        min-height: 125px;

        box-shadow:
            0px 5px 18px rgba(0, 0, 0, 0.30);
    }

    /* KPI Title */
    .kpi-title {
        color: #AAB2C0;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    /* KPI Value */
    .kpi-value {
        color: white;
        font-size: 30px;
        font-weight: 800;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #777F8C;
        margin-top: 55px;
        padding: 20px;
        font-size: 13px;
    }

</style>
""", unsafe_allow_html=True)


# ==================================================
# DATABASE CLASS
# ==================================================

class Database:

    # ------------------------------------------------
    # CONSTRUCTOR
    # ------------------------------------------------

    def __init__(self):

        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ipl_project"
        )

    # ------------------------------------------------
    # GET SEASONS
    # ------------------------------------------------

    def get_seasons(self):

        cursor = self.connection.cursor()

        query = """
        SELECT DISTINCT season
        FROM ipl_data
        ORDER BY season
        """

        cursor.execute(query)

        seasons = cursor.fetchall()

        cursor.close()

        return [row[0] for row in seasons]

    # ------------------------------------------------
    # GET TEAMS
    # ------------------------------------------------

    def get_teams(self, season="All"):

        cursor = self.connection.cursor()

        if season == "All":

            query = """
            SELECT DISTINCT team
            FROM (
                SELECT batting_team AS team
                FROM ipl_data

                UNION

                SELECT bowling_team AS team
                FROM ipl_data
            ) AS teams
            ORDER BY team
            """

            cursor.execute(query)

        else:

            query = """
            SELECT DISTINCT team
            FROM (
                SELECT batting_team AS team
                FROM ipl_data
                WHERE season = %s

                UNION

                SELECT bowling_team AS team
                FROM ipl_data
                WHERE season = %s
            ) AS teams
            ORDER BY team
            """

            cursor.execute(
                query,
                (season, season)
            )

        teams = cursor.fetchall()

        cursor.close()

        return [row[0] for row in teams]

    # ------------------------------------------------
    # TOTAL MATCHES
    # ------------------------------------------------

    def get_total_matches(
        self,
        season="All",
        team="All Teams"
    ):

        cursor = self.connection.cursor()

        query = """
        SELECT COUNT(DISTINCT match_id)
        FROM ipl_data
        WHERE 1=1
        """

        params = []

        # Season filter
        if season != "All":

            query += """
            AND season = %s
            """

            params.append(season)

        # Team filter
        if team != "All Teams":

            query += """
            AND (
                batting_team = %s
                OR bowling_team = %s
            )
            """

            params.extend([
                team,
                team
            ])

        cursor.execute(
            query,
            tuple(params)
        )

        result = cursor.fetchone()

        cursor.close()

        return result[0]

    # ------------------------------------------------
    # TOTAL TEAMS
    # ------------------------------------------------

    def get_total_teams(
        self,
        season="All",
        team="All Teams"
    ):

        # If specific team selected
        if team != "All Teams":

            return 1

        cursor = self.connection.cursor()

        if season == "All":

            query = """
            SELECT COUNT(DISTINCT team)
            FROM (
                SELECT batting_team AS team
                FROM ipl_data

                UNION

                SELECT bowling_team AS team
                FROM ipl_data
            ) AS teams
            """

            cursor.execute(query)

        else:

            query = """
            SELECT COUNT(DISTINCT team)
            FROM (
                SELECT batting_team AS team
                FROM ipl_data
                WHERE season = %s

                UNION

                SELECT bowling_team AS team
                FROM ipl_data
                WHERE season = %s
            ) AS teams
            """

            cursor.execute(
                query,
                (season, season)
            )

        result = cursor.fetchone()

        cursor.close()

        return result[0]

    # ------------------------------------------------
    # TOTAL RUNS
    # ------------------------------------------------

    def get_total_runs(
        self,
        season="All",
        team="All Teams"
    ):

        cursor = self.connection.cursor()

        query = """
        SELECT SUM(runs_total)
        FROM ipl_data
        WHERE 1=1
        """

        params = []

        # Season filter
        if season != "All":

            query += """
            AND season = %s
            """

            params.append(season)

        # Runs belong to batting team
        if team != "All Teams":

            query += """
            AND batting_team = %s
            """

            params.append(team)

        cursor.execute(
            query,
            tuple(params)
        )

        result = cursor.fetchone()

        cursor.close()

        if result[0] is None:
            return 0

        return result[0]

    # ------------------------------------------------
    # TOTAL WICKETS
    # ------------------------------------------------

    def get_total_wickets(
        self,
        season="All",
        team="All Teams"
    ):

        cursor = self.connection.cursor()

        query = """
        SELECT COUNT(*)
        FROM ipl_data
        WHERE wicket_kind IS NOT NULL
        """

        params = []

        # Season filter
        if season != "All":

            query += """
            AND season = %s
            """

            params.append(season)

        # Wickets belong to bowling team
        if team != "All Teams":

            query += """
            AND bowling_team = %s
            """

            params.append(team)

        cursor.execute(
            query,
            tuple(params)
        )

        result = cursor.fetchone()

        cursor.close()

        return result[0]

    # ------------------------------------------------
    # TEAM-WISE RUNS
    # ------------------------------------------------

    def get_team_runs(
        self,
        season="All",
        team="All Teams"
    ):

        cursor = self.connection.cursor()

        query = """
        SELECT
            batting_team,
            SUM(runs_total) AS total_runs
        FROM ipl_data
        WHERE 1=1
        """

        params = []

        # Season filter
        if season != "All":

            query += """
            AND season = %s
            """

            params.append(season)

        # Team filter
        if team != "All Teams":

            query += """
            AND batting_team = %s
            """

            params.append(team)

        query += """
        GROUP BY batting_team
        ORDER BY total_runs DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        data = cursor.fetchall()

        cursor.close()

        return data

    # ------------------------------------------------
    # TOP 10 BATSMEN
    # ------------------------------------------------

    def get_top_batsmen(
        self,
        season="All",
        team="All Teams"
    ):

        cursor = self.connection.cursor()

        query = """
        SELECT
            batter,
            SUM(runs_batter) AS total_runs
        FROM ipl_data
        WHERE 1=1
        """

        params = []

        # Season filter
        if season != "All":

            query += """
            AND season = %s
            """

            params.append(season)

        # Team filter
        if team != "All Teams":

            query += """
            AND batting_team = %s
            """

            params.append(team)

        query += """
        GROUP BY batter
        ORDER BY total_runs DESC
        LIMIT 10
        """

        cursor.execute(
            query,
            tuple(params)
        )

        data = cursor.fetchall()

        cursor.close()

        return data

    # ------------------------------------------------
    # CLOSE CONNECTION
    # ------------------------------------------------

    def close_connection(self):

        if self.connection.is_connected():

            self.connection.close()


# ==================================================
# IPL DASHBOARD CLASS
# ==================================================

class IPLDashboard:

    # ------------------------------------------------
    # CONSTRUCTOR
    # ------------------------------------------------

    def __init__(self):

        self.db = Database()

    # ------------------------------------------------
    # SHOW DASHBOARD
    # ------------------------------------------------

    def show_dashboard(self):

        # ============================================
        # HEADER
        # ============================================

        st.markdown(
            '<div class="main-title">'
            '🏏 IPL Analytics Dashboard'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">'
            'Indian Premier League — Performance Overview'
            '</div>',
            unsafe_allow_html=True
        )

        # ============================================
        # FILTERS
        # ============================================

        filter_col1, filter_col2 = st.columns(2)

        # --------------------------------------------
        # SEASON FILTER
        # --------------------------------------------

        with filter_col1:

            seasons = self.db.get_seasons()

            selected_season = st.selectbox(
                "📅 Select Season",
                ["All"] + seasons
            )

        # --------------------------------------------
        # TEAM FILTER
        # --------------------------------------------

        with filter_col2:

            teams = self.db.get_teams(
                selected_season
            )

            selected_team = st.selectbox(
                "🏏 Select Team",
                ["All Teams"] + teams
            )

        # ============================================
        # KPI DATA
        # ============================================

        total_matches = self.db.get_total_matches(
            selected_season,
            selected_team
        )

        total_teams = self.db.get_total_teams(
            selected_season,
            selected_team
        )

        total_runs = self.db.get_total_runs(
            selected_season,
            selected_team
        )

        total_wickets = self.db.get_total_wickets(
            selected_season,
            selected_team
        )

        # ============================================
        # KEY STATISTICS
        # ============================================

        st.markdown(
            '<div class="section-title">'
            '📊 Key Statistics'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        # --------------------------------------------
        # TOTAL MATCHES
        # --------------------------------------------

        with col1:

            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-title">'
                f'🏟️ TOTAL MATCHES'
                f'</div>'
                f'<div class="kpi-value">'
                f'{total_matches:,}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # --------------------------------------------
        # TEAMS
        # --------------------------------------------

        with col2:

            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-title">'
                f'👥 TEAMS INVOLVED'
                f'</div>'
                f'<div class="kpi-value">'
                f'{total_teams:,}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # --------------------------------------------
        # RUNS
        # --------------------------------------------

        with col3:

            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-title">'
                f'🏃 TOTAL RUNS'
                f'</div>'
                f'<div class="kpi-value">'
                f'{total_runs:,}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # --------------------------------------------
        # WICKETS
        # --------------------------------------------

        with col4:

            st.markdown(
                f'<div class="kpi-card">'
                f'<div class="kpi-title">'
                f'🎯 TOTAL WICKETS'
                f'</div>'
                f'<div class="kpi-value">'
                f'{total_wickets:,}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # ============================================
        # PERFORMANCE ANALYSIS
        # ============================================

        st.markdown(
            '<div class="section-title">'
            '📈 Performance Analysis'
            '</div>',
            unsafe_allow_html=True
        )

        chart_col1, chart_col2 = st.columns(2)

        # ============================================
        # TEAM-WISE RUNS CHART
        # ============================================

        with chart_col1:

            team_data = self.db.get_team_runs(
                selected_season,
                selected_team
            )

            if team_data:

                team_df = {
                    "Team": [
                        row[0]
                        for row in team_data
                    ],
                    "Runs": [
                        row[1]
                        for row in team_data
                    ]
                }

                fig_team = px.bar(
                    team_df,
                    x="Team",
                    y="Runs",
                    title="🏏 Team-wise Total Runs"
                )

                fig_team.update_layout(
                    height=450,
                    xaxis_title="Team",
                    yaxis_title="Runs",
                    margin=dict(
                        l=20,
                        r=20,
                        t=60,
                        b=20
                    )
                )

                st.plotly_chart(
                    fig_team,
                    use_container_width=True
                )

            else:

                st.info(
                    "No team data available."
                )

        # ============================================
        # TOP BATSMEN CHART
        # ============================================

        with chart_col2:

            batsman_data = self.db.get_top_batsmen(
                selected_season,
                selected_team
            )

            if batsman_data:

                batsman_df = {
                    "Batsman": [
                        row[0]
                        for row in batsman_data
                    ],
                    "Runs": [
                        row[1]
                        for row in batsman_data
                    ]
                }

                fig_batsman = px.bar(
                    batsman_df,
                    x="Runs",
                    y="Batsman",
                    orientation="h",
                    title="🔥 Top 10 Run Scorers"
                )

                fig_batsman.update_layout(
                    height=450,
                    xaxis_title="Runs",
                    yaxis_title="Batsman",
                    margin=dict(
                        l=20,
                        r=20,
                        t=60,
                        b=20
                    )
                )

                fig_batsman.update_yaxes(
                    categoryorder="total ascending"
                )

                st.plotly_chart(
                    fig_batsman,
                    use_container_width=True
                )

            else:

                st.info(
                    "No batsman data available."
                )

        # ============================================
        # FOOTER
        # ============================================

        st.markdown(
            '<div class="footer">'
            'IPL Analytics Dashboard • '
            'Python • MySQL • Streamlit • OOP'
            '</div>',
            unsafe_allow_html=True
        )

        # ============================================
        # CLOSE DATABASE
        # ============================================

        self.db.close_connection()


# ==================================================
# CREATE OBJECT
# ==================================================

dashboard = IPLDashboard()


# ==================================================
# RUN DASHBOARD
# ==================================================

dashboard.show_dashboard()
