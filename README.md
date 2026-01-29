# Lab 1: Create and Deploy Your First Azure Function
# CST8917 - Serverless Applications | Winter 2026

# Azure Serverless Text Analyzer

This project is an Azure Functions (Python) serverless application that analyzes text input and stores analysis results as JSON documents in Azure Cosmos DB (NoSQL, Serverless). It also provides an endpoint to retrieve past analysis results.

---

Youtube video link: https://youtu.be/vPrsV2PysUE


## Prerequisites

Before running the project locally, ensure you have the following installed:

- Python 3.9+  
- Azure Functions Core Tools v4  
- Azure CLI (optional, for deployment)  
- An Azure Cosmos DB account (NoSQL API, Serverless)

---

## Local Setup
First Clone the project and navigate to the root folder.
Create a file named local.settings.json in the project root (this file should not be committed to source control):

```bash
{
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_DB_CONNECTION_STRING": "<your-cosmos-connection-string>",
    "COSMOS_DB_DATABASE": "database id",
    "COSMOS_DB_CONTAINER": "container id"
  }
}
```

- Install Python dependencies : pip install -r requirements.txt
- Start the function locally : func start
- The functions will be available at:

http://localhost:7071/api/

Available Endpoints: 

**TextAnalyzer** :  
Analyzes text and stores the result in Cosmos DB.

Ex: /api/textanalyzer?text=Hello world

**GetAnalysisHistory**
Retrieves stored analysis results.


## Azure Deployment
Deploy the function to Azure using  VS Code (F1 -> Azure Functions: Deploy to Function App -> Choose your Function App and confirm deployment) or  Using CLI :
```bash
func azure functionapp publish <your-function-app-name>
```

## Azure Configuration
After deployment, the following Application Settings must be configured in the Azure Portal:

| Name                        | Description                     |
|-----------------------------|---------------------------------|
| COSMOS_DB_CONNECTION_STRING | Cosmos DB connection string     |
| COSMOS_DB_DATABASE          | Database ID                     |
| COSMOS_DB_CONTAINER         | Container ID                    |


Restart the Function App after adding or updating these settings.

**Verification**

- Call the TextAnalyzer endpoint and verify an id is returned
- Call GetAnalysisHistory to retrieve stored results
- Confirm data is stored in Cosmos DB via Data Explorer

**Notes**
- Cosmos DB is configured in serverless mode to minimize cost
- JSON documents are stored without a predefined schema
- Secrets are managed via environment variables only


