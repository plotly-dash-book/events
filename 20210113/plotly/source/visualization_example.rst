インタラクティブ可視化事例
==========================

次のボタンをクリックするとコードが実行できます。

.. thebe-button:: 実行

.. jupyter-execute::

    import os

    import pandas as pd

    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    df = pd.read_pickle("data.pickle")
    df.iloc[0].T

感染者の位置情報
----------------

.. jupyter-execute::

    after_oct_df = df.loc[df["確定日"] > "2020-10-01"]

    px.set_mapbox_access_token(os.environ["MAPBOX_TOKEN"])
    px.scatter_mapbox(
        after_oct_df,
        lat="Y",
        lon="X",
        size="人数",
        size_max=10,
        color="年代",
        hover_data=["性別", "発症日", "受診都道府県", "居住都道府県"],
        animation_frame=after_oct_df["確定日"].map(lambda x: f"{x:%m/%d}"),
        zoom=4,
        center={"lat": 36, "lon": 138},
        title="感染者の居住地",
        width=1000,
        height=800,
    )

感染者数の推移(年代別)
----------------------

.. jupyter-execute::

    age_df = (
        df.groupby(["確定日", "年代"]).size().reset_index().rename({0: "感染者数"}, axis=1)
    )
    age_df.head()

.. jupyter-execute::

    px.bar(
        age_df,
        x="確定日",
        y="感染者数",
        color="年代",
        title="感染者数の推移(年代別)"
    ).show()

.. jupyter-execute::

    prefectures_df = (
        df.groupby(["確定日", "居住都道府県"])
        .size()
        .reset_index()
        .rename({0: "感染者数"}, axis=1)
    )
    prefectures_df.head()

感染者数の推移(居住都道府県別)
------------------------------

.. jupyter-execute::

    px.bar(
        prefectures_df,
        x="確定日",
        y="感染者数",
        color="居住都道府県",
        title="感染者数の推移(居住都道府県別)"
    ).show()

レンジスライダ/レンジセレクタ
-----------------------------

.. jupyter-execute::

    fixed_date_sum_df = age_df.groupby("確定日").sum()
    fixed_date_sum_df.head()

.. jupyter-execute::

    line_fig = px.line(fixed_date_sum_df, x=fixed_date_sum_df.index, y="感染者数")
    line_fig.update_xaxes(
        rangeslider={"visible": True},
        rangeselector={
            "buttons": [
                {"count": 3, "label": "3m", "step": "month"},
                {"count": 1, "label": "1m", "step": "month"},
                {"count": 7, "label": "7d", "step": "day"},
            ]
        },
    )
    line_fig.show()

ツリーマップ
------------

.. jupyter-execute::

    latest_df = df.loc[
        df["確定日"] == df["確定日"].max(), ["確定日", "居住都道府県", "年代", "性別"]
    ].dropna()
    px.treemap(latest_df, path=["居住都道府県", "年代", "性別"])