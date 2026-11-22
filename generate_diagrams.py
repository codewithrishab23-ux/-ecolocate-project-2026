"""
Generate professional academic diagrams for EcoLocate Project Report matching the sample PDF style.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

diag_dir = os.path.join(os.path.dirname(__file__), 'report_assets', 'diagrams')
os.makedirs(diag_dir, exist_ok=True)

# 1. Figure 8.1: Project Timeline (Gantt Chart)
def make_fig_8_1():
    fig, ax = plt.subplots(figsize=(8, 3.5), dpi=300)
    tasks = [
        "Phase 1: Problem Identification & Requirement Analysis",
        "Phase 2: System Planning & Database Design",
        "Phase 3: Frontend & Backend Development",
        "Phase 4: Module Integration, Testing & Debugging",
        "Phase 5: Documentation, Final Review & Submission"
    ]
    starts = [0, 1, 2, 3, 4]
    durations = [1, 1, 1, 1, 1]
    colors = ['#2E75B6', '#2E75B6', '#2E75B6', '#2E75B6', '#2E75B6']
    
    y_pos = range(len(tasks)-1, -1, -1)
    ax.barh(y_pos, durations, left=starts, height=0.5, color=colors, edgecolor='#1F4E79')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=9, fontfamily='serif')
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_xticklabels(['Start', 'Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'], fontsize=9, fontfamily='serif')
    ax.set_xlabel('Project Timeline Schedule', fontsize=10, fontweight='bold', fontfamily='serif')
    ax.set_title('Figure 8.1: EcoLocate Project Timeline (5-Week Schedule)', fontsize=11, fontweight='bold', fontfamily='serif', pad=12)
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_8_1_timeline.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_8_1_timeline.png')

# 2. Figure 9.1: System Architecture (3-Layer)
def make_fig_9_1():
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    ax.axis('off')

    # Bounding boxes
    # Presentation Layer
    p_box = patches.FancyBboxPatch((0.08, 0.68), 0.84, 0.26, boxstyle="round,pad=0.02",
                                   ec="#2E75B6", fc="#F2F7FA", ls="--", lw=1.5)
    ax.add_patch(p_box)
    ax.text(0.5, 0.90, "Presentation Layer (Client Browser)", ha="center", va="center",
            fontsize=11, fontweight="bold", fontfamily="serif", color="#1F4E79")
    
    # Presentation boxes
    b1 = patches.FancyBboxPatch((0.12, 0.72), 0.36, 0.13, boxstyle="round,pad=0.02", ec="#2E75B6", fc="#FFFFFF", lw=1)
    ax.add_patch(b1)
    ax.text(0.30, 0.785, "Interactive Leaflet.js Map\n& Client Geolocation API", ha="center", va="center", fontsize=9, fontfamily="serif")

    b2 = patches.FancyBboxPatch((0.52, 0.72), 0.36, 0.13, boxstyle="round,pad=0.02", ec="#2E75B6", fc="#FFFFFF", lw=1)
    ax.add_patch(b2)
    ax.text(0.70, 0.785, "HTML5 / CSS3 / Vanilla JS\nResponsive Search & Dashboards", ha="center", va="center", fontsize=9, fontfamily="serif")

    # Application Layer
    a_box = patches.FancyBboxPatch((0.08, 0.35), 0.84, 0.27, boxstyle="round,pad=0.02",
                                   ec="#385723", fc="#F4F8F1", ls="--", lw=1.5)
    ax.add_patch(a_box)
    ax.text(0.5, 0.58, "Application Layer (Python Flask Web Server)", ha="center", va="center",
            fontsize=11, fontweight="bold", fontfamily="serif", color="#274015")

    b3 = patches.FancyBboxPatch((0.12, 0.39), 0.23, 0.13, boxstyle="round,pad=0.02", ec="#385723", fc="#FFFFFF", lw=1)
    ax.add_patch(b3)
    ax.text(0.235, 0.455, "Authentication &\nSession Management\n(Werkzeug Hashing)", ha="center", va="center", fontsize=8.5, fontfamily="serif")

    b4 = patches.FancyBboxPatch((0.385, 0.39), 0.23, 0.13, boxstyle="round,pad=0.02", ec="#385723", fc="#FFFFFF", lw=1)
    ax.add_patch(b4)
    ax.text(0.50, 0.455, "Haversine Engine &\nGeospatial Filter\n(/api/centres/nearby)", ha="center", va="center", fontsize=8.5, fontfamily="serif")

    b5 = patches.FancyBboxPatch((0.65, 0.39), 0.23, 0.13, boxstyle="round,pad=0.02", ec="#385723", fc="#FFFFFF", lw=1)
    ax.add_patch(b5)
    ax.text(0.765, 0.455, "Admin CRUD, CSV\n& User Activity Engine\n(db.py Connection Pool)", ha="center", va="center", fontsize=8.5, fontfamily="serif")

    # Data Layer
    d_box = patches.FancyBboxPatch((0.18, 0.05), 0.64, 0.22, boxstyle="round,pad=0.02",
                                   ec="#C55A11", fc="#FDF5EE", ls="--", lw=1.5)
    ax.add_patch(d_box)
    ax.text(0.5, 0.23, "Data Layer (MySQL ewaste_db Server)", ha="center", va="center",
            fontsize=11, fontweight="bold", fontfamily="serif", color="#833C0C")

    cyl = patches.FancyBboxPatch((0.24, 0.08), 0.52, 0.11, boxstyle="round,pad=0.02", ec="#C55A11", fc="#FFFFFF", lw=1.2)
    ax.add_patch(cyl)
    ax.text(0.5, 0.135, "ewaste_db: centres, users, admins,\ndevices, rewards_history, user_activity", ha="center", va="center", fontsize=9, fontfamily="serif")

    # Arrows
    ax.annotate('', xy=(0.5, 0.68), xytext=(0.5, 0.62), arrowprops=dict(arrowstyle="<->", color="#1F4E79", lw=1.5))
    ax.text(0.52, 0.65, "HTTP / JSON REST API", fontsize=8, fontfamily="serif", color="#1F4E79")

    ax.annotate('', xy=(0.5, 0.35), xytext=(0.5, 0.27), arrowprops=dict(arrowstyle="<->", color="#385723", lw=1.5))
    ax.text(0.52, 0.31, "Thread-Safe MySQL Connection Pool (Port 3307)", fontsize=8, fontfamily="serif", color="#385723")

    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_9_1_architecture.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_9_1_architecture.png')

# 3. Figure 9.2: Use Case Diagram
def make_fig_9_2():
    fig, ax = plt.subplots(figsize=(8, 6.2), dpi=300)
    ax.axis('off')

    # Actors
    ax.text(0.12, 0.78, "Citizen / Guest\nUser", ha="center", va="center", fontsize=10, fontweight="bold", fontfamily="serif",
            bbox=dict(boxstyle="round,pad=0.5", fc="#D9E1F2", ec="#2E75B6", lw=1.5))
    
    ax.text(0.12, 0.48, "Registered\nUser", ha="center", va="center", fontsize=10, fontweight="bold", fontfamily="serif",
            bbox=dict(boxstyle="round,pad=0.5", fc="#E2EFDA", ec="#385723", lw=1.5))

    ax.text(0.12, 0.18, "System\nAdministrator", ha="center", va="center", fontsize=10, fontweight="bold", fontfamily="serif",
            bbox=dict(boxstyle="round,pad=0.5", fc="#FCE4D6", ec="#C55A11", lw=1.5))

    # Use cases (Ovals)
    use_cases = [
        (0.65, 0.90, "Search Recycling Centres (State/City/Device)"),
        (0.65, 0.81, "Detect Nearest Centres via Geolocation"),
        (0.65, 0.72, "View Interactive Leaflet Map & Directions"),
        (0.65, 0.63, "Explore E-Waste Hazards & Guidelines"),
        (0.65, 0.54, "Calculate Recycling Reward Points"),
        (0.65, 0.45, "User Registration & Login Authentication"),
        (0.65, 0.36, "Save & View Personal Rewards History"),
        (0.65, 0.27, "Admin Dashboard Analytics (Chart.js)"),
        (0.65, 0.18, "Manage Recycling Centres (CRUD & Verification)"),
        (0.65, 0.09, "Ingest CPCB Facilities via Batch CSV"),
        (0.65, 0.00, "Monitor Live User Activity & Search Analytics")
    ]

    for x, y, title in use_cases:
        patch = patches.FancyBboxPatch((x-0.25, y-0.032), 0.50, 0.064, boxstyle="round,pad=0.02",
                                      fc="#FFFFFF", ec="#595959", lw=1)
        ax.add_patch(patch)
        ax.text(x, y, title, ha="center", va="center", fontsize=8.2, fontfamily="serif")

    # Connect Citizen (0.12, 0.78)
    for idx in [0, 1, 2, 3, 4, 5]:
        ax.plot([0.18, 0.40], [0.78, use_cases[idx][1]], color="#2E75B6", lw=1, ls="-")

    # Connect Registered User (0.12, 0.48)
    for idx in [0, 1, 2, 3, 4, 5, 6]:
        ax.plot([0.18, 0.40], [0.48, use_cases[idx][1]], color="#385723", lw=1, ls="-")

    # Connect Administrator (0.12, 0.18)
    for idx in [7, 8, 9, 10]:
        ax.plot([0.18, 0.40], [0.18, use_cases[idx][1]], color="#C55A11", lw=1, ls="-")

    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_9_2_use_case.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_9_2_use_case.png')

# 4. Figure 9.3: DFD Level 0 (Context Diagram)
def make_fig_9_3():
    fig, ax = plt.subplots(figsize=(8, 5.0), dpi=300)
    ax.axis('off')

    # Central process
    circle = plt.Circle((0.5, 0.5), 0.18, fc="#D9E1F2", ec="#2E75B6", lw=2)
    ax.add_patch(circle)
    ax.text(0.5, 0.52, "0.0\nEcoLocate\nE-Waste Locator\nSystem", ha="center", va="center",
            fontsize=10.5, fontweight="bold", fontfamily="serif")

    # External Entities
    # Citizen User
    ax.text(0.12, 0.80, "Citizen User\n(Public)", ha="center", va="center", fontsize=9.5, fontweight="bold", fontfamily="serif",
            bbox=dict(boxstyle="square,pad=0.5", fc="#FFFFFF", ec="#2E75B6", lw=1.5))
    
    # Registered User
    ax.text(0.12, 0.20, "Registered\nUser", ha="center", va="center", fontsize=9.5, fontweight="bold", fontfamily="serif",
            bbox=dict(boxstyle="square,pad=0.5", fc="#FFFFFF", ec="#385723", lw=1.5))

    # Administrator
    ax.text(0.88, 0.50, "Platform\nAdministrator", ha="center", va="center", fontsize=9.5, fontweight="bold", fontfamily="serif",
            bbox=dict(boxstyle="square,pad=0.5", fc="#FFFFFF", ec="#C55A11", lw=1.5))

    # Flow arrows
    # Citizen -> Process
    ax.annotate("Search params & coordinates", xy=(0.38, 0.60), xytext=(0.20, 0.77),
                arrowprops=dict(arrowstyle="->", color="#2E75B6", lw=1.2), fontsize=8, fontfamily="serif")
    ax.annotate("Centres, map pins & distances", xy=(0.20, 0.73), xytext=(0.35, 0.54),
                arrowprops=dict(arrowstyle="->", color="#2E75B6", lw=1.2), fontsize=8, fontfamily="serif")

    # User -> Process
    ax.annotate("Credentials & reward saves", xy=(0.38, 0.40), xytext=(0.20, 0.24),
                arrowprops=dict(arrowstyle="->", color="#385723", lw=1.2), fontsize=8, fontfamily="serif")
    ax.annotate("Session & calculation history", xy=(0.20, 0.20), xytext=(0.35, 0.35),
                arrowprops=dict(arrowstyle="->", color="#385723", lw=1.2), fontsize=8, fontfamily="serif")

    # Admin -> Process
    ax.annotate("Centre CRUD & CSV batch file", xy=(0.68, 0.53), xytext=(0.80, 0.55),
                arrowprops=dict(arrowstyle="->", color="#C55A11", lw=1.2), fontsize=8, fontfamily="serif")
    ax.annotate("Audit logs & dashboard metrics", xy=(0.80, 0.45), xytext=(0.68, 0.47),
                arrowprops=dict(arrowstyle="->", color="#C55A11", lw=1.2), fontsize=8, fontfamily="serif")

    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_9_3_dfd_level0.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_9_3_dfd_level0.png')

# 5. Figure 9.4: DFD Level 1
def make_fig_9_4():
    fig, ax = plt.subplots(figsize=(8, 6.0), dpi=300)
    ax.axis('off')

    # Processes
    procs = [
        (0.25, 0.82, "1.0 User\nAuthentication"),
        (0.70, 0.82, "2.0 Facility\nSearch & Maps"),
        (0.25, 0.48, "3.0 EcoRewards\nCalculation"),
        (0.70, 0.48, "4.0 Facility\nManagement"),
        (0.48, 0.18, "5.0 User Activity\nTracking & Logs")
    ]
    for x, y, title in procs:
        circ = plt.Circle((x, y), 0.10, fc="#F2F7FA", ec="#2E75B6", lw=1.5)
        ax.add_patch(circ)
        ax.text(x, y, title, ha="center", va="center", fontsize=8.5, fontweight="bold", fontfamily="serif")

    # Data Stores
    stores = [
        (0.48, 0.82, "D1: users"),
        (0.90, 0.48, "D2: centres"),
        (0.08, 0.48, "D3: devices"),
        (0.25, 0.20, "D4: rewards_history"),
        (0.72, 0.18, "D5: user_activity")
    ]
    for x, y, title in stores:
        ax.text(x, y, title, ha="center", va="center", fontsize=8.5, fontfamily="serif",
                bbox=dict(boxstyle="square,pad=0.3", fc="#FFF2CC", ec="#D6B656", lw=1.2))

    # Connecting arrows
    ax.annotate('', xy=(0.42, 0.82), xytext=(0.35, 0.82), arrowprops=dict(arrowstyle="->", color="#333", lw=1))
    ax.annotate('', xy=(0.70, 0.72), xytext=(0.70, 0.58), arrowprops=dict(arrowstyle="->", color="#333", lw=1))
    ax.annotate('', xy=(0.84, 0.48), xytext=(0.80, 0.48), arrowprops=dict(arrowstyle="<->", color="#333", lw=1))
    ax.annotate('', xy=(0.14, 0.48), xytext=(0.15, 0.48), arrowprops=dict(arrowstyle="<-", color="#333", lw=1))
    ax.annotate('', xy=(0.25, 0.38), xytext=(0.25, 0.24), arrowprops=dict(arrowstyle="->", color="#333", lw=1))
    ax.annotate('', xy=(0.48, 0.28), xytext=(0.48, 0.38), arrowprops=dict(arrowstyle="<-", color="#333", lw=1))
    ax.annotate('', xy=(0.66, 0.18), xytext=(0.58, 0.18), arrowprops=dict(arrowstyle="->", color="#333", lw=1))

    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_9_4_dfd_level1.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_9_4_dfd_level1.png')

# 6. Figure 9.5: ER Diagram
def make_fig_9_5():
    fig, ax = plt.subplots(figsize=(8, 5.8), dpi=300)
    ax.axis('off')

    # Entity Boxes
    def draw_entity(x, y, name, fields, bg_color):
        h = 0.05 + len(fields) * 0.035
        patch = patches.FancyBboxPatch((x-0.18, y-h/2), 0.36, h, boxstyle="round,pad=0.01",
                                      fc="#FFFFFF", ec=bg_color, lw=1.5)
        ax.add_patch(patch)
        # Header banner
        header = patches.Rectangle((x-0.18, y+h/2-0.05), 0.36, 0.05, fc=bg_color, ec=bg_color)
        ax.add_patch(header)
        ax.text(x, y+h/2-0.025, name, ha="center", va="center", fontsize=9.5, fontweight="bold", fontfamily="serif", color="#FFFFFF")
        # Text fields
        for idx, f in enumerate(fields):
            ax.text(x-0.16, y+h/2-0.08 - idx*0.035, f, ha="left", va="center", fontsize=8, fontfamily="serif")

    # Draw entities
    draw_entity(0.20, 0.78, "users", ["id (PK, INT)", "full_name (VARCHAR)", "email (VARCHAR)", "password_hash (VARCHAR)", "is_active (TINYINT)"], "#2E75B6")
    draw_entity(0.78, 0.78, "centres", ["id (PK, INT)", "centre_name (VARCHAR)", "state (VARCHAR)", "city (VARCHAR)", "latitude (DECIMAL)", "longitude (DECIMAL)"], "#385723")
    draw_entity(0.20, 0.28, "rewards_history", ["id (PK, INT)", "user_id (FK, INT)", "device_id (FK, INT)", "quantity (INT)", "total_points (INT)"], "#C55A11")
    draw_entity(0.78, 0.28, "user_activity", ["activity_id (PK, BIGINT)", "user_id (FK, INT)", "activity_type (VARCHAR)", "search_query (VARCHAR)", "centre_id (FK, INT)"], "#7030A0")
    draw_entity(0.49, 0.53, "devices", ["id (PK, INT)", "device_name (VARCHAR)", "points_per_unit (INT)"], "#41719C")

    # Connect relationships
    ax.annotate("1 : N", xy=(0.20, 0.62), xytext=(0.20, 0.42), arrowprops=dict(arrowstyle="->", color="#333", lw=1.2), fontsize=8, fontfamily="serif")
    ax.annotate("1 : N", xy=(0.38, 0.78), xytext=(0.60, 0.28), arrowprops=dict(arrowstyle="->", color="#333", lw=1.2, ls="--"), fontsize=8, fontfamily="serif")
    ax.annotate("1 : N", xy=(0.78, 0.60), xytext=(0.78, 0.44), arrowprops=dict(arrowstyle="->", color="#333", lw=1.2), fontsize=8, fontfamily="serif")
    ax.annotate("1 : N", xy=(0.49, 0.44), xytext=(0.35, 0.32), arrowprops=dict(arrowstyle="->", color="#333", lw=1.2), fontsize=8, fontfamily="serif")

    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_9_5_er_diagram.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_9_5_er_diagram.png')

# 7. Figure 9.6: User Session Flowchart
def make_fig_9_6():
    fig, ax = plt.subplots(figsize=(7, 7.5), dpi=300)
    ax.axis('off')

    steps = [
        (0.5, 0.94, "Start Session", "round"),
        (0.5, 0.84, "Access EcoLocate Portal (Home Page)", "box"),
        (0.5, 0.72, "Select Feature: Search Centres,\nAwareness, or Rewards", "box"),
        (0.5, 0.58, "Filter by State / City / Proximity\nor Input Device Count", "box"),
        (0.5, 0.44, "Backend Executes MySQL Query\nor Haversine Distance Calc", "diamond"),
        (0.5, 0.28, "Display Verified Centres on\nLeaflet Map & Results Directory", "box"),
        (0.5, 0.14, "Log User Activity (Search / View)\ninto MySQL user_activity", "box"),
        (0.5, 0.04, "End / Close Session", "round")
    ]

    for x, y, text, shape in steps:
        if shape == "round":
            patch = patches.FancyBboxPatch((x-0.18, y-0.035), 0.36, 0.07, boxstyle="round,pad=0.03", fc="#D9E1F2", ec="#2E75B6", lw=1.5)
        elif shape == "diamond":
            patch = patches.FancyBboxPatch((x-0.24, y-0.045), 0.48, 0.09, boxstyle="square,pad=0.02", fc="#FFF2CC", ec="#D6B656", lw=1.5)
        else:
            patch = patches.FancyBboxPatch((x-0.22, y-0.04), 0.44, 0.08, boxstyle="round,pad=0.01", fc="#FFFFFF", ec="#385723", lw=1.2)
        ax.add_patch(patch)
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5, fontfamily="serif")

    # Connect with arrows
    for i in range(len(steps)-1):
        ax.annotate('', xy=(steps[i+1][0], steps[i+1][1]+0.045), xytext=(steps[i][0], steps[i][1]-0.04),
                    arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=1.2))

    plt.tight_layout()
    plt.savefig(os.path.join(diag_dir, 'fig_9_6_flowchart.png'), bbox_inches='tight')
    plt.close()
    print('Generated fig_9_6_flowchart.png')

if __name__ == '__main__':
    make_fig_8_1()
    make_fig_9_1()
    make_fig_9_2()
    make_fig_9_3()
    make_fig_9_4()
    make_fig_9_5()
    make_fig_9_6()
    print('All diagrams generated successfully!')
