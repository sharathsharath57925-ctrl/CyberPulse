
import streamlit as st
import pandas as pd
from datetime import datetime

from backend.url_scanner import analyze_url
from database.db import save_scan, get_history
from backend.email_scanner import analyze_email


# ---------- PAGE CONFIGURATION ----------
st.set_page_config(
    page_title="CyberPulse | Security Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- CUSTOM DESIGN ----------
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(ellipse at top right,
            #10243d 0%, #071426 42%, #050b16 100%);
        color: #edf5ff;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071426, #0b1830);
        border-right: 1px solid #183553;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #d6e5f8;
    }

    h1, h2, h3 {
        color: #f2f7ff !important;
        letter-spacing: -0.5px;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #102541, #0a172a);
        border: 1px solid #21496a;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.22);
    }

    [data-testid="stMetricLabel"] {
        color: #a9c3df !important;
    }

    [data-testid="stMetricValue"] {
        color: #42e8c4 !important;
        font-weight: 750;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #1b3958;
        border-radius: 14px;
    }

    .hero {
        background: linear-gradient(115deg, #102e4d, #10203c 60%, #102f3e);
        border: 1px solid #235777;
        border-radius: 18px;
        padding: 25px 28px;
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #f4f8ff;
        margin-bottom: 7px;
    }

    .hero-subtitle {
        color: #b3cce5;
        font-size: 14px;
    }

    .eyebrow {
        color: #42e8c4;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }

    .section-note {
        color: #94abc5;
        font-size: 13px;
    }

    .status-panel {
        background: #0c1c30;
        border: 1px solid #1b3958;
        border-radius: 14px;
        padding: 18px;
        margin: 10px 0;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 42px;
        border: 1px solid #236c7c;
        transition: all 0.2s ease;
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

    hr {
        border-color: #1b3958;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
def show_header():
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">SECURITY OPERATIONS CENTER</div>
        <div class="hero-title">🛡️ CyberPulse</div>
        <div class="hero-subtitle">
            Your digital safety command center.
            Monitor scans, review warnings, and explore security activity.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------- NAVIGATION ----------
st.sidebar.markdown("""
<div style="padding:12px 0 22px 0;">
    <div style="font-size:27px;font-weight:800;color:#42e8c4;">
        🛡️ CyberPulse
    </div>
    <div style="font-size:11px;letter-spacing:2px;color:#8ca9c8;">
        SECURITY CENTER
    </div>
</div>
""", unsafe_allow_html=True)


page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "LinkShield",
        "EmailGuard",
        "NetworkWatch",
        "Scan History",
    ]
)


st.sidebar.divider()
st.sidebar.markdown("""
<div style="color:#42e8c4;font-weight:700;">
    YOUR DIGITAL SAFETY
</div>
<div style="color:#91a9c4;font-size:13px;line-height:2;">
    Safer links.<br>
    Safer emails.<br>
    A safer digital world.
</div>
""", unsafe_allow_html=True)

show_header()

history = get_history() or []


# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.subheader("Security Overview")
    st.caption("A live view of scan records saved in your database.")

    total_scans = len(history)

    review_count = sum(
        1 for row in history if row[3] == "Review Needed"
    )
    invalid_count = sum(
        1 for row in history if row[3] == "Invalid"
    )
    no_warning_count = sum(
        1 for row in history
        if row[3] == "No Basic Warning Found"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("TOTAL SCANS", total_scans)

    with col2:
        st.metric("⚠️ REVIEW NEEDED", review_count)

    with col3:
        st.metric("✓ NO BASIC WARNING", no_warning_count)

    with col4:
        st.metric("INVALID INPUTS", invalid_count)

    st.write("")

    chart_col, summary_col = st.columns([1.6, 1])

    with chart_col:
        st.markdown("### 📈 Scan Activity")
        st.caption("Number of scans recorded by date.")

        if history:
            dated_scans = [
                {"Date": str(row[4])[:10], "Scans": 1}
                for row in history if row[4]
            ]

            if dated_scans:
                trend_df = pd.DataFrame(dated_scans)
                daily_scans = (
                    trend_df.groupby("Date")["Scans"]
                    .sum()
                    .sort_index()
                )
                st.line_chart(daily_scans, height=280)
            else:
                st.info("No dated scans available yet.")
        else:
            st.info("Your activity chart will appear after your first scan.")

    with summary_col:
        st.markdown("### 🎯 Result Distribution")
        st.caption("Breakdown of recorded scan results.")

        if total_scans:
            result_df = pd.DataFrame({
                "Result": [
                    "Review Needed",
                    "No Basic Warning",
                    "Invalid"
                ],
                "Count": [
                    review_count,
                    no_warning_count,
                    invalid_count
                ]
            }).set_index("Result")

            st.bar_chart(result_df, height=280)
        else:
            st.info("No results to display yet.")

    st.divider()
    st.markdown("### 🕒 Recent Scans")

    if history:
        recent_rows = [
            {
                "Type": row[1],
                "Target": row[2],
                "Result": row[3],
                "Date": row[4]
            }
            for row in history[:7]
        ]

        st.dataframe(
            pd.DataFrame(recent_rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No scans yet. Start with LinkShield.")

    st.markdown("""
    <div class="section-note">
        Security note: these metrics summarize basic scanner results.
        They do not represent confirmed cyberattacks or guarantee safety.
    </div>
    """, unsafe_allow_html=True)


# ---------- LINKSHIELD ----------
elif page == "LinkShield":
    st.subheader("🔗 LinkShield")
    st.caption("Analyze a URL for basic suspicious indicators.")

    with st.container(border=True):
        url = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter the website address you want to inspect."
        )

        if st.button("🔍 Analyze URL", type="primary",
                     use_container_width=True):
            if not url.strip():
                st.warning("Please enter a URL first.")
            else:
                status, message = analyze_url(url)

                if status == "Invalid":
                    st.error(message)
                elif status == "Review Needed":
                    st.warning(f"⚠️ {status}")
                    st.markdown("**Analysis details**")
                    st.code(message, language="text")
                else:
                    st.success(f"✓ {status}")
                    st.info(message)

                if status != "Invalid":
                    save_scan("LinkShield", url.strip(), status)

    st.caption(
        "Basic heuristic analysis only. A clean result does not prove "
        "a website is safe. Google Safe Browsing integration is still "
        "being configured."
    )


# ---------- EMAILGUARD ----------

elif page == "EmailGuard":
    st.subheader("✉️ EmailGuard")
    st.caption("Check email text for common phishing warning signs.")

    with st.container(border=True):
        sender = st.text_input(
            "Sender email (optional)",
            placeholder="example@company.com"
        )

        email_text = st.text_area(
            "Paste email text",
            placeholder=(
                "Example: Your account will be suspended. "
                "Click here to verify your password."
            ),
            height=180
        )

        if st.button(
            "🔍 Analyze Email",
            type="primary",
            use_container_width=True
        ):
            if not email_text.strip():
                st.warning("Please paste some email text first.")
            else:
                result = analyze_email(email_text, sender)

                status = result["status"]
                score = result["score"]
                findings = result["findings"]
                urls = result["urls"]

                st.markdown("### Analysis Result")

                if status == "High Risk":
                    st.error(f"🚨 {status}")
                elif status == "Review Needed":
                    st.warning(f"⚠️ {status}")
                else:
                    st.info(f"ℹ️ {status}")

                st.progress(score / 100)
                st.metric("Warning Score", f"{score}/100")

                st.markdown("### Findings")
                for finding in findings:
                    st.markdown(f"- {finding}")

                if urls:
                    st.markdown("### Links Found")
                    for url in urls:
                        st.code(url)

                save_scan(
                    "EmailGuard",
                    "Email text submitted for analysis",
                    status
                )

    st.caption(
        "This is a heuristic demonstration, not proof that an email is "
        "safe or malicious. Avoid pasting private or confidential emails."
    )


# ---------- NETWORK WATCH ----------
elif page == "NetworkWatch":
    import socket
    from collections import Counter
    from io import BytesIO

    st.subheader("🌐 NetworkWatch")
    st.caption(
        "View local network details and inspect packet-capture files."
    )

    # Local network information
    st.markdown("### 🖥️ Local Network Information")

    with st.container(border=True):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Device Name", hostname)

            with col2:
                st.metric("Local IP Address", local_ip)

            st.caption(
                "These are basic local device details. "
                "They do not show every device on your network."
            )

        except OSError:
            st.warning("Unable to retrieve local network information.")

    st.divider()

    # Packet capture analysis
    st.markdown("### 📡 Traffic Analysis")
    st.write(
        "Upload a packet-capture file to review packet counts "
        "and source addresses."
    )

    uploaded_file = st.file_uploader(
        "Upload network capture",
        type=["pcap", "pcapng"],
        key="networkwatch_capture"
    )

    if uploaded_file is not None:
        st.info(
            "Only upload captures you are authorized to inspect. "
            "Capture files may contain sensitive information."
        )

        if st.button(
            "🔍 Analyze Traffic",
            type="primary",
            use_container_width=True
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

                c1, c2, c3 = st.columns(3)

                c1.metric("Total Packets", packet_count)
                c2.metric("TCP Packets", tcp_count)
                c3.metric("UDP Packets", udp_count)

                c4, c5 = st.columns(2)
                c4.metric("ICMP Packets", icmp_count)
                c5.metric("Other Packets", other_count)

                if source_counts:
                    st.markdown("### Top Source Addresses")

                    source_data = [
                        {"Source IP": ip, "Packet Count": count}
                        for ip, count in source_counts.most_common(10)
                    ]

                    st.dataframe(
                        source_data,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(
                        "No IP source addresses were found in this capture."
                    )

                result_status = "Capture Analyzed"

                save_scan(
                    "NetworkWatch",
                    uploaded_file.name,
                    result_status
                )

                st.success(
                    "Capture analysis completed. "
                    "Packet counts alone do not establish malicious activity."
                )

            except ImportError:
                st.error(
                    "Packet analysis requires Scapy. "
                    "Install it using: python -m pip install scapy"
                )

            except Exception as exc:
                st.error(
                    "Unable to analyze this capture. "
                    "Check that the file is a valid, supported packet capture."
                )
                st.caption(f"Technical details: {exc}")

    st.caption(
        "NetworkWatch currently provides local device details and "
        "basic packet statistics. It does not perform continuous "
        "monitoring or confirm cyberattacks."
    )

# ---------- SCAN HISTORY ----------
elif page == "Scan History":
    st.subheader("📋 Scan History")
    st.caption("Browse the scan results saved by CyberPulse.")

    if history:
        history_data = [
            {
                "ID": row[0],
                "Type": row[1],
                "Target": row[2],
                "Result": row[3],
                "Date": row[4]
            }
            for row in history
        ]

        st.dataframe(
            pd.DataFrame(history_data),
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Total records: {len(history)}")
    else:
        st.info("No scan history is available yet.")

# ---------- NETWORK WATCH ----------
elif page == "NetworkWatch":
    import socket
    from collections import Counter
    from io import BytesIO

    st.subheader("🌐 NetworkWatch")
    st.caption(
        "View local network details and inspect packet-capture files."
    )

    # Local network information
    st.markdown("### 🖥️ Local Network Information")

    with st.container(border=True):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Device Name", hostname)

            with col2:
                st.metric("Local IP Address", local_ip)

            st.caption(
                "These are basic local device details. "
                "They do not show every device on your network."
            )

        except OSError:
            st.warning("Unable to retrieve local network information.")

    st.divider()

    # Packet capture analysis
    st.markdown("### 📡 Traffic Analysis")
    st.write(
        "Upload a packet-capture file to review packet counts "
        "and source addresses."
    )

    uploaded_file = st.file_uploader(
        "Upload network capture",
        type=["pcap", "pcapng"],
        key="networkwatch_capture"
    )

    if uploaded_file is not None:
        st.info(
            "Only upload captures you are authorized to inspect. "
            "Capture files may contain sensitive information."
        )

        if st.button(
            "🔍 Analyze Traffic",
            type="primary",
            use_container_width=True
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

                c1, c2, c3 = st.columns(3)

                c1.metric("Total Packets", packet_count)
                c2.metric("TCP Packets", tcp_count)
                c3.metric("UDP Packets", udp_count)

                c4, c5 = st.columns(2)
                c4.metric("ICMP Packets", icmp_count)
                c5.metric("Other Packets", other_count)

                if source_counts:
                    st.markdown("### Top Source Addresses")

                    source_data = [
                        {"Source IP": ip, "Packet Count": count}
                        for ip, count in source_counts.most_common(10)
                    ]

                    st.dataframe(
                        source_data,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(
                        "No IP source addresses were found in this capture."
                    )

                result_status = "Capture Analyzed"

                save_scan(
                    "NetworkWatch",
                    uploaded_file.name,
                    result_status
                )

                st.success(
                    "Capture analysis completed. "
                    "Packet counts alone do not establish malicious activity."
                )

            except ImportError:
                st.error(
                    "Packet analysis requires Scapy. "
                    "Install it using: python -m pip install scapy"
                )

            except Exception as exc:
                st.error(
                    "Unable to analyze this capture. "
                    "Check that the file is a valid, supported packet capture."
                )
                st.caption(f"Technical details: {exc}")

    st.caption(
        "NetworkWatch currently provides local device details and "
        "basic packet statistics. It does not perform continuous "
        "monitoring or confirm cyberattacks."
    )
