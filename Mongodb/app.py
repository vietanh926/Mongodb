import streamlit as st 
from PIL import Image
from pymongo import MongoClient
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 
import plotly.express as px 

#Kết nối với mongodb để lấy dữ liệu về 
client = MongoClient("mongodb://localhost:27017/")
db = client['data']
collection = db['football']
data = pd.DataFrame(list(collection.find()))
data = data.drop(['_id','body_type'], axis = 1)


#Tạo hàm để thực hiện CRUD 
def create_collection(name_collection:str):
    return db[name_collection]
def add_data(collection,data):
    return collection.insert_one(data)
def read_data(collection):
    return pd.DataFrame(list(collection.find()))
def delete_data(collection,query: dict):
    return collection.delete_one(query)
def update_data(collection ,query: dict, new_data:dict):
    return collection.update_one(query,{'$set': new_data})



def main():
    st.title('FIFA')
    menu = ['Home','View data','Search','Graph','Create Team']
    choice = st.sidebar.selectbox("Menu",menu)
    
    
    if choice == "Home":
        st.subheader("Chào mừng đến với trang")
        st.image('0.jpg')
        
    elif choice == "View data":
        st.subheader('View data')
        st.write("### Bảng dữ liệu cầu thủ:")
        st.dataframe(data, use_container_width=True)
    
    
    elif choice == "Search":
        st.subheader('Search')
        player_names = data['name'].tolist()
        selected_player = st.selectbox("Tìm cầu thủ từ gợi ý", tuple(player_names),index=None,placeholder="Điền vào đây")
        st.write(f"Thông tin về cầu thủ: {selected_player}")    
        player_data = data[data["name"] == selected_player]
        st.write(player_data)

    
    elif choice == 'Graph':
        #Vẽ bar chart trực quan dữ liệu
        st.subheader('Phân tích dữ liệu')
        st.subheader('Top 10 nước sản sinh ra nhiều cầu thủ nhất')
        col = data["nationality"].value_counts()
        new = col.head(10)
        st.bar_chart(new)
        
        st.subheader('Top 20 cầu thủ có chỉ số trung bình tốt nhất')
        data['average'] = data.loc[:,'crossing':'sliding_tackle'].mean(axis=1)
        st.write(data.sort_values(by='average',ascending=False).head(20))

        st.subheader('Top 20 cầu thủ trẻ đầy tiềm năng')
        young_player = data[data['age'] < 23]
        st.write(young_player.sort_values(by=['overall_rating','potential','acceleration'],ascending=False).head(20))
    
    
    
    elif choice == 'Create Team':
        st.subheader('Create Team')
        price = st.slider("Select a price range", 0, 110500000, (0, 110500000))
        position = data['positions'].tolist()
        select_position = st.selectbox("Chọn vị trí muốn tìm", tuple(position),index = None, placeholder='Điền vào đây')
        
        
        df = data[data['value_euro'].between(price[0], price[1])]
        df = df[df['positions'] == select_position]
        

        st.button('Lưu đội hình vào cơ sở dữ liệu'):
        team_name = st.text_input('Nhập tên đội hình của bạn:')
        new_team = db[team_name]
        player = st.text_input('Tên cầu thủ')
        new_team.insert_one(player)
                
        
        st.write(df)
        

def plot_radar(player_data):
    stats = player_data[['crossing', 'finishing', 'short_passing', 'dribbling', 'defensive_awareness']].mean()
    radar = pd.DataFrame({
        'Attribute': stats.index,
        'Value': stats.values
    })
    fig = px.line_polar(radar, r='Value', theta='Attribute', line_close=True)
    st.plotly_chart(fig)






if __name__ == '__main__':
    main()