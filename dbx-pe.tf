// Create private DNS zone for Databricks UI/API
resource "azurerm_private_dns_zone" "databricks" {
  name                = "privatelink.azuredatabricks.net"
  resource_group_name = azurerm_resource_group.rg["shared-services"].name
}

// Link private DNS zone to VNets
resource "azurerm_private_dns_zone_virtual_network_link" "databricks" {
  for_each = local.workspace_config
  name                  = "${each.value.name}-dns-link"
  resource_group_name   = azurerm_resource_group.rg["shared-services"].name
  private_dns_zone_name = azurerm_private_dns_zone.databricks.name
  virtual_network_id    = each.value.vnet_name
}

// Create private endpoints for Databricks UI/API
resource "azurerm_private_endpoint" "databricks_ui_api" {
  for_each            = local.workspace_config
  name                = "${each.value.name}-ui-api-pe"
  location            = each.value.location
  resource_group_name = each.value.resource_group
  subnet_id           = [for s in azurerm_virtual_network.vn[replace(each.key, "dbw_", "databricks-")].subnet : s.id if s.name == "databricks-pe"][0]

  private_service_connection {
    name                           = "${each.value.name}-ui-api-psc"
    private_connection_resource_id = azurerm_databricks_workspace.this[each.key].id
    is_manual_connection          = false
    subresource_names            = ["databricks_ui_api"]
  }

  private_dns_zone_group {
    name                 = "private-dns-zone-group"
    private_dns_zone_ids = [azurerm_private_dns_zone.databricks.id]
  }
} 

import {
  to = databricks_mws_ncc_private_endpoint_rule.ncc_dbfs_storage_dfs_pe_prod
  id = "5a5903b5-f4da-4d65-b302-6e77a95d3071/d8b12d62-3641-41c2-92ec-788cdfe77490"
}

