import sys
import subprocess
import json
from pathlib import Path

banner = r"""
   █████████                                            █████                                              
  ███░░░░░███                                          ░░███                                               
 ░███    ░███   █████████ █████ ████ ████████   ██████  ░███         ██████   ██████   ████████  ████████  
 ░███████████  ░█░░░░███ ░░███ ░███ ░░███░░███ ███░░███ ░███        ███░░███ ░░░░░███ ░░███░░███░░███░░███ 
 ░███░░░░░███  ░   ███░   ░███ ░███  ░███ ░░░ ░███████  ░███       ░███████   ███████  ░███ ░░░  ░███ ░███ 
 ░███    ░███    ███░   █ ░███ ░███  ░███     ░███░░░   ░███      █░███░░░   ███░░███  ░███      ░███ ░███ 
 █████   █████  █████████ ░░████████ █████    ░░██████  ███████████░░██████ ░░████████ █████     ████ █████
░░░░░   ░░░░░  ░░░░░░░░░   ░░░░░░░░ ░░░░░      ░░░░░░  ░░░░░░░░░░░  ░░░░░░   ░░░░░░░░ ░░░░░     ░░░░ ░░░░░ 
                                                                                                                                                                                                                 
Welcome to AzureLearn! Let's start learning about Azure security.
"""
print(banner)


def highlight_commands(text):
    return f"\033[96m{text}\033[0m"

def highlight_title(text):
    return f"\033[95m{text}\033[0m"

def run_steps(steps, start_index=0):
    index = start_index
    while 0 <= index < len(steps):
        each_step = steps[index]
        print(f"STEP {index+1}: {each_step['title']}")
        print(each_step['text'])

        print("Options:")
        print("[1] Next")
        print("[2] Previous")
        print("[3] Remediation Steps")
        print("[4] Step Selection")
        print("[5] Exit")

        choice = input("choose your next action:").strip()
        if choice == "1":
            index += 1
        elif choice == "2":
            index -= 1
        elif choice == "3":
            print("In here you will learn how these misconfigurations can be prevented.")
            return "mitigation"
        elif choice == "4":
            print("Returning to step selection")
            return "resume"
        elif choice == "5":
            print("Exiting from guided mode")
            return
        else:
            print("please select a valid option")
    print("Congrats, you have completed the lab!")

cached_steps = None

def steps_elaboration(deploying=None):
    if deploying is None:
        print('Resuming mode activated')
    else:
        philip_upn = deploying["philip_upn"]["value"]
        philip_password = deploying["philip_password"]["value"]
        sas_url = deploying["leaks_container_sas_url"]["value"]
        registeruser_app_id = deploying["registeruser_app_id"]["value"]
        keyvault_name = deploying["key_vault_name"]["value"]

    steps = [
    {
        "title": "Initial Access",
        "text": f"""
        DEPLOYMENT IS COMPLETE.
        "title": {highlight_commands('Initial Access')}",
        For the lab simulation, we will refer to the deployed tenant as the {highlight_commands('Victim Tenant')}.

        For the initial access, we assume the attacker has compromised
        a low-privileged user account in the victim tenant.

        Use the following credentials for your *initial foothold*:

        Username: philip.fish@anneyulianastudentpresident.onmicrosoft.com
        Password: [REDACTED]

        Now we will learn about {highlight_commands('Multi-Factor Authentication Evasion')}

        Context:
        As of September 2025, Multi-Factor Authentication will be mandatory for all users in Azure cloud.
        This policy requires each user to put One-Time-Password (OTP) upon each login.
        This decreases attack surface, because even if the user credential is compromised, threat actors can't login unless they have access to the device where MFA is enabled.
        For more information: {highlight_commands('https://learn.microsoft.com/en-us/entra/identity/authentication/concept-mandatory-multifactor-authentication?tabs=dotnet')}

        To simulate the evasion of MFA, head over to {highlight_commands('https://portal.azure.com/')} and try to login using user Philip.
        You will be prompted with MFA.

        To evade this, we can retrieve the access token from other resources where MFA is not enabled.

        To retrieve the Graph API token you can authenticate to {highlight_commands('https://myapplications.microsoft.com')}

        To retrieve the ARM Azure Resource Management, you can authenticate to {highlight_commands('https://cosmos.azure.com/')}

        Both of these resources {highlight_commands('does not prompt')} user with MFA.
        

        Open a new PowerShell and store the token using variable {highlight_commands('ARMToken')} and {highlight_commands('graphToken')}, then on the same PowerShell session, 
        authenticate using the following command:
        {highlight_commands('Connect-AzAccount -AccessToken $ARMToken -MicrosoftGraphAccessToken $graphToken -AccountId philip.fish@anneyulianastudentpresident.onmicrosoft.com')}


        """,
    },
    {
        "title": "Insecure Blob Storage",
        "text": f"""
        "title": {highlight_commands('Insecure Blob Storage')}",

        To ensure a thorough enumeration, you are encouraged to enumerate resources as in-depth as possible

        Try using this command:
        {highlight_commands('Get-AzResource')}

        We can see that there exists two storage accounts and one key vault.

        Try to see the content of the key vault using the following commands:

        {highlight_commands('Get-AzKeyVaultSecret -VaultName [your_key_vault_name]')}

        You would see that your compromised user does not have access to the inside of the key vault.

        Keep this in mind, as this is an important context for the {highlight_commands('Privilege Escalation')} later

        """,
    },

    {
        "title": "Obtain Information From The Blob Storage",
        "text": f"""
        "title": {highlight_commands('Obtain Information From The Blob Storage')}",

        Upon enumerating, you would see that there is a storage account with the name {highlight_commands('filestorage')}

        You can see the content of the storage account by using the query:

        {highlight_commands('curl -i "https:[nameOfYourStorageAccount].blob.core.windows.net/files?restype=container&comp=list"')}

        In the query you should understand that:

        {highlight_commands('restype -> is utilized to request resource with the type "Container"')}
        {highlight_commands('comp -> is utilized to specify the type of operation, in this case "List"')}

        Inside the storage account, you would notice that there is a blob storage with the name specified on:
        {highlight_commands('<name>')}

        From that information, we can assume that there exists a blob storage with that name.

        Use the following command to enumerate the content of the blob storage:
        {highlight_commands('curl -i "https://filestoragexxx.blob.core.windows.net/files/[nameOfBlobStorage]"')}

        You would see that there is a {highlight_commands('SAS URL')} inside the blob storage.

        """,
    },

    {
        "title": "SAS URL Leak",
        "text": f"""
        "title": {highlight_commands('Using SAS URL')}",

        We have obtained the SAS URL with the assumption that it belongs to another user in the target tenant.

        Download and open {highlight_commands('Microsoft Azure Storage Explorer')}

        Choose the Connect Dialog option > Select a resource > choose Blob > choose using SAS URL

        Finally, use the SAS URL to authenticate.

        And see the content of the Blob.

        """,
    },

    {
        "title": "Application Admin Role Abuse",
        "text": f"""
        "title": {highlight_commands('Application Admin Abuse')}",

        Upon enumerating you would see that there is function apps in the tenant.

        Try to run {highlight_commands('Get-AzADApplication')}

        Attempt to add {highlight_commands('Client Secret')} to each function apps using automated tool.

        Use the following script to automate the attempts:
        https://github.com/lutzenfried/OffensiveCloud/blob/main/Azure/Tools/Add-AzADAppSecret.ps1

        Import the script (ensure you are in the same directory where the script is stored when running):
        {highlight_commands('. .\Add-AzADAppSecret.ps1')}

        Run with:
        {highlight_commands('Add-AzADAppSecret -GraphToken $graphaccesstoken -Verbose')}


        """,
    },
    {
        "title": "Authenticate Using Client Secret",
        "text": f"""
        "title": {highlight_commands('Authenticate Using Client Secret')}",

        Now use the Client Secret to authenticate.

        In your PowerShell, store the following client secret inside a variable:

        {highlight_commands('$password = ConvertTo-SecureString [your_client_secret] -AsPlainText -Force')}

        Then, specify the credential variable:

        {highlight_commands('$credential = New-Object System.Management.Automation.PSCredential([app_id], $password)')}

        After specifying the necessary components, authenticate:

        {highlight_commands('Connect-AzAccount -ServicePrincipal -Credential $credential -Tenant [tenant_id]')}



        """,
    },
        {
        "title": "Key Vault Abuse",
        "text": f"""
        "title": {highlight_commands('Key Vault Abuse')}",

        After we have authenticated using the client secret, we may start to enumerate again to see if there 
        are resources that we cannot gain access to earlier on.

        
        Let's try to enumerate the key vault:
        {highlight_commands('Get-AzKeyVault')}

        In here, we can see that the given service principal (application service) has reader access to the key vault.

        Let's see if we can access the inside of the key vault:

        {highlight_commands('Get-AzKeyVaultSecret -VaultName [your_vault_name]')}

        BOOM! As it turns out we have access to see the content, which the user Philip does not have access to earlier.

        Let's see the content of the secret:
        {highlight_commands('Get-AzKeyVaultSecret -VaultName [your_vault_name] -Name [name_of_the_vault]')}

        YAY!!!! YOU HAVE SUCCESSFULLY ESCALATE YOUR PRIVILEGE
        """,
    },
]
    return steps
    

def load_terraform():
    tf_dir = Path(__file__).resolve().parent

    print("Using Terraform Init, please wait!")
    subprocess.run(["terraform", "init"], cwd=tf_dir, check=True)

    print("Applying Terraform, please wait1")
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=tf_dir, check=True)

    print("Waiting...")
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=tf_dir,
        capture_output=True,
        text=True,
        check=True
    )
    
    return json.loads(result.stdout)


def choose_mode():
    print("Select your desired mode for this lab:\n")
    print("[1] Independent Mode --> explore this lab on your own at your own pace")
    print("[2] Guided Mode --> receive step-by-step support")
    print("[3] Resume --> resume your current progress (if any)")

    while True:

        choice = input("enter your choice here, please: ").strip()

        if choice == "1":
            print("You have selected independent mode, enjoy exploring the lab!")
            return "independent"
        if choice == "2":
            print("You have selected guided mode")
            return "guided"
        if choice == "3":
            print("You have selected to resume your previous progress")
            return "resume"
        else:
            print("please choose a valid option")

def mode_independent():
    sys.exit(0)

def mode_guided():
    print("Please wait for your lab to be deployed")
    deploying = load_terraform()
    steps = steps_elaboration(deploying)
    print("Deployment is done. Let's start learning!")
    result = run_steps(steps)
    if result == "mitigation":
        mitigation()
    elif result == "resume":
        mode_resume()

def mode_resume():
    global cached_steps
    print("Yay, let's resume on your learning progress")


    sections = ["Initial Access & Multi-Factor-Authentication Evasion", "Insecure Blob Storage", "Shared Access Signatural (SAS) URL Abuse", "Application Admin Role Abuse",
                "Key Vault Abuse"]
    
    for i, m in enumerate(sections, start=1):
        print(f"[{i}] {m}")
    while True:
        choice = input("Pick the selection you want to resume: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(sections):
            section_index = int(choice) - 1
            break
        print("Invalid section. Please choose the valid ones")
    if cached_steps is not None:
        steps = cached_steps
    else:
        print('resume mode')
        steps = steps_elaboration(deploying=None)


    print(f"Cool! Let's resume from {sections[section_index]}")
    result = run_steps(steps, start_index=section_index)

    if result == "resume":
        mode_resume()
    elif result == "mitigation":
        mitigation()

def mitigation_steps():
    return [
        {
            "title": "Initial Access & MFA Evasion",
            "text": f"""
                MITIGATION: Prevent Initial Access & MFA Evasion

                • Enforce phishing-resistant MFA (FIDO2 / certificate-based)
                • Disable legacy authentication protocols
                • Monitor token replay via Entra ID sign-in logs
                • Conditional Access: block non-interactive logins

            References:
            https://learn.microsoft.com/en-us/entra/identity/authentication/concept-phishing-resistant-mfa
        """
        },
        {
            "title": "Insecure Blob Storage",
            "text": f"""
            MITIGATION: Secure Blob Storage

            • Disable public blob access at account level
            • Enforce private containers only
            • Use Azure Policy:
                - Storage accounts should restrict public access
            • Monitor AnonymousSuccess via Storage Analytics

            CLI:
            {highlight_commands("az storage account update --allow-blob-public-access false")}

            References:
            https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent
            """
        },
        {
            "title": "SAS URL Abuse",
            "text": f"""
            MITIGATION: SAS Token Abuse Prevention

            • Use User Delegation SAS (Azure AD-backed)
            • Set shortest possible expiry
            • Restrict IP and protocol
            • Rotate storage keys regularly

            Detection:
            • Monitor SAS authentication events
            • Alert on long-lived SAS tokens

            References:
            https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview
            """
        },
        {
            "title": "Application Admin Role Abuse",
            "text": f"""
            MITIGATION: Application Administrator Abuse

            • Minimize Application Administrator assignments
            • Use Privileged Identity Management (PIM)
            • Alert on addPassword / addKey events
            • Require approval for app credential creation

            Detection:
            • AuditLogs → Add service principal credentials
            • Microsoft Graph auditLogs

            References:
            https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/privileged-roles-permissions
            """
        },
        {
            "title": "Key Vault Abuse",
            "text": f"""
            MITIGATION: Key Vault Hardening

            • Separate Key Vault into dedicated Resource Group
            • Avoid subscription-level Reader
            • Use RBAC over access policies
            • Enable Key Vault diagnostic logs

            Detection:
            • SecretGet / SecretList operations
            • AzureActivity + KeyVault logs

            References:
            https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide
            """
        }
    ]

def mitigation():
    global cached_steps
    mit_sections = ["Initial Access & Multi-Factor-Authentication Evasion", "Insecure Blob Storage", "Shared Access Signatural (SAS) URL Abuse", "Application Admin Role Abuse",
                "Key Vault Abuse"]
    
    for i, m in enumerate(mit_sections, start=1):
        print(f"[{i}] {m}")
    while True:
        choice = input("Pick the remediation step you'd like to know: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(mit_sections):
            mit_index = int(choice) - 1
            break
        print("Invalid section. Please choose the valid ones")
    mit_steps = mitigation_steps()


    print(f"Cool! Let's take a look defensive guidance for {mit_sections[mit_index]}")
    run_steps(mit_steps, start_index=mit_index)


def main():
    mode = choose_mode()

    if mode == "independent":
        mode_independent()
    elif mode == "guided":
        mode_guided()
    elif mode == "resume":
        mode_resume()
    elif mode == "mitigation":
        mitigation()
    else:
        print("")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser terminates the CLI, exiting now.")
    except Exception as e:
        print("\nUnexpected behavior occured.")

