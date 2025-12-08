# 🏭 Nexus Monitor - Floor Control Dashboard

A sophisticated **industrial equipment monitoring system** built with [Reflex](https://reflex.dev/). This application provides real-time visualization and automation capabilities for pharmaceutical manufacturing environments.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Reflex](https://img.shields.io/badge/Reflex-0.8.20-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 🖥️ 3D Equipment Visualization
- Interactive GLB model viewer for pharmaceutical manufacturing machinery
- Click-to-select equipment with raycasting
- Dynamic camera controls (rotate, pan, zoom)
- Equipment isolation/focus mode
- Real-time alert indicators on 3D model

### 🔧 Visual Workflow Builder
- Drag-and-drop ReactFlow canvas
- Connect equipment sensors to notification actions
- Configure threshold-based triggers (>, <, >=, <=, between)
- Save/load workflows with SQLite persistence
- Test workflows with simulated data
- Real-time simulation with configurable speed

### 📱 Multi-Channel Notifications
- **WhatsApp Business API** - Send alerts via Meta's WhatsApp Business Platform
- **Email (SMTP)** - Gmail and other SMTP providers
- **Webhooks** - Generic HTTP POST notifications
- Mock mode for development/testing

### 📊 Sensor Simulation
- Realistic data generation for testing
- Supports multiple equipment types (centrifuge, analyzer, robot, storage, conveyor)
- Anomaly injection (spike, drift, oscillation, flatline)
- Database logging for historical analysis

### 🧠 Knowledge Graph
- Equipment relationship visualization
- Dependency tracking (depends_on, affects)
- Product line associations
- RUL (Remaining Useful Life) indicators

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Reflex Frontend                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐│
│  │   Monitor Page  │  │ Workflow Builder │  │   Components    ││
│  │   (3D Viewer)   │  │  (ReactFlow)     │  │   (Shared UI)   ││
│  └────────┬────────┘  └────────┬─────────┘  └─────────────────┘│
│           │                    │                                │
│  ┌────────▼────────────────────▼─────────────────────────────┐ │
│  │                    State Management                        │ │
│  │  ┌──────────────┐  ┌────────────────┐                     │ │
│  │  │ MonitorState │  │ WorkflowState  │                     │ │
│  │  └──────────────┘  └────────────────┘                     │ │
│  └───────────────────────────┬───────────────────────────────┘ │
├──────────────────────────────┼─────────────────────────────────┤
│                        Services Layer                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │   Database    │  │  Workflow     │  │   Notification    │   │
│  │   (SQLite)    │  │   Engine      │  │   Service         │   │
│  └───────────────┘  └───────────────┘  └───────────────────┘   │
│  ┌───────────────┐  ┌───────────────┐                          │
│  │    Sensor     │  │  GLB Parser   │                          │
│  │   Simulator   │  │  (Equipment)  │                          │
│  └───────────────┘  └───────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Floor-Control-Dashboard/
├── app/
│   ├── app.py                 # Application entry point
│   ├── reactflow.py           # ReactFlow component wrappers
│   ├── workflow_builder.py    # Workflow builder logic
│   │
│   ├── components/
│   │   ├── monitor/           # Monitor page components
│   │   │   ├── model_viewer.py
│   │   │   ├── context_menu.py
│   │   │   ├── knowledge_graph.py
│   │   │   ├── sensor_dashboard.py
│   │   │   ├── alert_feed.py
│   │   │   └── chat_panel.py
│   │   │
│   │   ├── workflow/          # Workflow builder components
│   │   │   ├── canvas.py
│   │   │   ├── config_panel.py
│   │   │   ├── controls.py
│   │   │   ├── dialogs.py
│   │   │   ├── header.py
│   │   │   └── toolbox.py
│   │   │
│   │   └── shared/            # Shared components
│   │       └── design_tokens.py
│   │
│   ├── extractors/
│   │   └── glb_parser.py      # 3D model equipment extraction
│   │
│   ├── models/
│   │   └── __init__.py        # Data models (Workflow, Node, Edge, etc.)
│   │
│   ├── pages/
│   │   ├── monitor.py         # Main monitoring page
│   │   └── workflow_builder.py
│   │
│   ├── services/
│   │   ├── database.py        # SQLite persistence
│   │   ├── notification_service.py  # WhatsApp/Email/Webhook
│   │   ├── sensor_simulator.py      # Sensor data simulation
│   │   └── workflow_engine.py       # Workflow execution
│   │
│   └── states/
│       ├── monitor_state.py   # Monitor UI state
│       ├── nexus_state.py     # Core application state
│       └── workflow_state.py  # Workflow builder state
│
├── assets/
│   ├── pharmaceutical_manufacturing_machinery.glb  # 3D model
│   └── interaction.js         # JavaScript for 3D raycasting
│
├── data/                      # SQLite database storage
├── tests/                     # Test suite
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_notification_service.py
│   ├── test_sensor_simulator.py
│   ├── test_workflow_engine.py
│   └── test_glb_parser.py
│
├── .env                       # Environment variables (not in git)
├── pyproject.toml
├── requirements.txt
└── rxconfig.py               # Reflex configuration
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Floor-Control-Dashboard
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

   Or with pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file based on the example below:
   ```env
   # Notification Settings
   NOTIFICATION_MOCK_MODE=true  # Set to 'false' for real notifications
   
   # WhatsApp Business API
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   WHATSAPP_ACCESS_TOKEN=your_access_token
   
   # Email (SMTP)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   
   # Webhook (optional)
   DEFAULT_WEBHOOK_URL=https://your-webhook-endpoint.com
   ```

4. **Initialize the database**
   
   The database is automatically created on first run.

5. **Run the application**
   ```bash
   uv run reflex run
   ```

   The app will be available at `http://localhost:3000`

## 📖 Usage

### Monitor Page (`/`)

The main monitoring dashboard provides:

1. **3D Model Viewer** - Click on equipment to select it
2. **Context Menu** - Appears when equipment is selected, showing:
   - Equipment properties (temperature, pressure, status)
   - Quick actions (Stop, Report)
   - Link to create workflow for selected equipment
3. **Knowledge Graph** - Shows equipment relationships
4. **Alert Feed** - Displays recent alerts and notifications
5. **Chat Panel** - System messages and interactions

### Workflow Builder (`/workflow-builder`)

Create automation workflows:

1. **Equipment Panel** (left sidebar)
   - Drag equipment types onto the canvas
   - Drag action nodes (WhatsApp, Email, Webhook)

2. **Canvas** (center)
   - Drop nodes to add them
   - Connect nodes by dragging from source to target
   - Click nodes to configure them

3. **Configuration Panel** (appears on node click)
   - Select target equipment (from 3D model)
   - Choose sensor and threshold condition
   - Configure notification recipient

4. **Simulation Controls** (bottom)
   - Test workflow with simulated data
   - Run real-time simulation
   - Adjust simulation speed

5. **Header Actions**
   - Save workflow
   - Load existing workflows
   - Clear canvas

## ⚙️ Configuration

### Notification Channels

#### WhatsApp Business API

1. Set up a [Meta Business Account](https://business.facebook.com/)
2. Create a WhatsApp Business App
3. Get your Phone Number ID and Access Token
4. Add to `.env`:
   ```env
   WHATSAPP_PHONE_NUMBER_ID=your_id
   WHATSAPP_ACCESS_TOKEN=your_token
   ```

#### Email (Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Add to `.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

### Mock Mode

For development without real notifications:
```env
NOTIFICATION_MOCK_MODE=true
```

## 🧪 Testing

Run the test suite with pytest:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_database.py -v

# Run with coverage
uv run pytest tests/ -v --cov=app --cov-report=html
```

### Test Categories

- **test_database.py** - Database CRUD operations
- **test_notification_service.py** - Notification channels and routing
- **test_sensor_simulator.py** - Sensor data generation and anomalies
- **test_workflow_engine.py** - Condition evaluation and execution
- **test_glb_parser.py** - 3D model parsing and equipment extraction

## 🛠️ Development

### Adding New Equipment Types

1. Update `app/extractors/glb_parser.py`:
   - Add pattern to `_classify_equipment()`
   - Add sensor definitions to `get_sensors_for_type()`

2. Update sensor simulator if needed in `app/services/sensor_simulator.py`

### Adding New Notification Channels

1. Update `app/services/notification_service.py`:
   - Add new channel to `NotificationChannel` enum
   - Implement send method (e.g., `send_sms()`)
   - Add routing in `send_alert()`

2. Update workflow components as needed

### Adding New Workflow Conditions

1. Update `app/services/workflow_engine.py`:
   - Add operator to `ConditionOperator` enum
   - Implement logic in `evaluate_condition()`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Reflex](https://reflex.dev/) - Python-based web framework
- [ReactFlow](https://reactflow.dev/) - Node-based graph editor
- [Model Viewer](https://modelviewer.dev/) - 3D model display
- [TailwindCSS](https://tailwindcss.com/) - Utility-first CSS

---

Built with ❤️ for industrial automation