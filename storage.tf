# define the domain name with suffix 
locals {
  tenant_suffix = substr(replace(data.azurerm_client_config.current.tenant_id, "-", ""), 0, 6)
}

# create blob with public access and List permission
resource "azurerm_storage_account" "public" {
  name                     = "filestorage${local.tenant_suffix}"
  resource_group_name      = azurerm_resource_group.lab_rg.name
  location                 = azurerm_resource_group.lab_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "public_files" {
  name                  = "files"
  storage_account_name  = azurerm_storage_account.public.name
  container_access_type = "container"  # listable
}

# create private storage that can be accessed with SAS URL
resource "azurerm_storage_account" "private" {
  name                     = "privatestorage${local.tenant_suffix}"
  resource_group_name      = azurerm_resource_group.lab_rg.name
  location                 = azurerm_resource_group.lab_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "private_container" {
  name                  = "privatestorage"
  storage_account_name  = azurerm_storage_account.private.name
  container_access_type = "private"
}

# define the SAS so that it has read/list access di Storage Explorer
data "azurerm_storage_account_sas" "private_sas" {
  connection_string = azurerm_storage_account.private.primary_connection_string

  https_only = true
  start      = timeadd(timestamp(), "-5m")
  expiry     = timeadd(timestamp(), "720h") # ~30 days

  resource_types {
    service   = true
    container = true
    object    = true
  }

  services {
    blob  = true
    file  = false
    queue = false
    table = false
  }

  permissions {
    read    = true
    list    = true
    write   = false
    delete  = false
    add     = false
    create  = false
    update  = false
    process = false
    tag     = false
    filter  = false
  }
}

# unused
resource "azurerm_storage_blob" "registration_emails" {
  name                   = "registrationEmails.txt"
  storage_account_name   = azurerm_storage_account.private.name
  storage_container_name = azurerm_storage_container.private_container.name
  type                   = "Block"
  content_type           = "text/plain"

  source_content = <<EOT
Emails to contact to deal with customers registration:
adminregistration@gmail.com
customerregistration@gmail.com
supportregistration@gmail.com

Note: customerregistration@gmail.com is linked to internal automation workflows.
EOT
}

# hint for customerRegistration app
resource "azurerm_storage_blob" "customer_registration_creds" {
  name                   = "customerRegistration-creds.txt"
  storage_account_name   = azurerm_storage_account.private.name
  storage_container_name = azurerm_storage_container.private_container.name
  type                   = "Block"
  content_type           = "text/plain"

  source_content = <<EOT
API configuration for customer registration microservice (DO NOT COMMIT):

TENANT_ID     = ${data.azurerm_client_config.current.tenant_id}
CLIENT_ID     = ${azuread_application.customer_registration_app.client_id}
CLIENT_SECRET = ${azuread_application_password.customer_registration_secret.value}

Usage example (PowerShell):

$sec   = ConvertTo-SecureString '<CLIENT_SECRET>' -AsPlainText -Force
$creds = New-Object System.Management.Automation.PSCredential('<CLIENT_ID>', $sec)
Connect-AzAccount -ServicePrincipal -Tenant '<TENANT_ID>' -Credential $creds

Then use Get-AzAccessToken / Graph to enumerate and add secrets to other applications.
EOT

  depends_on = [
    azuread_application.customer_registration_app,
    azuread_service_principal.customer_registration_sp,
    azuread_application_password.customer_registration_secret
  ]
}

# specify isi public blob nya, dengan name userAccessToStorage dan berisi SAS URL
resource "azurerm_storage_blob" "access_instructions" {
  name                   = "userAccessToStorage"
  storage_account_name   = azurerm_storage_account.public.name
  storage_container_name = azurerm_storage_container.public_files.name
  type                   = "Block"
  content_type           = "text/plain"

  # SAS URL buat student
  source_content = <<EOT
If you haven't been provisioned access by sysadmin,
use this temporary link to view the company storage:

https://${azurerm_storage_account.private.name}.blob.core.windows.net/${azurerm_storage_container.private_container.name}${data.azurerm_storage_account_sas.private_sas.sas}

DO NOT FORWARD THIS LINK.
EOT
}
