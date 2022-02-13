mkdir -p ~/.streamlit/

cat << EOF > ~/.streamlit/credentials.toml
[general]
email = "paul.r.kiage@gmail.com"
EOF

cat << EOF > ~/.streamlit/config.toml
[server]
headless = true
enableCORS = false
port = $PORT
EOF