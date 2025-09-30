# Contributing to Knowledge Bot

Thank you for your interest in contributing to Knowledge Bot! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/Knowledge-Bot.git
   cd Knowledge-Bot
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

3. **Run locally**
   ```bash
   python main.py
   ```

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to functions and classes
- Keep functions focused and small
- Use descriptive variable names

## 🧪 Testing

Before submitting a PR:

1. Test your changes locally
2. Ensure the bot starts without errors
3. Test with actual video URLs
4. Verify Notion integration works
5. Check logs for errors

## 📦 Commit Guidelines

Use clear, descriptive commit messages:

```
feat: Add support for YouTube videos
fix: Resolve session cleanup memory leak
docs: Update README with deployment instructions
refactor: Improve video download error handling
```

Prefix types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

## 🔍 Pull Request Process

1. **Update documentation** if needed
2. **Test thoroughly** before submitting
3. **Describe your changes** clearly in the PR description
4. **Link related issues** if applicable
5. **Be responsive** to review feedback

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are tested locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description** - Clear description of the issue
2. **Steps to reproduce** - How to trigger the bug
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - Python version, OS, etc.
6. **Logs** - Relevant error logs

## 💡 Feature Requests

For feature requests:

1. Check if it's already requested
2. Describe the feature clearly
3. Explain the use case
4. Suggest implementation approach (optional)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the project
- Accept criticism gracefully

## 📞 Questions?

- Open an issue for technical questions
- Tag maintainers for urgent matters
- Check existing issues first

## 🎯 Priority Areas

We especially welcome contributions in:

- Additional video platform support
- Enhanced image generation
- Improved error handling
- Better test coverage
- Documentation improvements
- Performance optimizations

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Knowledge Bot! 🤖✨
