
import streamlit as st
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Audience Estimator", layout="centered")

# Full model logic (same as your React app)

# 1️⃣ Regression-based audience size (Google Sheets formula)
def regression_audience(seed_size):
    A = 64413674
    B = 9.91772e-08
    C = 1.06427
    return A * (1 - np.exp(-B * (seed_size ** C)))

# 2️⃣ Apply state suppression factor
def suppressed_audience(seed_size):
    reg_aud = regression_audience(seed_size)
    return reg_aud * 0.7439

# 3️⃣ Updated AQI model empirically fit from full data
def updated_aqi(audience_size):
    C = 1814.324
    D = 104.309
    return C - D * np.log(audience_size)


# Streamlit UI
st.title("📊 Audience Size & AQI Estimator")

seed_size = st.number_input("Enter Seed Size:", min_value=30000, max_value=70000000)

reg_aud = regression_audience(seed_size)
supp_aud = suppressed_audience(seed_size)
aqi = updated_aqi(seed_size)

# Display results
st.subheader("Estimates")
st.write(f"**Regression Audience Size:** {reg_aud:,.0f}")
st.write(f"**Suppressed Audience Size:** {supp_aud:,.0f}")
st.write(f"**AQI:** {aqi:.2f}")

# Generate chart data
seeds = np.linspace(10000, 10000000, 100)
reg_auds = [regression_audience(s) for s in seeds]
supp_auds = [suppressed_audience(s) for s in seeds]
aqis = [updated_aqi(s) for s in seeds]

# Plot audience size vs seed size
fig, ax1 = plt.subplots(figsize=(8, 5))

color = "tab:blue"
ax1.set_xlabel("Seed Size")
ax1.set_ylabel("Suppressed Audience Size", color=color)
ax1.plot(seeds, supp_auds, color=color, label="Suppressed Audience")
ax1.tick_params(axis="y", labelcolor=color)
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
color = "tab:orange"
ax2.set_ylabel("AQI", color=color)
ax2.plot(seeds, aqis, color=color, label="AQI")
ax2.tick_params(axis="y", labelcolor=color)
ax2.legend(loc="upper right")

fig.tight_layout()
st.pyplot(fig)
