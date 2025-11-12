import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from keycloak import KeycloakOpenID
import pymysql

app = FastAPI(title="Dolt Application")

DOLT_HOST = os.getenv("DOLT_HOST", "dolt")
DOLT_PORT = int(os.getenv("DOLT_PORT", "3306"))
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://keycloak:8443")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")

dolt_engine = None

keycloak_client = None

def get_dolt_engine():
    global dolt_engine
    if dolt_engine is None:
        try:
            connection_string = f"mysql+pymysql://root@{DOLT_HOST}:{DOLT_PORT}/"
            dolt_engine = create_engine(
                connection_string,
                connect_args={
                    "charset": "utf8mb4",
                    "connect_timeout": 10
                },
                pool_pre_ping=True,
                pool_recycle=3600
            )
        except Exception as e:
            print(f"Error creating Dolt engine: {e}")
    return dolt_engine

def get_keycloak_client():
    global keycloak_client
    if keycloak_client is None:
        try:
            keycloak_client = KeycloakOpenID(
                server_url=KEYCLOAK_URL,
                client_id="admin-cli",
                realm_name=KEYCLOAK_REALM,
                verify=False
            )
        except Exception as e:
            print(f"Error connecting to Keycloak: {e}")
    return keycloak_client


@app.get("/")
async def root():
    return {
        "message": "Dolt Application is running",
        "status": "ok",
        "dolt_host": DOLT_HOST,
        "dolt_port": DOLT_PORT,
        "keycloak_url": KEYCLOAK_URL
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/test/dolt")
async def test_dolt():
    try:
        engine = get_dolt_engine()
        if engine is None:
            raise HTTPException(status_code=500, detail="Failed to create Dolt engine")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            return {
                "status": "success",
                "message": "Dolt connection successful",
                "test_result": row[0] if row else None,
                "host": DOLT_HOST,
                "port": DOLT_PORT
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Dolt connection failed: {str(e)}. Host: {DOLT_HOST}, Port: {DOLT_PORT}"
        )


@app.get("/test/keycloak")
async def test_keycloak():
    try:
        client = get_keycloak_client()
        realm_info = client.well_known()
        return {
            "status": "success",
            "message": "Keycloak connection successful",
            "realm": KEYCLOAK_REALM,
            "issuer": realm_info.get("issuer", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keycloak connection failed: {str(e)}")


@app.get("/test/dolt/databases")
async def list_dolt_databases():
    try:
        engine = get_dolt_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result.fetchall()]
            return {
                "status": "success",
                "databases": databases
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list databases: {str(e)}")


@app.post("/test/dolt/create-db/{db_name}")
async def create_dolt_database(db_name: str):
    try:
        engine = get_dolt_engine()
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            conn.commit()
            return {
                "status": "success",
                "message": f"Database '{db_name}' created successfully"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create database: {str(e)}")

