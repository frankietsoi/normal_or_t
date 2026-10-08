import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(page_title="Stats Distribution Selector", layout="wide")

# --- QUESTION BANK ---
SCENARIOS = [
    {
        "id": 1,
        "title": "Scenario 1: Industrial Machine Calibration",
        "description": (
            "A factory engineer monitors bolt diameters. Historical data confirms the machine operates "
            "with a **known population standard deviation** $\\sigma = 0.05\\text{ mm}$. The engineer collects "
            "a random sample of $n = 16$ bolts from a normal production line to test if the mean diameter has shifted."
        ),
        "options": [
            "Standard Normal Distribution (Z)",
            "Student's t-Distribution (t)",
            "Neither (Non-parametric / Bootstrap required)"
        ],
        "correct_idx": 0,
        "key_factors": {
            "Parameter": "Population Mean (\\mu)",
            "Population Standard Deviation (\\sigma)": "Known (\\sigma = 0.05)",
            "Sample Size / Normality": "n = 16, Population is Normal"
        },
        "explanation_correct": (
            "**Correct! Use the Z-distribution.** Because the true population standard deviation $\\sigma$ is known "
            "and the underlying population is normal, the standardized test statistic "
            r"$Z = \frac{\bar{x} - \mu}{\sigma / \sqrt{n}}$ follows an exact standard normal distribution."
        ),
        "feedback_incorrect": {
            1: "❌ **Why t is incorrect:** Student's $t$ is strictly designed to account for the extra sampling variability introduced when you must estimate an unknown $\\sigma$ using $s$. Because $\\sigma$ is already known here, using $t$ needlessly inflates the critical values.",
            2: "❌ **Why Neither is incorrect:** Even though $n = 16 < 30$, the population is explicitly normal and $\\sigma$ is known, satisfying the requirements for the standard $Z$-test."
        }
    },
    {
        "id": 2,
        "title": "Scenario 2: Clinical Trial Recovery Time",
        "description": (
            "A doctor evaluates a new headache medication on $n = 22$ randomly assigned patients. "
            "The recovery times are roughly symmetric with no extreme outliers. The sample standard "
            "deviation is $s = 8.4\\text{ minutes}$. The true population standard deviation $\\sigma$ is unknown."
        ),
        "options": [
            "Standard Normal Distribution (Z)",
            "Student's t-Distribution (t)",
            "Neither (Non-parametric / Bootstrap required)"
        ],
        "correct_idx": 1,
        "key_factors": {
            "Parameter": "Population Mean (\\mu)",
            "Population Standard Deviation (\\sigma)": "Unknown (only sample s = 8.4 is available)",
            "Sample Size / Normality": "n = 22, roughly symmetric without outliers (df = 21)"
        },
        "explanation_correct": (
            "**Correct! Use Student's t-distribution with $df = 21$.** Because $\\sigma$ is unknown, we must estimate "
            "it using $s$. Dividing by $s / \\sqrt{n}$ introduces extra variability into the denominator, "
            "requiring heavier tails (Student's $t$ with $df = n - 1 = 21$)."
        ),
        "feedback_incorrect": {
            0: "❌ **Why Z is incorrect:** Using $Z$ assumes zero estimation error in the standard deviation. Because $\\sigma$ is replaced by the sample estimate $s$, the test statistic has higher dispersion than a standard normal, leading to an artificially high Type I error rate if $Z$ is used.",
            2: "❌ **Why Neither is incorrect:** The sample is roughly symmetric with no extreme outliers, which satisfies the robustness condition for the $t$-test even though $n < 30$."
        }
    },
    {
        "id": 3,
        "title": "Scenario 3: Large E-Commerce Dataset",
        "description": (
            "An analyst investigates average shopping cart values across $n = 250$ customers. "
            "The population variance is unknown, but the sample standard deviation is computed as $s = \\$14.20$."
        ),
        "options": [
            "Standard Normal Distribution (Z)",
            "Student's t-Distribution (t)",
            "Neither (Non-parametric / Bootstrap required)"
        ],
        "correct_idx": 1,
        "key_factors": {
            "Parameter": "Population Mean (\\mu)",
            "Population Standard Deviation (\\sigma)": "Unknown (sample s is used)",
            "Sample Size / Normality": "n = 250 (df = 249)"
        },
        "explanation_correct": (
            "**Correct! Use Student's t-distribution ($df = 249$).** Under modern inferential statistics standards, "
            "any mean inference where $\\sigma$ is estimated by $s$ is formally a $t$-distribution. While $t_{249} \\approx Z$, "
            "software and current textbooks use $t$ with $df = n - 1$."
        ),
        "feedback_incorrect": {
            0: "❌ **The Classic Textbook Trap:** Older tables approximated $t$ with $Z$ when $n \\ge 30$ because printed $t$-tables lacked rows for large degrees of freedom. Mathematically, whenever $\\sigma$ is unknown and replaced with $s$, the formal distribution is Student's $t$ with $df = n - 1$.",
            2: "❌ **Why Neither is incorrect:** With $n = 250$, the Central Limit Theorem guarantees that the sampling distribution of $\\bar{x}$ is approximately normal regardless of population shape."
        }
    },
    {
        "id": 4,
        "title": "Scenario 4: Startup Executive Salaries",
        "description": (
            "A researcher surveys $n = 11$ tech startup founders. The reported incomes are heavily right-skewed, "
            "with two extreme multi-millionaire outliers. The population standard deviation $\\sigma$ is unknown."
        ),
        "options": [
            "Standard Normal Distribution (Z)",
            "Student's t-Distribution (t)",
            "Neither (Non-parametric / Bootstrap required)"
        ],
        "correct_idx": 2,
        "key_factors": {
            "Parameter": "Population Mean (\\mu)",
            "Population Standard Deviation (\\sigma)": "Unknown",
            "Sample Size / Normality": "n = 11 (Severe skewness & extreme outliers present)"
        },
        "explanation_correct": (
            "**Correct! Neither parametric model is valid.** The $t$-distribution requires either an approximately "
            "normal population or a sufficiently large sample ($n \\ge 30$) to invoke the CLT. With $n = 11$ and extreme outliers, "
            "the normality assumption is severely violated. A non-parametric test (e.g., Wilcoxon-Mann-Whitney) or bootstrapping is required."
        ),
        "feedback_incorrect": {
            0: "❌ **Why Z is incorrect:** $\\sigma$ is unknown, and the sample size is far too small ($n = 11$) to apply the Central Limit Theorem to heavily skewed data.",
            1: "❌ **Why t is incorrect:** While $t$ is robust to mild non-normality, it fails in the presence of strong skewness combined with small sample sizes ($n < 15$) and extreme outliers. The sample mean and standard deviation become distorted."
        }
    },
    {
        "id": 5,
        "title": "Scenario 5: Political Polling & Proportions",
        "description": (
            "A national poll surveys $n = 1{,}000$ voters to estimate the proportion $p$ supporting a ballot measure. "
            "The sample proportion is $\\hat{p} = 0.53$."
        ),
        "options": [
            "Standard Normal Distribution (Z)",
            "Student's t-Distribution (t)",
            "Neither (Non-parametric / Bootstrap required)"
        ],
        "correct_idx": 0,
        "key_factors": {
            "Parameter": "Population Proportion (p)",
            "Standard Error": r"\sqrt{\hat{p}(1-\hat{p})/n}",
            "Success/Failure Condition": "np = 530 >= 10 and n(1-p) = 470 >= 10"
        },
        "explanation_correct": (
            "**Correct! Use the Z-distribution.** Categorical proportions **never use the t-distribution**. "
            "Inference for a population proportion relies on the normal approximation to the binomial distribution. "
            "Because $n\\hat{p} \\ge 10$ and $n(1 - \\hat{p}) \\ge 10$, the sampling distribution of $\\hat{p}$ is modeled using $Z$."
        ),
        "feedback_incorrect": {
            1: "❌ **Fundamental Rule:** Student's $t$ is used exclusively for quantitative continuous means ($\\mu$). It is never applied to categorical proportions ($p$).",
            2: "❌ **Why Neither is incorrect:** The large-sample success/failure condition ($n\\hat{p} \\ge 10$ and $n(1-\\hat{p}) \\ge 10$) is easily satisfied ($530 \\ge 10$ and $470 \\ge 10$)."
        }
    }
]

# --- SESSION STATE INITIALIZATION ---
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = {}

# --- SIDEBAR: CHEAT SHEET & NAVIGATION ---
st.sidebar.title("📚 Decision Assistant")

with st.sidebar.expander("🔍 Z vs. t Decision Framework", expanded=True):
    st.markdown(r"""
    **1. Is it a Mean ($\mu$) or a Proportion ($p$)?**
    * **Proportion ($p$):** Always **$Z$** *(verify $np \ge 10, n(1-p) \ge 10$)*. Never use $t$.
    * **Mean ($\mu$):** Move to Step 2.

    ---

    **2. Is the Population SD ($\sigma$) Known?**
    * **Yes:** Use **$Z$** *(requires normal population or $n \ge 30$)*.
    * **No (only sample $s$ is known):** Move to Step 3.

    ---

    **3. Does the data meet Normality Conditions?**
    * **$n \ge 30$:** Use **$t$ ($df = n-1$)** by Central Limit Theorem.
    * **$n < 30$ and roughly normal / symmetric:** Use **$t$ ($df = n-1$)**.
    * **$n < 30$ with heavy skew / outliers:** Use **Neither** *(non-parametric / bootstrap)*.
    """)

st.sidebar.divider()
total_questions = len(SCENARIOS)
completed = len(st.session_state.submitted)
st.sidebar.progress(completed / total_questions, text=f"Progress: {completed}/{total_questions} Completed")

if st.sidebar.button("🔄 Reset Quiz"):
    st.session_state.q_idx = 0
    st.session_state.user_answers = {}
    st.session_state.submitted = {}
    st.rerun()

# --- MAIN INTERFACE: TABS ---
tab_quiz, tab_viz = st.tabs(["📝 Practice Drill", "📊 Interactive Z vs. t Distribution Comparison"])

with tab_quiz:
    current_q = SCENARIOS[st.session_state.q_idx]

    col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])
    if col_nav1.button("⬅ Previous", disabled=(st.session_state.q_idx == 0)):
        st.session_state.q_idx -= 1
        st.rerun()
    col_nav2.markdown(f"<h3 style='text-align: center; margin: 0;'>Question {st.session_state.q_idx + 1} of {total_questions}</h3>", unsafe_allow_html=True)
    if col_nav3.button("Next ➡", disabled=(st.session_state.q_idx == total_questions - 1)):
        st.session_state.q_idx += 1
        st.rerun()

    st.markdown(f"### {current_q['title']}")
    st.info(current_q['description'])

    # Radio selection
    saved_answer = st.session_state.user_answers.get(current_q["id"], None)
    default_idx = current_q["options"].index(saved_answer) if saved_answer in current_q["options"] else 0

    selected_option = st.radio(
        "Which distribution should be used for inference?",
        options=current_q["options"],
        index=default_idx,
        key=f"radio_{current_q['id']}"
    )

    st.session_state.user_answers[current_q["id"]] = selected_option

    # Submit button
    if st.button("Check Answer", type="primary", key=f"btn_{current_q['id']}"):
        st.session_state.submitted[current_q["id"]] = True

    # Feedback Display
    if st.session_state.submitted.get(current_q["id"], False):
        chosen_idx = current_q["options"].index(selected_option)
        correct_idx = current_q["correct_idx"]

        st.divider()
        if chosen_idx == correct_idx:
            st.success(current_q["explanation_correct"])
        else:
            st.error(f"Incorrect selection: **{selected_option}**")
            st.markdown(current_q["feedback_incorrect"][chosen_idx])
            with st.expander("💡 View Complete Rationale"):
                st.markdown(current_q["explanation_correct"])

        # Structured breakdown of problem parameters
        st.markdown("#### Scenario Breakdown")
        cols = st.columns(len(current_q["key_factors"]))
        for col, (factor, val) in zip(cols, current_q["key_factors"].items()):
            col.metric(label=factor, value=val)

# --- VISUALIZER TAB ---
with tab_viz:
    st.subheader("Why the Degrees of Freedom Matter")
    st.markdown(
        "Because $\\sigma$ is estimated from data, the $t$-distribution accounts for added sampling variability "
        "by placing **more probability density into the tails**. As degrees of freedom ($df$) grow, the $t$-distribution converges to $Z$."
    )

    col_df, col_tail = st.columns([1, 1])
    df_val = col_df.slider("Select Degrees of Freedom (df):", min_value=1, max_value=60, value=3)
    alpha_level = col_tail.selectbox("Tail Significance Level (Two-sided $\\alpha$):", [0.10, 0.05, 0.01], index=1)

    # Compute critical values
    z_crit = stats.norm.ppf(1 - alpha_level / 2)
    t_crit = stats.t.ppf(1 - alpha_level / 2, df=df_val)

    # Render metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Standard Normal Critical Value ($z^*$)", f"±{z_crit:.3f}")
    m2.metric(f"Student's t Critical Value ($t^*_{{{df_val}}}$)", f"±{t_crit:.3f}")
    m3.metric("Tail Penalty (% Wider Margin)", f"+{((t_crit - z_crit) / z_crit) * 100:.1f}%")

    # Plot distributions
    x_axis = np.linspace(-4.5, 4.5, 600)
    y_norm = stats.norm.pdf(x_axis)
    y_t = stats.t.pdf(x_axis, df=df_val)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_axis, y=y_norm, mode='lines', name='Standard Normal (Z)', line=dict(color='#1f77b4', width=2.5)))
    fig.add_trace(go.Scatter(x=x_axis, y=y_t, mode='lines', name=f"Student's t (df = {df_val})", line=dict(color='#d62728', width=2.5, dash='dash')))

    # Highlight tail rejection area
    fig.add_vrect(x0=t_crit, x1=4.5, fillcolor="red", opacity=0.12, line_width=0, annotation_text=f"+t* ({t_crit:.2f})", annotation_position="top left")
    fig.add_vrect(x0=-4.5, x1=-t_crit, fillcolor="red", opacity=0.12, line_width=0, annotation_text=f"-t* ({-t_crit:.2f})", annotation_position="top right")

    fig.update_layout(
        title=f"Density Comparison: Standard Normal (Z) vs. Student's t (df = {df_val})",
        xaxis_title="Standard Deviations from Center",
        yaxis_title="Probability Density",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(yanchor="top", y=0.98, xanchor="right", x=0.98)
    )

    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)