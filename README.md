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

## Automated Tests

Run the automated unit tests from the repository root:

```bash
python3 -m unittest -v
```

The test suite contains five tests covering:

- Detection of the CSP `frame-ancestors` directive
- Case-insensitive directive matching
- Handling of a missing directive
- Rejection of unsupported URL schemes
- Rejection of invalid URL input

Run a Python syntax check with:

```bash
python3 -m py_compile header_checker.py
```

## Responsible Use

Test only websites and systems you own or have explicit permission
to assess. Respect the target's scope and rules of engagement.


## IP Address Validator

### Purpose
A small Python utility that validates IPv4 and IPv6 address input.

### Features
- Accepts an IP address from the user.
- Validates IPv4 and IPv6 using Python's built-in `ipaddress` module.
- Handles invalid input with a clear error message.

### Requirements
- Python 3
- No external packages required.

### Usage
Run from the repository directory:

`python3 ip_validator.py`

### Examples

**Valid IPv4:**
Input: `192.168.1.10`
Output: `Valid IP address: 192.168.1.10`

**Valid IPv6:**
Input: `2001:db8::1`
Output: `Valid IP address: 2001:db8::1`

**Invalid input:**
Input: `hello`
Output: `Invalid IP address.`

### Limitation
This tool validates IP address syntax only. It does not check whether a host is online, scan ports, or test network reachability.
