from pathlib import Path
from datetime import datetime, timedelta
import random
import json


# ============================================================
# KONNECT SYNTHETIC DATASET GENERATOR
# ============================================================

BASE_DIR = Path("data")

DOMAINS = [
    "jboss",
    "oracle",
    "application",
    "incidents",
    "error_codes",
    "troubleshooting",
]

random.seed(42)


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_directories():
    for domain in DOMAINS:
        (BASE_DIR / domain).mkdir(
            parents=True,
            exist_ok=True
        )


# ============================================================
# ERROR DEFINITIONS
# ============================================================

ERRORS = [
    {
        "code": "DB-CONNECTION-001",
        "domain": "oracle",
        "title": "Database Connection Failure",
        "cause": (
            "The application server is unable to establish "
            "a connection to the configured database."
        ),
        "checks": [
            "Verify database availability.",
            "Verify datasource configuration.",
            "Check database listener status.",
            "Verify network connectivity.",
            "Check configured database credentials."
        ]
    },
    {
        "code": "JBOSS-STARTUP-001",
        "domain": "jboss",
        "title": "JBoss Startup Failure",
        "cause": (
            "The JBoss server failed during startup because "
            "a required subsystem or configuration component "
            "could not initialize."
        ),
        "checks": [
            "Review the server startup log.",
            "Check the affected subsystem.",
            "Validate the server configuration.",
            "Check dependent services.",
            "Review errors reported before shutdown."
        ]
    },
    {
        "code": "JBOSS-DEPLOY-001",
        "domain": "jboss",
        "title": "Application Deployment Failure",
        "cause": (
            "The application deployment could not be completed "
            "because one or more deployment dependencies failed."
        ),
        "checks": [
            "Review deployment errors.",
            "Check application dependencies.",
            "Verify datasource availability.",
            "Validate deployment descriptors.",
            "Review JBoss server logs."
        ]
    },
    {
        "code": "APP-TIMEOUT-001",
        "domain": "application",
        "title": "Application Request Timeout",
        "cause": (
            "The application request exceeded the expected "
            "response time."
        ),
        "checks": [
            "Check application logs.",
            "Check downstream service availability.",
            "Review database response time.",
            "Check connection pool usage.",
            "Review infrastructure metrics."
        ]
    },
    {
        "code": "DB-LISTENER-001",
        "domain": "oracle",
        "title": "Database Listener Unavailable",
        "cause": (
            "The database listener required for establishing "
            "new database connections is unavailable."
        ),
        "checks": [
            "Verify listener availability.",
            "Verify database host connectivity.",
            "Check listener configuration.",
            "Review database server logs."
        ]
    },
]


# ============================================================
# SAMPLE TECHNICAL CONTENT
# ============================================================

JBOSS_DOCUMENTS = [
    (
        "jboss_startup_guide.txt",
        "JBoss Startup Troubleshooting",
        """
JBoss application servers perform multiple initialization steps
during startup. A startup failure should be investigated by reviewing
the server log and identifying the first meaningful error.

Errors reported near the end of a startup sequence may be symptoms
rather than the original cause.

When investigating startup problems, check configuration validity,
required subsystems, datasource initialization, network dependencies,
and deployment status.
"""
    ),
    (
        "jboss_datasource_guide.txt",
        "JBoss Datasource Troubleshooting",
        """
A datasource provides application access to a configured database.

When datasource initialization fails, the application may also fail
to deploy or start correctly.

Common investigation areas include database connectivity, datasource
configuration, credentials, network reachability, connection pool
configuration, and database listener availability.

The server log should be correlated with database-side information
before determining the root cause.
"""
    ),
    (
        "jboss_deployment_guide.txt",
        "JBoss Deployment Troubleshooting",
        """
Application deployment depends on successful initialization of the
required server subsystems and application dependencies.

A deployment failure should be investigated by reviewing the deployment
message, dependent datasource status, application configuration and
the server log.

If a deployment depends on a database and the datasource cannot
initialize, the deployment can fail as a downstream effect.
"""
    ),
]


ORACLE_DOCUMENTS = [
    (
        "oracle_connectivity.txt",
        "Oracle Connectivity Troubleshooting",
        """
Database connectivity problems can prevent application servers from
establishing new database sessions.

Investigation should include database availability, listener status,
network connectivity, configured connection details and credentials.

Application-side connection errors should be correlated with database
and listener information before determining the root cause.
"""
    ),
    (
        "oracle_listener.txt",
        "Oracle Listener Troubleshooting",
        """
The database listener accepts incoming connection requests.

If the listener is unavailable, applications attempting to establish
new database connections may report connection failures.

The investigation should verify listener availability, database host
reachability and listener configuration.
"""
    ),
    (
        "oracle_application_connectivity.txt",
        "Application Database Connectivity",
        """
An application database connection depends on multiple components.

The application configuration must identify the correct database
endpoint. Network connectivity must be available, the database must
be reachable, and the listener must accept connections.

A failure at any layer can appear as an application database error.
"""
    ),
]


APPLICATION_DOCUMENTS = [
    (
        "application_connectivity.txt",
        "Application Connectivity Troubleshooting",
        """
Application connectivity issues should be investigated across the
application, middleware and dependent services.

A database connectivity failure can appear as an application startup
or deployment failure.

Engineers should correlate timestamps across application logs,
middleware logs and dependent service information.
"""
    ),
    (
        "application_timeout.txt",
        "Application Timeout Troubleshooting",
        """
Application request timeouts can result from slow downstream
dependencies, database response delays, connection pool exhaustion
or infrastructure issues.

The investigation should begin with the request timestamp and then
correlate application, middleware and dependency logs.
"""
    ),
]


TROUBLESHOOTING_DOCUMENTS = [
    (
        "incident_investigation.txt",
        "Enterprise Incident Investigation",
        """
Incident investigation should begin with the observed symptom.

The first reported error is not always the root cause. Engineers
should correlate logs, error references, infrastructure information
and dependent-system documentation.

A reliable diagnosis should identify supporting evidence before
recommending corrective action.
"""
    ),
    (
        "root_cause_analysis.txt",
        "Root Cause Analysis Guidelines",
        """
Root cause analysis should distinguish between the original failure
and downstream symptoms.

For example, a database connectivity problem may cause datasource
initialization to fail, which may then cause application deployment
to fail.

The investigation should therefore follow the dependency chain
rather than treating the final error as the root cause.
"""
    ),
]


# ============================================================
# FILE WRITER
# ============================================================

def write_text_file(path, content):
    path.write_text(
        content.strip() + "\n",
        encoding="utf-8"
    )


# ============================================================
# GENERATE KNOWLEDGE DOCUMENTS
# ============================================================

def generate_knowledge_documents():

    for filename, title, content in JBOSS_DOCUMENTS:

        path = BASE_DIR / "jboss" / filename

        write_text_file(
            path,
            f"{title}\n\n{content}"
        )


    for filename, title, content in ORACLE_DOCUMENTS:

        path = BASE_DIR / "oracle" / filename

        write_text_file(
            path,
            f"{title}\n\n{content}"
        )


    for filename, title, content in APPLICATION_DOCUMENTS:

        path = BASE_DIR / "application" / filename

        write_text_file(
            path,
            f"{title}\n\n{content}"
        )


    for filename, title, content in TROUBLESHOOTING_DOCUMENTS:

        path = BASE_DIR / "troubleshooting" / filename

        write_text_file(
            path,
            f"{title}\n\n{content}"
        )


# ============================================================
# GENERATE ERROR REFERENCE DOCUMENTS
# ============================================================

def generate_error_documents():

    for error in ERRORS:

        content = f"""
Error Code: {error["code"]}

Title:
{error["title"]}

Domain:
{error["domain"]}

Description:
{error["cause"]}

Recommended Investigation:

"""

        for check in error["checks"]:
            content += f"- {check}\n"

        filename = f'{error["code"].lower()}.txt'

        path = BASE_DIR / "error_codes" / filename

        write_text_file(
            path,
            content
        )


# ============================================================
# GENERATE SYNTHETIC INCIDENTS
# ============================================================

def generate_incidents(count=100):

    start_time = datetime(2026, 1, 1, 8, 0, 0)

    for index in range(1, count + 1):

        incident_id = f"INC-{1000 + index}"

        error = random.choice(ERRORS)

        timestamp = (
            start_time +
            timedelta(
                minutes=index * 17
            )
        )

        incident = {
            "incident_id": incident_id,
            "timestamp": timestamp.isoformat(),
            "environment": random.choice(
                ["DEV", "UAT", "QA", "PROD-SIMULATION"]
            ),
            "application": random.choice(
                [
                    "CustomerService",
                    "PaymentService",
                    "AccountService",
                    "TransactionService",
                    "ReportingService",
                ]
            ),
            "server": random.choice(
                [
                    "APP-SRV-01",
                    "APP-SRV-02",
                    "APP-SRV-03",
                    "APP-SRV-04",
                ]
            ),
            "jboss_version": "7.4",
            "error_code": error["code"],
            "symptom": error["title"],
            "description": (
                f"Synthetic incident representing {error['title']}."
            ),
            "recommended_checks": error["checks"],
        }

        filename = f"{incident_id}.json"

        path = BASE_DIR / "incidents" / filename

        path.write_text(
            json.dumps(
                incident,
                indent=4
            ),
            encoding="utf-8"
        )


# ============================================================
# GENERATE SYNTHETIC SERVER LOGS
# ============================================================

def generate_logs(count=500):

    base_time = datetime(
        2026,
        2,
        1,
        9,
        0,
        0
    )

    for index in range(1, count + 1):

        incident_id = f"INC-{1000 + ((index - 1) % 100) + 1}"

        error = random.choice(ERRORS)

        timestamp = (
            base_time +
            timedelta(
                minutes=index * 5
            )
        )

        log_lines = [
            f"{timestamp.isoformat()} INFO  [server] Starting JBoss EAP 7.4",
            f"{timestamp.isoformat()} INFO  [server] Initializing server subsystems",
            f"{timestamp.isoformat()} INFO  [datasource] Initializing datasource",
        ]

        if error["code"] == "DB-CONNECTION-001":

            log_lines.extend(
                [
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[datasource] Database connection failed"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[datasource] Error Code: {error['code']}"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[deployment] Application deployment failed"
                    ),
                ]
            )

        elif error["code"] == "JBOSS-STARTUP-001":

            log_lines.extend(
                [
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[server] Server subsystem initialization failed"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[server] Error Code: {error['code']}"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[server] Server startup aborted"
                    ),
                ]
            )

        elif error["code"] == "JBOSS-DEPLOY-001":

            log_lines.extend(
                [
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[deployment] Application deployment failed"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[deployment] Error Code: {error['code']}"
                    ),
                ]
            )

        elif error["code"] == "APP-TIMEOUT-001":

            log_lines.extend(
                [
                    (
                        f"{timestamp.isoformat()} WARN "
                        f"[application] Request processing exceeded threshold"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[application] Error Code: {error['code']}"
                    ),
                ]
            )

        elif error["code"] == "DB-LISTENER-001":

            log_lines.extend(
                [
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[datasource] Database listener unavailable"
                    ),
                    (
                        f"{timestamp.isoformat()} ERROR "
                        f"[datasource] Error Code: {error['code']}"
                    ),
                ]
            )

        log_lines.append(
            f"{timestamp.isoformat()} INFO  [server] Incident reference: {incident_id}"
        )

        filename = f"server_log_{index:04d}.log"

        path = BASE_DIR / "jboss" / filename

        write_text_file(
            path,
            "\n".join(log_lines)
        )


# ============================================================
# GENERATE DATASET MANIFEST
# ============================================================

def generate_manifest():

    manifest = {
        "project": "KONNECT",
        "dataset_type": "synthetic",
        "purpose": (
            "Enterprise application and infrastructure "
            "knowledge retrieval and troubleshooting"
        ),
        "domains": DOMAINS,
        "contains_employer_data": False,
        "contains_production_logs": False,
        "generated_for": "KONNECT RAG demonstration",
    }

    path = BASE_DIR / "dataset_manifest.json"

    path.write_text(
        json.dumps(
            manifest,
            indent=4
        ),
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("Generating KONNECT synthetic dataset...")

    create_directories()

    generate_knowledge_documents()

    generate_error_documents()

    generate_incidents(
        count=100
    )

    generate_logs(
        count=500
    )

    generate_manifest()

    print("KONNECT dataset generation completed.")


if __name__ == "__main__":
    main()