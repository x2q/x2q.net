---
categories:
- XML
- Bash
- CLI
comments: true
date: "2012-11-20T00:00:00Z"
title: Pretty Printing XML with xmllint
---

Yesterday I was doing some tests towards Visa 3-D Secure test directory url, which responds in XML format.
    curl -s -X POST -d @vereq.xml --cert visa.crt \
    --key visa.key https://dropit.3dsecure.net:8443/PIT/DS

The raw response looked like this:
    <?xml version="1.0" encoding="UTF-8"?><ThreeDSecure><Message id="999"><VERes><version>1.0.2</version><CH><enrolled>Y</enrolled><acctID>A0fTY+pKUTs3A4AjhdYQ+g==</acctID></CH><url>https://dropit.3dsecure.net:9443/PIT/ACS</url><protocol>ThreeDSecure</protocol></VERes></Message></ThreeDSecure>

I used xmllint to pretty print the raw response:
    xmllint -format veres.xml --output -

and the pretty printed looked like this:
    <?xml version="1.0" encoding="UTF-8"?>
    <ThreeDSecure>
      <Message id="999">
        <VERes>
          <version>1.0.2</version>
          <CH>
            <enrolled>Y</enrolled>
            <acctID>A0fTY+pKUTv+96d4nonZQA==</acctID>
          </CH>
          <url>https://dropit.3dsecure.net:9443/PIT/ACS</url>
          <protocol>ThreeDSecure</protocol>
        </VERes>
      </Message>
    </ThreeDSecure>
