resource "azurerm_key_vault" "lab_kv" {
  name                        = "secretvault${substr(data.azurerm_client_config.current.tenant_id, 0, 6)}"
  location                    = azurerm_resource_group.lab_rg.location
  resource_group_name         = azurerm_resource_group.lab_rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  purge_protection_enabled    = false
  soft_delete_retention_days  = 7
  enable_rbac_authorization   = false
}

# Ensure Terraform has full secret permissions
resource "azurerm_key_vault_access_policy" "terraform_user" {
  key_vault_id = azurerm_key_vault.lab_kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = ["Get", "List", "Set", "Delete", "Purge"]
}

# Victim SP policy
resource "azurerm_key_vault_access_policy" "registeruser_policy" {
  key_vault_id = azurerm_key_vault.lab_kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azuread_service_principal.registeruser_sp.object_id

  secret_permissions = ["Get", "List"]
}

# Secret (ignore pre-read to remove 403 error)
resource "azurerm_key_vault_secret" "lab_secret" {
  depends_on = [azurerm_key_vault_access_policy.terraform_user]

  name         = "super-secret-vault"
  value        = "FLAG{C0nGr4tz_You_Ch41n3d_Th3_L4b}"
  key_vault_id = azurerm_key_vault.lab_kv.id

  lifecycle {
    ignore_changes = [value]
  }
}
