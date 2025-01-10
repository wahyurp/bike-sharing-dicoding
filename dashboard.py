import pandas as pd
pip install babel
from babel.dates import format_date
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

all_data = pd.read_excel('hours_df_clean.xlsx')
all_data['dteday'] = pd.to_datetime(all_data['dteday'])

all_data['dteday'] = pd.to_datetime(all_data['dteday'])

all_data['fulltime'] = all_data['dteday'] + pd.to_timedelta(all_data['hr'], unit='h')

def create_minimal_df(df):
    minimal_df = df[['dteday', 'fulltime', 'hr', 'temp', 'hum', 'windspeed', 'cnt']]
    return minimal_df

def create_bydate(df):
    bydate_df = df.groupby('dteday').agg({
        'cnt': 'sum'
    }).reset_index()
    return bydate_df

def create_by_weather(df):
    df['weathersit'] = df['weathersit'].astype(str)
    weathersit_df = df.groupby(by="weathersit").cnt.sum().reset_index()
    return weathersit_df

def create_by_season(df):
    df['season'] = df['season'].astype(str)
    season_df = df.groupby(by="season").cnt.sum().reset_index()
    return season_df

def create_sum_order_times_df(df):
    df['hr'] = df['hr'].astype(str)
    sum_order_hours_df = df.groupby("hr").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_order_hours_df

def create_sum_days_df(df):
    sum_days_df = df.groupby("weekday").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_days_df

def get_stat_days(df):
    temp = []
    df['konversi'] = df['dteday'].apply(lambda x: format_date(x, 'EEEE, dd MMMM yyyy', locale='id'))

    temp_ramai = []
    hari_ramai = df[df['traffic'] == 'Ramai']['cnt'].idxmax()
    hari_ramai = df.loc[hari_ramai, 'konversi']
    temp_ramai.append([hari_ramai, df[df['traffic'] == 'Ramai']['cnt'].idxmax()])
    temp.append(temp_ramai)

    temp_sedang = []
    try:
        hari_sedang = df[df['traffic'] == 'Sedang']['cnt'].median()
        hari_sedang = df[df['cnt'] == hari_sedang]['konversi'].values[0]
        temp_sedang.append([hari_sedang, df[df['traffic'] == 'Sedang']['cnt'].median()])
    except:
        temp_sedang.append(['Tidak Ada', '-'])
    temp.append(temp_sedang)

    temp_sepi = []
    hari_sepi = df[df['traffic'] == 'Sepi']['cnt'].idxmin()
    hari_sepi = df.loc[hari_sepi, 'konversi']
    temp_sepi.append([hari_sepi, df[df['traffic'] == 'Sepi']['cnt'].idxmin()])
    temp.append(temp_sepi)

    return temp

def get_count_cluster(df):
    trafic_season = df.pivot_table(index='traffic', columns='yr', values='dteday', aggfunc='count').reset_index()
    # trafic_season = df.pivot_table(index='traffic', columns='yr', values='dteday', aggfunc='count').reset_index()
    trafic_season.rename(columns={0: '2011', 1: '2012'}, inplace=True)
    return trafic_season

##filtering data
min_date = all_data['dteday'].min()
max_date = all_data['dteday'].max()

all_data['season'].replace([1,2,3,4],
                        ['Springer', 'Summer','Fall','Winter'], inplace=True)

all_data['weekday'].replace([0,1,2,3,4,5,6],
                        ['Minggu', 'Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'], inplace=True)

all_data['weathersit'].replace([1,2,3,4],
                        ['Clear', 'Mist','Light Snow/Rain','Heavy Snow/Rain'], inplace=True)

with st.sidebar:
    start_date, end_date = st.date_input('Pilih Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date])


main_df = all_data[(all_data['dteday'] >= str(start_date)) & (all_data['dteday'] <= str(end_date))]
main_df['traffic'] = pd.cut(main_df['cnt'], bins=3, labels=['Sepi', 'Sedang', 'Ramai'])
group_bydate = create_bydate(main_df)
sum_order_time_df = create_sum_order_times_df(main_df)
sum_weather_df = create_by_weather(main_df)
sum_season_df = create_by_season(main_df)
sum_days_df = create_sum_days_df(main_df)
get_stat_days = get_stat_days(main_df)
trafic_season = get_count_cluster(main_df)

st.header('Bike Rental Dashboard')
st.subheader('Penyewaan Sepeda')

col1, col2 = st.columns(2)

with col1:
    total_casual = main_df.casual.sum()
    st.metric('Total Penggguna Casual', value=total_casual)

with col2:
    total_registered = main_df.registered.sum()
    st.metric('Total Pengguna Registered', value=total_registered)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(group_bydate['dteday'], group_bydate['cnt'], label='Count of Total Rental Bikes')
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Time Performace
st.subheader('Waktu Terbaik Meminjam Sepeda')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# st.dataframe(sum_order_time_df)

sns.barplot(x="cnt", y="hr", data=sum_order_time_df.head(5), palette=colors,  ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Peminjaman", fontsize=30)
ax[0].set_title("Waktu Teramai Meminjam Sepeda", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="cnt", y="hr", data=sum_order_time_df.sort_values(by="cnt", ascending=True).head(5), palette=colors,  ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Peminjaman", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Waktu Tersepi Meminjam Sepeda", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)


# Day Characteristics
st.subheader("Karakteristik Hari")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    sns.barplot(
        y="cnt", 
        x="weathersit",
        data=sum_weather_df.sort_values(by="cnt", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Jumlah Pengguna Berdasarkan Cuaca", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#90CAF9","#D3D3D3" ,"#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="cnt", 
        x="season",
        data=sum_season_df.sort_values(by="cnt", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Jumlah Pengguna Berdasarkan Iklim", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="cnt", 
    y="weekday",
    data=sum_days_df.sort_values(by="cnt", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Penggunaan Berdasarkan Hari", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Day Characteristics
st.subheader("Statistik Hari")
col1, col2, col3 = st.columns(3)


with col1:
    st.metric(f"Terpadat: ({get_stat_days[0][0][0]})", value=get_stat_days[0][0][1])

with col2:
    st.metric(f"Tersedang: ({get_stat_days[1][0][0]})", value=get_stat_days[1][0][1])

with col3:
    st.metric(f"Tersepi: ({get_stat_days[2][0][0]})", value=get_stat_days[2][0][1]) 


st.bar_chart(trafic_season, x="traffic", y=trafic_season.columns[1:], use_container_width=True, x_label="Kepadatan", y_label="Jumlah Periode Waktu")
