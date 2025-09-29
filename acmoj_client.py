#!/usr/bin/env python3
# -- coding: utf-8 --
"""
ACMOJ API 客户端命令行工具 v2.1
"""
import requests
import json
import time
import argparse
import os
from typing import Dict, Any, Optional

class ACMOJClient:
    def __init__(self, access_token: str):
        self.api_base = "https://acm.sjtu.edu.cn/OnlineJudge/api/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "ACMOJ-Python-Client/2.1"
        }

    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Optional[Dict]:
        url = f"{self.api_base}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, data=data, timeout=10)
            else:
                print(f"Unsupported HTTP method: {method}")
                return None

            if response.status_code == 204:
                return {"status": "success", "message": "Operation successful"}
            
            response.raise_for_status()

            if response.content:
                return response.json()
            else:
                return {"status": "success"}
        except requests.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            if 'response' in locals() and response:
                print(f"Response text: {response.text}")
            return None

    def submit_solution(self, problem_id: int, language: str, code: str) -> Optional[Dict]:
        data = {"language": language, "code": code}
        return self._make_request("POST", f"/problem/{problem_id}/submit", data=data)

    def get_submission_detail(self, submission_id: int) -> Optional[Dict]:
        return self._make_request("GET", f"/submission/{submission_id}")

def main():
    parser = argparse.ArgumentParser(description="ACMOJ API Command Line Client")
    parser.add_argument("--token", help="ACMOJ Access Token", default=os.environ.get("ACMOJ_TOKEN"))
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command for submitting a solution
    submit_parser = subparsers.add_parser("submit", help="Submit a solution")
    submit_parser.add_argument("--problem-id", type=int, required=True, help="Problem ID")
    submit_parser.add_argument("--language", type=str, required=True, help="Language (e.g., cpp, python)")
    submit_parser.add_argument("--code-file", type=str, required=True, help="Path to the code file")

    # Sub-command for checking submission status
    status_parser = subparsers.add_parser("status", help="Check submission status")
    status_parser.add_argument("--submission-id", type=int, required=True, help="Submission ID")

    args = parser.parse_args()

    if not args.token:
        print("Error: Access token not provided. Use --token or set ACMOJ_TOKEN environment variable.")
        return

    client = ACMOJClient(args.token)

    if args.command == "submit":
        try:
            with open(args.code_file, 'r', encoding='utf-8') as f:
                code = f.read()
            result = client.submit_solution(args.problem_id, args.language, code)
        except FileNotFoundError:
            print(f"Error: Code file not found at {args.code_file}")
            result = None
    
    elif args.command == "status":
        result = client.get_submission_detail(args.submission_id)

    if result:
        print(json.dumps(result))
    else:
        # Exit with a non-zero status code to indicate failure to shell scripts
        exit(1)

if __name__ == "__main__":
    main()
