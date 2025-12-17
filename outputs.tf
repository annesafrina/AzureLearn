output "philip_upn" {
  value = azuread_user.philip.user_principal_name
}

output "philip_password" {
  value     = random_password.philip_password.result
  sensitive = true
}

output "public_files_list_url" {
  description = "URL Philip can use (or script) to list the public files container"
  value       = "https://${azurerm_storage_account.public.name}.blob.core.windows.net/files?restype=container&comp=list"
}

output "public_userAccessToStorage_blob" {
  description = "URL for the userAccessToStorage blob"
  value       = "https://${azurerm_storage_account.public.name}.blob.core.windows.net/files/userAccessToStorage"
}

output "customer_registration_client_id" {
  value = azuread_application.customer_registration_app.client_id
}

output "registeruser_app_id" {
  value = azuread_application.registeruser_app.client_id
}

output "key_vault_name" {
  value = azurerm_key_vault.lab_kv.name
}
