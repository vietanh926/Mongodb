import streamlit as st 
from pymongo import MongoClient
import pandas as pd 


#Kết nối với mongodb để lấy dữ liệu về 
client = MongoClient("mongodb://localhost:27017/")
db = client['data']
collection = db['football']
data = pd.DataFrame(list(collection.find()))
data = data.drop(['_id','body_type'], axis = 1)


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

        # Tạo session_state để lưu đội hình
        if 'user_select' not in st.session_state:
            st.session_state['user_select'] = []

        # Chọn hành động
        action = st.radio("Chọn", ["Tạo đội hình mới", "Xem đội hình đã lưu", "Sửa đội hình", "Xóa đội hình"])

        if action == "Tạo đội hình mới":
            team_name = st.text_input("Nhập tên đội hình của bạn:")
            price = st.slider("Chọn khoảng giá trị", 0, 110500000, (0, 110500000))
            positions = data['positions'].unique().tolist()
            select_position = st.selectbox("Chọn vị trí muốn tìm", positions, index=0)

            filtered_df = data[data['value_euro'].between(price[0], price[1])]
            filtered_df = filtered_df[filtered_df['positions'].str.strip().str.lower() == select_position.strip().lower()]

            for _, row in filtered_df.iterrows():
                if st.checkbox(f"Lấy {row['name']} giá {row['value_euro']} euro", key=f"{row['name']}_{row['value_euro']}"):
                    if row['name'] not in [player['name'] for player in st.session_state['user_select']]:
                        st.session_state['user_select'].append({
                            'name': row['name'],
                            'value_euro': row['value_euro'],
                            'positions': row['positions']
                        })

            st.write("### Đội hình của bạn:")
            if st.session_state['user_select']:
                selected_players_df = pd.DataFrame(st.session_state['user_select'])
                st.dataframe(selected_players_df)
            else:
                st.write("Bạn chưa chọn cầu thủ nào!")

            if st.button("Lưu đội hình"):
                if team_name.strip() and st.session_state['user_select']:
                    new_team = db[team_name.strip()]
                    new_team.insert_many(st.session_state['user_select'])
                    st.success(f"Đội hình '{team_name}' đã được lưu thành công!")
                else:
                    st.error("Vui lòng nhập tên đội hình và chọn ít nhất một cầu thủ.")

        elif action == "Xem đội hình đã lưu":
            team_names = db.list_collection_names()
            if not team_names:
                st.warning("Hiện tại chưa có đội hình nào được lưu!")
            else:
                selected_team = st.selectbox("Chọn đội hình để xem:", team_names)
                if selected_team:
                    team_data = pd.DataFrame(list(db[selected_team].find()))
                    if not team_data.empty:
                        st.write(f"### Đội hình: {selected_team}")
                        st.dataframe(team_data)
                    else:
                        st.warning("Đội hình này không có cầu thủ nào!")

        elif action == "Sửa đội hình":
            team_names = db.list_collection_names()
            if not team_names:
                st.warning("Hiện tại chưa có đội hình nào để sửa!")
            else:
                selected_team = st.selectbox("Chọn đội hình để sửa:", team_names)
                if selected_team:
                    team_data = pd.DataFrame(list(db[selected_team].find()))
                    st.write(f"### Đội hình hiện tại: {selected_team}")
                    st.dataframe(team_data)

                    # Thêm cầu thủ
                    st.write("### Thêm cầu thủ mới:")
                    new_player = st.selectbox("Chọn cầu thủ thêm vào đội hình:", data['name'])
                    if st.button("Thêm cầu thủ"):
                        player_data = data[data['name'] == new_player].to_dict(orient='records')[0]
                        db[selected_team].insert_one(player_data)
                        st.success(f"Đã thêm cầu thủ {new_player} vào đội hình {selected_team}!")

                    # Xóa cầu thủ
                    st.write("### Xóa cầu thủ:")
                    player_to_remove = st.selectbox("Chọn cầu thủ muốn xóa:", team_data['name'])
                    if st.button("Xóa cầu thủ"):
                        db[selected_team].delete_one({'name': player_to_remove})
                        st.success(f"Đã xóa cầu thủ {player_to_remove} khỏi đội hình {selected_team}!")

        elif action == "Xóa đội hình":
            team_names = db.list_collection_names()
            if not team_names:
                st.warning("Hiện tại chưa có đội hình nào để xóa!")
            else:
                selected_team = st.selectbox("Chọn đội hình để xóa:", team_names)
                if st.button("Xóa đội hình"):
                    db[selected_team].drop()
                    st.success(f"Đội hình {selected_team} đã được xóa thành công!")


if __name__ == '__main__':
    main()