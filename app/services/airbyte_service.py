"""
Airbyte Integration Service
Manages connections to third-party services via Airbyte
"""
import os
import requests
from typing import Dict, Any, Optional, List


class AirbyteService:
    """Service for managing Airbyte connections and syncs"""
    
    def __init__(self, server_url: str = "http://localhost:8001"):
        """Initialize Airbyte client
        
        Args:
            server_url: URL of the Airbyte server API
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = os.getenv("AIRBYTE_API_KEY", "")
        self.workspace_id = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    async def initialize(self):
        """Initialize and get or create workspace"""
        try:
            # Try to list workspaces
            response = requests.get(
                f"{self.server_url}/v1/workspaces",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                workspaces = data.get('data', [])
                
                if workspaces:
                    self.workspace_id = workspaces[0].get('workspaceId')
                else:
                    # Create workspace
                    create_response = requests.post(
                        f"{self.server_url}/v1/workspaces",
                        headers=self.headers,
                        json={
                            "name": "Usage-Revenue-Analyzer",
                            "email": os.getenv("ADMIN_EMAIL", "admin@example.com")
                        },
                        timeout=5
                    )
                    if create_response.status_code == 200:
                        self.workspace_id = create_response.json().get('workspaceId')
                
                return self.workspace_id is not None
            
            # Airbyte not available yet, that's okay
            print("Airbyte server not available - will connect later")
            return False
            
        except Exception as e:
            print(f"Airbyte connection note: {e}")
            return False
    
    def create_stripe_source(self, api_key: str, account_id: str) -> Optional[str]:
        """Create a Stripe source connection
        
        Args:
            api_key: Stripe API key
            account_id: Stripe account ID
            
        Returns:
            Source ID if successful, None otherwise
        """
        try:
            response = requests.post(
                f"{self.server_url}/v1/sources",
                headers=self.headers,
                json={
                    "workspaceId": self.workspace_id,
                    "name": "Stripe Revenue",
                    "sourceDefinitionId": "e094cb9a-26de-4645-8761-65c0c425d1de",  # Stripe
                    "connectionConfiguration": {
                        "client_secret": api_key,
                        "account_id": account_id,
                        "start_date": "2024-01-01T00:00:00Z"
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('sourceId')
            else:
                print(f"Failed to create Stripe source: {response.text}")
                return None
                
        except Exception as e:
            print(f"Failed to create Stripe source: {e}")
            return None
    
    def create_openai_source(self, api_key: str, org_id: str) -> Optional[str]:
        """Create an OpenAI source connection (custom)
        
        Note: OpenAI doesn't have a native Airbyte connector yet,
        so this would use a custom source or API connector.
        
        Args:
            api_key: OpenAI API key
            org_id: Organization ID
            
        Returns:
            Source ID if successful, None otherwise
        """
        # For now, return None as OpenAI doesn't have native connector
        # You'd need to create a custom connector or use HTTP API source
        print("OpenAI source creation - custom connector needed")
        return None
    
    def create_database_destination(self, db_path: str) -> Optional[str]:
        """Create a SQLite destination
        
        Args:
            db_path: Path to SQLite database file
            
        Returns:
            Destination ID if successful, None otherwise
        """
        try:
            response = requests.post(
                f"{self.server_url}/v1/destinations",
                headers=self.headers,
                json={
                    "workspaceId": self.workspace_id,
                    "name": "Local Database",
                    "destinationDefinitionId": "b76be0a6-27dc-4560-95f6-2623da0bd7b6",  # SQLite
                    "connectionConfiguration": {
                        "destination_path": db_path
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('destinationId')
            else:
                print(f"Failed to create destination: {response.text}")
                return None
                
        except Exception as e:
            print(f"Failed to create database destination: {e}")
            return None
    
    def create_connection(
        self, 
        source_id: str, 
        destination_id: str,
        sync_mode: str = "incremental"
    ) -> Optional[str]:
        """Create a connection between source and destination
        
        Args:
            source_id: Source connection ID
            destination_id: Destination connection ID
            sync_mode: Sync mode (full_refresh, incremental)
            
        Returns:
            Connection ID if successful, None otherwise
        """
        try:
            response = requests.post(
                f"{self.server_url}/v1/connections",
                headers=self.headers,
                json={
                    "sourceId": source_id,
                    "destinationId": destination_id,
                    "name": "Stripe to Database",
                    "namespaceDefinition": "destination",
                    "namespaceFormat": "${SOURCE_NAMESPACE}",
                    "status": "active",
                    "schedule": {
                        "units": 1,
                        "timeUnit": "hours"
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('connectionId')
            else:
                print(f"Failed to create connection: {response.text}")
                return None
                
        except Exception as e:
            print(f"Failed to create connection: {e}")
            return None
    
    def trigger_sync(self, connection_id: str) -> bool:
        """Manually trigger a sync for a connection
        
        Args:
            connection_id: Connection ID to sync
            
        Returns:
            True if sync triggered successfully
        """
        try:
            response = requests.post(
                f"{self.server_url}/v1/jobs",
                headers=self.headers,
                json={
                    "connectionId": connection_id,
                    "jobType": "sync"
                },
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Failed to trigger sync: {e}")
            return False
    
    def get_connection_status(self, connection_id: str) -> Dict[str, Any]:
        """Get the status of a connection
        
        Args:
            connection_id: Connection ID
            
        Returns:
            Dictionary with connection status details
        """
        try:
            response = requests.get(
                f"{self.server_url}/v1/connections/{connection_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                connection = response.json()
                
                # Get latest job for this connection
                jobs_response = requests.get(
                    f"{self.server_url}/v1/jobs",
                    headers=self.headers,
                    params={"connectionId": connection_id, "limit": 1},
                    timeout=10
                )
                
                latest_job = None
                if jobs_response.status_code == 200:
                    jobs = jobs_response.json().get('data', [])
                    latest_job = jobs[0] if jobs else None
                
                return {
                    "status": connection.get('status', 'unknown'),
                    "last_sync": latest_job.get('createdAt') if latest_job else None,
                    "sync_status": latest_job.get('status', 'never_run') if latest_job else "never_run",
                    "records_synced": latest_job.get('rowsSynced', 0) if latest_job else 0
                }
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"Failed to get connection status: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_connections(self) -> List[Dict[str, Any]]:
        """List all connections in the workspace
        
        Returns:
            List of connection details
        """
        try:
            response = requests.get(
                f"{self.server_url}/v1/connections",
                headers=self.headers,
                params={"workspaceId": self.workspace_id},
                timeout=10
            )
            
            if response.status_code == 200:
                connections = response.json().get('data', [])
                return [
                    {
                        "id": conn.get('connectionId'),
                        "name": conn.get('name'),
                        "status": conn.get('status'),
                        "source_id": conn.get('sourceId'),
                        "destination_id": conn.get('destinationId')
                    }
                    for conn in connections
                ]
            else:
                print(f"Failed to list connections: {response.text}")
                return []
                
        except Exception as e:
            print(f"Failed to list connections: {e}")
            return []
    
    def create_generic_source(
        self, 
        service_type: str, 
        service_name: str, 
        credentials: Dict[str, Any]
    ) -> Optional[str]:
        """Create a source for any billing service
        
        Args:
            service_type: Type of service (stripe, chargebee, paddle, etc.)
            service_name: Display name for the connection
            credentials: Service-specific credentials
            
        Returns:
            Source ID if successful, None otherwise
        """
        source_definition_id = self._get_source_definition_id(service_type)
        
        if not source_definition_id:
            print(f"No Airbyte connector found for {service_type}")
            return None
        
        # Build connection configuration based on service type
        connection_config = self._build_connection_config(service_type, credentials)
        
        try:
            response = requests.post(
                f"{self.server_url}/v1/sources",
                headers=self.headers,
                json={
                    "workspaceId": self.workspace_id,
                    "name": service_name,
                    "sourceDefinitionId": source_definition_id,
                    "connectionConfiguration": connection_config
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('sourceId')
            else:
                print(f"Failed to create {service_type} source: {response.text}")
                return None
                
        except Exception as e:
            print(f"Failed to create {service_type} source: {e}")
            return None
    
    def _build_connection_config(
        self, 
        service_type: str, 
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build service-specific connection configuration
        
        Args:
            service_type: Type of service
            credentials: Raw credentials from UI
            
        Returns:
            Formatted connection configuration
        """
        # Service-specific configuration mappings
        config_builders = {
            # Revenue Services
            "stripe": lambda c: {
                "client_secret": c.get("api_key"),
                "account_id": c.get("account_id", ""),
                "start_date": "2024-01-01T00:00:00Z"
            },
            "chargebee": lambda c: {
                "api_key": c.get("api_key"),
                "site": c.get("site"),
                "start_date": "2024-01-01T00:00:00Z"
            },
            "paddle": lambda c: {
                "api_key": c.get("api_key"),
                "vendor_id": c.get("vendor_id")
            },
            "recurly": lambda c: {
                "api_key": c.get("api_key"),
                "subdomain": c.get("subdomain"),
                "begin_time": "2024-01-01T00:00:00Z"
            },
            "braintree": lambda c: {
                "merchant_id": c.get("merchant_id"),
                "public_key": c.get("public_key"),
                "private_key": c.get("private_key"),
                "environment": "sandbox"
            },
            "custom-revenue": lambda c: {
                "api_key": c.get("api_key"),
                "base_url": c.get("base_url"),
                "account_id": c.get("account_id", "")
            },
            
            # Usage Services
            "openai": lambda c: {
                "api_key": c.get("api_key"),
                "org_id": c.get("org_id", ""),
                "base_url": "https://api.openai.com/v1"
            },
            "anthropic": lambda c: {
                "api_key": c.get("api_key"),
                "base_url": "https://api.anthropic.com/v1"
            },
            "aws": lambda c: {
                "access_key_id": c.get("access_key_id"),
                "secret_access_key": c.get("secret_access_key"),
                "region": c.get("region", "us-east-1")
            },
            "datadog": lambda c: {
                "api_key": c.get("api_key"),
                "app_key": c.get("app_key"),
                "site": c.get("site", "datadoghq.com")
            },
            "custom-usage": lambda c: {
                "api_key": c.get("api_key"),
                "base_url": c.get("base_url"),
                "account_id": c.get("account_id", "")
            }
        }
        
        builder = config_builders.get(service_type)
        if builder:
            return builder(credentials)
        
        # Default: pass through credentials
        return credentials
    
    def _get_source_definition_id(self, source_name: str) -> str:
        """Get the definition ID for a source type
        
        Args:
            source_name: Name of the source (e.g., 'stripe', 'chargebee', 'openai')
            
        Returns:
            Source definition ID
        """
        # Known Airbyte source definition IDs
        # These are the official Airbyte connector IDs
        known_ids = {
            # Revenue Services
            "stripe": "e094cb9a-26de-4645-8761-65c0c425d1de",
            "chargebee": "9b2d3607-7222-4709-9fa2-c2abdebbdd88",
            "paddle": "d1aa448b-7c54-498e-ad96-b9fdbe4c9e44",
            "recurly": "dfd93f08-0e34-48e2-8d1f-3b22d5d8a9f8",
            "braintree": "aefd9a0c-e6e8-4f36-9cf5-4f7e92e7e6c6",
            "custom-revenue": "b76be0a6-27dc-4560-95f6-2623da0bd7b6",
            
            # Usage Services
            "openai": "custom-http-source",  # Would need custom connector
            "anthropic": "custom-http-source",
            "aws": "4d46b5b9-7b4f-41c0-8e4e-0d6f6c6a8f8e",  # AWS CloudWatch
            "datadog": "3e9c5e0c-7c4e-4c4e-8c4e-4c4e4c4e4c4e",
            "custom-usage": "b76be0a6-27dc-4560-95f6-2623da0bd7b6"
        }
        return known_ids.get(source_name, "")
    
    def _get_destination_definition_id(self, destination_name: str) -> str:
        """Get the definition ID for a destination type
        
        Args:
            destination_name: Name of the destination (e.g., 'sqlite', 'postgres')
            
        Returns:
            Destination definition ID
        """
        # Known destination definition IDs
        known_ids = {
            "sqlite": "b76be0a6-27dc-4560-95f6-2623da0bd7b6",
            "postgres": "25c5221d-dce2-4163-ade9-739ef790f503"
        }
        return known_ids.get(destination_name, "")


# Global instance
airbyte_service = AirbyteService()
