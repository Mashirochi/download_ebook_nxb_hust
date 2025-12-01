# Contributing to Ebook Downloader

Thank you for your interest in contributing to the Ebook Downloader project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Question or Problem?](#question-or-problem)
- [Issues and Bugs](#issues-and-bugs)
- [Feature Requests](#feature-requests)
- [Submission Guidelines](#submission-guidelines)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Coding Rules](#coding-rules)
- [Commit Message Guidelines](#commit-message-guidelines)

## Question or Problem?

If you have a question or need help with the project:

1. Check the [README.md](README.md) file for documentation
2. Search existing [issues](https://github.com/Mashirochi/download_ebook_nxb_hust/issues) to see if your question has already been answered
3. If you still need help, [open a new issue](https://github.com/Mashirochi/download_ebook_nxb_hust/issues/new) with a clear title and detailed description

## Issues and Bugs

If you find a bug or issue in the project:

1. Search existing [issues](https://github.com/Mashirochi/download_ebook_nxb_hust/issues) to see if it has already been reported
2. If not, [create a new issue](https://github.com/Mashirochi/download_ebook_nxb_hust/issues/new)
3. Provide a clear title and detailed description
4. Include steps to reproduce the issue
5. If possible, provide:
   - Screenshots or error messages
   - Your operating system and Python version
   - The ebook URL you were trying to download (if applicable)

## Feature Requests

We welcome suggestions for new features or improvements:

1. Search existing [issues](https://github.com/Mashirochi/download_ebook_nxb_hust/issues) to see if the feature has already been requested
2. If not, [create a new issue](https://github.com/Mashirochi/download_ebook_nxb_hust/issues/new)
3. Provide a clear title and detailed description of the proposed feature
4. Explain why this feature would be useful
5. If possible, provide examples of how the feature would work

## Submission Guidelines

### Submitting an Issue

Before submitting an issue, please:

1. Search existing issues to avoid duplicates
2. Use a clear and descriptive title
3. Include as much relevant information as possible
4. Provide step-by-step instructions to reproduce the issue

### Submitting a Pull Request

1. Fork the repository
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the [Coding Rules](#coding-rules)
4. Commit your changes following the [Commit Message Guidelines](#commit-message-guidelines)
5. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Create a pull request from your fork to the main repository
7. Provide a clear title and description for your pull request
8. Link any related issues in your pull request description

## Pull Request Guidelines

Before submitting a pull request:

1. Ensure your changes are based on the latest version of the main branch
2. Test your changes thoroughly
3. Update documentation if necessary
4. Follow the project's coding standards
5. Include appropriate comments in your code
6. Write clear commit messages
7. Keep pull requests focused on a single feature or bug fix

## Coding Rules

To ensure consistency throughout the project, please follow these rules:

1. Use clear and descriptive variable names
2. Add comments to explain complex logic
3. Follow Python PEP 8 style guidelines
4. Write docstrings for functions and classes
5. Keep functions small and focused on a single task
6. Handle errors gracefully with appropriate error messages
7. Test your code before submitting

## Commit Message Guidelines

We follow conventional commit messages to maintain a clear history:

### Commit Message Format

```
<type>(<scope>): <subject>

<body>
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks, build changes, etc.

### Examples

```
feat(downloader): add support for new ebook format

Added support for downloading EPUB files in addition to PDF
```

```
fix(auth): resolve cookie expiration issue

Fixed issue where expired cookies were not being refreshed
```

```
docs(readme): update installation instructions

Added more detailed steps for cookie extraction process
```

Thank you for contributing to Ebook Downloader!
