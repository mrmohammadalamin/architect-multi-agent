# Construction AI Multi-Agent System

This project is a multi-agent system for managing construction projects, featuring a Flutter-based mobile frontend and a Python backend powered by FastAPI and Google's AI services.

## About the Project

The Construction AI Multi-Agent System is a workflow-driven platform that orchestrates a team of specialized AI agents to manage construction projects from inception to completion. The system is designed to streamline project management, improve decision-making, and provide real-time insights into project status, risks, and financials.

## Features

- **Workflow-Driven Project Management:** Projects are managed through a series of predefined stages, ensuring a structured and consistent process.
- **Multi-Agent System:** A team of specialized AI agents work together to perform tasks such as client intake, design, risk assessment, and financial planning.
- **Real-time Dashboards:** The system provides real-time dashboards for monitoring project status, risks, and financials.
- **Artifact Management:** All project artifacts, such as design documents, reports, and images, are stored and managed within the system.
- **Human-in-the-Loop:** The system includes decision gates where human approval is required to proceed, ensuring that project stakeholders are always in control.
- **Mobile-First Frontend:** A Flutter-based mobile application provides a user-friendly interface for interacting with the system.

## Meet the Agents

The Construction AI Multi-Agent System is powered by a team of specialized AI agents, each with a specific role in the construction project lifecycle. Here are the key agents in the system:

### Construction Agents

- **Project Manager Agent:** Orchestrates the entire project workflow, ensuring that tasks are completed on time and within budget.
- **Safety Inspector Agent:** Monitors the construction site for safety hazards and ensures compliance with safety regulations.
- **Logistics Coordinator Agent:** Manages the supply chain, ensuring that materials and equipment are delivered to the construction site as needed.

### Architectural Agents

- **Lead Architect Agent:** Responsible for the overall design of the building, ensuring that it meets the client's requirements and complies with building codes.
- **Structural Engineer Agent:** Analyzes the structural integrity of the building and designs the structural system.
- **MEP Engineer Agent:** Designs the mechanical, electrical, and plumbing systems for the building.

### Interior Design Agents

- **Interior Designer Agent:** Creates the interior design concept for the building, including the layout, materials, and finishes.
- **Lighting Designer Agent:** Designs the lighting system for the building, creating a comfortable and visually appealing environment.
- **Acoustic Consultant Agent:** Analyzes the acoustics of the building and designs solutions to control noise and improve sound quality.

## Installation Guide

### Prerequisites

- Flutter SDK
- Python 3.10+
- Pip (Python package installer)
- Git

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/construction-ai.git
   cd construction-ai/backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the `backend` directory and add the following:
   ```
   GOOGLE_API_KEY="your-google-api-key"
   ```

5. **Run the backend server:**
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install the dependencies:**
   ```bash
   flutter pub get
   ```

3. **Set up environment variables:**
   Create a `.env` file in the `frontend` directory and add the following:
   ```
   API_BASE_URL="http://localhost:8000"
   ```

4. **Run the frontend application:**
   ```bash
   flutter run
   ```

## Output Details

The application provides a rich user experience, allowing users to create and manage construction projects seamlessly.

### Screenshots

Here are some screenshots of the application:

![Project Creation Screen](screen.png)

![Project Creation Screen](https://github.com/mrmohammadalamin/architect-multi-agent/blob/f7668923424c8bfbc580232151b36d9a18bfe7f4/backend/project_store/4223f937-3d9a-4d26-ba84-409329dce304/stage_12/code_compliance_sheet.png)
![Project Creation Screen](https://github.com/mrmohammadalamin/architect-multi-agent/blob/15e599c455d90eb34305d95f749b76f500b90a42/backend/project_store/4223f937-3d9a-4d26-ba84-409329dce304/stage_10/2025-09-09%20091650.png)


*(You can add more screenshots here by replacing the placeholder above with the actual path to your screenshot file.)*

### Video Demo

Here is a video demo of the application:
[![Construction AI Demo](https://img.youtube.com/vi/MibL8O5Ff_4/0.jpg)](https://www.youtube.com/watch?v=MibL8O5Ff_4)


*(Replace `your-video-id` with the ID of your YouTube video.)*
