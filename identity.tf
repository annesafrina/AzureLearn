data "azuread_client_config" "current" {}

#defining the user for initial access
resource "random_password" "philip_password" {
  length  = 18
  special = true
}

resource "azuread_user" "philip" {
  display_name        = "Philip Fish"
  mail_nickname       = "philip.fish"
  user_principal_name = "philip.fish@${var.tenant_domain}"
  password            = random_password.philip_password.result
  account_enabled     = true
}

# Assigning reader role to the user
resource "azurerm_role_assignment" "philip_reader" {
  principal_id         = azuread_user.philip.object_id
  role_definition_name = "Reader"
  scope                = "/subscriptions/${data.azurerm_client_config.current.subscription_id}"
}

resource "azuread_application" "customer_registration_app" {
  display_name = "customerRegistration"
}

resource "azuread_service_principal" "customer_registration_sp" {
  client_id = azuread_application.customer_registration_app.client_id
}

# App Admin role – allows adding secrets to any app (via Graph addPassword)
resource "azuread_directory_role" "app_admin_role" {
  display_name = "Application Administrator"
}

resource "azuread_directory_role_assignment" "customer_registration_admin" {
  role_id             = azuread_directory_role.app_admin_role.template_id
  principal_object_id = azuread_service_principal.customer_registration_sp.id
}


# clue for customerRegistration app (this is what we’ll leak in blob)
resource "azuread_application_password" "customer_registration_secret" {
  application_object_id = azuread_application.customer_registration_app.object_id
  display_name          = "customerRegistration-api-key"
  end_date_relative     = "720h"
}

resource "azuread_application" "registeruser_app" {
  display_name = "registeruser"
}

resource "azuread_service_principal" "registeruser_sp" {
  client_id = azuread_application.registeruser_app.client_id
}

resource "azurerm_role_assignment" "registeruser_reader" {
  principal_id         = azuread_service_principal.registeruser_sp.object_id
  role_definition_name = "Reader"
  scope                = "/subscriptions/${data.azurerm_client_config.current.subscription_id}"
}

#unused service
resource "azuread_application_owner" "customerregistration_owns_registeruser" {
  application_id  = azuread_application.registeruser_app.id
  owner_object_id = azuread_service_principal.customer_registration.id
}

data "azuread_directory_role" "dir_readers" {
  display_name = "Directory Readers"
}

resource "azuread_directory_role_assignment" "customerregistration_read" {
  role_object_id      = data.azuread_directory_role.dir_readers.id
  principal_object_id = azuread_service_principal.customer_registration.id
}

