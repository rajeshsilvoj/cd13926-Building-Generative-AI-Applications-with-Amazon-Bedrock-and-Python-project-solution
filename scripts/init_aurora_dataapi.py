#!/usr/bin/env python3
import boto3
import json
import time

# Initialize RDS Data API client
rds_client = boto3.client('rds-data', region_name='us-east-1')

# Database configuration
cluster_arn = "arn:aws:rds:us-east-1:981462100936:cluster:my-aurora-serverless"
secret_arn = "arn:aws:secretsmanager:us-east-1:981462100936:secret:my-aurora-serverless-0oDpOo"
database_name = "myapp"

# SQL commands to execute
sql_commands = [
    {
        "name": "Create pgvector extension",
        "sql": "CREATE EXTENSION IF NOT EXISTS vector;"
    },
    {
        "name": "Create bedrock_integration schema",
        "sql": "CREATE SCHEMA IF NOT EXISTS bedrock_integration;"
    },
    {
        "name": "Create bedrock_user role",
        "sql": "DO $$ BEGIN CREATE ROLE bedrock_user LOGIN; EXCEPTION WHEN duplicate_object THEN RAISE NOTICE 'Role already exists'; END $$;"
    },
    {
        "name": "Grant privileges to bedrock_user",
        "sql": "GRANT ALL ON SCHEMA bedrock_integration to bedrock_user;"
    },
    {
        "name": "Create bedrock_kb table",
        "sql": """
        CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
            id uuid PRIMARY KEY,
            embedding vector(1536),
            chunks text,
            metadata json
        );
        """
    },
    {
        "name": "Create HNSW index on embeddings",
        "sql": "CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx ON bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);"
    }
]

def execute_sql(sql, description):
    """Execute SQL statement using RDS Data API"""
    try:
        response = rds_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql=sql
        )
        print(f"✓ {description}")
        return True
    except Exception as e:
        print(f"✗ {description}: {str(e)}")
        return False

def verify_setup():
    """Verify the database setup"""
    try:
        # Check if pgvector extension exists
        response = rds_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT extname FROM pg_extension WHERE extname = 'vector';"
        )
        if response.get('records'):
            print("\n✓ pgvector extension is installed")
        
        # Check if schema exists
        response = rds_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'bedrock_integration';"
        )
        if response.get('records'):
            print("✓ bedrock_integration schema exists")
        
        # Check if table exists
        response = rds_client.execute_statement(
            resourceArn=cluster_arn,
            secretArn=secret_arn,
            database=database_name,
            sql="SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'bedrock_integration';"
        )
        if response.get('records'):
            tables = [record[0]['stringValue'] for record in response['records']]
            print(f"✓ Tables in bedrock_integration: {tables}")
        
        return True
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Aurora PostgreSQL Database Initialization")
    print("Using RDS Data API")
    print("=" * 60)
    print(f"\nCluster: {cluster_arn}")
    print(f"Database: {database_name}\n")
    
    # Execute all SQL commands
    success_count = 0
    for cmd in sql_commands:
        if execute_sql(cmd['sql'], cmd['name']):
            success_count += 1
    
    print(f"\n{success_count}/{len(sql_commands)} commands executed successfully")
    
    # Verify the setup
    print("\nVerifying database setup...")
    verify_setup()
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
