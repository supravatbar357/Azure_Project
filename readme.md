# Azure Modern Data Platform – End-to-End Pipeline

This project implements a scalable, production-grade Azure data pipeline to ingest, store, transform, and visualize data. It leverages native Azure services for efficient data engineering and advanced analytics.

## ⚙️ Components & Technologies

| Component              | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| **Azure Data Factory** | Orchestrates data ingestion from GitHub APIs and SQL Tables                 |
| **ADLS Gen2 (Raw)**    | Stores raw ingested data in hierarchical file structures                    |
| **Azure Databricks**   | Performs ETL/ELT transformations, joins with MongoDB enrichment datasets    |
| **MongoDB**            | External enrichment data source used in transformation logic                |
| **ADLS Gen2 (Transformed)** | Stores cleansed and enriched data ready for analytics                  |
| **Azure Synapse**      | Warehouses transformed data for downstream analytics and BI consumption     |
| **Power BI / Tableau / Fabric** | Consumes Synapse data for real-time dashboards and visual analytics |

---

## 🔄 Data Flow Pipeline

### 1. **Ingestion Layer**
- Triggered via **Azure Data Factory**
- Data Sources:
  - GitHub REST API (JSON over HTTP)
  - SQL Server tables (using self-hosted integration runtime if on-prem)
- Output: `.json` / `.csv` into `landing/raw` container in **ADLS Gen2**

### 2. **Storage Layer**
- Raw data stored with appropriate folder hierarchy (`source/year/month/day`)
- ADLS Gen2 provides security via RBAC and fine-grained ACLs

### 3. **Transformation Layer**
- **Azure Databricks** notebooks/scripts perform:
  - Data cleansing and schema normalization
  - Lookup joins with **MongoDB** (via Spark Mongo Connector)
  - Data quality checks (null handling, type casting, deduplication)
  - Output stored in `curated/transformed` zone in ADLS Gen2

### 4. **Analytics Layer**
- **Synapse Pipelines or PolyBase** used to load data from ADLS to Synapse SQL Pools
- Schema-on-read or materialized views configured for reporting use cases

### 5. **Consumption Layer**
- **Power BI / Tableau / Fabric** dashboards connect to Synapse for:
  - Real-time reporting
  - Cross-filtering and drill-down analysis
  - Historical trend monitoring

---

## 🛡️ Security & Governance

- **ADLS Gen2** secured using Azure RBAC and managed identities
- Databricks notebooks versioned with Git integration
- MongoDB access controlled via connection string secrets (Key Vault recommended)
- Role-based access for Synapse and Power BI workspaces
- Future Enhancement: Integrate Azure Purview for data cataloging

---

## 🧪 Testing & Monitoring

- Unit testing of transformation logic using PyTest in Databricks
- Integration tests for pipeline execution via Data Factory triggers
- Azure Monitor and Log Analytics configured for operational telemetry

---

## 🔧 Deployment

> Recommended via Infrastructure-as-Code (IaC):
- **Terraform or Bicep** to deploy ADF, ADLS, Synapse
- CI/CD pipeline with **GitHub Actions** or **Azure DevOps** for notebook deployments

---

## 📌 Prerequisites

- Azure Subscription
- Azure Resource Group
- Access to GitHub API & SQL Server source
- MongoDB database with sample reference tables
- Power BI / Tableau Desktop for report design


