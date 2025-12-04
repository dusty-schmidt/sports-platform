# Sports Data Microservices Architecture

## 1. Executive Summary

This document details the architecture of the Sports Data Platform, a system designed for high-volume, real-time sports data management. It leverages a **Microservices Architecture** orchestrated with **Docker Compose** to ensure robustness, flexibility, and fault tolerance. The platform's core philosophy emphasizes **Modularity and Isolation**, encapsulating major functional requirements into independent, containerized services. This approach facilitates independent management of data collection, processing, and delivery for various sports data streams, including DFS pools, live odds, and statistical projections.

## 2. Introduction and Core Philosophy

The Sports Data Platform is built upon the principles of **Modularity and Isolation**. Each significant functional component, such as data ingestion, simulation, or API serving, operates as a distinct, containerized service. This design ensures that services can be developed, deployed, scaled, and maintained independently, leading to a more resilient and adaptable system.

## 3. Architectural Overview: The Three-Tier Data Pipeline

The platform follows a clear, three-tiered data pipeline structure, guiding data flow from external sources to the end-user.

*   **Tier I: Ingestion**
    *   **Function:** Data Collection
    *   **Description:** Dedicated services for acquiring raw, high-volume data from external APIs and sources (e.g., weather, odds, DFS salaries). These services are scheduled independently.
    *   **Key Services:** `ingest-dfs`, `ingest-weather`, `ingest-odds`, `ingest-injury`

*   **Tier II: Processing**
    *   **Function:** Compute & Analysis
    *   **Description:** Services responsible for consuming raw data from the database, applying complex logic (simulations, optimization), and writing refined data back to the database.
    *   **Key Services:** `sim-engine`, `optimizer`

*   **Tier III: Interface**
    *   **Function:** Delivery & Access
    *   **Description:** The user-facing layer, providing secure data access, managing user uploads (like custom CSV projections), and hosting the visual dashboard.
    *   **Key Services:** `backend-api`, `frontend`

## 4. Key Services and Responsibilities

### Tier I: Ingestion Services

These services act as data scrapers and fetchers, interacting solely with external APIs and the central database.

*   **DFS Pool Ingestion:** Collects current DFS pools, salaries, and slate information across all supported sports.
*   **Live Odds Ingestion:** Captures real-time betting odds and line movements across various markets.
*   **Weather Provider:** Monitors and records relevant weather data for upcoming games at defined intervals.
*   **Injury Monitor:** Scans designated sources (e.g., news feeds) for critical, late-breaking injury information.

### Tier II: Processing Engines

These are the core analytical components, relying on the internal data state for their execution.

*   **Simulation Engine (`sim-engine`):** Reads normalized data (stats, weather, odds) and executes probabilistic simulations to generate Projections. Outputs are stored as structured projection sets in the database.
*   **Lineup Optimizer (`optimizer`):** Consumes DFS pools and calculated (or user-uploaded custom) Projections to solve the optimization problem, generating final Lineups.

### Tier III: Interface and User Access

This layer abstracts the data pipeline's complexity from the user experience.

*   **Backend API (`backend-api`):** Serves as the single point of contact for the frontend. It handles business logic such as CSV validation, user authentication, and serving structured data queries from the processing engines.
*   **Frontend UI (`frontend`):** The user interface (initially Streamlit for prototyping, later React) for visualizing data, running simulations via the API, and managing lineup optimization.

## 5. Technical Foundation

| Technology             | Role in Architecture                 | Benefit                                                                                             |
| :--------------------- | :----------------------------------- | :-------------------------------------------------------------------------------------------------- |
| Docker / Docker Compose | Orchestration and Containerization   | Ensures a 100% consistent operating environment across different systems (Linux Fedora and Windows) and solves Python dependency conflicts. |
| Python                 | Core Implementation Language         | Used across all ingestion and processing containers.                                                |
| PostgreSQL (db)        | Central Database / Shared State      | A high-integrity, relational database serving as the single source of truth for all raw data, projections, and lineup results. |
| Shared Common Library  | Code Reusability                     | A locally mounted Python package containing shared database models (SQLAlchemy/SQLModel) and utility functions, drastically reducing redundant code across multiple services. |

## 6. Architectural Benefits

*   **Cross-OS Compatibility:** The platform works identically on both Linux and Windows environments due to Docker encapsulation.
*   **Fault Tolerance:** A failure in one service (e.g., the Odds scraper) will not crash unrelated services (e.g., the Simulation Engine).
*   **Scalability & Maintenance:** Services can be scaled up (by running more instances of a container) or updated (by rebuilding a single Docker image) without affecting the others.
*   **Clear Separation of Concerns:** Enforces modular code practices, making the codebase easier to debug, test, and expand as new features (e.g., player props analysis) are introduced.
