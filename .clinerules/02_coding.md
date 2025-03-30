## Code style

- Prefer composition over inheritance.
- Organize code into distinct layers or services.
- Use repository pattern for data access.
- Minimize direct dependencies between system parts.
- Decouple services using events.
- Use descriptive names for files, functions, and variables.
- Adhere to the style guide and idioms of the applicable programming language.
- Ignore line length code actions.
- Ignore spacing code actions.

## Code documentation

- Use only one set of triple quotes for docstrings.
- Write clear, concise comments for all sections of code.
- Succintly comment the purpose and usage of functions, classes and modules.
- Comment the data types of function arguments and return values.
- Do NOT prioritise code completion over documentation.

## Code structure and organization

- Keep files small and modular.
- Split large components into smaller, manageable parts.
- Move constants, configurations, and long strings to separate files.

## Credential Management

- Explain the purpose of each credential when requesting from users.
- Guide users to obtain any missing credentials.
- Always test the validity of credentials before using them.
- Implement proper refresh procedures for expiring credentials.
- Provide guidance on secure credential storage methods.

## Third-Party Services Integration

- Verify that the user has completed all setup requirements for each service.
- Check all necessary permissions and settings.
- Test service connections before using them in workflows.
- Document version requirements and service dependencies.
- Prepare contingency plans for potential service outages or failures.

## Error handling and reporting

- Implement detailed and actionable error reporting.
- Log errors with context and timestamps.
- Provide users with clear steps for error recovery.
- Track error history to identify patterns.
- Implement escalation procedures for unresolved issues.
- Ensure all systems have robust error handling mechanisms.

## Security Best Practices

- Implement proper authentication and authorization mechanisms.
- Use secure communication protocols (HTTPS) for all network interactions.
- Sanitize and validate all user inputs to prevent injection attacks.
- Regularly update dependencies to patch known vulnerabilities.
- Follow the principle of least privilege in system design.
- DO NOT read or modify any file containing API keys, tokens, or credentials.
- Never commit sensitive files.
- Keep credentials out of logs and output.
- Never store credentials in plaintext; use environment variables.

## Performance Optimization

- Optimize database queries for efficiency.
- Implement caching strategies where appropriate.
- Minimize network requests and payload sizes.
- Use asynchronous operations for I/O-bound tasks.
- Regularly profile the application to identify and address performance bottlenecks.

## Compliance and Standards

- Ensure the application complies with relevant data protection regulations (e.g., GDPR, CCPA).
- Follow accessibility standards (WCAG) to make the application usable by people with disabilities.
- Adhere to industry-standard coding conventions and style guides.

## Testing and Quality Assurance

- Implement comprehensive unit tests for all components.
- Perform integration testing to ensure different parts of the system work together.
- Conduct thorough end-to-end testing to validate user workflows.
- Maintain high test coverage.
- Test edge cases and boundary conditions.
- Include negative tests for API errors and unexpected inputs.

## Dependencies and Libraries

- Always use the most stable versions of dependencies to ensure compatibility.
- Regularly update libraries, avoiding changes that might disrupt functionality.

## Execution environment

- Hardware: MacBook Air M1 with macOS Sonoma 14.7.
- Software: Python 3.10 and VS Code 1.98.2 (Universal) with extensions: Home Assistant Config Helper, Jinja, YAML, Flake8, Pylance, GitHub Pull Requests, GitLens and GitHub Actions.
