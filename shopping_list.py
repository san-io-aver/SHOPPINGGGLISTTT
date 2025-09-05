import streamlit as st
import requests, json
import firebase_admin
from firebase_admin import credentials, firestore

firebase_config = dict(st.secrets["firebase"])
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

db = firestore.client()
collection_ref = db.collection("shopping_list")

st.markdown(
    """
    <style>
    div[data-testid="stButton"] button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        padding: 6px 12px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.title("🛒 Smart Shopping List")


if "shopping_list" not in st.session_state:
    docs = collection_ref.stream()
    st.session_state.shopping_list = [doc.to_dict() for doc in docs]
    
def fetch_metadata(url):
    try:
        api_key = "0dc782bbc4837d1895519edba1149eb3"  # Replace with your LinkPreview API key
        api_url = f"https://api.linkpreview.net/?key={api_key}&q={url}"
        r = requests.get(api_url)
        data = r.json()

        title = data.get("title", "Unknown Product")
        image = data.get("image")
        return title, image
    except Exception as e:
        return f"Error: {e}", None

url = st.text_input("Paste a product link:")
    
#add to list button
if st.button("Add to List") and url:
    title, image = fetch_metadata(url)
    item = {"url": url, "title": title, "image": image}
    
    if item in st.session_state.shopping_list:
        st.warning("Item already in your shopping list!")
    else:
        st.session_state.shopping_list.append(item)
        collection_ref.add(item)
        st.success("Item added to your shopping list!")


# Display shopping list
st.subheader("🧾 Your Shopping List")

cols = st.columns(3)
for i, item in enumerate(st.session_state.shopping_list):
    col = cols[i % 3]
    with col:
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
                height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                background-color: #f9f9f9;
            ">
                <div style="text-align: center;">
                    {'<img src="' + item['image'] + '" width="200">' if item.get('image') else '<div style="height:100px; background:#eee; display:flex; align-items:center; justify-content:center;">No Image</div>'}
                </div>
                <div style="margin-top:10px; text-align:center;">
                    <p style="font-weight:bold; font-size:13px; margin-bottom:6px; color:#333;">{item['title'][:45] + '...' if len(item['title']) > 45 else item['title']}</p>
                    <a href="{item['url']}" target="_blank">🔗 View Product</a>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # Real button centered below the card
        with col:
            st.markdown("<div style='text-align:center; margin-top:-20px;'>", unsafe_allow_html=True)
            if st.button("🗑️ Remove", key=f"remove_{hash(item['url'])}"):
                docs = collection_ref.where("url", "==", item["url"]).stream()
                for doc in docs:
                    doc.reference.delete()
                st.session_state.shopping_list = [x for x in st.session_state.shopping_list if x["url"] != item["url"]]
            st.markdown("</div>", unsafe_allow_html=True)



