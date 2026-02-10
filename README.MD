# Excel Ingestion Self-Service  
`SharePoint` → `Microsoft Fabric` (Streamlit App)

## Overview

This project is a `self-service` Excel ingestion tool that enables users to ingest Excel files from `SharePoint` into `Microsoft Fabric` using a `Streamlit-based` interface.

The application is designed for controlled, repeatable ingestion without requiring technical expertise from end users.

## Features

- Fetch Excel files from SharePoint
- Validate Excel schema and structure
- Load data into Microsoft Fabric (Lakehouse or Warehouse)
- Simple self-service UI using Streamlit

## Tech Stack

- Python
- Streamlit
- Pandas
- SharePoint (Microsoft Graph / Office365)
- Microsoft Fabric

## Project Structure

```
├── app.py
|
├── .env.example
└── README.md
```

## Setup

### 1. Clone Repository
```
git clone <repository-url>  
cd <repository-name>
```

### 2. Create Virtual Environment

Virtual environment name: myenv

Windows:
```
python -m venv myenv  
myenv\Scripts\activate
```
Mac / Linux:
```
python3 -m venv myenv  
source myenv/bin/activate
```
### 3. Install Dependencies
```
pip install -r requirements.txt
```
### 4. Environment Variables

Copy the example environment file:

Windows:
```
copy .env.example .env
```
Mac / Linux:
```
cp .env.example .env
```
Fill in the values inside .env:
```
TENANT_ID=
APP_ID=
OBJECT_ID=
SECRET_ID=
SECRET_VALUE=
SITE_ID=
DRIVE_ID=
DEV_WS_ID= 
```
## Run Application
```
streamlit run app.py
```
`available soon`

## High-Level Flow

1. User selects an Excel file from SharePoint
2. Application downloads the file
3. Excel file is read using Pandas
4. Schema validation is applied
5. Optional transformation is executed
6. Data is loaded into Microsoft Fabric

## Requirements

All dependencies are defined in requirements.txt.

Typical libraries include:

- streamlit
- pandas
- python-dotenv
- office365 or msal
- requests

## Notes

- Do not commit .env files
- Use a service principal for SharePoint and Fabric authentication
- Ensure SharePoint permissions allow read access to the source files
