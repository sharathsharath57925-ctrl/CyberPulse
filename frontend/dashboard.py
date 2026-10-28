
import socket
from collections import Counter
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.url_scanner import analyze_url
from backend.email_scanner import analyze_email
from database.db import save_scan, get_history


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="CyberPulse | Security Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# FUTURISTIC DARK THEME
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background:
            radial-gradient(ellipse at 85% 0%, #102b48 0%, transparent 40%),
            linear-gradient(135deg, #050b16, #091426 55%, #07101e);
        color: #e8f1ff;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07101f, #0a1930);
        border-right: 1px solid #193650;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #c3d6ec;
    }

    h1, h2, h3 {
        color: #f1f7ff !important;
        letter-spacing: -0.5px;
    }

    p, label, .stCaption {
        color: #b5c8df;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #112944, #0b192c);
        border: 1px solid #244866;
        padding: 19px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, .18);
    }

    [data-testid="stMetricLabel"] {
        color: #a9c3df !important;
        font-size: 12px;
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        color: #42e8c4 !important;
        font-weight: 800;
    }

    .hero {
        background: linear-gradient(115deg, #102b49, #101d36 60%, #10323d);
        border: 1px solid #285571;
        border-radius: 20px;
        padding: 28px;
        margin: 4px 0 28px 0;
        box-shadow: 0 12px 35px rgba(0, 0, 0, .20);
    }

    .hero-label {
        color: #42e8c4;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 10px;
    }

    .hero-title {
        color: #f3f8ff;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-description {
        color: #b5cce5;
        font-size: 14px;
        line-height: 1.7;
    }

    .section-label {
        color: #42e8c4;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
    }

    .small-note {
        color: #8fa8c4;
        font-size: 12px;
        line-height: 1.7;
    }

    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid #28677a;
        transition: all .2s ease;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #087e8b, #0ba98e);
        color: white;
        border: none;
    }

    .stButton > button:hover {
        border-color: #42e8c4;
        color: white;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #1b3958;
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #1b3958;
        border-radius: 15px;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #0c1b2e;
        border-color: #284762;
    }

    hr {
        border-color: #203b56;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <div class="hero-label">SECURITY OPERATIONS CENTER</div>
    <div class="hero-title">🛡️ CyberPulse</div>
    <div class="hero-description">
        Your digital safety command center.<br>
        Analyze suspicious links, inspect email warning signs,
        and review network packet captures in one place.
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
st.sidebar.markdown("""
<div style="padding: 10px 0 20px 0;">
    <div style="font-size:27px;font-weight:800;color:#42e8c4;">
        🛡️ CyberPulse
    </div>
    <div style="font-size:11px;letter-spacing:2px;color:#8ca9c8;">
        SECURITY CENTER
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- CYBERPULSE INTERACTIVE NAVIGATION ----------

# ---------- CYBERPULSE INTERACTIVE NAVIGATION ----------

# Modern animated navigation card styling
st.markdown("""
<style>
/* Navigation section heading */
.nav-section-title {
    display: flex;
    align-items: center;
    gap: 9px;
    padding-left: 10px;
    margin: 18px 0 12px;
    color: #8da4bc;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
}

.nav-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #42e8c4;
    box-shadow: 0 0 8px #42e8c480;
}

/* Navigation cards only */
section[data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    min-height: 58px;
    padding: 12px 14px;
    margin: 3px 0;
    border: 1px solid #20384f;
    border-radius: 12px;
    background: linear-gradient(135deg, #101e30, #0b1524);
    color: #dce9f7;
    font-size: 14px;
    font-weight: 600;
    text-align: left;
    transition: background 180ms ease,
                border-color 180ms ease,
                transform 180ms ease,
                box-shadow 180ms ease;
}

/* Hover animation */
section[data-testid="stSidebar"] div.stButton > button:hover {
    background: linear-gradient(135deg, #12334a, #10243a);
    border-color: #42e8c4;
    color: #ffffff;
    transform: translateX(3px);
    box-shadow: 0 0 12px #42e8c420;
}

/* Active navigation card */
section[data-testid="stSidebar"]
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #123e55, #102a40);
    border: 1px solid #42e8c4;
    color: #42e8c4;
    box-shadow: 0 0 12px #42e8c418;
}

/* Smooth keyboard focus */
section[data-testid="stSidebar"] div.stButton > button:focus-visible {
    outline: 2px solid #42e8c4;
    outline-offset: 2px;
}
</style>
""", unsafe_allow_html=True)

NAV_ITEMS = {
    "Dashboard": "🏠  Dashboard",
    "LinkShield": "🛡️  LinkShield · URL Scanner",
    "EmailGuard": "✉️  EmailGuard · Phishing",
    "NetworkWatch": "🌐  NetworkWatch · Network",
    "Scan History": "📊  Scan History",
}

# Keep track of the active page
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

with st.sidebar:
    st.markdown("""
        <div class="nav-section-title">
            <span class="nav-dot"></span>
            SECURITY MODULES
        </div>
    """, unsafe_allow_html=True)

    for page_name, card_label in NAV_ITEMS.items():
        selected = st.session_state.active_page == page_name

        if st.button(
            card_label,
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            st.session_state.active_page = page_name
            st.rerun()

page = st.session_state.active_page

# ---------- END NAVIGATION ----------

if page == "Dashboard":
    # Keep your existing dashboard code here
    ...

elif page == "LinkShield":
    # Keep your existing URL scanner code here
    ...

elif page == "EmailGuard":
    # Keep your existing email scanner code here
    ...

elif page == "NetworkWatch":
    # Keep your existing network analysis code here
    ...

elif page == "Scan History":
    # Keep your existing scan history code here
    ...
# =========================================================
# LOAD DATABASE HISTORY
# =========================================================
history = get_history() or []

# Expected database row format:
# ID, scan_type, target, status, timestamp


# =========================================================
# HELPER: DISPLAY SCAN HISTORY
# =========================================================
def history_dataframe(rows):
    return pd.DataFrame([
        {
            "ID": row[0],
            "Type": row[1],
            "Target": row[2],
            "Result": row[3],
            "Date": row[4],
        }
        for row in rows
    ])


# =========================================================
# HELPER: CLASSIFY SAVED RESULTS
# =========================================================
def is_review_result(status):
    status = str(status).lower()
    return (
        status in {"review needed", "medium risk", "high risk"}
        or "suspicious" in status
    )


def is_invalid_result(status):
    return str(status).lower() == "invalid"


def is_low_warning_result(status):
    status = str(status).lower()
    return status in {
        "no basic warning found",
        "low risk",
        "no indicators found",
    }


# =========================================================

# =========================================================
# DASHBOARD
# =========================================================
if page == "Dashboard":

    st.markdown(
        '<div class="section-label">OVERVIEW</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Security Dashboard")
    st.caption("Your cybersecurity activity at a glance.")

    # Refresh saved database records
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

    # Result classification from actual saved records
    statuses = [str(row[3]).strip().lower() for row in history]

    total_scans = len(history)

    high_count = statuses.count("high risk")
    medium_count = statuses.count("medium risk")
    low_count = sum(
        status in {
            "low risk",
            "no indicators found",
            "no basic warning found",
        }
        for status in statuses
    )
    review_count = statuses.count("review needed")
    invalid_count = statuses.count("invalid")

    classified_count = (
        high_count + medium_count + low_count
        + review_count + invalid_count
    )
    other_count = max(0, total_scans - classified_count)

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("TOTAL SCANS", total_scans)
    c2.metric("🔴 HIGH RISK", high_count)
    c3.metric("🟠 MEDIUM RISK", medium_count)
    c4.metric("⚠️ REVIEW NEEDED", review_count)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🟢 LOW-WARNING RESULTS", low_count)
    c2.metric("❌ INVALID INPUTS", invalid_count)
    c3.metric("📦 OTHER RESULTS", other_count)

    network_scans = sum(
        1 for row in history if row[1] == "NetworkWatch"
    )
    c4.metric("🌐 NETWORK CAPTURES", network_scans)

    st.divider()

    # Scan activity and result distribution
    chart_col, result_col = st.columns([1.5, 1])

    with chart_col:
        st.markdown("### 📈 Scan Activity")
        st.caption("Number of saved scans per date.")

        dated_rows = [
            {"Date": str(row[4])[:10], "Scans": 1}
            for row in history
            if len(row) > 4 and row[4]
        ]

        if dated_rows:
            activity_df = pd.DataFrame(dated_rows)
            daily_activity = (
                activity_df.groupby("Date")["Scans"]
                .sum()
                .sort_index()
            )
            st.line_chart(daily_activity, height=300)
        else:
            st.info("Scan activity will appear after your first scan.")

    with result_col:
        st.markdown("### 🎯 Result Distribution")
        st.caption("Classification of saved scan results.")

        distribution_df = pd.DataFrame({
            "Result": [
                "High Risk",
                "Medium Risk",
                "Low Warning",
                "Review Needed",
                "Invalid",
                "Other",
            ],
            "Count": [
                high_count,
                medium_count,
                low_count,
                review_count,
                invalid_count,
                other_count,
            ],
        }).set_index("Result")

        if total_scans:
            st.bar_chart(distribution_df, height=300)
        else:
            st.info("No results to display yet.")

    st.divider()

    # Module activity
    st.markdown("### 🧩 Module Activity")

    module_names = [
        "LinkShield",
        "EmailGuard",
        "NetworkWatch",
    ]

    module_counts = {
        name: sum(1 for row in history if row[1] == name)
        for name in module_names
    }

    m1, m2, m3 = st.columns(3)

    m1.metric("🔗 LinkShield", module_counts["LinkShield"])
    m2.metric("✉️ EmailGuard", module_counts["EmailGuard"])
    m3.metric("🌐 NetworkWatch", module_counts["NetworkWatch"])

    module_df = pd.DataFrame({
        "Module": module_names,
        "Scans": [module_counts[name] for name in module_names],
    }).set_index("Module")

    if total_scans:
        st.bar_chart(module_df, height=200)

    st.divider()

    
    # Scan modules
    
    


# =========================================================
# LINKSHIELD
# =========================================================
elif page == "LinkShield":

    st.subheader("🔗 LinkShield")
    st.caption("Analyze a website address for basic suspicious indicators.")

    with st.container(border=True):
        st.markdown("### URL Analysis")

        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the URL you want to inspect.",
        )

        if st.button(
            "🔍 Analyze URL",
            type="primary",
            use_container_width=True,
        ):
            if not url.strip():
                st.warning("Please enter a URL first.")
            else:
                try:
                    status, message = analyze_url(url.strip())

                    st.markdown("### Analysis Result")

                    if status == "Invalid":
                        st.error(f"❌ {status}")
                    elif status == "Review Needed":
                        st.warning(f"⚠️ {status}")
                    else:
                        st.success(f"✓ {status}")

                    st.markdown("**Analysis details**")
                    st.code(str(message), language="text")

                    if status != "Invalid":
                        save_scan("LinkShield", url.strip(), status)
                        st.caption("Result saved to Scan History.")

                except Exception as exc:
                    st.error("The URL could not be analyzed.")
                    st.caption(f"Technical details: {exc}")

    st.info(
        "A basic scan cannot prove a website is safe. "
        "Avoid entering passwords or personal information on suspicious sites."
    )


# =========================================================
# EMAILGUARD
# =========================================================
elif page == "EmailGuard":

    st.subheader("✉️ EmailGuard")
    st.caption("Check email text for common phishing warning signs.")

    with st.container(border=True):

        sender = st.text_input(
            "Sender email (optional)",
            placeholder="example@company.com",
        )

        email_text = st.text_area(
            "Paste email text",
            placeholder=(
                "Example: Your account needs attention. "
                "Please verify your details."
            ),
            height=190,
        )

        if st.button(
            "🔍 Analyze Email",
            type="primary",
            use_container_width=True,
        ):
            if not email_text.strip():
                st.warning("Please paste some email text first.")
            else:
                try:
                    result = analyze_email(email_text, sender)

                    status = result["status"]
                    score = result["score"]
                    findings = result["findings"]
                    urls = result["urls"]

                    st.markdown("### Analysis Result")

                    if status == "High Risk":
                        st.error(f"🚨 {status}")
                    elif status in {"Review Needed", "Medium Risk"}:
                        st.warning(f"⚠️ {status}")
                    elif status == "Invalid":
                        st.error(f"❌ {status}")
                    else:
                        st.info(f"ℹ️ {status}")

                    st.metric("Warning Score", f"{score}/100")
                    st.progress(max(0.0, min(1.0, float(score) / 100)))

                    st.markdown("### Findings")

                    if findings:
                        for finding in findings:
                            st.markdown(f"- {finding}")
                    else:
                        st.write("No findings were returned by the scanner.")

                    if urls:
                        st.markdown("### Links Found")
                        for found_url in urls:
                            st.code(str(found_url), language="text")

                    save_scan(
                        "EmailGuard",
                        "Email text submitted for analysis",
                        status,
                    )

                    st.caption("Result saved to Scan History.")

                except Exception as exc:
                    st.error("The email could not be analyzed.")
                    st.caption(f"Technical details: {exc}")

    st.info(
        "This tool uses basic indicators and cannot guarantee that an "
        "email is safe or malicious. Avoid pasting private or confidential emails."
    )


# =========================================================
# NETWORKWATCH
# =========================================================
elif page == "NetworkWatch":

    st.subheader("🌐 NetworkWatch")
    st.caption("View local device information and inspect packet captures.")

    # Local device information
    st.markdown("### 🖥️ Local Network Information")

    with st.container(border=True):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            n1, n2 = st.columns(2)
            n1.metric("Device Name", hostname)
            n2.metric("Local IP Address", local_ip)

        except OSError:
            st.warning("Unable to retrieve local network information.")

        st.caption(
            "These details describe this computer; they do not list "
            "every device connected to your network."
        )

    st.divider()

    # Packet capture upload
    st.markdown("### 📡 Traffic Analysis")
    st.write(
        "Upload a PCAP or PCAPNG file to count packets and review source addresses."
    )

    uploaded_file = st.file_uploader(
        "Upload network capture",
        type=["pcap", "pcapng"],
        key="networkwatch_capture",
    )

    if uploaded_file is not None:
        st.warning(
            "Only analyze capture files you are authorized to inspect. "
            "Packet captures may contain sensitive information."
        )

        if st.button(
            "🔍 Analyze Traffic",
            type="primary",
            use_container_width=True,
        ):
            try:
                from scapy.utils import PcapReader
                from scapy.layers.inet import IP, TCP, UDP, ICMP
                from scapy.layers.inet6 import IPv6

                packet_count = 0
                tcp_count = 0
                udp_count = 0
                icmp_count = 0
                other_count = 0
                source_counts = Counter()

                capture = BytesIO(uploaded_file.getvalue())

                with PcapReader(capture) as packets:
                    for packet in packets:
                        packet_count += 1

                        if IP in packet:
                            source_counts[packet[IP].src] += 1
                        elif IPv6 in packet:
                            source_counts[packet[IPv6].src] += 1

                        if TCP in packet:
                            tcp_count += 1
                        elif UDP in packet:
                            udp_count += 1
                        elif ICMP in packet:
                            icmp_count += 1
                        else:
                            other_count += 1

                st.markdown("### Analysis Results")

                p1, p2, p3 = st.columns(3)
                p1.metric("Total Packets", packet_count)
                p2.metric("TCP Packets", tcp_count)
                p3.metric("UDP Packets", udp_count)

                p4, p5 = st.columns(2)
                p4.metric("ICMP Packets", icmp_count)
                p5.metric("Other Packets", other_count)

                protocol_df = pd.DataFrame({
                    "Protocol": ["TCP", "UDP", "ICMP", "Other"],
                    "Packets": [
                        tcp_count,
                        udp_count,
                        icmp_count,
                        other_count,
                    ],
                }).set_index("Protocol")

                st.markdown("### Protocol Distribution")
                st.bar_chart(protocol_df)

                if source_counts:
                    st.markdown("### Top Source Addresses")

                    source_data = [
                        {"Source IP": ip, "Packet Count": count}
                        for ip, count in source_counts.most_common(10)
                    ]

                    st.dataframe(
                        pd.DataFrame(source_data),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("No IP source addresses were found in this capture.")

                save_scan(
                    "NetworkWatch",
                    uploaded_file.name,
                    "Capture Analyzed",
                )

                st.success("Capture analysis completed and saved to Scan History.")

            except ImportError:
                st.error(
                    "Scapy is required. Install it with: "
                    "python -m pip install scapy"
                )

            except Exception as exc:
                st.error(
                    "Unable to analyze this file. "
                    "Check that it is a valid, supported packet capture."
                )
                st.caption(f"Technical details: {exc}")

    st.info(
        "NetworkWatch displays packet statistics. It does not continuously "
        "monitor your network or confirm malicious activity."
    )


# =========================================================
# SCAN HISTORY
# =========================================================
elif page == "Scan History":

    st.subheader("📋 Scan History")
    st.caption("Browse results saved by CyberPulse.")

    if history:

        # Search and filter
        search_text = st.text_input(
            "🔎 Search by target or result",
            placeholder="Enter a URL, filename, or result...",
        )

        available_types = sorted(set(str(row[1]) for row in history))

        selected_types = st.multiselect(
            "Filter by module",
            options=available_types,
            default=available_types,
        )

        filtered_rows = [
            row for row in history
            if row[1] in selected_types
            and search_text.lower() in (
                str(row[2]) + " " + str(row[3])
            ).lower()
        ]

        st.metric("Matching Records", len(filtered_rows))

        if filtered_rows:
            st.dataframe(
                history_dataframe(filtered_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No records match your search or filters.")

    else:
        st.info("No scan history is available yet. Run a scan first.")

    st.caption(
        "History displays saved scanner results; it does not independently "
        "verify whether a target is malicious."
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.markdown("""
<div style="text-align:center; padding:10px 0 20px 0;">
    <div style="color:#42e8c4;font-weight:800;letter-spacing:2px;">
        🛡️ CYBERPULSE
    </div>
    <div style="color:#8199b5;font-size:11px;margin-top:5px;">
        Student Cybersecurity Dashboard · Educational Use
    </div>
</div>
""", unsafe_allow_html=True)
