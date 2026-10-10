# Software Requirements Specification (SRS)

## Infinity Hack '26 --- AI Project Manager: Meeting to Execution

**Document version:** 1.0\
**Status:** Design baseline\
**Date:** 10 October 2026\
**Target implementation:** Django REST Framework backend with PostgreSQL
and OpenRouter\
**Document purpose:** Define the functional and non-functional
requirements for the backend API. This document is a specification; it
does not contain implementation code.

------------------------------------------------------------------------

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification defines the requirements for
the backend of the Infinity Hack '26 AI Project Manager challenge. The
system converts meeting transcripts into structured project and task
plans, allows an administrator to review and correct the generated
draft, validates the draft, and saves approved records to a database.

The backend also provides authentication, role-based access control, and
APIs for users to view the projects and tasks they are authorized to
access.

### 1.2 Scope

The system is a lightweight project-management CRM for the fictional
company NovaWorks Technologies in Lahore, Pakistan.

The backend shall support:

-   Authentication for seeded demo users.
-   Three roles: administrator, project manager, and developer agent.
-   Project and task data storage in PostgreSQL.
-   Role-scoped project and task read APIs.
-   AI-assisted extraction of projects and tasks from meeting
    transcripts using OpenRouter.
-   A preview, validation, review, and explicit confirmation workflow
    before persistence.
-   Validation and atomic saving so a failed confirmation does not leave
    partial project/task records.
-   Repeatable demo-data seeding and setup documentation.

The scope is limited to the challenge requirements and the architecture
decisions confirmed for this project.

### 1.3 Intended Audience

This document is intended for:

-   Backend engineers.
-   Frontend engineers integrating with the API.
-   QA engineers and testers.
-   Hackathon team members.
-   Demonstrators and judges who need to understand expected behavior.

### 1.4 Definitions and Acronyms

  -----------------------------------------------------------------------
  Term                                Definition
  ----------------------------------- -----------------------------------
  Admin                               Administrator role. Can access all
                                      project/task data and use
                                      transcript-to-project creation.

  Manager                             Project manager role. Can access
                                      projects assigned to them and tasks
                                      within those projects.

  Agent                               Developer agent role. Can access
                                      their own tasks and related project
                                      information.

  Draft                               AI-extracted or subsequently edited
                                      project/task data that has not yet
                                      been committed as business records.

  OpenRouter                          External API service used to access
                                      a configurable AI model.

  JWT                                 JSON Web Token used for API
                                      authentication.

  Idempotency key                     Client-supplied identifier used to
                                      prevent a repeated operation from
                                      creating duplicate records.

  Atomic transaction                  A database operation in which all
                                      intended changes succeed together
                                      or none are committed.

  SRS                                 Software Requirements
                                      Specification.
  -----------------------------------------------------------------------

### 1.5 Reference Materials

This specification is based on the supplied Infinity Hack '26 student
challenge pack and rulebook, the supplied README template, and the
architecture decisions confirmed during planning.

The selected backend technologies---Django REST Framework, PostgreSQL,
JWT authentication, and configurable OpenRouter integration---are
architecture decisions for this implementation.

------------------------------------------------------------------------

## 2. Overall Description

### 2.1 Product Perspective

The backend is a single Django application exposing versioned REST APIs.
It integrates with PostgreSQL for persistence and OpenRouter for
AI-assisted transcript extraction. The frontend communicates with the
backend over HTTP and is responsible for presenting the draft to the
administrator for review.

The backend, not the frontend or AI model, is the authority for
authentication, authorization, validation, and persistence.

### 2.2 User Classes

#### Administrator (`ADMIN`)

The administrator can:

-   Authenticate using a seeded demo account.
-   View all projects and tasks.
-   Submit meeting transcripts for extraction.
-   Preview the generated draft.
-   Review and correct draft fields.
-   Request validation of a draft.
-   Confirm a valid draft for persistence.
-   View the resulting project and task records.

#### Project Manager (`MANAGER`)

A project manager can:

-   Authenticate using a seeded demo account.
-   List and retrieve projects managed by them.
-   View tasks belonging to their managed projects.
-   View relevant team information permitted by the API.

A manager cannot use the transcript-creation workflow and cannot access
another manager's project or its tasks.

#### Developer Agent (`AGENT`)

An agent can:

-   Authenticate using a seeded demo account.
-   View tasks assigned to them.
-   View related project information, including the project name and
    manager.
-   View only the task details they are authorized to access.

An agent cannot access another agent's tasks by guessing or supplying a
record identifier.

### 2.3 Operating Environment

The intended backend environment includes:

-   A supported Python runtime compatible with the selected Django
    release.
-   Django and Django REST Framework.
-   PostgreSQL.
-   A JWT authentication package and configured token lifecycle.
-   Network access to the configured OpenRouter API when transcript
    extraction is requested.
-   Environment-based configuration for secrets and deployment settings.

Exact runtime and dependency versions shall be pinned in the
implementation's dependency manifest.

### 2.4 Design and Implementation Constraints

-   A custom Django user model must be configured before initial
    database migrations.
-   PostgreSQL is the target database.
-   OpenRouter model selection must be configurable through an
    environment variable.
-   The OpenRouter API key and Django secret must not be committed to
    source control.
-   Passwords must be stored using Django's password hashing mechanisms.
-   The AI model must not receive passwords, password hashes, JWTs, or
    other authentication secrets.
-   The system must use real database relationships between users,
    projects, and tasks.
-   No user-signup or password-reset workflow is required.
-   The backend must not rely on frontend-only authorization checks.

### 2.5 Assumptions and Dependencies

-   The required ten demo accounts are seeded before the demonstration.
-   The OpenRouter key and a valid model identifier are configured in
    the environment.
-   The selected model supports the structured extraction approach used
    by the implementation; the exact model is a deployment configuration
    choice.
-   The frontend will provide an administrator review and confirmation
    interface.
-   The initial demo dataset is the authoritative source for employee
    identities and the specified project/task plan.
-   If the AI provider is unavailable, the backend will report a
    controlled failure rather than silently saving an incomplete draft.

------------------------------------------------------------------------

## 3. System Features and Functional Requirements

Requirement identifiers are intended to remain stable for implementation
and test traceability.

### 3.1 Authentication

**FR-AUTH-001 --- Login**\
The system shall allow a seeded user to authenticate using their email
and password.

**FR-AUTH-002 --- Token issuance**\
On successful authentication, the system shall return the configured JWT
token response and a safe user summary containing the user's identifier,
name, email, and role.

**FR-AUTH-003 --- Invalid credentials**\
The system shall reject invalid credentials without revealing whether a
particular email address exists.

**FR-AUTH-004 --- Authenticated endpoints**\
Endpoints requiring authentication shall reject requests with missing,
invalid, or expired access tokens.

**FR-AUTH-005 --- Current user**\
The system shall provide an endpoint for retrieving the authenticated
user's safe profile.

**FR-AUTH-006 --- Token refresh and logout**\
The system shall support token refresh. Logout shall invalidate refresh
tokens if refresh-token blacklisting is enabled in the selected JWT
configuration.

**FR-AUTH-007 --- No public registration**\
The system shall not expose public signup or password-reset
functionality for the challenge MVP.

### 3.2 Demo Accounts and Team Directory

**FR-TEAM-001 --- Seeded users**\
The system shall support ten seeded demo accounts: one administrator,
three project managers, and six developer agents.

**FR-TEAM-002 --- Stable references**\
The seed process shall use stable employee references such as `PM01` and
`DEV01` to map challenge identities to database users.

**FR-TEAM-003 --- Safe team data**\
Team API responses shall not expose password hashes, passwords, tokens,
or other authentication secrets.

**FR-TEAM-004 --- Repeatable seeding**\
Running the seed process repeatedly shall not create duplicate demo
users or unexpectedly reset existing credentials unless an explicit
reset operation is designed and documented.

**FR-TEAM-005 --- Assignment eligibility**\
Only existing users with the correct role may be selected as project
managers or task assignees.

### 3.3 Projects

**FR-PROJ-001 --- Project fields**\
A project shall store an identifier, name, client name, description,
manager reference, and deadline.

**FR-PROJ-002 --- Manager relationship**\
Each project shall reference one existing user with the `MANAGER` role.

**FR-PROJ-003 --- Project listing**\
The system shall provide a project list endpoint whose results are
scoped to the authenticated user's role.

**FR-PROJ-004 --- Project detail**\
The system shall provide a project detail endpoint that returns a
project only when the user is authorized to view it.

**FR-PROJ-005 --- Project/task relationship**\
Tasks shall reference an existing project.

### 3.4 Tasks

**FR-TASK-001 --- Task fields**\
A task shall store an identifier, project reference, title, description,
assignee reference, deadline, and estimated hours.

**FR-TASK-002 --- Assignee relationship**\
Each task shall reference an existing user with the `AGENT` role.

**FR-TASK-003 --- Estimated hours**\
Estimated hours shall be a positive numeric value within the limits
selected and documented by the implementation.

**FR-TASK-004 --- Task deadline**\
A task deadline shall not be later than the deadline of its parent
project, unless the challenge requirements are explicitly revised.

**FR-TASK-005 --- Task listing**\
The system shall provide task list and task detail endpoints that
enforce role-based data access.

**FR-TASK-006 --- My tasks**\
The system shall provide a current-user task endpoint. For an agent, it
shall return only tasks assigned to that agent. Behavior for non-agent
roles shall be documented consistently by the API.

### 3.5 Transcript Extraction

**FR-AI-001 --- Admin-only access**\
Only authenticated administrators shall be able to invoke transcript
extraction, draft validation, or confirmation endpoints.

**FR-AI-002 --- Transcript submission**\
The system shall accept meeting transcript text through a versioned REST
endpoint.

**FR-AI-003 --- OpenRouter integration**\
The system shall send the transcript, an allowed team directory, and the
required output structure to the configured OpenRouter model.

**FR-AI-004 --- Configurable model**\
The OpenRouter model identifier shall be supplied through environment
configuration rather than hardcoded in business logic.

**FR-AI-005 --- Structured draft**\
The system shall transform valid model output into a structured draft
containing project fields and nested or associated task fields.

**FR-AI-006 --- Existing team only**\
The extraction process shall not invent employees. Every proposed
manager and assignee must resolve to an existing eligible database user.

**FR-AI-007 --- Decisions versus suggestions**\
The extraction instructions and validation process shall distinguish
final agreed decisions from rejected ideas, superseded suggestions, and
unapproved proposals.

**FR-AI-008 --- Required fields**\
The system shall identify missing or invalid required project/task
fields and report them as validation findings.

**FR-AI-009 --- No persistence during preview**\
The preview operation shall not create project or task business records.

**FR-AI-010 --- Provider failures**\
Timeouts, rate limits, unavailable models, malformed responses, and
other provider errors shall be handled through controlled API errors.
The system shall not save a partial draft as completed business data.

### 3.6 Draft Review and Validation

**FR-DRAFT-001 --- Preview response**\
The preview endpoint shall return the extracted draft, its identifier or
version reference, and validation findings.

**FR-DRAFT-002 --- Editable draft**\
The administrator shall be able to submit corrected draft data for
validation.

**FR-DRAFT-003 --- Full revalidation**\
Every edited draft shall be revalidated, including all project fields,
task fields, user references, date rules, and relationships.

**FR-DRAFT-004 --- Actionable errors**\
Validation responses shall identify the affected field or record and
provide a useful explanation of the failure.

**FR-DRAFT-005 --- Version tracking**\
The backend shall track the version of the draft that was validated. A
change after validation shall require validation again.

**FR-DRAFT-006 --- Explicit confirmation**\
Business records shall be created only after an explicit administrator
confirmation of the validated draft.

**FR-DRAFT-007 --- Stale draft protection**\
The confirmation endpoint shall reject a stale or mismatched draft
version.

### 3.7 Persistence and Duplicate Protection

**FR-SAVE-001 --- Atomic creation**\
The backend shall create all projects and tasks in one database
transaction for a single confirmation operation.

**FR-SAVE-002 --- Rollback on failure**\
If any project or task fails to save, the transaction shall roll back
all business-record changes from that confirmation.

**FR-SAVE-003 --- Revalidation at confirmation**\
The backend shall recheck the draft and relevant database references
immediately before committing records.

**FR-SAVE-004 --- Idempotency**\
The preview/confirmation workflow shall use an idempotency strategy so
repeated client submissions cannot create duplicate project/task
records.

**FR-SAVE-005 --- Success response**\
On success, the API shall return identifiers and summaries for the
created projects and tasks.

**FR-SAVE-006 --- Persistence**\
Created records shall remain available after application restarts,
subject to normal database durability and deployment practices.

### 3.8 Authorization

**FR-PERM-001 --- Admin visibility**\
An administrator shall be able to view all projects and tasks.

**FR-PERM-002 --- Manager visibility**\
A manager shall only be able to view projects for which they are the
assigned manager and tasks belonging to those projects.

**FR-PERM-003 --- Agent visibility**\
An agent shall only be able to view tasks assigned to them. They may
view limited information about related projects, including project name
and manager, as required by the challenge.

**FR-PERM-004 --- Object-level protection**\
The system shall enforce permissions in server-side querysets and
object-level checks. Hiding a record in the frontend is not sufficient.

**FR-PERM-005 --- Unauthorized identifiers**\
A user shall not gain access by guessing another project or task
identifier. The API shall return a consistent not-found or forbidden
response according to the selected security policy.

**FR-PERM-006 --- No unauthorized writes**\
No role shall be able to alter project/task records through an endpoint
that has not been explicitly authorized and specified.

### 3.9 API Documentation and Demo Support

**FR-DOC-001 --- API contract**\
The project shall document endpoints, authentication requirements,
request fields, response fields, and error responses.

**FR-DOC-002 --- Setup instructions**\
The README shall describe environment setup, database setup, migrations,
seeding, running the server, and testing the transcript workflow.

**FR-DOC-003 --- Demo credentials**\
The README shall document the fictional demo accounts and their intended
roles. Credentials shall be limited to the challenge demo environment.

**FR-DOC-004 --- Limitations**\
The documentation shall identify unimplemented or out-of-scope features
and any provider/setup limitations.

------------------------------------------------------------------------

## 4. Business Rules

The following rules apply to transcript-derived project and task
creation.

1.  A project must have a valid name, client name, description, manager,
    and deadline.
2.  A project manager must be an existing user whose role is `MANAGER`.
3.  A task must have a valid project, title, description, eligible
    agent, deadline, and positive estimated hours.
4.  A task assignee must be an existing user whose role is `AGENT`.
5.  A task deadline must be consistent with the parent project deadline.
6.  Rejected ideas and superseded suggestions must not be converted into
    approved tasks.
7.  Employees must not be invented or created by the AI workflow.
8.  Ambiguous or missing required information must be corrected and
    validated before confirmation.
9.  The AI model's output is untrusted input and must be validated by
    the backend.
10. A failed confirmation must not leave partial project/task records.
11. Passwords and authentication secrets must never be sent to
    OpenRouter.
12. The initial challenge plan consists of three projects and twelve
    tasks.

### 4.1 Required Initial Challenge Dataset

  ---------------------------------------------------------------------------------
  Project       Client        Manager    Project          Task count          Total
                                         deadline                         estimated
                                                                              hours
  ------------- ------------- ---------- ------------ -------------- --------------
  UrbanCart     UrbanCart     Ayesha     2026-10-20                4             40
  Website       Clothing      Khan                                   
                              (`PM01`)                               

  QuickServe    QuickServe    Bilal      2026-10-24                4             46
  Mobile App    Services      Ahmed                                  
                              (`PM02`)                               

  HelpDeskPro   HelpDeskPro   Hina Malik 2026-10-22                4             38
  AI Assistant  Solutions     (`PM03`)                               

  **Total**                                                   **12**        **124**
  ---------------------------------------------------------------------------------

The detailed task assignments and deadlines shall follow the supplied
challenge pack. The seed dataset and acceptance tests should use those
supplied values as the expected baseline.

### 4.2 Out-of-Scope Features

The following features are not part of the required MVP:

-   Public signup.
-   Forgot-password and email-verification workflows.
-   User-management UI or general-purpose user administration.
-   Payment processing.
-   Inventory integration.
-   Maps or mapping integrations.
-   External real-email integration.
-   Automatic creation of employees from transcript content.

------------------------------------------------------------------------

## 5. External Interface Requirements

### 5.1 REST API

-   API base path: `/api/v1/`.
-   Data exchange format: JSON, except where a request format is
    explicitly documented otherwise.
-   Dates: ISO 8601 date format for date-only fields.
-   Authentication: JWT bearer access token for protected endpoints.
-   The API shall use appropriate HTTP status codes and consistent error
    structures.
-   Pagination and filtering behavior shall be documented if enabled.

### 5.2 Endpoint Inventory

  -----------------------------------------------------------------------------------
  Method            Endpoint                      Access            Description
  ----------------- ----------------------------- ----------------- -----------------
  `POST`            `/auth/login/`                Public            Authenticate user

  `POST`            `/auth/refresh/`              Refresh token     Refresh access
                                                                    token

  `POST`            `/auth/logout/`               Authenticated     Invalidate
                                                                    refresh token
                                                                    when supported

  `GET`             `/auth/me/`                   Authenticated     Current-user
                                                                    profile

  `GET`             `/team/`                      Authenticated,    Permitted team
                                                  scoped            directory

  `GET`             `/team/{id}/`                 Authenticated,    Permitted
                                                  scoped            team-member
                                                                    detail

  `GET`             `/projects/`                  Authenticated,    Visible project
                                                  scoped            list

  `GET`             `/projects/{id}/`             Authenticated,    Visible project
                                                  scoped            detail

  `GET`             `/projects/{id}/tasks/`       Authenticated,    Visible tasks for
                                                  scoped            a project

  `GET`             `/tasks/`                     Authenticated,    Visible task list
                                                  scoped            

  `GET`             `/tasks/{id}/`                Authenticated,    Visible task
                                                  scoped            detail

  `GET`             `/tasks/my-tasks/`            Authenticated     Current-user task
                                                                    view

  `POST`            `/ai/transcripts/preview/`    Admin             Extract draft
                                                                    without saving
                                                                    business records

  `POST`            `/ai/transcripts/validate/`   Admin             Validate or
                                                                    revalidate draft

  `POST`            `/ai/transcripts/create/`     Admin             Confirm and save
                                                                    a validated draft
  -----------------------------------------------------------------------------------

### 5.3 Standard HTTP Status Codes

  -----------------------------------------------------------------------
  Status                              Intended use
  ----------------------------------- -----------------------------------
  `200 OK`                            Successful retrieval, validation,
                                      preview, or supported token
                                      operation

  `201 Created`                       Successful creation of project/task
                                      records

  `400 Bad Request`                   Invalid input or business-rule
                                      validation errors

  `401 Unauthorized`                  Missing or invalid authentication

  `403 Forbidden`                     Authenticated caller lacks
                                      permission

  `404 Not Found`                     Record is missing or not visible
                                      under the chosen access policy

  `409 Conflict`                      Stale draft, version conflict, or
                                      conflicting duplicate operation

  `429 Too Many Requests`             Rate limit reached

  `502 Bad Gateway`                   Invalid or failed upstream AI
                                      response

  `503 Service Unavailable`           Temporarily unavailable dependency
                                      or service
  -----------------------------------------------------------------------

The implementation shall define the precise status code for each failure
mode and use it consistently.

### 5.4 Error Response Requirements

An error response should include:

-   A stable error code.
-   A human-readable message.
-   Field-level or record-level validation details where applicable.
-   A request or correlation identifier where available.

Error responses must not include stack traces, API keys, passwords,
password hashes, tokens, or unfiltered upstream error payloads.

------------------------------------------------------------------------

## 6. Data Requirements

### 6.1 User

  -----------------------------------------------------------------------
  Field                               Requirement
  ----------------------------------- -----------------------------------
  ID                                  Primary key

  Employee reference                  Stable seed identifier where
                                      applicable

  Name                                Required

  Email                               Required and unique

  Password hash                       Required for password
                                      authentication; never returned by
                                      API

  Role                                Required; one of `ADMIN`,
                                      `MANAGER`, `AGENT`

  Specialization                      Supported profile field

  Skills                              Supported profile field
  -----------------------------------------------------------------------

### 6.2 Project

  Field         Requirement
  ------------- ------------------------------------
  ID            Primary key
  Name          Required
  Client name   Required
  Description   Required
  Manager       Foreign key to an eligible manager
  Deadline      Required date

### 6.3 Task

  Field             Requirement
  ----------------- ----------------------------------
  ID                Primary key
  Project           Foreign key to project
  Title             Required
  Description       Required
  Assignee          Foreign key to an eligible agent
  Deadline          Required date
  Estimated hours   Required positive numeric value

### 6.4 Transcript Draft and Run Metadata

The implementation shall preserve enough metadata to support preview,
validation, version checks, failure reporting, and idempotency. The
exact persistence strategy for drafts---database records or another
server-side mechanism---must be selected and documented before
implementation.

If a transcript-run record is stored, it should include only necessary
metadata, such as status, draft version, timestamps, validation outcome,
and operation identifier. Raw transcript retention should be minimized
and documented.

### 6.5 Data Integrity

-   Enforce email uniqueness.
-   Enforce valid role values.
-   Enforce foreign-key integrity.
-   Enforce positive estimated hours.
-   Validate manager and agent roles before saving.
-   Validate project/task deadline relationships.
-   Use database transactions for multi-record creation.
-   Add indexes where they materially support common lookups, including
    manager-scoped projects and assignee-scoped tasks.

------------------------------------------------------------------------

## 7. Non-Functional Requirements

### 7.1 Security

**NFR-SEC-001** --- All protected endpoints shall require valid
authentication.\
**NFR-SEC-002** --- Authorization shall be enforced server-side for list
and detail operations.\
**NFR-SEC-003** --- Passwords shall be stored as secure password
hashes.\
**NFR-SEC-004** --- Secrets shall be supplied through environment
configuration or an approved secret store.\
**NFR-SEC-005** --- Secrets and authentication tokens shall not appear
in application logs or AI prompts.\
**NFR-SEC-006** --- AI output shall be treated as untrusted input and
validated before use.\
**NFR-SEC-007** --- Production deployment shall use HTTPS.\
**NFR-SEC-008** --- The API shall validate input types, lengths,
required fields, and relationships.

### 7.2 Reliability and Data Integrity

**NFR-REL-001** --- A multi-record confirmation shall be atomic.\
**NFR-REL-002** --- Repeated confirmation requests shall not create
duplicate records.\
**NFR-REL-003** --- Provider errors shall not result in partial
business-record creation.\
**NFR-REL-004** --- Database constraints and application validation
shall work together to preserve data integrity.

### 7.3 Performance

**NFR-PERF-001** --- Ordinary authenticated read APIs should respond
promptly under the expected small hackathon demo workload.\
**NFR-PERF-002** --- AI extraction latency shall be bounded by
configured timeouts and reported as a controlled failure when exceeded.\
**NFR-PERF-003** --- List endpoints shall avoid unnecessary database
queries and support pagination if the dataset grows.

Specific numerical performance targets are not defined in the supplied
challenge materials and must be agreed if formal load testing is
required.

### 7.4 Maintainability

**NFR-MAINT-001** --- Code shall be organized into clear Django
application boundaries.\
**NFR-MAINT-002** --- AI-provider request logic shall be isolated from
project/task business logic.\
**NFR-MAINT-003** --- Model and dependency versions shall be
documented.\
**NFR-MAINT-004** --- Configuration differences between local
development and deployment shall be handled through environment
settings.\
**NFR-MAINT-005** --- Business rules shall be testable without depending
on live AI responses wherever practical.

### 7.5 Testability

**NFR-TEST-001** --- Authentication and role permissions shall have
automated tests.\
**NFR-TEST-002** --- Cross-user access attempts shall be tested using
direct object identifiers.\
**NFR-TEST-003** --- AI extraction tests shall include mocked provider
responses.\
**NFR-TEST-004** --- Validation tests shall cover invalid references,
missing fields, and deadline violations.\
**NFR-TEST-005** --- Transaction tests shall confirm rollback on
failure.\
**NFR-TEST-006** --- Seed operations shall be repeatable and verifiable.

### 7.6 Usability and Documentation

**NFR-USE-001** --- Validation errors shall be clear enough for an
administrator to correct the draft.\
**NFR-DOC-001** --- The README shall include setup, migrations, seed
instructions, environment variables, demo credentials, and transcript
testing steps.\
**NFR-DOC-002** --- The documentation shall state the limitations and
excluded features.

### 7.7 Privacy and Logging

-   Log operational events needed for troubleshooting and audit.
-   Avoid logging passwords, tokens, API keys, or unnecessary transcript
    contents.
-   Limit retention of transcript data and AI-provider responses to what
    the application needs.
-   Restrict access to operational logs in deployed environments.

------------------------------------------------------------------------

## 8. Error Handling and Recovery

1.  **Invalid transcript or draft:** Return validation findings; do not
    create project/task records.
2.  **Unknown employee:** Reject the affected draft rather than
    inventing or creating a user.
3.  **Invalid deadline or hours:** Return a field-level validation
    error.
4.  **OpenRouter timeout or outage:** Return a controlled
    upstream/service error and permit a safe retry where appropriate.
5.  **Malformed AI output:** Reject the response or use a bounded retry
    policy; do not treat malformed output as valid.
6.  **Draft edited after validation:** Require revalidation before
    confirmation.
7.  **Duplicate confirmation:** Return the prior result or a conflict
    response according to the documented idempotency policy; do not
    duplicate records.
8.  **Database failure during confirmation:** Roll back the transaction
    and return a controlled server error.
9.  **Unauthorized record access:** Do not disclose protected record
    contents.

------------------------------------------------------------------------

## 9. Acceptance Criteria and Test Scenarios

The system shall satisfy the following acceptance checks before the
hackathon demonstration.

### 9.1 Authentication

-   [ ] Each of the ten seeded demo users can authenticate with the
    configured demo credentials.
-   [ ] Invalid credentials are rejected.
-   [ ] Protected endpoints reject missing or invalid tokens.
-   [ ] API responses do not expose password hashes or secrets.

### 9.2 Role-Based Access

-   [ ] Admin can list all three seeded projects and all twelve tasks.
-   [ ] Ayesha Khan can access the UrbanCart Website project but cannot
    access projects managed by other managers.
-   [ ] Bilal Ahmed can access the QuickServe Mobile App project but
    cannot access projects managed by other managers.
-   [ ] Hina Malik can access the HelpDeskPro AI Assistant project but
    cannot access projects managed by other managers.
-   [ ] Ali Raza can see only tasks assigned to Ali, along with
    permitted related project information.
-   [ ] Hamza Shah can see only Hamza's tasks across the projects to
    which those tasks belong.
-   [ ] Direct requests using another user's project or task identifier
    do not bypass authorization.

### 9.3 Transcript Workflow

-   [ ] Admin can submit the supplied meeting transcript and receive a
    draft.
-   [ ] Preview does not create persistent project/task business
    records.
-   [ ] The expected challenge transcript produces three projects and
    twelve tasks after review and confirmation.
-   [ ] Rejected ideas and superseded suggestions are not included as
    agreed tasks.
-   [ ] The AI cannot assign a task to a person who is not in the seeded
    team.
-   [ ] A draft with missing or invalid required fields is not
    confirmable.
-   [ ] Correcting a draft triggers complete revalidation.
-   [ ] Changing a draft after validation invalidates the prior
    validation result.
-   [ ] Confirming a valid draft creates all expected records.
-   [ ] An injected save failure results in rollback rather than partial
    creation.
-   [ ] Repeating a confirmation does not create duplicate records.
-   [ ] Provider timeout and malformed output are handled safely.

### 9.4 Data Persistence

-   [ ] Seeded and created records remain available after an application
    restart.
-   [ ] Project and task foreign-key relationships are correct.
-   [ ] Task deadlines do not exceed parent project deadlines.
-   [ ] The seed operation does not create duplicate demo accounts when
    run repeatedly.

### 9.5 Documentation and Demo

-   [ ] A new developer can configure the environment using the README.
-   [ ] Database migration and seed steps are documented.
-   [ ] OpenRouter configuration is documented without publishing a real
    API key.
-   [ ] Demo credentials and the intended demonstration sequence are
    documented.
-   [ ] Known limitations and excluded features are listed.

------------------------------------------------------------------------

## 10. Seeded Demo Accounts

All account names and email addresses below are fictional challenge
data.

  ------------------------------------------------------------------------------------------
  Reference      Name           Email                        Role           Specialization
  -------------- -------------- ---------------------------- -------------- ----------------
  `ADMIN`        Admin          `admin@novaworks.example`    `ADMIN`        Company
                                                                            overview,
                                                                            transcript
                                                                            creation

  `PM01`         Ayesha Khan    `ayesha@novaworks.example`   `MANAGER`      Web PM

  `PM02`         Bilal Ahmed    `bilal@novaworks.example`    `MANAGER`      Mobile PM

  `PM03`         Hina Malik     `hina@novaworks.example`     `MANAGER`      AI PM

  `DEV01`        Ali Raza       `ali@novaworks.example`      `AGENT`        Full-Stack

  `DEV02`        Hamza Shah     `hamza@novaworks.example`    `AGENT`        Full-Stack

  `DEV03`        Sara Noor      `sara@novaworks.example`     `AGENT`        App Developer

  `DEV04`        Usman Tariq    `usman@novaworks.example`    `AGENT`        App Developer

  `DEV05`        Zain Abbas     `zain@novaworks.example`     `AGENT`        AI Developer

  `DEV06`        Maryam Asif    `maryam@novaworks.example`   `AGENT`        AI Developer
  ------------------------------------------------------------------------------------------

The challenge pack specifies `Demo123!` as the password for each demo
account. These are demo-only credentials and must not be reused in
production. The application shall store only password hashes.

------------------------------------------------------------------------

## 11. Implementation and Delivery Plan

The recommended delivery sequence is:

1.  **Foundation:** Django configuration, PostgreSQL connectivity,
    environment settings, API versioning, and custom user model.
2.  **Authentication and seed data:** JWT flow, role definitions,
    permission foundation, and repeatable demo seeding.
3.  **Project and task APIs:** Models, relationships, serializers, read
    endpoints, and access-scope tests.
4.  **AI integration:** OpenRouter adapter, configurable model,
    structured extraction, provider error handling, and preview
    endpoint.
5.  **Draft lifecycle:** Server-side draft/version management, edit
    validation, confirmation checks, and idempotency.
6.  **Transactional persistence:** Atomic project/task creation and
    rollback tests.
7.  **Documentation and demo readiness:** README, environment template,
    test instructions, acceptance run-through, and demonstration
    preparation.

The implementation shall prioritize the required MVP over optional
features.

------------------------------------------------------------------------

## 12. Open Decisions to Resolve During Detailed Design

The high-level architecture is finalized, but the following
implementation details require explicit choices before or during
development:

1.  The exact OpenRouter model identifier and its structured-output
    capabilities.
2.  The precise draft storage and expiration policy.
3.  The idempotency-key format, retention window, and replay-response
    behavior.
4.  Maximum transcript size, task-count limits, and estimated-hours
    bounds.
5.  JWT access/refresh lifetimes and whether refresh-token blacklisting
    is enabled.
6.  Pagination defaults and filtering/sorting options.
7.  Whether audit records retain transcript text or only metadata.
8.  The deployment platform and any numerical performance targets.

These choices shall be documented; they must not silently weaken the
functional or security requirements in this SRS.

------------------------------------------------------------------------

## 13. Definition of Done

The backend is ready for the intended hackathon demonstration when:

-   The documented setup works from a clean environment.
-   PostgreSQL migrations and demo seeding succeed.
-   Authentication and role-scoped access tests pass.
-   The administrator can preview, validate, edit, and confirm the
    required transcript workflow.
-   The expected three projects and twelve tasks are saved correctly and
    atomically.
-   Invalid, stale, unauthorized, or duplicate requests are handled
    safely.
-   The application does not expose secrets in API responses, logs, or
    AI prompts.
-   The README and demo instructions are complete.
-   The team can explain the architecture, security boundaries,
    validation process, and limitations.

------------------------------------------------------------------------

**End of document**
