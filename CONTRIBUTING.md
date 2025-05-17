# Contributing to Bill Calculator

Thank you for considering contributing to this project! Your help is appreciated. Please follow these guidelines to ensure a smooth process for everyone.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Write clear, concise code** and include docstrings and type annotations where appropriate.
3. **Add or update tests** for any new features or bug fixes.
4. **Run all tests** and ensure they pass before submitting a pull request.
5. **Lint your code** using `pylint` or your preferred linter.
6. **Document your changes** in the README or relevant documentation files if necessary.

## Adding New Bill Types or Output Strategies
- To add a new bill type, create a subclass of `Bill` in `src/bill_type.py` and implement the `calculate` method.
- To add a new output strategy, create a subclass of `OutputStrategy` in `src/output_strategy.py` and implement the `output` method.
- Update the main application logic in `main.py` to use your new class if needed.

## Submitting a Pull Request
1. Push your branch to your fork.
2. Open a pull request against the `main` branch.
3. Provide a clear description of your changes and reference any related issues.

## Code of Conduct
Please be respectful and considerate in your communications and code reviews.

---
*Last updated: May 2025*
