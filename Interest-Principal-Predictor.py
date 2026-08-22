import streamlit as st
import pandas as pd
from datetime import datetime, date

# Get the current year
now = datetime.now()
current_year = now.year

# Sorting values in ascending order:
def sort_values_t(values_list, t_list):
    val_copy = list(values_list)
    t_copy = list(t_list)
    len_val = len(val_copy)
    
    for i in range(len_val):
        for j in range(0, len_val - i - 1):
            if val_copy[j] > val_copy[j + 1]:
                val_copy[j], val_copy[j + 1] = val_copy[j + 1], val_copy[j]
                t_copy[j], t_copy[j + 1] = t_copy[j + 1], t_copy[j]
                
    return val_copy, t_copy

# functions for calculating interest and principal
def a_f_ans(p, r_per, n, t):
    a_ans = p * (1 + r_per / n) ** (n * t)
    a_ans = a_ans - p
    return a_ans
def p_f_ans(ap, r_per, n, t):
    p_ans = ap / (1 + r_per / n) ** (n * t)
    return p_ans

def predictions(p, r_per, n, t, backward_t, forward_t, ap=0):
    values_list = []
    t_list = []
    
    # backward predictions
    current_t = t
    for _ in range(backward_t):
        current_t -= 1
        if current_t < 0:
            st.info(f"🕒 Year 0 reached! This corresponds to the calendar year **{current_year - t}**.")
            break
        
        if ap == 0:
            current_val = round(a_f_ans(p, r_per, n, current_t), 2)
        else:
            current_val = round(p_f_ans(ap, r_per, n, current_t), 2)
            
        t_list.append(current_t)
        values_list.append(current_val)

    # forward predictions
    current_t = t - 1
    crossover_triggered = False
    for _ in range(forward_t):
        current_t += 1
        current_val = round(a_f_ans(p if ap == 0 else p_f_ans(ap, r_per, n, t), r_per, n, current_t), 2)
        
        t_list.append(current_t)
        values_list.append(current_val)
        
        # check values for a crossover
        target_p = p if ap == 0 else p_f_ans(ap, r_per, n, t)
        if current_val >= target_p and not crossover_triggered:
            
            crossover_calendar_year = current_year + (current_t - t)
            st.success(f"🎉 Crossover reached at Year {current_t} (Calendar Year {crossover_calendar_year})! Your interest (${current_val:,.2f}) matched/exceeded your principal (${target_p:,.2f}).")
            crossover_triggered = True
            
    return sort_values_t(values_list, t_list)


# Streamlit UI
st.title("💰 Interest & Principal Predictor")
st.write(f"Predict future and past interest growth based on your financial goals. (Current Reference Year: **{current_year}**)")

if "mode" not in st.session_state:
    st.session_state.mode = "standard"

with st.form("input_form"):
    if st.session_state.mode == "standard":
        st.header("Calculate Interest Amount")
        p = st.number_input("Enter the principal amount ($):", min_value=0.0, value=1000.0, step=100.0)
        ap = 0
    else:
        st.header("Find Your Original Principal")
        ap = st.number_input("Enter Total Balance (Principal + Interest):", min_value=0.0, value=1500.0, step=100.0)
        p = 0
        
    r = st.number_input("Enter the rate of interest (%):", min_value=0.0, value=5.0, step=0.1)
    n = st.number_input("Compounding cycles per year:", min_value=1, value=12, step=1)
    t = st.number_input("Current time in bank (Years):", min_value=0, value=5, step=1)
    backward_t = st.number_input("Years into the PAST to predict:", min_value=0, value=3, step=1)
    forward_t = st.number_input("Years into the FUTURE to predict:", min_value=0, value=5, step=1)
    
    submit = st.form_submit_button("Calculate & Predict")

col1, col2 = st.columns([3, 1])
with col2:
    if st.session_state.mode == "standard":
        if st.button("Forgot Principal Amount?", key="switch_to_forgot"):
            st.session_state.mode = "forgot"
            st.rerun()
    else:
        if st.button("Back to Standard Mode", key="switch_to_standard"):
            st.session_state.mode = "standard"
            st.rerun()

# computing user inputs to generate appropriate outputs
if submit:
    r_per = r / 100
    
    if st.session_state.mode == "standard":
        current_a = a_f_ans(p, r_per, n, t)
        st.metric(label=f"Interest Generated after {t} Years ({current_year})", value=f"${current_a:,.2f}")
        sorted_vals, sorted_times = predictions(p, r_per, n, t, backward_t, forward_t, ap=0)
    else:
        calculated_p = p_f_ans(ap, r_per, n, t)
        st.metric(label=f"Calculated Starting Principal ({current_year - t})", value=f"${calculated_p:,.2f}")
        sorted_vals, sorted_times = predictions(calculated_p, r_per, n, t, backward_t, forward_t, ap=ap)
        
    # Convert the sorted times into corresponding calendar years
    calendar_years = [current_year + (val_t - t) for val_t in sorted_times]
        
    # Build tables
    df_presentation = pd.DataFrame({
        "Timeline (Years)": sorted_times,
        "Calendar Year": [str(yr) for yr in calendar_years],
        "Values ($)": sorted_vals
    })
    
    st.write("---")
    display_tab1, display_tab2 = st.tabs(["📈 Visual Chart", "📋 Data Table"])
    
    with display_tab1:
        st.subheader("Growth Chart")
        st.line_chart(df_presentation, x="Calendar Year", y="Values ($)")
        
    with display_tab2:
        st.subheader("Analysis Timeline (Sorted by Value)")
        st.dataframe(df_presentation, use_container_width=True, hide_index=True)
