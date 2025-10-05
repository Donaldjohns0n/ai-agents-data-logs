# Logs Directory

Centralized logging for all AI agent activities and system operations.

## Structure

- **access/**: User and system access logs
- **audit/**: Security and compliance audit logs
- **error/**: Error logs and exception tracking
- **performance/**: Performance metrics and monitoring logs

## Log Formats

All logs follow structured JSON format for consistent parsing and analysis:
- ISO 8601 timestamps
- Agent identification
- Operation context
- Severity levels
- Correlation IDs for distributed tracing