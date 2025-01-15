provider "azapi" {}

resource "azapi_resource" "approve_endpoint" {
  type      = "Microsoft.Storage/storageAccounts/privateEndpointConnections@2021-04-01"
  name      = "connection-name"
  parent_id = azurerm_storage_account.example.id
  
  body = jsonencode({
    properties = {
      privateLinkServiceConnectionState = {
        status      = "Approved"
        description = "Approved via Terraform"
      }
    }
  })
}
