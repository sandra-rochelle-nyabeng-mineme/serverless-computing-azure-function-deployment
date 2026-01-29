# =============================================================================
# IMPORTS
# =============================================================================
import azure.functions as func
import logging
import json
import re
import os
import uuid
from datetime import datetime
from azure.cosmos import CosmosClient

# =============================================================================
# COSMOS DB CONFIG (FROM ENV VARS)
# =============================================================================
COSMOS_CONNECTION_STRING = os.environ["COSMOS_DB_CONNECTION_STRING"]
DATABASE_NAME = os.environ["COSMOS_DB_DATABASE"]
CONTAINER_NAME = os.environ["COSMOS_DB_CONTAINER"]

cosmos_client = CosmosClient.from_connection_string(
    COSMOS_CONNECTION_STRING
)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

# =============================================================================
# CREATE FUNCTION APP
# =============================================================================
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# =============================================================================
# TEXT ANALYZER FUNCTION
# =============================================================================
@app.route(route="TextAnalyzer", methods=["POST", "GET"])
def TextAnalyzer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Text Analyzer API was called")

    # -------------------------------------------------------------------------
    # GET INPUT TEXT
    # -------------------------------------------------------------------------
    text = req.params.get("text")

    if not text:
        try:
            req_body = req.get_json()
            text = req_body.get("text")
        except ValueError:
            pass

    if not text:
        return func.HttpResponse(
            json.dumps({"error": "No text provided"}, indent=2),
            mimetype="application/json",
            status_code=400
        )

    # -------------------------------------------------------------------------
    # ANALYSIS
    # -------------------------------------------------------------------------
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    sentence_count = len(re.findall(r"[.!?]+", text)) or 1
    paragraph_count = len([p for p in text.split("\n\n") if p.strip()])
    reading_time_minutes = round(word_count / 200, 1)
    avg_word_length = round(char_count_no_spaces / word_count, 1) if word_count else 0
    longest_word = max(words, key=len) if words else ""

    analysis_result = {
        "wordCount": word_count,
        "characterCount": char_count,
        "characterCountNoSpaces": char_count_no_spaces,
        "sentenceCount": sentence_count,
        "paragraphCount": paragraph_count,
        "averageWordLength": avg_word_length,
        "longestWord": longest_word,
        "readingTimeMinutes": reading_time_minutes
    }

    # -------------------------------------------------------------------------
    # STORE RESULT IN COSMOS DB
    # -------------------------------------------------------------------------
    analysis_id = str(uuid.uuid4())

    document = {
        "id": analysis_id,
        "analysis": analysis_result,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "textPreview": text[:100]
        },
        "originalText": text
    }

    container.create_item(body=document)

    # -------------------------------------------------------------------------
    # RETURN RESPONSE
    # -------------------------------------------------------------------------
    return func.HttpResponse(
        json.dumps(
            {
                "id": analysis_id,
                "analysis": analysis_result
            },
            indent=2
        ),
        mimetype="application/json",
        status_code=200
    )
# =============================================================================
# GET ANALYSIS HISTORY FUNCTION
# =============================================================================
@app.route(route="GetAnalysisHistory", methods=["GET"])
def GetAnalysisHistory(req: func.HttpRequest) -> func.HttpResponse:
    """
    Retrieves past text analysis results from Cosmos DB.

    Query Parameters:
        limit (optional): Maximum number of results to return (default: 10)

    Returns:
        JSON response containing count and results array
    """

    try:
        # ---------------------------------------------------------------------
        # READ LIMIT PARAMETER (DEFAULT = 10)
        # ---------------------------------------------------------------------
        limit_param = req.params.get("limit")
        limit = int(limit_param) if limit_param and limit_param.isdigit() else 10

        # Safety cap (optional but good practice)
        limit = min(limit, 50)

        # ---------------------------------------------------------------------
        # QUERY COSMOS DB
        # ---------------------------------------------------------------------
        query = f"""
        SELECT TOP {limit}
            c.id,
            c.analysis,
            c.metadata
        FROM c
        ORDER BY c.metadata.timestamp DESC
        """

        items = list(
            container.query_items(
                query=query,
                enable_cross_partition_query=True
            )
        )

        # ---------------------------------------------------------------------
        # BUILD RESPONSE
        # ---------------------------------------------------------------------
        response = {
            "count": len(items),
            "results": items
        }

        return func.HttpResponse(
            json.dumps(response, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
