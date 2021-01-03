コールバックを利用した可視化事例
================================

次のボタンをクリックするとコードが実行できます。

.. thebe-button:: 実行

.. jupyter-execute::

    import pandas as pd

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    df = pd.read_pickle("https://github.com/plotly-dash-book/events/raw/plotly/20210113/plotly/data.pickle")
    age_df = (
        df.groupby(["確定日", "年代"]).size().reset_index().rename({0: "感染者数"}, axis=1)
    )
    prefectures_df = (
        df.groupby(["確定日", "居住都道府県"])
        .size()
        .reset_index()
        .rename({0: "感染者数"}, axis=1)
    )
    fixed_date_sum_df = age_df.groupby("確定日").sum()

    age_prefectures_fig = go.FigureWidget(
        make_subplots(
            rows=2,
            cols=2,
            specs=[
                [{"type": "xy", "colspan": 2}, None],
                [{"type": "domain"}, {"type": "xy"}],
            ],
            subplot_titles=("感染者数の推移", "年代別内訳", "居住都道府県"),
        )
    )
    age_prefectures_fig.update_layout(height=800)
    age_prefectures_fig.add_trace(
        go.Bar(x=fixed_date_sum_df.index, y=fixed_date_sum_df["感染者数"]), row=1, col=1
    )
    age_prefectures_fig.add_trace(go.Pie(textinfo="label+percent"), row=2, col=1)
    age_prefectures_fig.add_trace(go.Bar(), row=2, col=2)


    def update_age_prefectures(trace, points, selector):
        n = points.point_inds[0]
        date = age_df.iloc[n, 0]
        age_by_day_df = age_df.loc[age_df["確定日"] == date].sort_values("感染者数")
        age_prefectures_fig.data[1].values = age_by_day_df["感染者数"]
        age_prefectures_fig.data[1].labels = age_by_day_df["年代"]

        prefectures_by_day_df = prefectures_df.loc[
            prefectures_df["確定日"] == date
        ].sort_values("感染者数", ascending=False)
        age_prefectures_fig.data[2].x = prefectures_by_day_df["居住都道府県"]
        age_prefectures_fig.data[2].y = prefectures_by_day_df["感染者数"]


    age_prefectures_fig.data[0].on_click(update_age_prefectures)
    age_prefectures_fig

.. jupyter-execute::

    dayname_jp = {0: "月曜日", 1: "火曜日", 2: "水曜日", 3: "木曜日", 4: "金曜日", 5: "土曜日", 6: "日曜日"}

    day_df = fixed_date_sum_df.reset_index().copy()
    day_df.index = day_df["確定日"].dt.dayofweek
    day_df.index.name = "dayofweek"
    day_df["曜日"] = day_df.index.map(lambda x: dayname_jp[x])

    day_fig = go.FigureWidget(
        make_subplots(
            rows=2, cols=1, subplot_titles=("感染者数の推移", "各曜日の感染者数の推移"), shared_xaxes=True
        )
    )
    day_fig.update_layout(height=800)
    day_fig.add_trace(
        go.Bar(x=day_df["確定日"], y=day_df["感染者数"], name="感染者数", hovertext=day_df["曜日"]),
        row=1,
        col=1,
    )
    day_fig.add_trace(
        go.Scatter(x=day_df["確定日"], y=day_df["感染者数"].rolling(7).mean(), name="7日移動平均"),
        row=1,
        col=1,
    )
    day_fig.add_trace(go.Scatter(), row=2, col=1)


    def update_dayofweek(trace, points, selector):
        try:
            n = points.point_inds[0]
        except IndexError:
            return
        
        date = day_df.iloc[n]["確定日"]
        dayofweek = day_df.loc[day_df["確定日"] == date].index[0]
        dayofweek_df = day_df.loc[dayofweek]
        day_fig.data[2].x = dayofweek_df["確定日"]
        day_fig.data[2].y = dayofweek_df["感染者数"]
        dayname = dayname_jp[dayofweek]
        day_fig.data[2].name = dayname
        day_fig.layout.annotations[1].text = f"{dayname}の感染者数の推移"


    day_fig.data[0].on_click(update_dayofweek)
    day_fig