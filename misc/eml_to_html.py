#!/usr/bin/env python3
from email import policy
from email.parser import BytesParser
import sys

with open(sys.argv[1], "rb") as f:
    msg = BytesParser(policy=policy.default).parse(f)

body = msg.get_body(preferencelist=('html'))

if body:
    print(body.get_content())
