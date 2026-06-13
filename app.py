import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Advanced News Headlines App", layout="wide")

NEWS_URL = "https://newsapi.org/v2/top-headlines"

# Better: store this in .streamlit/secrets.toml
API_KEY = st.secrets.get("NEWS_API_KEY", "a3f417b116fa4104b3c547e8ee9d32e1")

COUNTRIES = {
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "Germany": "de",
    "France": "fr",
    "Japan": "jp",
    "China": "cn",
}

CATEGORIES = [
    "general",
    "business",
    "entertainment",
    "health",
    "science",
    "sports",
    "technology",
]

st.title("📰 Advanced News Headlines App")
st.caption("Fetch and filter live headlines using NewsAPI")

with st.sidebar:
    st.header("Filters")

    country_name = st.selectbox("Location", list(COUNTRIES.keys()))
    country = COUNTRIES[country_name]

    category = st.selectbox("Topic", CATEGORIES)

    keyword = st.text_input("Search keyword", placeholder="Example: AI, cricket, economy")

    article_count = st.slider("Number of articles", 1, 100, 10)

    search_btn = st.button("Fetch News", use_container_width=True)


@st.cache_data(ttl=300)
def fetch_news(country, category, keyword, article_count):
    params = {
        "apiKey": API_KEY,
        "country": country,
        "category": category,
        "pageSize": article_count,
    }

    if keyword.strip():
        params["q"] = keyword.strip()

    response = requests.get(NEWS_URL, params=params, timeout=10)
    data = response.json()

    if response.status_code != 200 or data.get("status") != "ok":
        raise Exception(data.get("message", "Failed to fetch news"))

    return data.get("articles", [])


if search_btn:
    try:
        articles = fetch_news(country, category, keyword, article_count)

        st.subheader(f"Top {len(articles)} Headlines")
        st.write(f"**Location:** {country_name} | **Topic:** {category.title()}")

        if keyword:
            st.write(f"**Keyword:** {keyword}")

        if not articles:
            st.warning("No articles found. Try another topic or keyword.")

        for article in articles:
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])

                with col1:
                    if article.get("urlToImage"):
                        st.image(article["urlToImage"], use_container_width=True)
                    else:
                        st.write("No image available")

                with col2:
                    st.markdown(f"### {article.get('title', 'No title')}")

                    source = article.get("source", {}).get("name", "Unknown Source")
                    author = article.get("author", "Unknown Author")
                    published = article.get("publishedAt")

                    if published:
                        published = datetime.fromisoformat(
                            published.replace("Z", "+00:00")
                        ).strftime("%d %b %Y, %I:%M %p")

                    st.write(f"**Source:** {source}")
                    st.write(f"**Author:** {author}")
                    st.write(f"**Published:** {published}")

                    description = article.get("description")
                    if description:
                        st.write(description)

                    url = article.get("url")
                    if url:
                        st.link_button("Read Full Article", url)

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Choose filters from the sidebar and click **Fetch News**.")