# Infoys / CareerCast

CareerCast is the AI-powered career exploration application in
[`careercast/`](careercast/). Start with the [project guide](careercast/README.md).

The UI has been rebuilt around the supplied navy/lavender references, and
milestone 1 and 2 training, parsing, prediction, ranking, and evaluation workflows
have been added. **Not every benchmark acceptance target is met.** See
[the milestone report](careercast/MILESTONES.md) for measured results and limits.

`careercast.zip` is the updated source distribution. It excludes personal
resume uploads, local databases, dependencies, and large training checkpoints.

## Authentication

CareerCast uses **FastAPI email/password authentication**, **bcrypt password
hashing through Passlib**, and **HS256 JWT access tokens through python-jose**.
Tokens expire after eight hours. React AuthContext manages the browser session,
and Axios sends bearer tokens to protected API endpoints. Account data is scoped
to the signed-in user through SQLAlchemy (SQLite by default).

See the [authentication details](careercast/README.md#authentication) for the
login flow, token storage, logout behavior, and current limitations.
