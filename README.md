# Python HTTP Security Header Checker

A Python command-line tool that inspects selected HTTP security
response headers on a specified web target.

## Features

- Sends an HTTP GET request to a supplied URL.
- Displays the final URL and HTTP status code.
- Checks for Strict-Transport-Security.
- Checks for Content-Security-Policy.
- Checks for X-Content-Type-Options.
- Looks for framing protection through X-Frame-Options or
  the CSP frame-ancestors directive.
- Checks Referrer-Policy and Permissions-Policy.
- Handles invalid URL schemes and common request errors.
- Uses a request timeout.

## Requirements

- Python 3.10 or later
- No third-party Python packages required

## Usage

Run the tool with:

    python3 header_checker.py https://example.com

Display command-line help:

    python3 header_checker.py --help

Check Python syntax:

    python3 -m py_compile header_checker.py

## How It Works

The program sends one GET request, inspects the received response
headers, and prints whether selected headers are present or missing.

## Limitations

This is a basic learning tool. It does not perform a full security
assessment or prove that a website is vulnerable. A missing header
must be evaluated in the context of the application and its security
requirements. Header values are not comprehensively audited.

## Testing Performed

- Valid HTTPS URL
- Unsupported URL scheme
- Invalid URL input
- Python syntax compilation

## Responsible Use

Test only websites and systems you own or have explicit permission
to assess. Respect the target's scope and rules of engagement.
