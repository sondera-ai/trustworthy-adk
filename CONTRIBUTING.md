# Contributing to Trustworthy ADK

Thank you for your interest in contributing to the Trustworthy Agent Development Kit! This project aims to make AI agents more secure and trustworthy, and we welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Provide clear, detailed descriptions with steps to reproduce
- Include relevant code snippets, error messages, and environment details
- Check existing issues to avoid duplicates

### Submitting Changes

1. **Fork the repository** and create a feature branch
2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/trustworthy-adk.git
cd trustworthy-adk

# Install in development mode with all dependencies
uv pip install -e ".[dev]"

# Run tests to ensure everything works
uv run pytest
```

### Development Dependencies

The development environment includes:

- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting and code analysis
- **mypy**: Type checking
- **coverage**: Test coverage analysis

## 📝 Coding Standards

### Code Style

- Follow [PEP 8](https://pep8.org/) Python style guidelines
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [Ruff](https://docs.astral.sh/ruff/) for linting
- Maximum line length: 88 characters (Black default)

```bash
# Format code
uv run black src/ tests/

# Check linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### Documentation

- Use clear, descriptive docstrings for all public functions and classes
- Follow [Google style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Include type hints for all function parameters and return values
- Update README.md for significant changes

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/trustworthy --cov-report=html

# Run specific test file
uv run pytest tests/test_action_selector_agent.py -v
```

## 🔒 Security Considerations

This project focuses on security, so special attention is required:

### Security Review Process

- All security-related changes require thorough review
- Include threat model considerations in your PR description
- Test against known attack vectors when applicable
- Document security assumptions and limitations

### Sensitive Information

- Never commit API keys, secrets, or credentials
- Use mock data for examples and tests
- Sanitize any real-world data used in examples
- Be mindful of information disclosure in error messages

### Security Testing

- Test defensive mechanisms against bypass attempts
- Include adversarial test cases
- Validate input sanitization and validation
- Test error handling and edge cases

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines (Black + Ruff)
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated as needed
- [ ] Security implications considered
- [ ] No secrets or sensitive data committed

### PR Description Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Security Impact
Describe any security implications of this change.

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added and passing
```

## 🏗️ Project Structure

### Adding New Components

When adding new security components:

1. **Agents**: Add to `src/trustworthy/agents/`
2. **Plugins**: Add to `src/trustworthy/plugins/`
3. **Analysis Tools**: Add to `src/trustworthy/analysis/`
4. **Examples**: Add to `examples/` with documentation

### File Organization

- Keep related functionality together
- Use clear, descriptive module names
- Include `__init__.py` files with proper exports
- Add comprehensive docstrings to all modules

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Security Tests**: Test defensive mechanisms
4. **Example Tests**: Ensure examples work correctly

### Test Data

- Use realistic but sanitized test data
- Include edge cases and error conditions
- Test both valid and invalid inputs
- Mock external dependencies appropriately

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **API Documentation**: Function and class documentation
3. **User Documentation**: README and usage examples
4. **Developer Documentation**: This file and architecture docs

### Documentation Standards

- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include practical examples
- Document security considerations and limitations

## 🚀 Release Process

### Version Management

- Follow [Semantic Versioning](https://semver.org/)
- Update version in `pyproject.toml` and `src/trustworthy/__init__.py`
- Create release notes highlighting security improvements

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Version numbers updated
- [ ] Release notes prepared

## 🆘 Getting Help

### Community Support

- **GitHub Discussions**: For questions and general discussion
- **GitHub Issues**: For bug reports and feature requests
- **Security Issues**: Email security@[domain] for sensitive security issues

### Resources

- [Google ADK Documentation](https://developers.google.com/adk)
- [Python Security Best Practices](https://python.org/dev/security/)
- [OWASP AI Security Guide](https://owasp.org/www-project-ai-security-and-privacy-guide/)

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- Release notes for significant contributions
- README acknowledgments section
- Project documentation

Thank you for helping make AI agents more secure and trustworthy! 🛡️