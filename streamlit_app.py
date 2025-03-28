import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
import base64
import json

# Storage keys for offline capability
PROJECT_STORAGE_KEY = "tls_fieldwork_project"

st.set_page_config(page_title="TLS Fieldworks", layout="wide")
st.title("TLS Fieldwork Planner")

# Sidebar for navigation
view = st.sidebar.radio("Navigation", ["All Field Works", "Create/Edit Field Work"])

# Load saved fieldworks from local storage
if PROJECT_STORAGE_KEY in st.session_state:
    field_works = st.session_state[PROJECT_STORAGE_KEY]
else:
    field_works = {}

# Utility to create ID
create_id = lambda: f"fw_{int(datetime.datetime.utcnow().timestamp())}"

def save_projects():
    st.session_state[PROJECT_STORAGE_KEY] = field_works

def export_csv(data, filename):
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # B64 encode
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
    return href

if view == "All Field Works":
    st.subheader("All Field Works")
    if not field_works:
        st.info("No field works created yet.")
    else:
        for fw_id, fw in field_works.items():
            with st.expander(f"{fw['projectName']} ({fw_id})"):
                st.write(f"Plot Size: {fw['width']} x {fw['length']} m")
                st.write(f"Grid Size: {fw['gridSize']} m")
                st.markdown(export_csv(pd.DataFrame(fw['points']), f"{fw['projectName']}_{fw_id}.csv"), unsafe_allow_html=True)
                if st.button("Edit", key=f"edit_{fw_id}"):
                    st.session_state['edit_fw_id'] = fw_id
                    st.experimental_rerun()
                if st.button("Delete", key=f"delete_{fw_id}"):
                    field_works.pop(fw_id)
                    save_projects()
                    st.success("Deleted successfully.")
                    st.experimental_rerun()

if view == "Create/Edit Field Work":
    st.subheader("Create or Edit Field Work")
    editing = 'edit_fw_id' in st.session_state
    fw_data = field_works[st.session_state['edit_fw_id']] if editing else {}
    
    with st.form("field_form"):
        project_name = st.text_input("Project Name", value=fw_data.get("projectName", ""))
        width = st.number_input("Plot width (x, m)", value=fw_data.get("width", 0.0))
        length = st.number_input("Plot length (y, m)", value=fw_data.get("length", 0.0))
        grid_size = st.number_input("Grid Size (m)", value=fw_data.get("gridSize", 1.0))
        prefix = st.text_input("Prefix", value=fw_data.get("prefix", "ScanPos"))
        submitted = st.form_submit_button("Generate Grid")

    if submitted:
        points = []
        count = 1
        for i in range(int(width // grid_size) + 1):
            x = i * grid_size
            for j in range(int(length // grid_size) + 1):
                y = j * grid_size
                points.append({
                    "x": x,
                    "y": y,
                    "upright": f"{prefix}{str(count).zfill(3)}",
                    "tilt": f"{prefix}{str(count + 1).zfill(3)}",
                    "complete": False,
                    "completeTimestamp": "",
                    "notes": ""
                })
                count += 2

        fw_id = st.session_state['edit_fw_id'] if editing else create_id()
        field_works[fw_id] = {
            "id": fw_id,
            "projectName": project_name,
            "width": width,
            "length": length,
            "gridSize": grid_size,
            "prefix": prefix,
            "points": points
        }
        save_projects()
        st.success("Grid generated and field work saved.")
        st.session_state.pop('edit_fw_id', None)
        st.experimental_rerun()

    if editing:
        points_df = pd.DataFrame(fw_data["points"])
        edited_df = st.data_editor(points_df, num_rows="dynamic", use_container_width=True)
        if st.button("Save Changes"):
            field_works[st.session_state['edit_fw_id']]['points'] = edited_df.to_dict(orient="records")
            save_projects()
            st.success("Changes saved.")

        st.markdown(export_csv(edited_df, f"{fw_data['projectName']}_{fw_data['id']}.csv"), unsafe_allow_html=True)

        # Simple visualisation
        st.subheader("Scan Point Visualisation")
        import plotly.express as px
        fig = px.scatter(edited_df, x="x", y="y", color=edited_df["complete"].map(lambda x: "Complete" if x else "Incomplete"))
        st.plotly_chart(fig, use_container_width=True)
