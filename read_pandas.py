import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

def read_my_csv():
    df = pd.read_csv("data/activities/activity.csv", sep=",")
    selected_columns = ["Duration", "PowerOriginal", "HeartRate"]  
    return df[selected_columns]

def read_data_csv():
    df = pd.read_csv("data/activities/activity.csv", sep=",")
    selected_columns = ["Duration", "PowerOriginal"]  
    return df[selected_columns]

def assign_hr_zone(hr, max_hr):
    if hr <= 0.6 * max_hr:
        return 1
    elif hr <= 0.7 * max_hr:
        return 2
    elif hr <= 0.8 * max_hr:
        return 3
    elif hr <= 0.9 * max_hr:
        return 4
    else:
        return 5
    
def find_best_effort(PowerOriginal, duration_seconds):
    return PowerOriginal.rolling(window=duration_seconds).mean().max()

def generate_power_curve(power_series, durations_s):
    best_powers = [find_best_effort(power_series, d) for d in durations_s]
    return pd.DataFrame({
        'duration_s': durations_s,
        'best_avg_power': best_powers,
    })

def seconds_to_mmss(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{int(minutes):02d}:{int(sec):02d}"


def make_plot(df, max_hr):
    df_plot = df.head(2000).copy()
    df_plot["Time"] = df_plot.index
    
    # Assign HR zones using max_hr dynamically
    df_plot["HR_Zone"] = df_plot["HeartRate"].apply(lambda hr: assign_hr_zone(hr, max_hr))

    zone_colors = {
        1: "blue",
        2: "green",
        3: "yellow",
        4: "orange",
        5: "red"
    }

    fig = go.Figure()

    # Add Power trace (left y-axis)
    fig.add_trace(go.Scatter(
        x=df_plot["Time"], y=df_plot["PowerOriginal"],
        name="Power", yaxis="y1",
        line=dict(color="purple")
    ))

    # Add Heart Rate traces split by zone (right y-axis)
    for zone in range(1, 6):
        zone_data = df_plot[df_plot["HR_Zone"] == zone]
        fig.add_trace(go.Scatter(
            x=zone_data["Time"], y=zone_data["HeartRate"],
            mode='markers',
            name=f"HR Zone {zone}",
            yaxis="y2",
            marker=dict(color=zone_colors[zone], size=5),
            line=dict(color=zone_colors[zone]),
            hovertemplate='Time: %{x}<br>HR: %{y}<br>Zone: '+str(zone)+'<extra></extra>'
        ))

    fig.update_layout(
        title="Power and Heart Rate (with Zones) over Time",
        xaxis=dict(title="Time"),
        yaxis=dict(title="Power (W)", side="left"),
        yaxis2=dict(title="Heart Rate (bpm)", overlaying="y", side="right"),
        legend=dict(title="Legend")
    )

    return fig, df_plot



if __name__ == "__main__":
    df = read_data_csv()

    pio.renderers.default = "browser"
    #fig = make_plot(df)
    #fig.show()
    #print(df.head(10))
    #print(find_best_effort(df["PowerOriginal"], 1))
    durations_s = [10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 300,
               600, 900, 1200, 1800, 2400, 3600, 5400]

    df_powercurve = generate_power_curve(df["PowerOriginal"], durations_s)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_powercurve['duration_s'],
        y=df_powercurve['best_avg_power'],
        mode='lines+markers',
        line=dict(shape='spline', color='royalblue'),
        marker=dict(size=6),
        name='Best Avg Power'
    ))

    tick_vals = durations_s

    tick_text = []
    for t in tick_vals:
        if t < 60:
            tick_text.append(f"{t}s")
        else:
            minutes = t / 60
            if minutes.is_integer():
                tick_text.append(f"{int(minutes)} min")
            else:
                tick_text.append(f"{minutes:.1f} min")

    fig.update_layout(
        title='Power Curve',
        xaxis=dict(
            title='Duration(s)',
            type='log',
            tickvals=tick_vals,
            ticktext=tick_text,
            showticklabels=True,
            dtick=1,  # sets ticks every power of 10
            gridcolor='lightgray',
            zeroline=False
        ),
        yaxis=dict(
            title='Power (W)',
            gridcolor='lightgray'
        ),
        template='plotly_white'
    )

    fig.show()
    fig.write_image("power_curve.png")
